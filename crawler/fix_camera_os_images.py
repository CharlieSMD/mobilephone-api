#!/usr/bin/env python3
"""
修复Camera、OS和Images字段
1. 从GSMArena抓取Camera信息
2. 根据品牌自动填充OS信息  
3. 从GSMArena获取真实产品图片
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
        logging.FileHandler('fix_camera_os_images.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CameraOSImagesFixer:
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
        
    def get_phones_to_fix(self):
        """Get phones that need Camera/OS/Images fixes"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            query = '''
            SELECT "Id", "Brand", "Model" 
            FROM "Phones" 
            WHERE ("Brand" IN ('Samsung', 'OnePlus'))
            AND "Camera" = 'TBD'
            ORDER BY "Brand", "Model"
            LIMIT 15
            '''
            
            cur.execute(query)
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
    
    def extract_camera_os_image_data(self, phone_url, brand):
        """Extract Camera, OS and Image data from GSMArena phone page"""
        try:
            response = self.session.get(phone_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {}
            
            # 1. Extract Camera information
            # Method 1: Look for camera specs in highlights
            camera_elem = soup.find('span', {'data-spec': 'camerapixels-hl'})
            if camera_elem:
                camera_text = camera_elem.get_text(strip=True)
                # Try to determine camera count based on MP info
                if 'MP' in camera_text:
                    mp_value = camera_text.replace('MP', '').strip()
                    # This is a simplified approach - could be improved
                    if '+' in mp_value or 'Triple' in soup.get_text() or 'triple' in soup.get_text().lower():
                        data['camera'] = 'Triple'
                    elif 'Dual' in soup.get_text() or 'dual' in soup.get_text().lower():
                        data['camera'] = 'Dual'
                    else:
                        data['camera'] = 'Single'
                    logger.info(f"✅ Camera: {data['camera']}")
            
            # Method 2: Look for camera info in detailed specs
            if not data.get('camera'):
                # Search for camera specifications in the page
                page_text = soup.get_text().lower()
                if 'triple' in page_text or '3 cam' in page_text:
                    data['camera'] = 'Triple'
                elif 'dual' in page_text or '2 cam' in page_text:
                    data['camera'] = 'Dual'
                else:
                    data['camera'] = 'Single'  # Default assumption
                logger.info(f"✅ Camera (from text): {data['camera']}")
            
            # 2. Extract Operating System
            os_elem = soup.find('span', {'data-spec': 'os-hl'})
            if os_elem:
                os_text = os_elem.get_text(strip=True)
                data['os'] = os_text
                logger.info(f"✅ OS: {os_text}")
            else:
                # Auto-fill based on brand
                if brand.lower() == 'apple':
                    data['os'] = 'iOS'
                else:
                    data['os'] = 'Android'
                logger.info(f"✅ OS (auto-filled): {data['os']}")
            
            # 3. Extract Product Image
            # Look for the main product image
            img_elements = soup.find_all('img')
            for img in img_elements:
                src = img.get('src', '')
                alt = img.get('alt', '').lower()
                
                # Look for main product images
                if (('phone' in alt or 'smartphone' in alt or brand.lower() in alt) 
                    and ('.jpg' in src or '.png' in src or '.webp' in src)
                    and 'logo' not in src.lower()
                    and 'icon' not in src.lower()
                    and src.startswith('http')):
                    
                    data['image_url'] = src
                    logger.info(f"✅ Image: {src}")
                    break
            
            # Fallback: look for any large image
            if not data.get('image_url'):
                for img in img_elements:
                    src = img.get('src', '')
                    if (('.jpg' in src or '.png' in src or '.webp' in src)
                        and src.startswith('http')
                        and 'logo' not in src.lower()
                        and 'icon' not in src.lower()):
                        data['image_url'] = src
                        logger.info(f"✅ Image (fallback): {src}")
                        break
            
            logger.info(f"Extracted data for {phone_url}: {list(data.keys())}")
            return data
            
        except Exception as e:
            logger.error(f"Error extracting data from {phone_url}: {e}")
            return {}
    
    def update_phone_data(self, phone_id, data):
        """Update phone with Camera, OS and Image data"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Build update query
            update_fields = []
            values = []
            
            if data.get('camera'):
                update_fields.append('"Camera" = %s')
                values.append(data['camera'])
            
            if data.get('os'):
                update_fields.append('"Os" = %s')
                values.append(data['os'])
            
            if data.get('image_url'):
                update_fields.append('"ImageUrl" = %s')
                values.append(data['image_url'])
            
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
    
    def fix_camera_os_images(self):
        """Main method to fix Camera, OS and Images"""
        phones = self.get_phones_to_fix()
        
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
            
            # Extract Camera, OS and Image data
            data = self.extract_camera_os_image_data(phone_url, brand)
            
            if not data:
                logger.error(f"❌ No data extracted for {brand} {model}")
                fail_count += 1
                continue
            
            # Update database
            if self.update_phone_data(phone_id, data):
                success_count += 1
                logger.info(f"✅ Successfully updated {brand} {model}")
            else:
                fail_count += 1
                logger.error(f"❌ Failed to update {brand} {model}")
            
            # Add delay between requests
            time.sleep(4)
        
        logger.info(f"\n🎯 Camera/OS/Images Fix completed!")
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
    
    fixer = CameraOSImagesFixer(db_config)
    fixer.fix_camera_os_images()

if __name__ == "__main__":
    main()
