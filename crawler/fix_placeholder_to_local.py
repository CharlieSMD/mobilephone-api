#!/usr/bin/env python3
"""
修复数据库中的placeholder链接
将有对应图片文件的手机从placeholder改为本地图片路径
"""

import os
import psycopg2
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_placeholder_images():
    """将有图片文件的placeholder链接改为本地路径"""
    try:
        # 连接数据库
        conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
        cur = conn.cursor()
        
        # 获取所有placeholder记录
        cur.execute('''
            SELECT "Id", "Brand", "Model", "ImageUrl" 
            FROM "Phones" 
            WHERE "ImageUrl" LIKE '%placeholder%'
        ''')
        
        placeholder_phones = cur.fetchall()
        logger.info(f"Found {len(placeholder_phones)} phones with placeholder images")
        
        # 检查图片目录
        images_dir = Path("/Users/shenmeidun/UoW_IT/COMPX576/MobilePhone/backend/MobilePhoneAPI/wwwroot/images/phones")
        
        fixed_count = 0
        
        for phone_id, brand, model, current_url in placeholder_phones:
            # 生成可能的文件名模式
            possible_names = [
                f"{brand}_{model}.jpg",
                f"{brand}_{model}_front.jpg",
                f"{brand.replace(' ', '_')}_{model.replace(' ', '_')}.jpg",
                f"{brand.replace(' ', '_')}_{model.replace(' ', '_')}_front.jpg",
            ]
            
            # 检查哪个文件存在
            found_file = None
            for name in possible_names:
                file_path = images_dir / name
                if file_path.exists():
                    found_file = name
                    break
            
            if found_file:
                # 更新数据库路径
                new_url = f"http://localhost:5198/images/phones/{found_file}"
                cur.execute(
                    'UPDATE "Phones" SET "ImageUrl" = %s WHERE "Id" = %s',
                    (new_url, phone_id)
                )
                logger.info(f"✅ Fixed {brand} {model}: {found_file}")
                fixed_count += 1
            else:
                logger.warning(f"⚠️ No image found for {brand} {model}")
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"🎉 Successfully fixed {fixed_count} placeholder images!")
        return fixed_count
        
    except Exception as e:
        logger.error(f"Error fixing placeholder images: {e}")
        return 0

if __name__ == "__main__":
    fixed_count = fix_placeholder_images()
    print(f"\n📊 Summary: Fixed {fixed_count} images from placeholder to local paths")

