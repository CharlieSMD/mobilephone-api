#!/usr/bin/env python3
"""
Backfill phone Colors for records where Colors is NULL or empty.
Primary source: GSMArena (Colors field). Fallback: ZOL (Chinese "颜色/配色").
Dry-run supported.
"""

import os
import re
import sys
import time
import logging
from typing import Optional, Dict, List

import psycopg2
import requests
from bs4 import BeautifulSoup


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backfill_colors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


DB_CONFIG = {
    'host': 'localhost',
    'database': 'mobilephone_db',
    'user': 'postgres'
}


class ColorBackfiller:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.base_delay_seconds = 6.0  # base polite delay between requests
        self.max_retries = 5

    def request_with_backoff(self, method: str, url: str, **kwargs):
        import random
        delay = 30.0  # start higher for rate limits
        last_exc = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.request(method, url, timeout=kwargs.pop('timeout', 25), **kwargs)
                if resp.status_code == 429:
                    jitter = random.uniform(-2.0, 2.0)
                    sleep_s = max(5.0, delay + jitter)
                    logger.warning(f"429 Too Many Requests for {url} (attempt {attempt}); sleeping {sleep_s:.1f}s")
                    time.sleep(sleep_s)
                    delay = min(180.0, delay * 2)
                    continue
                resp.raise_for_status()
                # Small polite delay between successful requests
                polite = max(3.0, self.base_delay_seconds + random.uniform(-2.0, 2.0))
                time.sleep(polite)
                return resp
            except requests.exceptions.RequestException as e:
                last_exc = e
                jitter = random.uniform(-2.0, 2.0)
                sleep_s = max(5.0, delay + jitter)
                logger.warning(f"Request error for {url} (attempt {attempt}): {e}; sleeping {sleep_s:.1f}s")
                time.sleep(sleep_s)
                delay = min(180.0, delay * 2)
        if last_exc:
            raise last_exc
        return None

    def get_targets(self, limit: Optional[int] = None, brand_like: Optional[str] = None, model_like: Optional[str] = None) -> List[Dict]:
        clauses = ["(\"Colors\" IS NULL OR LENGTH(BTRIM(COALESCE(\"Colors\", ''))) = 0)"]
        params: List = []
        if brand_like:
            clauses.append('LOWER("Brand") LIKE LOWER(%s)')
            params.append(f"%{brand_like}%")
        if model_like:
            clauses.append('LOWER("Model") LIKE LOWER(%s)')
            params.append(f"%{model_like}%")

        where_sql = ' AND '.join(clauses)
        query = f'''
            SELECT "Id", "Brand", "Model"
            FROM "Phones"
            WHERE {where_sql}
            ORDER BY "Brand", "Model"
        '''
        if limit:
            query += f"\nLIMIT {int(limit)}"

        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                return [ {'id': r[0], 'brand': r[1], 'model': r[2]} for r in rows ]

    def search_gsmarena(self, brand: str, model: str) -> Optional[str]:
        base = 'https://www.gsmarena.com'
        search_url = f'{base}/results.php3'
        # Normalize query: avoid duplicate brand words, keep key tokens
        query = f"{brand} {model}".strip()
        params = {'sQuickSearch': 'yes', 'sName': query}
        try:
            r = self.request_with_backoff('GET', search_url, params=params)
            soup = BeautifulSoup(r.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                text = a.get_text(strip=True).lower()
                if not href or not href.endswith('.php'):
                    continue
                # Heuristic: must contain brand and at least one digit from model if exists
                brand_ok = brand.lower() in text
                digits = re.findall(r'\d+', model)
                digit_ok = True if not digits else any(d in text for d in digits)
                if brand_ok and digit_ok:
                    return f'{base}/{href}'
        except Exception as e:
            logger.warning(f"GSMArena search failed for {brand} {model}: {e}")
        return None

    def extract_colors_gsmarena(self, url: str) -> Optional[str]:
        try:
            r = self.request_with_backoff('GET', url)
            soup = BeautifulSoup(r.content, 'html.parser')

            # Preferred: data-spec="colors"
            colors_elem = soup.find(attrs={'data-spec': 'colors'})
            if colors_elem:
                text = colors_elem.get_text(separator=' ', strip=True)
                if text:
                    return text

            # Fallback: rows labeled 'Colors'
            for row in soup.find_all('tr'):
                header = row.find('th') or row.find('td')
                if not header:
                    continue
                key = header.get_text(separator=' ', strip=True)
                if key and 'colors' in key.lower():
                    # Value often in td with class 'nfo'
                    nfos = row.find_all('td')
                    if nfos:
                        val = nfos[-1].get_text(separator=' ', strip=True)
                        if val:
                            return val

            # Last resort: any element whose text starts with 'Colors'
            for elem in soup.find_all(text=True):
                s = elem.strip()
                if s.lower().startswith('colors'):
                    # try sibling text
                    parent = elem.parent
                    if parent and parent.next_sibling:
                        val = parent.next_sibling.get_text(separator=' ', strip=True)
                        if val:
                            return val
        except Exception as e:
            logger.warning(f"GSMArena extract failed for {url}: {e}")
        return None

    def extract_colors_zol(self, brand: str, model: str) -> Optional[str]:
        # Minimal fallback using site search is complex; skip unless needed
        return None

    def normalize_colors(self, colors_text: str) -> str:
        # Split on commas or slashes, trim, dedupe, cap length
        raw = re.split(r'[\,/]|\s{2,}', colors_text)
        cleaned = []
        seen = set()
        for c in raw:
            name = c.strip().strip('.;:')
            if not name:
                continue
            key = name.lower()
            if key not in seen:
                seen.add(key)
                cleaned.append(name)
        result = ', '.join(cleaned)
        return result[:480]

    def update_colors(self, phone_id: int, colors: str, dry_run: bool = True) -> bool:
        if dry_run:
            logger.info(f"[DRY-RUN] Would update Id={phone_id} Colors='{colors}'")
            return True
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute('UPDATE "Phones" SET "Colors" = %s WHERE "Id" = %s', (colors, phone_id))
                    conn.commit()
                    return cur.rowcount == 1
        except Exception as e:
            logger.error(f"DB update failed for {phone_id}: {e}")
            return False

    def backfill(self, limit: Optional[int] = None, dry_run: bool = True, brand_like: Optional[str] = None, model_like: Optional[str] = None):
        targets = self.get_targets(limit=limit, brand_like=brand_like, model_like=model_like)
        logger.info(f"Found {len(targets)} phones missing colors")
        success = 0
        for i, t in enumerate(targets, 1):
            brand, model, pid = t['brand'], t['model'], t['id']
            logger.info(f"({i}/{len(targets)}) {brand} {model}")
            url = self.search_gsmarena(brand, model)
            if not url:
                logger.info("No GSMArena match; skipping")
                continue
            colors = self.extract_colors_gsmarena(url)
            if not colors:
                logger.info("No colors found on GSMArena; skipping")
                continue
            norm = self.normalize_colors(colors)
            if not norm:
                logger.info("Colors normalized to empty; skipping")
                continue
            if self.update_colors(pid, norm, dry_run=dry_run):
                success += 1
            # Additional spacing between items
            import random
            time.sleep(max(3.0, self.base_delay_seconds + random.uniform(-2.0, 2.0)))
        logger.info(f"Completed. Updated={success} / {len(targets)}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Backfill Colors for phones with empty Colors field')
    parser.add_argument('--limit', type=int, default=20, help='Limit number of phones to process')
    parser.add_argument('--apply', action='store_true', help='Apply changes (disable dry-run)')
    parser.add_argument('--brand', type=str, default=None, help='Filter brand (LIKE match)')
    parser.add_argument('--model', type=str, default=None, help='Filter model (LIKE match)')
    args = parser.parse_args()

    bf = ColorBackfiller()
    bf.backfill(limit=args.limit, dry_run=not args.apply, brand_like=args.brand, model_like=args.model)


if __name__ == '__main__':
    main()


