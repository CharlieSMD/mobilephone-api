#!/usr/bin/env python3
"""
Samsung Batch Crawler - First Batch
Specifically targets Samsung Galaxy phones that failed in the previous crawl
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
        logging.FileHandler('samsung_batch_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SamsungBatchCrawler:
    def __init__(self, db_config):
        self.db_config = db_config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.base_url = "https://www.gsmarena.com"
        self.search_url = "https://www.gsmarena.com/results.php3"
        
        # Samsung phones to crawl (from failed list)
        self.samsung_phones = [
            "Galaxy Note20", "Galaxy Note20 Ultra",
            "Galaxy S20", "Galaxy S20 Ultra", "Galaxy S20+",
            "Galaxy S21", "Galaxy S21 Ultra", "Galaxy S21+", 
            "Galaxy S22", "Galaxy S22 Ultra", "Galaxy S22+",
            "Galaxy S23", "Galaxy S23 Ultra", "Galaxy S23+",
            "Galaxy S24", "Galaxy S24 Ultra", "Galaxy S24+",
            "Galaxy Z Flip", "Galaxy Z Flip3", "Galaxy Z Flip4", "Galaxy Z Flip5", "Galaxy Z Flip6",
            "Galaxy Z Fold2", "Galaxy Z Fold3", "Galaxy Z Fold4", "Galaxy Z Fold5", "Galaxy Z Fold6"
        ]
    
    def normalize_model_for_search(self, brand, model):
        """Normalize Samsung model name for GSMArena search"""
        # Remove brand name from model if it's duplicated
        if brand.lower() in model.lower():
            model = re.sub(rf'\b{re.escape(brand)}\b', '', model, flags=re.IGNORECASE).strip()
        
        # Samsung specific handling
        if brand == 'Samsung':
            # "Galaxy S24 Ultra" -> "Galaxy S24 Ultra"
            pass  # Keep as is for Samsung
        
        return model.strip()
    
    def search_phone_on_gsmarena(self, brand, model):
        """Search for phone on GSMArena and return the product page URL"""
        try:
            search_model = self.normalize_model_for_search(brand, model)
            search_query = f"{brand} {search_model}"
            
            logger.info(f"🔍 Searching GSMArena for: {search_query}")
            
            params = {
                'sQuickSearch': 'yes',
                'sName': search_query
            }
            
            response = self.session.get(self.search_url, params=params, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for phone links
            phone_links = soup.find_all('a', href=True)
            
            for link in phone_links:
                href = link.get('href', '')
                if href.startswith('/') and '_' in href and '-' in href:
                    # Extract phone name from URL and text
                    link_text = link.get_text(strip=True).lower()
                    url_name = href.replace('/', '').replace('.php', '').replace('-', ' ').replace('_', ' ')
                    
                    # Normalize search terms
                    search_normalized = search_query.lower().replace(' ', '').replace('-', '').replace('_', '')
                    link_normalized = link_text.replace(' ', '').replace('-', '').replace('_', '')
                    url_normalized = url_name.replace(' ', '').replace('-', '').replace('_', '')
                    
                    # Check if this is a good match
                    if (search_normalized in link_normalized or 
                        search_normalized in url_normalized or
                        link_normalized in search_normalized):
                        
                        full_url = urljoin(self.base_url, href)
                        logger.info(f"✅ Found potential match: {link_text} -> {full_url}")
                        return full_url
            
            logger.warning(f"❌ No product page found for: {search_query}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Search failed for {brand} {model}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error searching for {brand} {model}: {e}")
            return None
    
    def extract_phone_details(self, url):
        """Extract detailed phone specifications from GSMArena product page"""
        try:
            logger.info(f"📱 Extracting details from: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {}
            
            # Extract specifications from the specs table
            spec_tables = soup.find_all('table', {'cellspacing': '0'})
            
            for table in spec_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        # Map GSMArena fields to our database fields
                        if 'weight' in key and 'g' in value:
                            try:
                                weight_match = re.search(r'(\d+\.?\d*)\s*g', value)
                                if weight_match:
                                    details['weight'] = float(weight_match.group(1))
                            except:
                                pass
                        
                        elif 'dimensions' in key:
                            details['dimensions'] = value[:100]  # Limit length
                        
                        elif any(word in key for word in ['chipset', 'cpu', 'processor']):
                            details['processor'] = value[:200]
                        
                        elif 'os' in key or 'android' in key.lower() or 'ios' in key.lower():
                            details['os'] = value[:100]
                        
                        elif any(word in key for word in ['network', '2g', '3g', '4g', '5g']):
                            details['network_type'] = value[:100]
                        
                        elif any(word in key for word in ['charging', 'battery']) and any(word in value.lower() for word in ['w', 'watt', 'fast']):
                            details['charging_power'] = value[:100]
                        
                        elif any(word in key for word in ['protection', 'water', 'dust', 'ip']):
                            details['water_resistance'] = value[:100]
                        
                        elif any(word in key for word in ['build', 'materials', 'body']):
                            details['material'] = value[:200]
                        
                        elif 'colors' in key or 'colour' in key:
                            details['colors'] = value[:200]
            
            logger.info(f"📊 Extracted {len(details)} specifications")
            return details
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to extract details from {url}: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ Unexpected error extracting details from {url}: {e}")
            return {}
    
    def get_phone_id_from_db(self, brand, model):
        """Get phone ID from database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT "Id" FROM "Phones" WHERE "Brand" = %s AND "Model" = %s',
                (brand, model)
            )
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"❌ Database error getting phone ID: {e}")
            return None
    
    def update_phone_in_db(self, phone_id, details):
        """Update phone details in database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Build update query dynamically
            update_fields = []
            values = []
            
            field_mapping = {
                'weight': '"Weight"',
                'dimensions': '"Dimensions"', 
                'processor': '"Processor"',
                'os': '"Os"',
                'network_type': '"NetworkType"',
                'charging_power': '"ChargingPower"',
                'water_resistance': '"WaterResistance"',
                'material': '"Material"',
                'colors': '"Colors"'
            }
            
            for key, value in details.items():
                if key in field_mapping and value is not None:
                    update_fields.append(f'{field_mapping[key]} = %s')
                    values.append(value)
            
            if update_fields:
                values.append(phone_id)
                query = f'UPDATE "Phones" SET {", ".join(update_fields)} WHERE "Id" = %s'
                
                cursor.execute(query, values)
                conn.commit()
                
                logger.info(f"✅ Updated phone ID {phone_id} with {len(update_fields)} fields")
            
            cursor.close()
            conn.close()
            
            return len(update_fields)
            
        except Exception as e:
            logger.error(f"❌ Failed to update phone {phone_id}: {e}")
            return 0
    
    def crawl_samsung_phones(self):
        """Main crawling function for Samsung phones"""
        logger.info("🚀 Starting Samsung batch crawling")
        
        total_phones = len(self.samsung_phones)
        updated_count = 0
        failed_count = 0
        
        for i, model in enumerate(self.samsung_phones, 1):
            print(f"\n📱 Processing {i}/{total_phones}: Samsung {model}")
            logger.info(f"Processing phone {i}/{total_phones}: Samsung {model}")
            
            try:
                # Get phone ID from database
                phone_id = self.get_phone_id_from_db("Samsung", model)
                if not phone_id:
                    logger.warning(f"❌ Phone not found in database: Samsung {model}")
                    failed_count += 1
                    continue
                
                # Search for phone on GSMArena
                product_url = self.search_phone_on_gsmarena("Samsung", model)
                if not product_url:
                    print("❌ No product page found")
                    failed_count += 1
                    time.sleep(3)  # Wait before next request
                    continue
                
                # Extract details
                details = self.extract_phone_details(product_url)
                if not details:
                    print("❌ No details extracted")
                    failed_count += 1
                    time.sleep(3)
                    continue
                
                # Update database
                updated_fields = self.update_phone_in_db(phone_id, details)
                if updated_fields > 0:
                    print(f"✅ Successfully updated with {updated_fields} details")
                    updated_count += 1
                else:
                    print("❌ Failed to update database")
                    failed_count += 1
                
                # Wait between requests to avoid rate limiting
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Unexpected error processing Samsung {model}: {e}")
                print(f"❌ Error: {e}")
                failed_count += 1
                time.sleep(3)
        
        logger.info(f"🎉 Samsung batch crawling completed: {updated_count} updated, {failed_count} failed")
        print(f"\n🎉 Samsung batch completed!")
        print(f"✅ Successfully updated: {updated_count} phones")
        print(f"❌ Failed: {failed_count} phones")
        
        return updated_count, failed_count

def main():
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'mobilephone_db',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    # Create crawler and run
    crawler = SamsungBatchCrawler(db_config)
    updated, failed = crawler.crawl_samsung_phones()
    
    return updated, failed

if __name__ == "__main__":
    main()

