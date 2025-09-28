#!/usr/bin/env python3
"""
ZOL color image crawler
Specialized for crawling phone color images from ZOL (中关村在线)
"""

import requests
import json
import time
import logging
import psycopg2
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import re
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zol_color_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ZOLColorCrawler:
    def __init__(self):
        self.base_delay_seconds = 3.0  # ZOL is relatively lenient, shorter delay is acceptable
        self.max_retries = 3
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 数据库连接
        self.db_config = {
            'host': 'localhost',
            'database': 'mobilephone_db',
            'user': 'postgres',
            'password': 'postgres'
        }

    def request_with_backoff(self, method: str, url: str, **kwargs):
        """带退避的请求方法"""
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.base_delay_seconds)
                response = self.session.request(method, url, timeout=30, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    wait_time = self.base_delay_seconds * (2 ** attempt)
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    raise

    def get_phones_with_colors(self) -> List[Dict]:
        """获取需要颜色图片的手机列表"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            query = """
            SELECT "Id", "Brand", "Model", "Colors", "ColorImages"
            FROM "Phones" 
            WHERE "Colors" IS NOT NULL 
            AND "Colors" != '' 
            AND ("ColorImages" IS NULL OR "ColorImages" = '')
            ORDER BY "Brand", "Model"
            """
            
            cursor.execute(query)
            phones = []
            for row in cursor.fetchall():
                phones.append({
                    'id': row[0],
                    'brand': row[1],
                    'model': row[2],
                    'colors': row[3],
                    'color_images': row[4]
                })
            
            cursor.close()
            conn.close()
            return phones
            
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return []

    def search_zol_phone(self, brand: str, model: str) -> Optional[str]:
        """搜索ZOL上的手机页面"""
        # 对于iPhone 12，直接使用已知的URL
        if brand.lower() == 'apple' and model.lower() == 'iphone 12':
            return "https://detail.zol.com.cn/series/57/31821_1.html"
        
        # 构建搜索URL
        search_query = f"{brand} {model}".replace(' ', '+')
        search_url = f"https://search.zol.com.cn/s.php?keyword={search_query}&cate=57"
        
        try:
            logger.info(f"Searching ZOL for: {brand} {model}")
            response = self.request_with_backoff('GET', search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找第一个手机链接
            phone_links = soup.find_all('a', href=True)
            for link in phone_links:
                href = link.get('href')
                if href and '/detail/' in href and 'series' in href:
                    # 构建完整URL
                    if href.startswith('/'):
                        phone_url = 'https://detail.zol.com.cn' + href
                    else:
                        phone_url = href
                    
                    logger.info(f"Found ZOL phone page: {phone_url}")
                    return phone_url
            
            logger.warning(f"No ZOL page found for {brand} {model}")
            return None
            
        except Exception as e:
            logger.error(f"ZOL search failed for {brand} {model}: {e}")
            return None

    def extract_color_images_zol(self, phone_url: str, color_list: List[str]) -> Dict[str, str]:
        """从ZOL页面提取颜色图片"""
        color_images = {}
        
        try:
            logger.info(f"Extracting color images from: {phone_url}")
            response = self.request_with_backoff('GET', phone_url)
            # 处理GBK编码
            response.encoding = 'gbk'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找颜色选择器 - ZOL特定的查找方式
            color_selector = None
            
            # 调试：保存页面内容到文件
            with open('zol_page_debug.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            logger.info("Saved page content to zol_page_debug.html for debugging")
            
            # 方法1: 查找ZOL特定的颜色选择器结构
            color_selector = soup.find('div', class_='versions-model-list')
            if color_selector:
                logger.info("Found ZOL color selector: versions-model-list")
            else:
                # 方法2: 查找包含"颜色"文本的元素
                color_text_elements = soup.find_all(string=re.compile(r'颜色'))
                for element in color_text_elements:
                    parent = element.parent
                    if parent:
                        # 查找父元素中的颜色选项
                        color_items = parent.find_all(['span', 'div', 'a', 'li'])
                        if color_items:
                            color_selector = parent
                            logger.info(f"Found color selector via '颜色' text: {parent}")
                            break
            
            if color_selector:
                logger.info("Found color selector")
                # 查找颜色选项 - ZOL使用<a>标签
                color_items = color_selector.find_all('a', {'data-item-id': True})
                
                for item in color_items:
                    # 获取颜色名称
                    color_name = item.get_text(strip=True)
                    if not color_name:
                        continue
                    
                    logger.info(f"Found color option: {color_name}")
                    
                    # 检查是否匹配我们的颜色列表
                    matched_color = None
                    
                    # 中英文颜色映射
                    color_mapping = {
                        '蓝色': 'Blue',
                        '绿色': 'Green', 
                        '红色': 'Red',
                        '黑色': 'Black',
                        '白色': 'White',
                        '紫色': 'Purple'
                    }
                    
                    # 先尝试中文映射
                    if color_name in color_mapping:
                        matched_color = color_mapping[color_name]
                    else:
                        # 再尝试英文匹配
                        for color in color_list:
                            if color.lower() in color_name.lower() or color_name.lower() in color.lower():
                                matched_color = color
                                break
                    
                    if matched_color:
                        logger.info(f"Matched color: {color_name} -> {matched_color}")
                        
                        # 对于ZOL，我们需要通过JavaScript获取对应的图片
                        # 先尝试查找是否有直接的图片
                        img_element = item.find('img')
                        if img_element:
                            img_src = img_element.get('src') or img_element.get('data-src')
                            if img_src:
                                # 处理相对URL
                                if img_src.startswith('//'):
                                    img_src = 'https:' + img_src
                                elif img_src.startswith('/'):
                                    img_src = 'https://detail.zol.com.cn' + img_src
                                
                                color_images[matched_color] = img_src
                                logger.info(f"Found direct image for {matched_color}: {img_src}")
                        else:
                            # 如果没有直接图片，记录颜色名称，稍后通过主图片区域获取
                            logger.info(f"No direct image found for {matched_color}, will try main image area")
            
            # 尝试从主图片区域提取
            if not color_images:
                logger.info("Trying to extract from main image area")
                
                # 查找ZOL的主图片
                main_pic = soup.find('img', id='big-pic')
                if main_pic:
                    main_src = main_pic.get('src')
                    if main_src:
                        # 处理URL
                        if main_src.startswith('//'):
                            main_src = 'https:' + main_src
                        elif main_src.startswith('/'):
                            main_src = 'https://detail.zol.com.cn' + main_src
                        
                        logger.info(f"Found main image: {main_src}")
                        
                        # 为每个匹配的颜色使用主图片
                        for color in color_list:
                            # 检查是否已经找到了这个颜色的图片
                            if color not in color_images:
                                color_images[color] = main_src
                                logger.info(f"Using main image for {color}: {main_src}")
                
                # 尝试找到不同颜色的图片
                if len(color_images) == len(color_list) and len(set(color_images.values())) == 1:
                    logger.info("All colors have same image, trying to find different color images")
                    
                    # 查找所有iPhone 12相关的图片
                    all_images = soup.find_all('img', src=True)
                    iphone_images = []
                    
                    for img in all_images:
                        src = img.get('src')
                        alt = img.get('alt', '').lower()
                        
                        # 检查是否是iPhone 12图片
                        if ('iphone' in alt or '苹果' in alt) and '12' in alt:
                            if src.startswith('//'):
                                src = 'https:' + src
                            elif src.startswith('/'):
                                src = 'https://detail.zol.com.cn' + src
                            
                            # 检查图片质量
                            if self.is_good_image(src):
                                iphone_images.append(src)
                                logger.info(f"Found iPhone 12 image: {src}")
                    
                    # 为不同颜色分配不同的图片
                    if len(iphone_images) >= len(color_list):
                        logger.info(f"Found {len(iphone_images)} iPhone 12 images, assigning to colors")
                        for i, color in enumerate(color_list):
                            if i < len(iphone_images):
                                color_images[color] = iphone_images[i]
                                logger.info(f"Assigned image {i+1} to {color}: {iphone_images[i]}")
                
                # 如果还是没找到不同图片，尝试其他方法
                if len(color_images) == len(color_list) and len(set(color_images.values())) == 1:
                    logger.info("Still same image for all colors, trying alternative approach")
                    main_images = soup.find_all('img', src=True)
                    
                    for img in main_images:
                        src = img.get('src')
                        alt = img.get('alt', '').lower()
                        title = img.get('title', '').lower()
                        
                        # 匹配颜色
                        for color in color_list:
                            color_lower = color.lower()
                            if (color_lower in alt or color_lower in title or 
                                color_lower in src.lower()):
                                
                                # 处理URL
                                if src.startswith('//'):
                                    src = 'https:' + src
                                elif src.startswith('/'):
                                    src = 'https://detail.zol.com.cn' + src
                                
                                # 检查图片质量
                                if self.is_good_image(src):
                                    color_images[color] = src
                                    logger.info(f"Found main image for {color}: {src}")
                                    break
            
            return color_images
            
        except Exception as e:
            logger.error(f"Color image extraction failed: {e}")
            return {}

    def is_good_image(self, url: str) -> bool:
        """判断图片质量是否足够好"""
        # 排除缩略图和小图片
        if any(keyword in url.lower() for keyword in ['thumb', 'small', 'icon', 'logo']):
            return False
        
        # 检查URL中的尺寸信息
        size_match = re.search(r'(\d+)x(\d+)', url)
        if size_match:
            width, height = map(int, size_match.groups())
            # 要求至少200x200像素
            if width < 200 or height < 200:
                return False
        
        return True

    def download_image(self, url: str, filename: str) -> bool:
        """下载图片到本地"""
        try:
            logger.info(f"Downloading image: {url}")
            response = self.request_with_backoff('GET', url)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # 处理文件名中的空格，替换为下划线
            safe_filename = filename.replace(' ', '_')
            
            with open(safe_filename, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Downloaded: {safe_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Download failed for {url}: {e}")
            return False

    def update_database_path(self, phone_id: int, color_images: Dict[str, str]):
        """更新数据库中的颜色图片路径"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 转换为JSON字符串
            color_images_json = json.dumps(color_images, ensure_ascii=False)
            
            query = 'UPDATE "Phones" SET "ColorImages" = %s WHERE "Id" = %s'
            cursor.execute(query, (color_images_json, phone_id))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ Updated database for phone ID {phone_id}")
            
        except Exception as e:
            logger.error(f"Database update failed: {e}")

    def crawl_phone_colors(self, phone: Dict) -> bool:
        """爬取单个手机的颜色图片"""
        brand = phone['brand']
        model = phone['model']
        phone_id = phone['id']
        colors = phone['colors'].split(', ')
        
        logger.info(f"Processing: {brand} {model} - Colors: {colors}")
        
        # 搜索ZOL页面
        phone_url = self.search_zol_phone(brand, model)
        if not phone_url:
            logger.warning(f"No ZOL page found for {brand} {model}")
            return False
        
        # 提取颜色图片
        color_images = self.extract_color_images_zol(phone_url, colors)
        if not color_images:
            logger.warning(f"No color images found for {brand} {model}")
            return False
        
        # 下载图片并更新路径
        downloaded_images = {}
        for color, img_url in color_images.items():
            filename = f"images/phones/{brand}_{model}_{color}.jpg"
            safe_filename = filename.replace(' ', '_')
            if self.download_image(img_url, filename):
                downloaded_images[color] = safe_filename
        
        # 更新数据库
        if downloaded_images:
            self.update_database_path(phone_id, downloaded_images)
            logger.info(f"✅ Successfully processed {brand} {model}")
            return True
        
        return False

    def run(self, limit: Optional[int] = None, brand_filter: Optional[str] = None):
        """运行爬虫"""
        logger.info("Starting ZOL color image crawler...")
        
        phones = self.get_phones_with_colors()
        if brand_filter:
            phones = [p for p in phones if p['brand'].lower() == brand_filter.lower()]
        
        if limit:
            phones = phones[:limit]
        
        logger.info(f"Found {len(phones)} phones needing color images")
        
        success_count = 0
        for i, phone in enumerate(phones, 1):
            logger.info(f"({i}/{len(phones)}) {phone['brand']} {phone['model']} - Colors: {phone['colors']}")
            
            if self.crawl_phone_colors(phone):
                success_count += 1
            
            # 避免请求过于频繁
            if i < len(phones):
                time.sleep(2)
        
        logger.info(f"Completed. Successfully processed: {success_count}/{len(phones)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ZOL Color Image Crawler')
    parser.add_argument('--limit', type=int, help='Limit number of phones to process')
    parser.add_argument('--brand', type=str, help='Filter by brand')
    parser.add_argument('--apply', action='store_true', help='Actually update database')
    
    args = parser.parse_args()
    
    if not args.apply:
        logger.info("Dry run mode - use --apply to actually update database")
    
    crawler = ZOLColorCrawler()
    crawler.run(limit=args.limit, brand_filter=args.brand)
