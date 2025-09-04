#!/usr/bin/env python3
"""
通用规格修复器 - 按Samsung Note20标准修复所有手机数据
修复字段: ScreenSize, Ram, Battery, Storage (如果缺失)
适用于: Apple, Google, Honor, Huawei, ASUS, Sony, Xiaomi, vivo等所有品牌
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
        logging.FileHandler('universal_specs_fixer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UniversalSpecsFixer:
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
        
    def get_phones_to_fix(self, batch_size=20):
        """Get phones that need specs fixes (excluding Samsung which is already complete)"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            query = '''
            SELECT "Id", "Brand", "Model" 
            FROM "Phones" 
            WHERE "Brand" IN ('Google', 'Honor')
            AND ("ScreenSize" = 'TBD' 
                 OR "Ram" IN ('TBD', 'Card slot', 'No')
                 OR "Battery" IN ('TBD', 'Type mAh') 
                 OR "Battery" LIKE '%rating%'
                 OR "Storage" IN ('TBD', 'Card slot', 'No'))
            ORDER BY "Model"
            LIMIT %s
            '''
            
            cur.execute(query, (batch_size,))
            phones = cur.fetchall()
            
            cur.close()
            conn.close()
            
            logger.info(f"Found {len(phones)} phones to fix")
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
                
                # Handle special cases for brand matching
                if brand_lower == 'oneplus':
                    brand_patterns = ['oneplus', 'one plus']
                elif brand_lower == 'oppo':
                    brand_patterns = ['oppo']
                elif brand_lower in ['samsung', 'apple', 'google', 'honor', 'huawei', 'xiaomi', 'sony', 'asus', 'vivo']:
                    brand_patterns = [brand_lower]
                else:
                    brand_patterns = [brand_lower]
                
                # Check if brand matches
                brand_match = any(pattern in link_text for pattern in brand_patterns)
                
                # Check if model matches (more flexible matching)
                model_words = model_lower.split()
                model_match = any(word in link_text for word in model_words if len(word) > 2)
                
                if brand_match and model_match:
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
    
    def extract_specs_data(self, phone_url):
        """Extract comprehensive specs data from GSMArena phone page"""
        try:
            response = self.session.get(phone_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {}
            
            # 1. Extract Screen Size
            screen_elem = soup.find('span', {'data-spec': 'displaysize-hl'})
            if screen_elem:
                screen_text = screen_elem.get_text(strip=True)
                # Extract just the size (e.g., "6.7"" from "6.7" 1344x2992 pixels")
                screen_match = re.search(r'(\d+\.?\d*)"', screen_text)
                if screen_match:
                    data['screen_size'] = screen_match.group(1) + '"'
                    logger.info(f"✅ Screen Size: {data['screen_size']}")
            
            # 2. Extract RAM
            ram_elem = soup.find('span', {'data-spec': 'ramsize-hl'})
            if ram_elem:
                ram_text = ram_elem.get_text(strip=True)
                # Clean up RAM text (e.g., "4GB" or "4GB/8GB/12GB")
                data['ram'] = ram_text
                logger.info(f"✅ RAM: {data['ram']}")
            
            # 3. Extract Battery
            battery_elem = soup.find('span', {'data-spec': 'batsize-hl'})
            if battery_elem:
                battery_text = battery_elem.get_text(strip=True)
                # Extract numeric mAh value
                battery_match = re.search(r'(\d+)\s*mAh', battery_text)
                if battery_match:
                    data['battery'] = battery_match.group(1) + 'mAh'
                    logger.info(f"✅ Battery: {data['battery']}")
                else:
                    # Fallback - use original text if no mAh pattern found
                    data['battery'] = battery_text
                    logger.info(f"✅ Battery (fallback): {data['battery']}")
            
            # 4. Extract Storage (Internal Memory)
            storage_elem = soup.find('span', {'data-spec': 'internalmemory'})
            if storage_elem:
                storage_text = storage_elem.get_text(strip=True)
                data['storage'] = storage_text
                logger.info(f"✅ Storage: {data['storage']}")
            
            # 5. Extract Weight (if missing)
            weight_elem = soup.find('span', {'data-spec': 'body-hl'})
            if weight_elem:
                weight_text = weight_elem.get_text(strip=True)
                weight_match = re.search(r'(\d+(?:\.\d+)?)\s*g', weight_text)
                if weight_match:
                    data['weight'] = float(weight_match.group(1))
                    logger.info(f"✅ Weight: {data['weight']}g")
            
            # 6. Extract OS (if not already done)
            os_elem = soup.find('span', {'data-spec': 'os-hl'})
            if os_elem:
                os_text = os_elem.get_text(strip=True)
                data['os'] = os_text
                logger.info(f"✅ OS: {data['os']}")
            
            logger.info(f"Extracted data fields: {list(data.keys())}")
            return data
            
        except Exception as e:
            logger.error(f"Error extracting data from {phone_url}: {e}")
            return {}
    
    def update_phone_specs(self, phone_id, data):
        """Update phone with extracted specs data"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Build update query - only update fields that have data
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
            
            if data.get('weight') is not None:
                update_fields.append('"Weight" = %s')
                values.append(data['weight'])
            
            if data.get('os'):
                update_fields.append('"Os" = %s')
                values.append(data['os'])
            
            if update_fields:
                query = f'UPDATE "Phones" SET {", ".join(update_fields)} WHERE "Id" = %s'
                values.append(phone_id)
                
                cur.execute(query, values)
                conn.commit()
                
                logger.info(f"✅ Updated phone {phone_id} with {len(update_fields)} fields")
                return True
            else:
                logger.warning(f"No data to update for phone {phone_id}")
                return False
                
        except Exception as e:
            logger.error(f"Database update error for phone {phone_id}: {e}")
            return False
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()
    
    def fix_universal_specs(self, batch_size=15):
        """Main method to fix specs for all brands"""
        phones = self.get_phones_to_fix(batch_size)
        
        if not phones:
            logger.info("No phones to fix found")
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
            
            # Extract specs data
            data = self.extract_specs_data(phone_url)
            
            if not data:
                logger.error(f"❌ No data extracted for {brand} {model}")
                fail_count += 1
                continue
            
            # Update database
            if self.update_phone_specs(phone_id, data):
                success_count += 1
                logger.info(f"✅ Successfully updated {brand} {model}")
            else:
                fail_count += 1
                logger.error(f"❌ Failed to update {brand} {model}")
            
            # Add delay between requests to avoid rate limiting
            time.sleep(3)
        
        logger.info(f"\n🎯 Universal Specs Fix completed!")
        logger.info(f"✅ Success: {success_count}")
        logger.info(f"❌ Failed: {fail_count}")
        logger.info(f"📊 Total: {len(phones)}")

def main():
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'mobilephone_db',
        'user': 'postgres'
    }
    
    fixer = UniversalSpecsFixer(db_config)
    fixer.fix_universal_specs(batch_size=10)  # Process 10 phones at a time

if __name__ == "__main__":
    main()
