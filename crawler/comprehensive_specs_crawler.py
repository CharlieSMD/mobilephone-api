#!/usr/bin/env python3
"""
Comprehensive Specs Crawler - Fix all fields
Correctly crawl ScreenSize, RAM, Battery and other fields
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
        logging.FileHandler('comprehensive_specs_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveSpecsCrawler:
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
        
    def get_phones_missing_specs(self):
        """Get phones that have processor but missing other specs"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            query = '''
            SELECT "Id", "Brand", "Model" 
            FROM "Phones" 
            WHERE ("Brand" IN ('Samsung', 'OnePlus', 'OPPO'))
            AND "Processor" IS NOT NULL 
            AND "Processor" != 'TBD'
            AND ("ScreenSize" = 'TBD' OR "Ram" = 'Card slot' OR "Ram" = 'No')
            ORDER BY "Brand", "Model"
            '''
            
            cur.execute(query)
            phones = cur.fetchall()
            
            cur.close()
            conn.close()
            
            logger.info(f"Found {len(phones)} phones missing comprehensive specs")
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
                elif brand_lower == 'apple':
                    brand_patterns = ['apple']
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
    
    def extract_comprehensive_specs(self, phone_url):
        """Extract comprehensive specs from GSMArena phone page"""
        try:
            response = self.session.get(phone_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            specs = {}
            
            # Method 1: Extract from highlight specs (data-spec attributes)
            # Screen Size
            screen_size_elem = soup.find('span', {'data-spec': 'displaysize-hl'})
            if screen_size_elem:
                screen_size = screen_size_elem.get_text(strip=True)
                specs['screen_size'] = screen_size
                logger.info(f"✅ Screen Size: {screen_size}")
            
            # RAM Size
            ram_size_elem = soup.find('span', {'data-spec': 'ramsize-hl'})
            if ram_size_elem:
                ram_size = ram_size_elem.get_text(strip=True)
                specs['ram'] = f"{ram_size}GB RAM"
                logger.info(f"✅ RAM: {ram_size}GB RAM")
            
            # Battery Size
            battery_elem = soup.find('span', {'data-spec': 'batsize-hl'})
            if battery_elem:
                battery_size = battery_elem.get_text(strip=True)
                specs['battery'] = f"{battery_size}mAh"
                logger.info(f"✅ Battery: {battery_size}mAh")
            
            # Internal Storage (already have this but let's make sure it's correct)
            storage_elem = soup.find('span', {'data-spec': 'storage-hl'})
            if storage_elem:
                storage_info = storage_elem.get_text(strip=True)
                specs['storage_summary'] = storage_info
                logger.info(f"✅ Storage Summary: {storage_info}")
            
            # Weight (from body-hl)
            body_elem = soup.find('span', {'data-spec': 'body-hl'})
            if body_elem:
                body_info = body_elem.get_text(strip=True)
                # Extract weight (format: "164g, 7.4mm thickness")
                weight_match = re.search(r'(\d+(?:\.\d+)?)g', body_info)
                if weight_match:
                    specs['weight'] = weight_match.group(1)  # Only the number, no 'g'
                    logger.info(f"✅ Weight: {weight_match.group(1)}g")
            
            # Method 2: Extract from detailed specs table if highlights are missing
            if not specs.get('screen_size'):
                # Look for size in detailed specs
                size_elements = soup.find_all('td', {'data-spec': re.compile(r'size|display')})
                for elem in size_elements:
                    text = elem.get_text(strip=True)
                    if '"' in text and any(char.isdigit() for char in text):
                        specs['screen_size'] = text.split(',')[0].strip()  # Take first part
                        logger.info(f"✅ Screen Size (detailed): {specs['screen_size']}")
                        break
            
            # Method 3: Look for battery in mAh pattern if not found
            if not specs.get('battery'):
                battery_pattern = re.search(r'(\d+)\s*mAh', soup.get_text())
                if battery_pattern:
                    specs['battery'] = f"{battery_pattern.group(1)}mAh"
                    logger.info(f"✅ Battery (pattern): {specs['battery']}")
            
            logger.info(f"Extracted specs for {phone_url}: {list(specs.keys())}")
            return specs
            
        except Exception as e:
            logger.error(f"Error extracting specs from {phone_url}: {e}")
            return {}
    
    def update_phone_comprehensive_specs(self, phone_id, specs):
        """Update phone with comprehensive specs"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Build update query
            update_fields = []
            values = []
            
            field_mapping = {
                'screen_size': 'ScreenSize',
                'ram': 'Ram',
                'battery': 'Battery',
                'weight': 'Weight'
            }
            
            # Check what fields exist in the database first
            for spec_key, db_field in field_mapping.items():
                if spec_key in specs and specs[spec_key]:
                    if db_field in ['ScreenSize', 'Ram', 'Battery', 'Weight']:  # Known fields
                        update_fields.append(f'"{db_field}" = %s')
                        values.append(specs[spec_key])
            
            if update_fields:
                query = f'UPDATE "Phones" SET {", ".join(update_fields)} WHERE "Id" = %s'
                values.append(phone_id)
                
                cur.execute(query, values)
                conn.commit()
                
                logger.info(f"✅ Updated phone {phone_id} with {len(update_fields)} comprehensive specs")
                return True
            else:
                logger.warning(f"No comprehensive specs to update for phone {phone_id}")
                return False
                
        except Exception as e:
            logger.error(f"Database update error for phone {phone_id}: {e}")
            return False
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()
    
    def crawl_comprehensive_specs(self):
        """Main method to crawl comprehensive specs"""
        phones = self.get_phones_missing_specs()
        
        if not phones:
            logger.info("No phones missing comprehensive specs found")
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
            
            # Extract comprehensive specs
            specs = self.extract_comprehensive_specs(phone_url)
            
            if not specs:
                logger.error(f"❌ No specs extracted for {brand} {model}")
                fail_count += 1
                continue
            
            # Update database with comprehensive specs
            if self.update_phone_comprehensive_specs(phone_id, specs):
                success_count += 1
                logger.info(f"✅ Successfully updated {brand} {model}")
            else:
                fail_count += 1
                logger.error(f"❌ Failed to update {brand} {model}")
            
            # Add delay between requests
            time.sleep(4)
        
        logger.info(f"\n🎯 Comprehensive Specs Crawling completed!")
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
    
    crawler = ComprehensiveSpecsCrawler(db_config)
    crawler.crawl_comprehensive_specs()

if __name__ == "__main__":
    main()
