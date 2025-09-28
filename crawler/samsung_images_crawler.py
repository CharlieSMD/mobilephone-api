#!/usr/bin/env python3
"""
Samsung Image Crawler
Crawler specialized for downloading images for Samsung phones
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

# Get parent directory of script location (project root)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
IMAGES_DIR = os.path.join(PROJECT_ROOT, "images", "phones")

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'mobilephone_db',
    'user': 'postgres',
    'password': 'postgres'
}

# GSMArena base URL
GSMARENA_BASE = "https://www.gsmarena.com"
SEARCH_URL = "https://www.gsmarena.com/results.php3?sQuickSearch=yes&sName="

# Request headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def get_samsung_phones_without_images():
    """Get Samsung phones without images"""
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
        print(f"Database query failed: {e}")
        if conn:
            conn.close()
        return []

def search_phone_on_gsmarena(phone_model):
    """Search phone on GSMArena"""
    search_term = f"Samsung {phone_model}"
    search_url = SEARCH_URL + requests.utils.quote(search_term)
    
    try:
        print(f"🔍 Search: {search_term}")
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find search results
        results = soup.find_all('div', class_='makers')
        if not results:
            return None
        
        # Get first result
        first_result = results[0].find('a')
        if not first_result:
            return None
        
        phone_url = urljoin(GSMARENA_BASE, first_result['href'])
        print(f"✅ Found phone page: {phone_url}")
        
        return phone_url
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return None

def get_phone_images(phone_url):
    """Fetch phone images"""
    try:
        print(f"📱 Fetch phone images: {phone_url}")
        response = requests.get(phone_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find images
        images = []
        
        # Find main image
        main_image = soup.find('div', class_='specs-photo-main')
        if main_image:
            img_tag = main_image.find('img')
            if img_tag and img_tag.get('src'):
                img_url = urljoin(GSMARENA_BASE, img_tag['src'])
                images.append(img_url)
        
        # Find other images
        photo_gallery = soup.find('div', class_='specs-photo-main')
        if photo_gallery:
            gallery_images = photo_gallery.find_all('img')
            for img in gallery_images:
                if img.get('src'):
                    img_url = urljoin(GSMARENA_BASE, img['src'])
                    if img_url not in images:
                        images.append(img_url)
        
        print(f"📸 Found {len(images)} images")
        return images
        
    except Exception as e:
        print(f"❌ Failed to fetch images: {e}")
        return []

def download_image(image_url, local_path):
    """Download image"""
    try:
        print(f"⬇️ Download image: {image_url}")
        response = requests.get(image_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Save image
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Image saved: {local_path}")
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def update_database_image_url(phone_model, image_url):
    """Update image URL in database"""
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
        
        print(f"✅ Database updated: {phone_model}")
        return True
        
    except Exception as e:
        print(f"❌ Database update failed: {e}")
        if conn:
            conn.close()
        return False

def process_samsung_phone(phone_model):
    """Process a single Samsung phone"""
    print(f"\n🚀 Start processing: Samsung {phone_model}")
    
    # Search phone
    phone_url = search_phone_on_gsmarena(phone_model)
    if not phone_url:
        print(f"❌ Phone not found: {phone_model}")
        return False
    
    # Fetch images
    images = get_phone_images(phone_url)
    if not images:
        print(f"❌ No images found: {phone_model}")
        return False
    
    # Download the first image
    image_url = images[0]
    local_filename = f"Samsung_{phone_model.replace(' ', '_')}.jpg"
    local_path = os.path.join(IMAGES_DIR, local_filename)
    
    if download_image(image_url, local_path):
        # Update database
        db_url = f"http://localhost:5198/images/phones/{local_filename}"
        if update_database_image_url(phone_model, db_url):
            print(f"🎉 Processed successfully: {phone_model}")
            return True
    
    return False

def main():
    """Main function"""
    print("🔄 Samsung images crawler started")
    print("=" * 50)
    print(f"📁 Image save directory: {IMAGES_DIR}")
    
    # Get phones to process
    phones = get_samsung_phones_without_images()
    if not phones:
        print("✅ All Samsung phones already have images!")
        return
    
    print(f"📱 Found {len(phones)} Samsung phones needing images:")
    for brand, model, image_url in phones:
        print(f"  • {model}")
    
    print("\n" + "=" * 50)
    
    # Process each phone
    success_count = 0
    total_count = len(phones)
    
    for i, (brand, model, image_url) in enumerate(phones, 1):
        print(f"\n📊 Progress: {i}/{total_count}")
        
        if process_samsung_phone(model):
            success_count += 1
        
        # Random delay to avoid being rate-limited
        if i < total_count:
            delay = random.uniform(3, 8)
            print(f"⏳ Waiting {delay:.1f} seconds...")
            time.sleep(delay)
    
    print("\n" + "=" * 50)
    print(f"🎉 Crawler finished!")
    print(f"✅ Success: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")

if __name__ == "__main__":
    main()
