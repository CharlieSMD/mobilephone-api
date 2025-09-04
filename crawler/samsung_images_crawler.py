#!/usr/bin/env python3
"""
Samsung Image Crawler
专门为三星手机下载图片的爬虫
"""

import requests
import time
import random
import os
import sys
import psycopg2
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import json

# 获取脚本所在目录的上级目录（项目根目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
IMAGES_DIR = os.path.join(PROJECT_ROOT, "images", "phones")

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'database': 'mobilephone_db',
    'user': 'postgres',
    'password': 'postgres'
}

# GSMArena基础URL
GSMARENA_BASE = "https://www.gsmarena.com"
SEARCH_URL = "https://www.gsmarena.com/results.php3?sQuickSearch=yes&sName="

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def get_samsung_phones_without_images():
    """获取没有图片的三星手机"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT "Brand", "Model", "ImageUrl" 
            FROM "Phones" 
            WHERE "Brand" = 'Samsung' 
            AND "ImageUrl" LIKE '%placeholder%'
            ORDER BY "Model"
        """)
        
        phones = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return phones
    except Exception as e:
        print(f"查询数据库失败: {e}")
        if conn:
            conn.close()
        return []

def search_phone_on_gsmarena(phone_model):
    """在GSMArena搜索手机"""
    search_term = f"Samsung {phone_model}"
    search_url = SEARCH_URL + requests.utils.quote(search_term)
    
    try:
        print(f"🔍 搜索: {search_term}")
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找搜索结果
        results = soup.find_all('div', class_='makers')
        if not results:
            return None
        
        # 获取第一个结果
        first_result = results[0].find('a')
        if not first_result:
            return None
        
        phone_url = urljoin(GSMARENA_BASE, first_result['href'])
        print(f"✅ 找到手机页面: {phone_url}")
        
        return phone_url
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return None

def get_phone_images(phone_url):
    """获取手机图片"""
    try:
        print(f"📱 获取手机图片: {phone_url}")
        response = requests.get(phone_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找图片
        images = []
        
        # 查找主图片
        main_image = soup.find('div', class_='specs-photo-main')
        if main_image:
            img_tag = main_image.find('img')
            if img_tag and img_tag.get('src'):
                img_url = urljoin(GSMARENA_BASE, img_tag['src'])
                images.append(img_url)
        
        # 查找其他图片
        photo_gallery = soup.find('div', class_='specs-photo-main')
        if photo_gallery:
            gallery_images = photo_gallery.find_all('img')
            for img in gallery_images:
                if img.get('src'):
                    img_url = urljoin(GSMARENA_BASE, img['src'])
                    if img_url not in images:
                        images.append(img_url)
        
        print(f"📸 找到 {len(images)} 张图片")
        return images
        
    except Exception as e:
        print(f"❌ 获取图片失败: {e}")
        return []

def download_image(image_url, local_path):
    """下载图片"""
    try:
        print(f"⬇️ 下载图片: {image_url}")
        response = requests.get(image_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # 保存图片
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ 图片已保存: {local_path}")
        return True
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

def update_database_image_url(phone_model, image_url):
    """更新数据库中的图片URL"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE "Phones" 
            SET "ImageUrl" = %s 
            WHERE "Brand" = 'Samsung' AND "Model" = %s
        """, (image_url, phone_model))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ 数据库已更新: {phone_model}")
        return True
        
    except Exception as e:
        print(f"❌ 数据库更新失败: {e}")
        if conn:
            conn.close()
        return False

def process_samsung_phone(phone_model):
    """处理单个三星手机"""
    print(f"\n🚀 开始处理: Samsung {phone_model}")
    
    # 搜索手机
    phone_url = search_phone_on_gsmarena(phone_model)
    if not phone_url:
        print(f"❌ 未找到手机: {phone_model}")
        return False
    
    # 获取图片
    images = get_phone_images(phone_url)
    if not images:
        print(f"❌ 未找到图片: {phone_model}")
        return False
    
    # 下载第一张图片
    image_url = images[0]
    local_filename = f"Samsung_{phone_model.replace(' ', '_')}.jpg"
    local_path = os.path.join(IMAGES_DIR, local_filename)
    
    if download_image(image_url, local_path):
        # 更新数据库
        db_url = f"http://localhost:5198/images/phones/{local_filename}"
        if update_database_image_url(phone_model, db_url):
            print(f"🎉 成功处理: {phone_model}")
            return True
    
    return False

def main():
    """主函数"""
    print("🔄 三星手机图片爬虫启动")
    print("=" * 50)
    print(f"📁 图片保存目录: {IMAGES_DIR}")
    
    # 获取需要处理的手机
    phones = get_samsung_phones_without_images()
    if not phones:
        print("✅ 所有三星手机都有图片了！")
        return
    
    print(f"📱 找到 {len(phones)} 部需要图片的三星手机:")
    for brand, model, image_url in phones:
        print(f"  • {model}")
    
    print("\n" + "=" * 50)
    
    # 处理每部手机
    success_count = 0
    total_count = len(phones)
    
    for i, (brand, model, image_url) in enumerate(phones, 1):
        print(f"\n📊 进度: {i}/{total_count}")
        
        if process_samsung_phone(model):
            success_count += 1
        
        # 随机延迟，避免被限制
        if i < total_count:
            delay = random.uniform(3, 8)
            print(f"⏳ 等待 {delay:.1f} 秒...")
            time.sleep(delay)
    
    print("\n" + "=" * 50)
    print(f"🎉 爬虫完成！")
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失败: {total_count - success_count}/{total_count}")

if __name__ == "__main__":
    main()
