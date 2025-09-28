#!/usr/bin/env python3
"""
Download all phone images to local storage
Download GSMArena images and other external images to local images folder
"""

import requests
import psycopg2
import os
import logging
from urllib.parse import urlparse
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download_images.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImageDownloader:
    def __init__(self, images_dir):
        self.images_dir = images_dir
        self.phones_dir = os.path.join(images_dir, 'phones')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Ensure directory exists
        os.makedirs(self.phones_dir, exist_ok=True)
        
    def get_images_to_download(self):
        """Get list of images that need to be downloaded"""
        try:
            conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
            cur = conn.cursor()
            
            # 获取所有外部图片URL
            cur.execute('''
                SELECT "Id", "Brand", "Model", "ImageUrl" 
                FROM "Phones" 
                WHERE "ImageUrl" LIKE 'https://%' 
                   OR "ImageUrl" LIKE 'http://%'
                ORDER BY "Brand", "Model"
            ''')
            
            images = cur.fetchall()
            cur.close()
            conn.close()
            
            logger.info(f"Found {len(images)} images to download")
            return images
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            return []
    
    def generate_local_filename(self, brand, model, image_url):
        """生成本地文件名"""
        # 获取文件扩展名
        parsed_url = urlparse(image_url)
        file_ext = os.path.splitext(parsed_url.path)[1] or '.jpg'
        
        # 清理品牌和型号名称，移除特殊字符
        clean_brand = "".join(c for c in brand if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_model = "".join(c for c in model if c.isalnum() or c in (' ', '-', '_')).strip()
        
        # 生成文件名
        filename = f"{clean_brand}_{clean_model}{file_ext}".replace(' ', '_')
        return filename
    
    def download_image(self, image_url, local_path):
        """下载单张图片"""
        try:
            response = self.session.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Downloaded: {os.path.basename(local_path)}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to download {image_url}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error saving {local_path}: {e}")
            return False
    
    def update_database_path(self, phone_id, new_local_path):
        """更新数据库中的图片路径"""
        try:
            conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
            cur = conn.cursor()
            
            # 更新为本地路径
            local_url = f"http://localhost:5198/images/phones/{os.path.basename(new_local_path)}"
            cur.execute('UPDATE "Phones" SET "ImageUrl" = %s WHERE "Id" = %s', (local_url, phone_id))
            conn.commit()
            
            cur.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Database update error for phone {phone_id}: {e}")
            return False
    
    def download_all_images(self):
        """下载所有外部图片到本地"""
        images = self.get_images_to_download()
        
        if not images:
            logger.info("No images to download")
            return
        
        success_count = 0
        fail_count = 0
        
        for i, (phone_id, brand, model, image_url) in enumerate(images, 1):
            logger.info(f"\n📸 Processing {i}/{len(images)}: {brand} {model}")
            
            # 跳过已经是本地路径的图片
            if image_url.startswith('http://localhost:5198/'):
                logger.info(f"⏭️ Already local: {brand} {model}")
                continue
            
            # 生成本地文件名
            filename = self.generate_local_filename(brand, model, image_url)
            local_path = os.path.join(self.phones_dir, filename)
            
            # 如果文件已存在，跳过下载
            if os.path.exists(local_path):
                logger.info(f"⏭️ File exists: {filename}")
                # 更新数据库路径
                if self.update_database_path(phone_id, local_path):
                    success_count += 1
                continue
            
            # 下载图片
            if self.download_image(image_url, local_path):
                # 更新数据库路径
                if self.update_database_path(phone_id, local_path):
                    success_count += 1
                    logger.info(f"✅ {brand} {model}: {filename}")
                else:
                    fail_count += 1
            else:
                fail_count += 1
                logger.error(f"❌ Failed: {brand} {model}")
            
            # 添加延迟避免请求过快
            time.sleep(1)
        
        logger.info(f"\n🎯 Image Download completed!")
        logger.info(f"✅ Success: {success_count}")
        logger.info(f"❌ Failed: {fail_count}")
        logger.info(f"📊 Total processed: {len(images)}")
    
    def verify_local_images(self):
        """验证本地图片完整性"""
        try:
            conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
            cur = conn.cursor()
            
            cur.execute('''
                SELECT "Brand", "Model", "ImageUrl" 
                FROM "Phones" 
                WHERE "ImageUrl" LIKE 'http://localhost:5198/images/%'
            ''')
            
            local_images = cur.fetchall()
            cur.close()
            conn.close()
            
            missing_files = []
            for brand, model, image_url in local_images:
                # 提取文件名
                filename = image_url.split('/')[-1]
                local_path = os.path.join(self.phones_dir, filename)
                
                if not os.path.exists(local_path):
                    missing_files.append((brand, model, filename))
            
            if missing_files:
                logger.warning(f"⚠️ Found {len(missing_files)} missing local files:")
                for brand, model, filename in missing_files[:5]:  # 只显示前5个
                    logger.warning(f"   - {brand} {model}: {filename}")
            else:
                logger.info("✅ All local image files verified successfully!")
            
            return len(missing_files) == 0
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False

def main():
    # 设置图片目录
    images_dir = "/Users/shenmeidun/UoW_IT/COMPX576/MobilePhone/images"
    
    downloader = ImageDownloader(images_dir)
    
    logger.info("🚀 Starting image download process...")
    downloader.download_all_images()
    
    logger.info("\n🔍 Verifying downloaded images...")
    downloader.verify_local_images()
    
    logger.info("\n✨ Image download process completed!")

if __name__ == "__main__":
    main()

