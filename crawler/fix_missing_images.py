#!/usr/bin/env python3
"""
Fix missing image paths
Change non-existent local image paths to appropriate placeholders
"""

import psycopg2
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_missing_image_paths():
    """修复缺失的图片路径"""
    try:
        conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
        cur = conn.cursor()
        
        # 获取所有本地图片路径
        cur.execute('''
            SELECT "Id", "Brand", "Model", "ImageUrl" 
            FROM "Phones" 
            WHERE "ImageUrl" LIKE 'http://localhost:5198/images/%'
        ''')
        
        local_images = cur.fetchall()
        images_dir = "/Users/shenmeidun/UoW_IT/COMPX576/MobilePhone/images/phones"
        
        fixed_count = 0
        
        for phone_id, brand, model, image_url in local_images:
            # 提取文件名
            filename = image_url.split('/')[-1]
            local_path = os.path.join(images_dir, filename)
            
            # 检查文件是否存在
            if not os.path.exists(local_path):
                # 生成一个更好的placeholder
                placeholder_url = f"https://via.placeholder.com/400x600/667eea/FFFFFF?text={brand}+{model}".replace(' ', '+')
                
                # 更新数据库
                cur.execute('UPDATE "Phones" SET "ImageUrl" = %s WHERE "Id" = %s', (placeholder_url, phone_id))
                logger.info(f"Fixed missing image: {brand} {model}")
                fixed_count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"✅ Fixed {fixed_count} missing image paths")
        
    except Exception as e:
        logger.error(f"Error fixing image paths: {e}")

if __name__ == "__main__":
    fix_missing_image_paths()

