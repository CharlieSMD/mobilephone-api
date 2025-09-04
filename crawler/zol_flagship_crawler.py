#!/usr/bin/env python3
"""
ZOL Flagship Phone Crawler
Crawls detailed specifications and images for flagship phones from ZOL (zhongguancun.com)
Targets the 167 flagship models from 2020-2024 in the database
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
        logging.FileHandler('zol_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ZOLCrawler:
    def __init__(self, db_config):
        self.db_config = db_config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.base_url = "https://detail.zol.com.cn"
        self.search_url = "https://search.zol.com.cn/s/shouji_"
        
        # Create images directory
        self.images_dir = os.path.join("..", "..", "images", "phones")
        os.makedirs(self.images_dir, exist_ok=True)
        
    def normalize_brand_for_search(self, brand):
        """Normalize brand name for ZOL search"""
        brand_mapping = {
            'Apple': '苹果',
            'Samsung': '三星',
            'Google': '谷歌',
            'Sony': '索尼',
            'Xiaomi': '小米',
            'OPPO': 'OPPO',
            'vivo': 'vivo',
            'OnePlus': '一加',
            'ASUS': '华硕',
            'Huawei': '华为',
            'Honor': '荣耀'
        }
        return brand_mapping.get(brand, brand)
    
    def normalize_model_for_search(self, model):
        """Normalize model name for ZOL search"""
        # Remove common suffixes that might not match
        model = re.sub(r'\s+(5G|4G|LTE|Dual|SIM)(\s|$)', ' ', model, flags=re.IGNORECASE)
        
        # Handle specific model patterns
        if 'iPhone' in model:
            # Convert "iPhone 15 Pro Max" to "iPhone15 Pro Max"
            model = re.sub(r'iPhone\s+(\d+)', r'iPhone\1', model)
        elif 'Galaxy' in model:
            # Convert "Galaxy S24 Ultra" to "Galaxy S24 Ultra"
            pass  # Keep as is for Samsung
        elif 'Pixel' in model:
            # Convert "Pixel 8 Pro" to "Pixel8 Pro"
            model = re.sub(r'Pixel\s+(\d+)', r'Pixel\1', model)
        elif 'Xperia' in model:
            # Convert "Xperia 1 VI" to "Xperia1 VI"
            model = re.sub(r'Xperia\s+(\d+)', r'Xperia\1', model)
        
        return model.strip()
    
    def search_phone_on_zol(self, brand, model):
        """Search for phone on ZOL and return the product page URL"""
        try:
            # Normalize brand and model for search
            search_brand = self.normalize_brand_for_search(brand)
            search_model = self.normalize_model_for_search(model)
            
            # Construct search query
            search_query = f"{search_brand} {search_model}"
            encoded_query = quote(search_query.encode('utf-8'))
            search_url = f"{self.search_url}{encoded_query}.html"
            
            logger.info(f"Searching ZOL for: {search_query}")
            logger.info(f"Search URL: {search_url}")
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for product links in search results
            product_links = soup.find_all('a', href=re.compile(r'/detail\.zol\.com\.cn/.*\.html'))
            
            if not product_links:
                # Try alternative search patterns
                product_links = soup.find_all('a', href=re.compile(r'detail\.zol\.com\.cn'))
            
            for link in product_links:
                href = link.get('href')
                if href:
                    # Ensure full URL
                    if href.startswith('//'):
                        href = 'https:' + href
                    elif href.startswith('/'):
                        href = 'https://search.zol.com.cn' + href
                    
                    # Check if this looks like a phone detail page
                    if 'detail.zol.com.cn' in href and any(keyword in href.lower() for keyword in ['shouji', 'mobile', 'phone']):
                        logger.info(f"Found potential match: {href}")
                        return href
            
            logger.warning(f"No product page found for {brand} {model}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Search failed for {brand} {model}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error searching {brand} {model}: {e}")
            return None
    
    def extract_phone_details(self, product_url):
        """Extract detailed specifications from ZOL product page"""
        try:
            logger.info(f"Extracting details from: {product_url}")
            
            response = self.session.get(product_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {}
            
            # Extract specifications from parameter table
            param_tables = soup.find_all('table', class_=re.compile(r'param.*table|spec.*table'))
            if not param_tables:
                param_tables = soup.find_all('table')
            
            for table in param_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        # Map common specifications
                        if any(keyword in key for keyword in ['处理器', 'CPU', '芯片']):
                            details['processor'] = value
                        elif any(keyword in key for keyword in ['操作系统', 'OS', '系统']):
                            details['os'] = value
                        elif any(keyword in key for keyword in ['尺寸', '机身尺寸', '外观尺寸']):
                            details['dimensions'] = value
                        elif any(keyword in key for keyword in ['重量', '机身重量']):
                            # Extract numeric weight
                            weight_match = re.search(r'(\d+(?:\.\d+)?)', value)
                            if weight_match:
                                details['weight'] = float(weight_match.group(1))
                        elif any(keyword in key for keyword in ['电池', '电池容量']):
                            details['battery'] = value
                        elif any(keyword in key for keyword in ['充电', '充电功率', '快充']):
                            details['charging_power'] = value
                        elif any(keyword in key for keyword in ['防水', '防护等级']):
                            details['water_resistance'] = value
                        elif any(keyword in key for keyword in ['材质', '机身材质']):
                            details['material'] = value
                        elif any(keyword in key for keyword in ['颜色', '机身颜色', '配色']):
                            details['colors'] = value
                        elif any(keyword in key for keyword in ['网络', '网络制式', '网络类型']):
                            details['network_type'] = value
                        elif any(keyword in key for keyword in ['屏幕尺寸', '显示屏尺寸']):
                            details['screen_size'] = value
                        elif any(keyword in key for keyword in ['存储', '机身内存', 'ROM']):
                            details['storage'] = value
                        elif any(keyword in key for keyword in ['运行内存', 'RAM', '内存']):
                            details['ram'] = value
                        elif any(keyword in key for keyword in ['摄像头', '后置摄像头', '主摄']):
                            details['camera'] = value
            
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
        """Extract product images from the page"""
        image_urls = {}
        
        try:
            # Look for main product image
            main_img = soup.find('img', {'id': re.compile(r'.*bigpic.*|.*mainpic.*|.*product.*img.*')})
            if not main_img:
                main_img = soup.find('img', class_=re.compile(r'.*product.*|.*main.*|.*big.*'))
            if not main_img:
                # Fallback: look for any large image
                imgs = soup.find_all('img')
                for img in imgs:
                    src = img.get('src') or img.get('data-src')
                    if src and any(size in src for size in ['800x', '600x', '400x']):
                        main_img = img
                        break
            
            if main_img:
                src = main_img.get('src') or main_img.get('data-src')
                if src:
                    full_url = urljoin(base_url, src)
                    image_urls['image_front'] = full_url
            
            # Look for additional images in gallery
            gallery_imgs = soup.find_all('img', src=re.compile(r'.*\.(jpg|jpeg|png|webp)', re.IGNORECASE))
            
            count = 0
            for img in gallery_imgs:
                if count >= 2:  # Limit to avoid too many images
                    break
                    
                src = img.get('src') or img.get('data-src')
                if src and src != image_urls.get('image_front'):
                    full_url = urljoin(base_url, src)
                    if count == 0 and 'image_back' not in image_urls:
                        image_urls['image_back'] = full_url
                    elif count == 1 and 'image_side' not in image_urls:
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
    
    def get_phones_from_database(self):
        """Get all flagship phones from database that need details"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        SELECT "Id", "Brand", "Model", "ReleaseYear"
                        FROM "Phones" 
                        WHERE "Processor" IS NULL OR "Processor" = 'TBD'
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
                    
                    logger.info(f"Found {len(phones)} phones needing details")
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
                        'image_side': 'ImageSide'
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
        """Main crawling function for flagship phones"""
        logger.info("Starting ZOL flagship phone crawling")
        
        phones = self.get_phones_from_database()
        if not phones:
            logger.warning("No phones found to crawl")
            return
        
        total_phones = len(phones)
        updated_count = 0
        failed_count = 0
        
        for i, phone in enumerate(phones, 1):
            logger.info(f"Processing phone {i}/{total_phones}: {phone['brand']} {phone['model']}")
            
            try:
                # Search for product page
                product_url = self.search_phone_on_zol(phone['brand'], phone['model'])
                
                if not product_url:
                    logger.warning(f"No product page found for {phone['brand']} {phone['model']}")
                    failed_count += 1
                    continue
                
                # Extract details
                details = self.extract_phone_details(product_url)
                
                if not details:
                    logger.warning(f"No details extracted for {phone['brand']} {phone['model']}")
                    failed_count += 1
                    continue
                
                # Download images if found
                image_fields = ['image_front', 'image_back', 'image_side']
                for field in image_fields:
                    if field in details and details[field]:
                        # Generate local filename
                        brand_clean = re.sub(r'[^\w\-_]', '_', phone['brand'])
                        model_clean = re.sub(r'[^\w\-_]', '_', phone['model'])
                        filename = f"{brand_clean}_{model_clean}_{field.split('_')[1]}.jpg"
                        
                        local_path = self.download_image(details[field], filename)
                        if local_path:
                            details[field] = local_path
                        else:
                            del details[field]
                
                # Update database
                if self.update_phone_details(phone['id'], details):
                    updated_count += 1
                    logger.info(f"Successfully updated {phone['brand']} {phone['model']}")
                else:
                    failed_count += 1
                
                # Rate limiting
                time.sleep(2)  # 2 seconds between requests
                
            except Exception as e:
                logger.error(f"Error processing {phone['brand']} {phone['model']}: {e}")
                failed_count += 1
                continue
        
        logger.info(f"Crawling completed: {updated_count} updated, {failed_count} failed")

def main():
    """Main function"""
    print("🚀 ZOL Flagship Phone Crawler")
    print("Crawling detailed specifications for 167 flagship phones")
    
    db_config = {
        'host': 'localhost',
        'database': 'mobilephone_db',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    crawler = ZOLCrawler(db_config)
    crawler.crawl_flagship_phones()

if __name__ == "__main__":
    main()
