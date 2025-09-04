#!/usr/bin/env python3
"""
修复Apple iPhone系列的ScreenSize、RAM、Battery数据
按照Samsung Note20的标准进行修复
"""

import requests
import time
import psycopg2
from bs4 import BeautifulSoup
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fix_apple_specs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AppleSpecsFixer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        self.base_url = "https://www.gsmarena.com"
        
    def get_apple_phones(self):
        """Get Apple phones that need fixing"""
        try:
            conn = psycopg2.connect(
                host='localhost',
                database='mobilephone_db',
                user='postgres'
            )
            cur = conn.cursor()
            
            cur.execute('''
                SELECT "Id", "Model" 
                FROM "Phones" 
                WHERE "Brand" = 'Apple'
                AND ("ScreenSize" = 'TBD' OR "Ram" = 'Card slot')
                ORDER BY "Model"
                LIMIT 15
            ''')
            
            phones = cur.fetchall()
            cur.close()
            conn.close()
            
            logger.info(f"Found {len(phones)} Apple phones to fix")
            return phones
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            return []
    
    def search_iphone_on_gsmarena(self, model):
        """Search for iPhone on GSMArena"""
        try:
            search_term = f"Apple {model}".replace(" ", "+")
            search_url = f"{self.base_url}/results.php3?sQuickSearch=yes&sName={search_term}"
            
            logger.info(f"Searching: {search_url}")
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for iPhone links
            phone_links = soup.find_all('a', href=re.compile(r'apple.*\.php$'))
            
            for link in phone_links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True).lower()
                
                # Check if this matches our iPhone model
                model_lower = model.lower()
                
                if 'iphone' in link_text and any(word in link_text for word in model_lower.split()):
                    phone_url = f"{self.base_url}/{href}"
                    logger.info(f"Found match: {phone_url}")
                    return phone_url
            
            logger.warning(f"No product page found for Apple {model}")
            return None
            
        except Exception as e:
            logger.error(f"Search error for Apple {model}: {e}")
            return None
    
    def extract_iphone_specs(self, phone_url):
        """Extract iPhone specs from GSMArena"""
        try:
            response = self.session.get(phone_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            data = {}
            
            # Extract Screen Size
            screen_elem = soup.find('span', {'data-spec': 'displaysize-hl'})
            if screen_elem:
                screen_text = screen_elem.get_text(strip=True)
                screen_match = re.search(r'(\d+\.?\d*)"', screen_text)
                if screen_match:
                    data['screen_size'] = screen_match.group(1) + '"'
                    logger.info(f"✅ Screen Size: {data['screen_size']}")
            
            # Extract RAM - for iPhones this might be in different places
            ram_elem = soup.find('span', {'data-spec': 'ramsize-hl'})
            if ram_elem:
                ram_text = ram_elem.get_text(strip=True)
                data['ram'] = ram_text
                logger.info(f"✅ RAM: {data['ram']}")
            else:
                # For iPhones, RAM might not be prominently displayed
                # Let's try to extract from specs table
                specs_tables = soup.find_all('table')
                for table in specs_tables:
                    for row in table.find_all('tr'):
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            if 'memory' in cells[0].get_text().lower() and 'ram' in cells[0].get_text().lower():
                                ram_text = cells[1].get_text(strip=True)
                                data['ram'] = ram_text
                                logger.info(f"✅ RAM (from table): {data['ram']}")
                                break
            
            # Extract Battery
            battery_elem = soup.find('span', {'data-spec': 'batsize-hl'})
            if battery_elem:
                battery_text = battery_elem.get_text(strip=True)
                # Extract mAh value
                battery_match = re.search(r'(\d+)\s*mAh', battery_text)
                if battery_match:
                    data['battery'] = battery_match.group(1) + 'mAh'
                    logger.info(f"✅ Battery: {data['battery']}")
            
            # Extract Storage (Internal Memory)
            storage_elem = soup.find('span', {'data-spec': 'internalmemory'})
            if storage_elem:
                storage_text = storage_elem.get_text(strip=True)
                data['storage'] = storage_text
                logger.info(f"✅ Storage: {data['storage']}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error extracting specs from {phone_url}: {e}")
            return {}
    
    def update_iphone_specs(self, phone_id, data):
        """Update iPhone with extracted specs"""
        try:
            conn = psycopg2.connect(
                host='localhost',
                database='mobilephone_db',
                user='postgres'
            )
            cur = conn.cursor()
            
            update_fields = []
            values = []
            
            if data.get('screen_size'):
                update_fields.append('"ScreenSize" = %s')
                values.append(data['screen_size'])
            
            if data.get('ram'):
                update_fields.append('"Ram" = %s')
                values.append(data['ram'])
            
            if data.get('battery'):
                update_fields.append('"Battery" = %s')
                values.append(data['battery'])
            
            if data.get('storage'):
                update_fields.append('"Storage" = %s')
                values.append(data['storage'])
            
            if update_fields:
                query = f'UPDATE "Phones" SET {", ".join(update_fields)} WHERE "Id" = %s'
                values.append(phone_id)
                
                cur.execute(query, values)
                conn.commit()
                
                logger.info(f"✅ Updated phone {phone_id} with {len(update_fields)} fields")
                return True
            
            cur.close()
            conn.close()
            return False
                
        except Exception as e:
            logger.error(f"Database update error for phone {phone_id}: {e}")
            return False
    
    def fix_apple_specs(self):
        """Main method to fix Apple iPhone specs"""
        phones = self.get_apple_phones()
        
        if not phones:
            logger.info("No Apple phones to fix found")
            return
        
        success_count = 0
        fail_count = 0
        
        for i, (phone_id, model) in enumerate(phones, 1):
            logger.info(f"\n📱 Processing iPhone {i}/{len(phones)}: {model}")
            
            # Search for iPhone on GSMArena
            phone_url = self.search_iphone_on_gsmarena(model)
            
            if not phone_url:
                logger.error(f"❌ No product page found for Apple {model}")
                fail_count += 1
                continue
            
            # Extract specs data
            data = self.extract_iphone_specs(phone_url)
            
            if not data:
                logger.error(f"❌ No data extracted for Apple {model}")
                fail_count += 1
                continue
            
            # Update database
            if self.update_iphone_specs(phone_id, data):
                success_count += 1
                logger.info(f"✅ Successfully updated Apple {model}")
            else:
                fail_count += 1
                logger.error(f"❌ Failed to update Apple {model}")
            
            # Add delay between requests
            time.sleep(4)
        
        logger.info(f"\n🎯 Apple iPhone Fix completed!")
        logger.info(f"✅ Success: {success_count}")
        logger.info(f"❌ Failed: {fail_count}")
        logger.info(f"📊 Total: {len(phones)}")

def main():
    fixer = AppleSpecsFixer()
    fixer.fix_apple_specs()

if __name__ == "__main__":
    main()

