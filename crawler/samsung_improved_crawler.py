#!/usr/bin/env python3
"""
Samsung Improved Crawler - Fixed search matching logic
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
        logging.FileHandler('samsung_improved_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SamsungImprovedCrawler:
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
        
        # Samsung phones to crawl
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
    
    def search_phone_on_gsmarena(self, brand, model):
        """Improved search for Samsung phones on GSMArena"""
        try:
            search_query = f"{brand} {model}"
            logger.info(f"🔍 Searching GSMArena for: {search_query}")
            
            params = {
                'sQuickSearch': 'yes',
                'sName': search_query
            }
            
            response = self.session.get(self.search_url, params=params, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for phone links in the search results
            phone_links = soup.find_all('a', href=True)
            
            for link in phone_links:
                href = link.get('href', '')
                if href.startswith('samsung_') and href.endswith('.php'):
                    # Extract phone name from the link text
                    link_spans = link.find_all('span')
                    if link_spans:
                        link_text = ' '.join([span.get_text(strip=True) for span in link_spans])
                    else:
                        link_text = link.get_text(strip=True)
                    
                    # Clean up model names for comparison
                    model_clean = model.lower().replace(' ', '').replace('+', 'plus').replace('z fold', 'zfold').replace('z flip', 'zflip')
                    link_clean = link_text.lower().replace(' ', '').replace('+', 'plus').replace('z fold', 'zfold').replace('z flip', 'zflip')
                    
                    # Check if this is a good match
                    if self.is_phone_match(model_clean, link_clean, href):
                        full_url = urljoin(self.base_url, href)
                        logger.info(f"✅ Found match: {link_text} -> {full_url}")
                        return full_url
            
            # If no match found, try alternative search
            return self.alternative_search(brand, model)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Search failed for {brand} {model}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error searching for {brand} {model}: {e}")
            return None
    
    def is_phone_match(self, model_clean, link_clean, href):
        """Check if the link matches the phone model"""
        # Extract model from URL
        url_model = href.replace('samsung_galaxy_', '').replace('.php', '').replace('-', '').replace('_', '')
        url_model = url_model.replace('plus', '+')
        
        # Various matching strategies
        strategies = [
            model_clean in link_clean,
            model_clean in url_model,
            link_clean.endswith(model_clean),
            url_model.startswith(model_clean.replace('galaxy', '')),
            # Handle special cases
            model_clean.replace('galaxy', '') in url_model,
            # Handle + sign
            model_clean.replace('+', 'plus') in url_model,
            # Handle Z series
            model_clean.replace('zfold', 'z_fold').replace('zflip', 'z_flip') in href,
        ]
        
        return any(strategies)
    
    def alternative_search(self, brand, model):
        """Try alternative search patterns"""
        # Try without 'Galaxy' prefix
        if 'Galaxy' in model:
            simple_model = model.replace('Galaxy ', '').strip()
            search_query = f"{brand} {simple_model}"
            
            try:
                params = {
                    'sQuickSearch': 'yes',
                    'sName': search_query
                }
                
                response = self.session.get(self.search_url, params=params, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                phone_links = soup.find_all('a', href=True)
                
                for link in phone_links:
                    href = link.get('href', '')
                    if href.startswith('samsung_') and href.endswith('.php'):
                        # More lenient matching for alternative search
                        model_simple = simple_model.lower().replace(' ', '').replace('+', 'plus')
                        href_simple = href.lower().replace('samsung_galaxy_', '').replace('.php', '').replace('-', '').replace('_', '')
                        
                        if model_simple in href_simple or href_simple.startswith(model_simple):
                            full_url = urljoin(self.base_url, href)
                            logger.info(f"✅ Alternative search found: {simple_model} -> {full_url}")
                            return full_url
            except:
                pass
        
        logger.warning(f"❌ No product page found for: {brand} {model}")
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
                            details['dimensions'] = value[:100]
                        
                        elif any(word in key for word in ['chipset', 'cpu', 'processor']):
                            details['processor'] = value[:200]
                        
                        elif 'os' in key or 'android' in key.lower():
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
        logger.info("🚀 Starting Samsung improved crawling")
        
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
                    time.sleep(3)
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
                
                # Wait between requests
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Unexpected error processing Samsung {model}: {e}")
                print(f"❌ Error: {e}")
                failed_count += 1
                time.sleep(3)
        
        logger.info(f"🎉 Samsung improved crawling completed: {updated_count} updated, {failed_count} failed")
        print(f"\n🎉 Samsung crawling completed!")
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
    crawler = SamsungImprovedCrawler(db_config)
    updated, failed = crawler.crawl_samsung_phones()
    
    return updated, failed

if __name__ == "__main__":
    main()

