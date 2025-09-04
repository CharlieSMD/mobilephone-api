#!/usr/bin/env python3
"""
Fix Storage & RAM Crawler
Specifically targets Storage and RAM data for Samsung/OnePlus/OPPO phones
"""

import requests
import time
import json
import psycopg2
import os
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, quote
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fix_storage_ram_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FixStorageRamCrawler:
    def __init__(self, db_config):
        self.db_config = db_config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.base_url = "https://www.gsmarena.com"
        
    def get_phones_missing_storage_ram(self):
        """Get phones that have NetworkType but missing Storage/RAM"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            query = '''
            SELECT "Id", "Brand", "Model" 
            FROM "Phones" 
            WHERE ("Brand" IN ('Samsung', 'OnePlus', 'OPPO'))
            AND "NetworkType" IS NOT NULL 
            AND ("Storage" = 'TBD' OR "Ram" = 'TBD')
            ORDER BY "Brand", "Model"
            '''
            
            cur.execute(query)
            phones = cur.fetchall()
            
            cur.close()
            conn.close()
            
            logger.info(f"Found {len(phones)} phones missing Storage/RAM data")
            return phones
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            return []
    
    def search_phone_on_gsmarena(self, brand, model):
        """Search for phone on GSMArena"""
        try:
            # Clean the model name for search
            search_term = f"{brand} {model}".replace(" ", "+")
            search_url = f"{self.base_url}/results.php3?sQuickSearch=yes&sName={search_term}"
            
            logger.info(f"Searching: {search_url}")
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for phone links in search results
            phone_links = soup.find_all('a', href=re.compile(r'\.php$'))
            
            for link in phone_links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True).lower()
                
                # Check if this link matches our phone
                brand_lower = brand.lower()
                model_lower = model.lower()
                
                # Handle special cases
                if brand_lower == 'oneplus':
                    brand_patterns = ['oneplus', 'one plus']
                elif brand_lower == 'oppo':
                    brand_patterns = ['oppo']
                elif brand_lower == 'samsung':
                    brand_patterns = ['samsung']
                else:
                    brand_patterns = [brand_lower]
                
                # Check if brand matches
                brand_match = any(pattern in link_text for pattern in brand_patterns)
                
                if brand_match and any(word in link_text for word in model_lower.split()):
                    phone_url = urljoin(self.base_url, href)
                    logger.info(f"Found match: {phone_url}")
                    return phone_url
            
            logger.warning(f"No product page found for {brand} {model}")
            return None
            
        except requests.exceptions.RequestException as e:
            if "429" in str(e):
                logger.error(f"❌ Rate limited (429) for {brand} {model}")
            else:
                logger.error(f"Request error for {brand} {model}: {e}")
            return None
        except Exception as e:
            logger.error(f"Search error for {brand} {model}: {e}")
            return None
    
    def extract_storage_ram_specs(self, phone_url):
        """Extract Storage and RAM specs from phone page"""
        try:
            response = self.session.get(phone_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            specs = {}
            
            # Look for memory/storage information in various places
            # Method 1: Look in the main specs table
            spec_tables = soup.find_all('table')
            for table in spec_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        # Look for internal storage / memory
                        if any(term in key for term in ['internal', 'storage', 'memory']) and not any(term in key for term in ['card', 'external', 'slot']):
                            if not specs.get('storage'):
                                specs['storage'] = value
                                logger.info(f"Found storage: {value}")
                        
                        # Look for card slot / RAM info
                        elif any(term in key for term in ['card slot', 'microsd', 'memory card']):
                            if not specs.get('ram'):
                                specs['ram'] = value
                                logger.info(f"Found RAM info: {value}")
            
            # Method 2: Look for memory info in the quick specs section
            quick_spec_divs = soup.find_all('div', class_='help-display')
            for div in quick_spec_divs:
                text = div.get_text(strip=True)
                # Look for patterns like "128GB 6GB RAM"
                if re.search(r'\d+GB.*RAM', text, re.IGNORECASE):
                    if not specs.get('storage'):
                        specs['storage'] = text
                        logger.info(f"Found storage in quick specs: {text}")
            
            # Method 3: Look in the detailed specifications sections
            spec_sections = soup.find_all(['table', 'div'], class_=['st', 'specs'])
            for section in spec_sections:
                section_text = section.get_text().lower()
                if 'memory' in section_text or 'storage' in section_text:
                    rows = section.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            key = cells[0].get_text(strip=True).lower()
                            value = cells[1].get_text(strip=True)
                            
                            if 'internal' in key and not specs.get('storage'):
                                specs['storage'] = value
                                logger.info(f"Found detailed storage: {value}")
                            elif 'card slot' in key and not specs.get('ram'):
                                specs['ram'] = value  
                                logger.info(f"Found detailed RAM: {value}")
            
            # Method 4: Try to extract from the phone title/header area
            title_area = soup.find('div', class_='specs-phone-name-title')
            if title_area:
                title_text = title_area.get_text()
                # Look for storage patterns in title
                storage_match = re.search(r'(\d+GB[^,]*)', title_text)
                if storage_match and not specs.get('storage'):
                    specs['storage'] = storage_match.group(1)
                    logger.info(f"Found storage in title: {storage_match.group(1)}")
            
            logger.info(f"Extracted specs for {phone_url}: {specs}")
            return specs
            
        except Exception as e:
            logger.error(f"Error extracting specs from {phone_url}: {e}")
            return {}
    
    def update_phone_storage_ram(self, phone_id, specs):
        """Update phone with Storage and RAM data"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Build update query for Storage and RAM only
            update_fields = []
            values = []
            
            if specs.get('storage'):
                update_fields.append('"Storage" = %s')
                values.append(specs['storage'])
            
            if specs.get('ram'):
                update_fields.append('"Ram" = %s')
                values.append(specs['ram'])
            
            if update_fields:
                query = f'UPDATE "Phones" SET {", ".join(update_fields)} WHERE "Id" = %s'
                values.append(phone_id)
                
                cur.execute(query, values)
                conn.commit()
                
                logger.info(f"✅ Updated phone {phone_id} with {len(update_fields)} storage/RAM fields")
                return True
            else:
                logger.warning(f"No storage/RAM specs to update for phone {phone_id}")
                return False
                
        except Exception as e:
            logger.error(f"Database update error for phone {phone_id}: {e}")
            return False
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()
    
    def crawl_storage_ram(self):
        """Main crawling method for Storage and RAM"""
        phones = self.get_phones_missing_storage_ram()
        
        if not phones:
            logger.info("No phones missing Storage/RAM data")
            return
        
        success_count = 0
        fail_count = 0
        
        for i, (phone_id, brand, model) in enumerate(phones, 1):
            logger.info(f"\n📱 Processing phone {i}/{len(phones)}: {brand} {model}")
            
            # Search for phone on GSMArena
            phone_url = self.search_phone_on_gsmarena(brand, model)
            
            if not phone_url:
                logger.error(f"❌ No product page found for {brand} {model}")
                fail_count += 1
                continue
            
            # Extract Storage and RAM specs
            specs = self.extract_storage_ram_specs(phone_url)
            
            if not specs:
                logger.error(f"❌ No storage/RAM specs extracted for {brand} {model}")
                fail_count += 1
                continue
            
            # Update database
            if self.update_phone_storage_ram(phone_id, specs):
                success_count += 1
                logger.info(f"✅ Successfully updated {brand} {model}")
            else:
                fail_count += 1
                logger.error(f"❌ Failed to update {brand} {model}")
            
            # Add delay between requests
            time.sleep(4)  # Slightly longer delay for safety
        
        logger.info(f"\n🎯 Storage/RAM Fix completed!")
        logger.info(f"✅ Success: {success_count}")
        logger.info(f"❌ Failed: {fail_count}")
        logger.info(f"📊 Total: {len(phones)}")

def main():
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'mobilephone_db',
        'user': 'postgres',
        'password': 'your_password_here'
    }
    
    crawler = FixStorageRamCrawler(db_config)
    crawler.crawl_storage_ram()

if __name__ == "__main__":
    main()

