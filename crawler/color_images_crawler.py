#!/usr/bin/env python3
"""
Color Images Crawler
Crawl color variant images for phones
Supports GSMArena and ZOL websites
"""

import os
import re
import sys
import time
import logging
import json
import requests
from typing import Optional, Dict, List, Tuple
from urllib.parse import urljoin, urlparse
import psycopg2
from bs4 import BeautifulSoup

# Get parent directory of script location (project root)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
IMAGES_DIR = os.path.join(PROJECT_ROOT, "images", "phones")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('color_images_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'mobilephone_db',
    'user': 'postgres'
}

class ColorImagesCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.base_delay_seconds = 8.0  # Increase to 8 seconds for safety
        self.max_retries = 5
        
        # 确保图片目录存在
        os.makedirs(IMAGES_DIR, exist_ok=True)

    def request_with_backoff(self, method: str, url: str, **kwargs):
        """带退避的请求方法"""
        import random
        delay = 30.0
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
                # 礼貌延迟
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

    def get_phones_with_colors(self, limit: Optional[int] = None, brand_like: Optional[str] = None) -> List[Dict]:
        """获取有颜色信息但缺少颜色图片的手机"""
        clauses = [
            '"Colors" IS NOT NULL',
            'LENGTH(BTRIM(COALESCE("Colors", \'\'))) > 0',
            '("ColorImages" IS NULL OR LENGTH(BTRIM(COALESCE("ColorImages", \'\'))) = 0)'
        ]
        params: List = []
        
        if brand_like:
            clauses.append('LOWER("Brand") LIKE LOWER(%s)')
            params.append(f"%{brand_like}%")

        where_sql = ' AND '.join(clauses)
        query = f'''
            SELECT "Id", "Brand", "Model", "Colors"
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
                return [{'id': r[0], 'brand': r[1], 'model': r[2], 'colors': r[3]} for r in rows]

    def search_gsmarena(self, brand: str, model: str) -> Optional[str]:
        """在GSMArena搜索手机页面"""
        base = 'https://www.gsmarena.com'
        search_url = f'{base}/results.php3'
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
                
                # 匹配品牌和型号
                brand_ok = brand.lower() in text
                digits = re.findall(r'\d+', model)
                digit_ok = True if not digits else any(d in text for d in digits)
                
                if brand_ok and digit_ok:
                    return f'{base}/{href}'
        except Exception as e:
            logger.warning(f"GSMArena search failed for {brand} {model}: {e}")
        return None

    def extract_color_images_gsmarena(self, url: str, colors: str) -> Dict[str, str]:
        """从GSMArena页面提取颜色图片"""
        color_images = {}
        color_list = [c.strip() for c in colors.split(',')]
        
        try:
            r = self.request_with_backoff('GET', url)
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # 查找图片库部分
            gallery_section = soup.find('div', class_='article-info-meta')
            if not gallery_section:
                gallery_section = soup.find('div', {'id': 'pictures'})
            
            if gallery_section:
                # 查找所有图片链接
                img_links = gallery_section.find_all('a', href=True)
                for link in img_links:
                    href = link.get('href')
                    if href and ('pictures' in href or 'gallery' in href):
                        # 进入图片库页面
                        gallery_url = urljoin(url, href)
                        gallery_images = self.extract_gallery_images(gallery_url, color_list)
                        color_images.update(gallery_images)
            
            # 如果没找到图片库，尝试从主页面查找
            if not color_images:
                color_images = self.extract_main_page_images(soup, color_list, url)
                
        except Exception as e:
            logger.warning(f"GSMArena color images extraction failed for {url}: {e}")
        
        return color_images

    def extract_gallery_images(self, gallery_url: str, color_list: List[str]) -> Dict[str, str]:
        """从图片库页面提取颜色图片"""
        color_images = {}
        
        try:
            r = self.request_with_backoff('GET', gallery_url)
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # 查找图片元素
            img_elements = soup.find_all('img', src=True)
            for img in img_elements:
                src = img.get('src')
                alt = img.get('alt', '').lower()
                title = img.get('title', '').lower()
                
                # 匹配颜色 - 改进的匹配逻辑
                for color in color_list:
                    color_lower = color.lower()
                    
                    # 更严格的匹配条件
                    # 1. 图片尺寸应该合理（不是缩略图）
                    # 2. 颜色名称应该在alt或title中明确出现
                    # 3. 排除新闻图片和广告图片
                    if (color_lower in alt or color_lower in title) and \
                       'news' not in src.lower() and \
                       'ad' not in src.lower() and \
                       'banner' not in src.lower():
                        
                        # 检查图片尺寸，优先选择较大的图片
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            src = 'https://www.gsmarena.com' + src
                        
                        # 如果还没有这个颜色的图片，或者找到更大的图片，则更新
                        if color not in color_images or self.is_better_image(src, color_images[color]):
                            color_images[color] = src
                        
        except Exception as e:
            logger.warning(f"Gallery images extraction failed for {gallery_url}: {e}")
        
        return color_images

    def is_better_image(self, new_src: str, current_src: str) -> bool:
        """比较两个图片URL，判断新的是否更好"""
        # 简单的启发式规则：优先选择更大的图片
        # 通过URL中的尺寸信息判断
        import re
        
        # 提取尺寸信息
        new_dims = re.findall(r'(\d+)x(\d+)', new_src)
        current_dims = re.findall(r'(\d+)x(\d+)', current_src)
        
        if new_dims and current_dims:
            new_w, new_h = map(int, new_dims[0])
            current_w, current_h = map(int, current_dims[0])
            new_area = new_w * new_h
            current_area = current_w * current_h
            return new_area > current_area
        
        # 如果没有尺寸信息，优先选择不包含"thumb"或"small"的图片
        if 'thumb' in new_src.lower() or 'small' in new_src.lower():
            return False
        if 'thumb' in current_src.lower() or 'small' in current_src.lower():
            return True
        
        return False

    def extract_main_page_images(self, soup: BeautifulSoup, color_list: List[str], base_url: str) -> Dict[str, str]:
        """从主页面提取颜色图片"""
        color_images = {}
        
        # 查找所有图片
        img_elements = soup.find_all('img', src=True)
        for img in img_elements:
            src = img.get('src')
            alt = img.get('alt', '').lower()
            title = img.get('title', '').lower()
            
            # 匹配颜色
            for color in color_list:
                color_lower = color.lower()
                if (color_lower in alt or color_lower in title or 
                    color_lower in src.lower()):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://www.gsmarena.com' + src
                    
                    color_images[color] = src
                    break
        
        return color_images

    def download_color_image(self, image_url: str, brand: str, model: str, color: str) -> Optional[str]:
        """下载颜色图片到本地"""
        try:
            # 生成文件名
            clean_brand = "".join(c for c in brand if c.isalnum() or c in (' ', '-', '_')).strip()
            clean_model = "".join(c for c in model if c.isalnum() or c in (' ', '-', '_')).strip()
            clean_color = "".join(c for c in color if c.isalnum() or c in (' ', '-', '_')).strip()
            
            # 获取文件扩展名
            parsed_url = urlparse(image_url)
            file_ext = os.path.splitext(parsed_url.path)[1] or '.jpg'
            
            filename = f"{clean_brand}_{clean_model}_{clean_color}{file_ext}".replace(' ', '_')
            local_path = os.path.join(IMAGES_DIR, filename)
            
            # 下载图片
            response = self.request_with_backoff('GET', image_url)
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Downloaded color image: {filename}")
            return f"images/phones/{filename}"
            
        except Exception as e:
            logger.error(f"❌ Failed to download color image {image_url}: {e}")
            return None

    def update_color_images(self, phone_id: int, color_images: Dict[str, str], dry_run: bool = True) -> bool:
        """更新数据库中的颜色图片信息"""
        if dry_run:
            logger.info(f"[DRY-RUN] Would update Id={phone_id} ColorImages='{json.dumps(color_images)}'")
            return True
        
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute('UPDATE "Phones" SET "ColorImages" = %s WHERE "Id" = %s', 
                              (json.dumps(color_images), phone_id))
                    conn.commit()
                    return cur.rowcount == 1
        except Exception as e:
            logger.error(f"DB update failed for {phone_id}: {e}")
            return False

    def crawl_color_images(self, limit: Optional[int] = None, dry_run: bool = True, 
                          brand_like: Optional[str] = None, download_images: bool = True):
        """爬取颜色图片的主方法"""
        targets = self.get_phones_with_colors(limit=limit, brand_like=brand_like)
        logger.info(f"Found {len(targets)} phones needing color images")
        
        success = 0
        for i, t in enumerate(targets, 1):
            brand, model, colors, pid = t['brand'], t['model'], t['colors'], t['id']
            logger.info(f"({i}/{len(targets)}) {brand} {model} - Colors: {colors}")
            
            # 搜索GSMArena页面
            url = self.search_gsmarena(brand, model)
            if not url:
                logger.info("No GSMArena match; skipping")
                continue
            
            # 提取颜色图片
            color_images = self.extract_color_images_gsmarena(url, colors)
            if not color_images:
                logger.info("No color images found; skipping")
                continue
            
            # 下载图片到本地
            if download_images:
                local_color_images = {}
                for color, image_url in color_images.items():
                    local_path = self.download_color_image(image_url, brand, model, color)
                    if local_path:
                        local_color_images[color] = local_path
                color_images = local_color_images
            
            if color_images:
                if self.update_color_images(pid, color_images, dry_run=dry_run):
                    success += 1
                    logger.info(f"✅ Updated {len(color_images)} color images")
            
            # 额外延迟
            import random
            time.sleep(max(3.0, self.base_delay_seconds + random.uniform(-2.0, 2.0)))
        
        logger.info(f"Completed. Updated={success} / {len(targets)}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Crawl color images for phones')
    parser.add_argument('--limit', type=int, default=10, help='Limit number of phones to process')
    parser.add_argument('--apply', action='store_true', help='Apply changes (disable dry-run)')
    parser.add_argument('--brand', type=str, default=None, help='Filter brand (LIKE match)')
    parser.add_argument('--no-download', action='store_true', help='Skip downloading images, only update URLs')
    args = parser.parse_args()

    crawler = ColorImagesCrawler()
    crawler.crawl_color_images(
        limit=args.limit, 
        dry_run=not args.apply, 
        brand_like=args.brand,
        download_images=not args.no_download
    )


if __name__ == '__main__':
    main()
