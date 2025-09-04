#!/usr/bin/env python3
"""
Final Storage Fix Crawler
Correctly extracts internal memory specs from GSMArena
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
        logging.FileHandler('final_storage_fix.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinalStorageFix:
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
        
    def get_phones_with_wrong_storage(self):
        """Get phones that have 'Card slot' as Storage"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            query = '''
            SELECT "Id", "Brand", "Model" 
            FROM "Phones" 
            WHERE ("Brand" IN ('Samsung', 'OnePlus', 'OPPO'))
            AND "Storage" = 'Card slot'
            ORDER BY "Brand", "Model"
            '''
            
            cur.execute(query)
            phones = cur.fetchall()
            
            cur.close()
            conn.close()
            
            logger.info(f"Found {len(phones)} phones with wrong storage data")
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
    
    def extract_correct_storage_specs(self, phone_url):
        """Extract correct internal memory specs from GSMArena phone page"""
        try:
            response = self.session.get(phone_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            specs = {}
            
            # Method 1: Look for data-spec="internalmemory"
            internal_memory_cell = soup.find('td', {'data-spec': 'internalmemory'})
            if internal_memory_cell:
                internal_memory = internal_memory_cell.get_text(strip=True)
                specs['storage'] = internal_memory
                logger.info(f"✅ Found internal memory: {internal_memory}")
            
            # Method 2: Look for data-spec="memoryslot" for RAM info
            memory_slot_cell = soup.find('td', {'data-spec': 'memoryslot'})
            if memory_slot_cell:
                memory_slot = memory_slot_cell.get_text(strip=True)
                specs['ram'] = memory_slot
                logger.info(f"✅ Found memory slot: {memory_slot}")
            
            # Method 3: If method 1 failed, look in table structure
            if not specs.get('storage'):
                # Look for "Internal" row in the specs table
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            key_cell = cells[0]
                            value_cell = cells[1]
                            
                            # Check if this is the internal memory row
                            if 'internal' in key_cell.get_text().lower():
                                internal_value = value_cell.get_text(strip=True)
                                # Validate that this looks like memory specs (contains GB and RAM)
                                if 'GB' in internal_value and 'RAM' in internal_value:
                                    specs['storage'] = internal_value
                                    logger.info(f"✅ Found internal memory (table method): {internal_value}")
                                    break
                    if specs.get('storage'):
                        break
            
            logger.info(f"Extracted specs for {phone_url}: {specs}")
            return specs
            
        except Exception as e:
            logger.error(f"Error extracting specs from {phone_url}: {e}")
            return {}
    
    def update_phone_correct_storage(self, phone_id, specs):
        """Update phone with correct Storage and RAM data"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Build update query for Storage and RAM
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
                
                logger.info(f"✅ Updated phone {phone_id} with correct storage/RAM data")
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
    
    def fix_storage_data(self):
        """Main method to fix incorrect storage data"""
        phones = self.get_phones_with_wrong_storage()
        
        if not phones:
            logger.info("No phones with wrong storage data found")
            return
        
        success_count = 0
        fail_count = 0
        
        for i, (phone_id, brand, model) in enumerate(phones, 1):
            logger.info(f"\n📱 Fixing phone {i}/{len(phones)}: {brand} {model}")
            
            # Search for phone on GSMArena
            phone_url = self.search_phone_on_gsmarena(brand, model)
            
            if not phone_url:
                logger.error(f"❌ No product page found for {brand} {model}")
                fail_count += 1
                continue
            
            # Extract correct storage specs
            specs = self.extract_correct_storage_specs(phone_url)
            
            if not specs.get('storage'):
                logger.error(f"❌ No storage specs extracted for {brand} {model}")
                fail_count += 1
                continue
            
            # Update database with correct data
            if self.update_phone_correct_storage(phone_id, specs):
                success_count += 1
                logger.info(f"✅ Successfully fixed {brand} {model}")
            else:
                fail_count += 1
                logger.error(f"❌ Failed to update {brand} {model}")
            
            # Add delay between requests
            time.sleep(4)
        
        logger.info(f"\n🎯 Storage Fix completed!")
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
    
    crawler = FinalStorageFix(db_config)
    crawler.fix_storage_data()

if __name__ == "__main__":
    main()

