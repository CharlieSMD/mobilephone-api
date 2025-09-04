#!/usr/bin/env python3
"""
GSMArena Flagship Phone Crawler
Crawls detailed specifications and images for 167 flagship phones from GSMArena
Optimized for the standardized flagship phone database (2020-2024)
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
        logging.FileHandler('gsmarena_flagship_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GSMArenaFlagshipCrawler:
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
        
        # Create images directory
        self.images_dir = os.path.join("..", "..", "images", "phones")
        os.makedirs(self.images_dir, exist_ok=True)
    
    def normalize_model_for_search(self, brand, model):
        """Normalize model name for GSMArena search"""
        # Remove brand name from model if it's duplicated
        if brand.lower() in model.lower():
            model = re.sub(rf'\b{re.escape(brand)}\b', '', model, flags=re.IGNORECASE).strip()
        
        # Handle specific brand patterns
        if brand == 'Apple':
            # "iPhone 15 Pro Max" -> "iPhone 15 Pro Max"
            pass  # Keep as is for Apple
        elif brand == 'Samsung':
            # "Galaxy S24 Ultra" -> "Galaxy S24 Ultra"
            pass  # Keep as is for Samsung
        elif brand == 'Google':
            # "Pixel 8 Pro" -> "Pixel 8 Pro"
            pass  # Keep as is for Google
        elif brand == 'Xiaomi':
            # "Xiaomi 14 Ultra" -> "14 Ultra" (remove brand)
            if model.startswith('Xiaomi '):
                model = model[7:]
            elif model.startswith('Mi '):
                model = model[3:]
        elif brand == 'OnePlus':
            # "12" -> "OnePlus 12"
            if not model.startswith('OnePlus'):
                model = f"OnePlus {model}"
        
        # Remove common suffixes that GSMArena doesn't use
        model = re.sub(r'\s+(5G|4G|LTE|Dual|SIM)(\s|$)', ' ', model, flags=re.IGNORECASE)
        
        return model.strip()
    
    def search_phone_on_gsmarena(self, brand, model):
        """Search for phone on GSMArena and return the product page URL"""
        try:
            # Normalize model for search
            search_model = self.normalize_model_for_search(brand, model)
            search_query = f"{brand} {search_model}"
            
            logger.info(f"Searching GSMArena for: {search_query}")
            
            # Search on GSMArena
            params = {
                'sQuickSearch': 'yes',
                'sName': search_query
            }
            
            response = self.session.get(self.search_url, params=params, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for phone links in search results
            phone_links = soup.find_all('a', href=True)
            
            for link in phone_links:
                href = link.get('href')
                if href and href.endswith('.php'):
                    # Check if this is a phone detail page
                    link_text = link.get_text(strip=True).lower()
                    
                    # Match criteria: contains brand and key model terms
                    brand_match = brand.lower() in link_text
                    
                    # Extract key model identifiers
                    model_keywords = []
                    if 'iPhone' in model:
                        numbers = re.findall(r'\d+', model)
                        if numbers:
                            model_keywords.append(numbers[0])
                        if 'Pro' in model:
                            model_keywords.append('pro')
                        if 'Max' in model:
                            model_keywords.append('max')
                        if 'mini' in model:
                            model_keywords.append('mini')
                    elif 'Galaxy' in model:
                        if 'S' in model:
                            numbers = re.findall(r'S(\d+)', model)
                            if numbers:
                                model_keywords.extend(['s', numbers[0]])
                        if 'Note' in model:
                            model_keywords.append('note')
                        if 'Fold' in model:
                            model_keywords.append('fold')
                        if 'Flip' in model:
                            model_keywords.append('flip')
                        if 'Ultra' in model:
                            model_keywords.append('ultra')
                    elif 'Pixel' in model:
                        numbers = re.findall(r'\d+', model)
                        if numbers:
                            model_keywords.extend(['pixel', numbers[0]])
                        if 'Pro' in model:
                            model_keywords.append('pro')
                    else:
                        # Generic approach: extract numbers and key words
                        numbers = re.findall(r'\d+', model)
                        model_keywords.extend(numbers)
                        for keyword in ['pro', 'max', 'ultra', 'plus', 'mini']:
                            if keyword in model.lower():
                                model_keywords.append(keyword)
                    
                    # Check if link text contains model keywords
                    model_match = all(keyword.lower() in link_text for keyword in model_keywords) if model_keywords else False
                    
                    if brand_match and (model_match or len(model_keywords) == 0):
                        full_url = urljoin(self.base_url, href)
                        logger.info(f"Found potential match: {link_text} -> {full_url}")
                        return full_url
            
            logger.warning(f"No product page found for {brand} {model}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Search failed for {brand} {model}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error searching {brand} {model}: {e}")
            return None
    
    def extract_phone_details(self, product_url):
        """Extract detailed specifications from GSMArena product page"""
        try:
            logger.info(f"Extracting details from: {product_url}")
            
            response = self.session.get(product_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {}
            
            # Extract basic info from specs table
            spec_tables = soup.find_all('table')
            
            for table in spec_tables:
                rows = table.find_all('tr')
                current_category = None
                
                for row in rows:
                    # Check if this is a category header
                    th = row.find('th')
                    if th and th.get('colspan'):
                        current_category = th.get_text(strip=True)
                        continue
                    
                    # Extract spec data
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        # Map specifications based on key
                        if 'OS' in key or 'operating system' in key.lower():
                            details['os'] = value
                        elif 'Chipset' in key or 'chipset' in key.lower():
                            details['processor'] = value
                        elif 'CPU' in key and 'processor' not in details:
                            details['processor'] = value
                        elif 'Dimensions' in key or 'dimensions' in key.lower():
                            details['dimensions'] = value
                        elif 'Weight' in key or 'weight' in key.lower():
                            # Extract numeric weight
                            weight_match = re.search(r'(\d+(?:\.\d+)?)', value)
                            if weight_match:
                                details['weight'] = float(weight_match.group(1))
                        elif 'Battery' in key or 'battery' in key.lower():
                            details['battery'] = value
                        elif 'Charging' in key or 'charging' in key.lower():
                            details['charging_power'] = value
                        elif 'protection' in key.lower() or 'water' in key.lower():
                            details['water_resistance'] = value
                        elif 'Build' in key or 'build' in key.lower():
                            details['material'] = value
                        elif 'Colors' in key or 'colors' in key.lower():
                            details['colors'] = value
                        elif 'Network' in key or '2G' in key or '3G' in key or '4G' in key or '5G' in key:
                            if 'network_type' not in details:
                                details['network_type'] = value
                        elif 'Display' in key and 'Size' in key:
                            details['screen_size'] = value
                        elif 'Internal' in key or 'internal' in key.lower():
                            if 'storage' not in details:
                                details['storage'] = value
                        elif 'RAM' in key or 'Memory' in key:
                            if 'ram' not in details:
                                details['ram'] = value
                        elif 'Camera' in key and ('Main' in key or 'Primary' in key):
                            details['camera'] = value
            
            # Extract release year from announcement date
            announced_elem = soup.find('span', {'data-spec': 'released-hl'})
            if not announced_elem:
                # Alternative search for announcement info
                for elem in soup.find_all(['td', 'span'], string=re.compile(r'20\d{2}')):
                    text = elem.get_text()
                    year_match = re.search(r'(20\d{2})', text)
                    if year_match:
                        details['release_year'] = int(year_match.group(1))
                        break
            else:
                year_text = announced_elem.get_text()
                year_match = re.search(r'(20\d{2})', year_text)
                if year_match:
                    details['release_year'] = int(year_match.group(1))
            
            # Extract images
            image_urls = self.extract_product_images(soup, product_url)
            if image_urls:
                details.update(image_urls)
            
            logger.info(f"Extracted {len(details)} specifications")
            return details
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to extract details from {product_url}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error extracting details: {e}")
            return {}
    
    def extract_product_images(self, soup, base_url):
        """Extract product images from GSMArena page"""
        image_urls = {}
        
        try:
            # Look for main product image
            main_img = soup.find('div', class_='specs-photo-main')
            if main_img:
                img = main_img.find('img')
                if img:
                    src = img.get('src')
                    if src:
                        full_url = urljoin(base_url, src)
                        image_urls['image_front'] = full_url
            
            # Look for additional images in gallery
            gallery = soup.find('div', class_='specs-photo-gallery')
            if gallery:
                imgs = gallery.find_all('img')
                count = 0
                for img in imgs:
                    if count >= 2:  # Limit to 2 additional images
                        break
                    
                    src = img.get('src')
                    if src and src != image_urls.get('image_front'):
                        full_url = urljoin(base_url, src)
                        if count == 0:
                            image_urls['image_back'] = full_url
                        elif count == 1:
                            image_urls['image_side'] = full_url
                        count += 1
            
            return image_urls
            
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
            return {}
    
    def download_image(self, url, filename):
        """Download image and save locally"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            filepath = os.path.join(self.images_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Return relative path for database storage
            return f"/images/phones/{filename}"
            
        except Exception as e:
            logger.error(f"Failed to download image {url}: {e}")
            return None
    
    def get_flagship_phones_from_database(self):
        """Get all 167 flagship phones from database that need details"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        SELECT "Id", "Brand", "Model", "ReleaseYear"
                        FROM "Phones" 
                        WHERE ("Processor" IS NULL OR "Processor" = 'TBD')
                        ORDER BY "Brand", "Model"
                    ''')
                    
                    phones = []
                    for row in cur.fetchall():
                        phones.append({
                            'id': row[0],
                            'brand': row[1],
                            'model': row[2],
                            'year': row[3]
                        })
                    
                    logger.info(f"Found {len(phones)} flagship phones needing details")
                    return phones
                    
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return []
    
    def update_phone_details(self, phone_id, details):
        """Update phone details in database"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    update_fields = []
                    values = []
                    
                    # Map extracted details to database fields
                    field_mapping = {
                        'processor': 'Processor',
                        'os': 'Os',
                        'dimensions': 'Dimensions',
                        'weight': 'Weight',
                        'battery': 'Battery',
                        'charging_power': 'ChargingPower',
                        'water_resistance': 'WaterResistance',
                        'material': 'Material',
                        'colors': 'Colors',
                        'network_type': 'NetworkType',
                        'screen_size': 'ScreenSize',
                        'storage': 'Storage',
                        'ram': 'Ram',
                        'camera': 'Camera',
                        'image_front': 'ImageFront',
                        'image_back': 'ImageBack',
                        'image_side': 'ImageSide',
                        'release_year': 'ReleaseYear'
                    }
                    
                    for detail_key, db_field in field_mapping.items():
                        if detail_key in details and details[detail_key]:
                            update_fields.append(f'"{db_field}" = %s')
                            values.append(details[detail_key])
                    
                    if update_fields:
                        values.append(phone_id)
                        query = f'''
                            UPDATE "Phones" 
                            SET {", ".join(update_fields)}
                            WHERE "Id" = %s
                        '''
                        
                        cur.execute(query, values)
                        conn.commit()
                        
                        logger.info(f"Updated phone ID {phone_id} with {len(update_fields)} fields")
                        return True
                    
                    logger.warning(f"No valid details to update for phone ID {phone_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update phone {phone_id}: {e}")
            return False
    
    def crawl_flagship_phones(self):
        """Main crawling function for 167 flagship phones"""
        logger.info("Starting GSMArena flagship phone crawling")
        
        phones = self.get_flagship_phones_from_database()
        if not phones:
            logger.warning("No phones found to crawl")
            return
        
        total_phones = len(phones)
        updated_count = 0
        failed_count = 0
        
        print(f"🚀 Starting to crawl {total_phones} flagship phones from GSMArena")
        
        for i, phone in enumerate(phones, 1):
            print(f"\n📱 Processing {i}/{total_phones}: {phone['brand']} {phone['model']}")
            logger.info(f"Processing phone {i}/{total_phones}: {phone['brand']} {phone['model']}")
            
            try:
                # Search for product page
                product_url = self.search_phone_on_gsmarena(phone['brand'], phone['model'])
                
                if not product_url:
                    print(f"❌ No product page found")
                    failed_count += 1
                    continue
                
                # Extract details
                details = self.extract_phone_details(product_url)
                
                if not details:
                    print(f"❌ No details extracted")
                    failed_count += 1
                    continue
                
                # Download images if found
                image_fields = ['image_front', 'image_back', 'image_side']
                for field in image_fields:
                    if field in details and details[field]:
                        # Generate local filename
                        brand_clean = re.sub(r'[^\w\-_]', '_', phone['brand'])
                        model_clean = re.sub(r'[^\w\-_\s]', '_', phone['model'])
                        model_clean = re.sub(r'\s+', '_', model_clean)
                        filename = f"{brand_clean}_{model_clean}_{field.split('_')[1]}.jpg"
                        
                        local_path = self.download_image(details[field], filename)
                        if local_path:
                            details[field] = local_path
                        else:
                            del details[field]
                
                # Update database
                if self.update_phone_details(phone['id'], details):
                    updated_count += 1
                    print(f"✅ Successfully updated with {len(details)} details")
                else:
                    failed_count += 1
                    print(f"❌ Failed to update database")
                
                # Rate limiting - be respectful to GSMArena
                time.sleep(3)  # 3 seconds between requests
                
            except Exception as e:
                logger.error(f"Error processing {phone['brand']} {phone['model']}: {e}")
                print(f"❌ Error: {e}")
                failed_count += 1
                continue
        
        print(f"\n🎉 Crawling completed!")
        print(f"✅ Successfully updated: {updated_count} phones")
        print(f"❌ Failed: {failed_count} phones")
        logger.info(f"Crawling completed: {updated_count} updated, {failed_count} failed")

def main():
    """Main function"""
    print("🚀 GSMArena Flagship Phone Crawler")
    print("Crawling detailed specifications for 167 flagship phones (2020-2024)")
    
    db_config = {
        'host': 'localhost',
        'database': 'mobilephone_db',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    crawler = GSMArenaFlagshipCrawler(db_config)
    crawler.crawl_flagship_phones()

if __name__ == "__main__":
    main()
