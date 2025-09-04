#!/usr/bin/env python3
"""
修复剩余的图片路径匹配问题
处理文件名格式不匹配的情况
"""

import os
import psycopg2
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_remaining_images():
    """修复剩余的图片路径匹配问题"""
    try:
        # 连接数据库
        conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
        cur = conn.cursor()
        
        # 图片目录
        images_dir = Path("/Users/shenmeidun/UoW_IT/COMPX576/MobilePhone/backend/MobilePhoneAPI/wwwroot/images/phones")
        
        # 获取所有图片文件
        all_images = list(images_dir.glob("*.jpg"))
        image_names = [img.name for img in all_images]
        
        logger.info(f"Found {len(image_names)} image files")
        
        # 手动映射一些特殊情况
        manual_mappings = {
            # Honor
            ('Honor', '30 Pro+'): 'Honor_30_Pro__front.jpg',
            ('Honor', 'Magic3 Pro+'): 'Honor_Magic3_Pro__front.jpg',
            
            # Huawei  
            ('Huawei', 'Mate 60 Pro+'): 'Huawei_Mate_60_Pro__front.jpg',
            ('Huawei', 'P40 Pro+'): 'Huawei_P40_Pro__front.jpg',
        }
        
        fixed_count = 0
        
        # 处理手动映射
        for (brand, model), filename in manual_mappings.items():
            if filename in image_names:
                new_url = f"http://localhost:5198/images/phones/{filename}"
                cur.execute(
                    'UPDATE "Phones" SET "ImageUrl" = %s WHERE "Brand" = %s AND "Model" = %s',
                    (new_url, brand, model)
                )
                logger.info(f"✅ Fixed {brand} {model}: {filename}")
                fixed_count += 1
            else:
                logger.warning(f"⚠️ File not found: {filename} for {brand} {model}")
        
        # 检查Samsung是否有任何图片文件
        samsung_images = [img for img in image_names if 'samsung' in img.lower()]
        logger.info(f"📱 Samsung images found: {len(samsung_images)}")
        for img in samsung_images[:5]:  # 显示前5个
            logger.info(f"   - {img}")
        
        # 如果有Samsung图片，尝试匹配
        if samsung_images:
            # 获取Samsung placeholder记录
            cur.execute('''
                SELECT "Id", "Brand", "Model" 
                FROM "Phones" 
                WHERE "Brand" = 'Samsung' AND "ImageUrl" LIKE '%placeholder%'
            ''')
            samsung_phones = cur.fetchall()
            
            for phone_id, brand, model in samsung_phones:
                # 尝试多种文件名格式
                possible_names = [
                    f"Samsung_{model.replace(' ', '_')}.jpg",
                    f"Samsung_Galaxy_{model.replace('Galaxy ', '').replace(' ', '_')}.jpg",
                    f"Samsung_{model.replace(' ', '_')}_front.jpg",
                ]
                
                found_file = None
                for name in possible_names:
                    if name in image_names:
                        found_file = name
                        break
                
                if found_file:
                    new_url = f"http://localhost:5198/images/phones/{found_file}"
                    cur.execute(
                        'UPDATE "Phones" SET "ImageUrl" = %s WHERE "Id" = %s',
                        (new_url, phone_id)
                    )
                    logger.info(f"✅ Fixed Samsung {model}: {found_file}")
                    fixed_count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"🎉 Successfully fixed {fixed_count} additional images!")
        return fixed_count
        
    except Exception as e:
        logger.error(f"Error fixing remaining images: {e}")
        return 0

if __name__ == "__main__":
    fixed_count = fix_remaining_images()
    print(f"\n📊 Summary: Fixed {fixed_count} additional images")

