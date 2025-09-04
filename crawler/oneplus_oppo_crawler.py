#!/usr/bin/env python3
"""
OnePlus + OPPO Batch Crawler
Specifically targets OnePlus and OPPO phones
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
        logging.FileHandler('oneplus_oppo_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OnePlusOppoCrawler:
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
        
    def get_phones_to_update(self):
        """Get OnePlus and OPPO phones that need detailed specs"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            query = '''
            SELECT "Id", "Brand", "Model" 
            FROM "Phones" 
            WHERE ("Brand" = 'OnePlus' OR "Brand" = 'OPPO') 
            AND ("Processor" IS NULL OR "Processor" = 'TBD')
            ORDER BY "Brand", "Model"
            '''
            
            cur.execute(query)
            phones = cur.fetchall()
            
            cur.close()
            conn.close()
            
            logger.info(f"Found {len(phones)} OnePlus/OPPO phones to update")
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
    
    def extract_phone_specs(self, phone_url):
        """Extract detailed specs from phone page"""
        try:
            response = self.session.get(phone_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            specs = {}
            
            # Extract specifications from the specs table
            spec_table = soup.find('table', {'cellspacing': '0'})
            if spec_table:
                rows = spec_table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        # Map GSMArena fields to our database fields
                        if 'weight' in key:
                            specs['weight'] = value
                        elif 'dimensions' in key:
                            specs['dimensions'] = value
                        elif any(word in key for word in ['chipset', 'cpu', 'processor']):
                            specs['processor'] = value
                        elif 'os' in key:
                            specs['os'] = value
                        elif any(word in key for word in ['network', '2g', '3g', '4g', '5g']):
                            specs['network_type'] = value
                        elif any(word in key for word in ['charging', 'battery']):
                            specs['charging_power'] = value
                        elif any(word in key for word in ['water', 'protection', 'ip']):
                            specs['water_resistance'] = value
                        elif any(word in key for word in ['build', 'body', 'material']):
                            specs['material'] = value
            
            # Also try to extract from detailed specs sections
            spec_sections = soup.find_all('table', class_='st')
            for section in spec_sections:
                rows = section.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        if not specs.get('weight') and 'weight' in key:
                            specs['weight'] = value
                        elif not specs.get('dimensions') and 'dimensions' in key:
                            specs['dimensions'] = value
                        elif not specs.get('processor') and any(word in key for word in ['chipset', 'cpu']):
                            specs['processor'] = value
                        elif not specs.get('os') and 'os' in key:
                            specs['os'] = value
            
            logger.info(f"Extracted {len(specs)} specs: {list(specs.keys())}")
            return specs
            
        except Exception as e:
            logger.error(f"Error extracting specs from {phone_url}: {e}")
            return {}
    
    def update_phone_in_db(self, phone_id, specs):
        """Update phone with extracted specs"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Build update query dynamically based on available specs
            update_fields = []
            values = []
            
            field_mapping = {
                'weight': 'Weight',
                'dimensions': 'Dimensions', 
                'processor': 'Processor',
                'os': 'Os',
                'network_type': 'NetworkType',
                'charging_power': 'ChargingPower',
                'water_resistance': 'WaterResistance',
                'material': 'Material'
            }
            
            for spec_key, db_field in field_mapping.items():
                if spec_key in specs and specs[spec_key]:
                    update_fields.append(f'"{db_field}" = %s')
                    values.append(specs[spec_key])
            
            if update_fields:
                query = f'UPDATE "Phones" SET {", ".join(update_fields)} WHERE "Id" = %s'
                values.append(phone_id)
                
                cur.execute(query, values)
                conn.commit()
                
                logger.info(f"✅ Updated phone {phone_id} with {len(update_fields)} fields")
                return True
            else:
                logger.warning(f"No specs to update for phone {phone_id}")
                return False
                
        except Exception as e:
            logger.error(f"Database update error for phone {phone_id}: {e}")
            return False
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()
    
    def crawl_phones(self):
        """Main crawling method"""
        phones = self.get_phones_to_update()
        
        if not phones:
            logger.info("No OnePlus/OPPO phones to update")
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
            
            # Extract specs
            specs = self.extract_phone_specs(phone_url)
            
            if not specs:
                logger.error(f"❌ No specs extracted for {brand} {model}")
                fail_count += 1
                continue
            
            # Update database
            if self.update_phone_in_db(phone_id, specs):
                success_count += 1
                logger.info(f"✅ Successfully updated {brand} {model}")
            else:
                fail_count += 1
                logger.error(f"❌ Failed to update {brand} {model}")
            
            # Add delay between requests
            time.sleep(3)
        
        logger.info(f"\n🎯 OnePlus/OPPO Crawling completed!")
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
    
    crawler = OnePlusOppoCrawler(db_config)
    crawler.crawl_phones()

if __name__ == "__main__":
    main()

