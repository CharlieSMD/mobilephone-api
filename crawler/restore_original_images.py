#!/usr/bin/env python3
"""
紧急恢复原始图片链接！
撤销刚才错误的placeholder替换操作
"""

import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def restore_original_images():
    """恢复原始图片链接"""
    try:
        conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
        cur = conn.cursor()
        
        # 恢复Apple iPhone的本地图片路径
        apple_phones = [
            ('iPhone 12', 'Apple_iPhone_12_front.jpg'),
            ('iPhone 12 Pro', 'Apple_iPhone_12_Pro_front.jpg'),
            ('iPhone 12 Pro Max', 'Apple_iPhone_12_Pro_Max_front.jpg'),
            ('iPhone 12 mini', 'Apple_iPhone_12_mini_front.jpg'),
            ('iPhone 13', 'Apple_iPhone_13_front.jpg'),
            ('iPhone 13 Pro', 'Apple_iPhone_13_Pro_front.jpg'),
            ('iPhone 13 Pro Max', 'Apple_iPhone_13_Pro_Max_front.jpg'),
            ('iPhone 13 mini', 'Apple_iPhone_13_mini_front.jpg'),
            ('iPhone 14', 'Apple_iPhone_14_front.jpg'),
            ('iPhone 14 Plus', 'Apple_iPhone_14_Plus_front.jpg'),
            ('iPhone 14 Pro', 'Apple_iPhone_14_Pro_front.jpg'),
            ('iPhone 14 Pro Max', 'Apple_iPhone_14_Pro_Max_front.jpg'),
            ('iPhone 15', 'Apple_iPhone_15_front.jpg'),
            ('iPhone 15 Plus', 'Apple_iPhone_15_Plus_front.jpg'),
            ('iPhone 15 Pro', 'Apple_iPhone_15_Pro_front.jpg'),
            ('iPhone 15 Pro Max', 'Apple_iPhone_15_Pro_Max_front.jpg'),
            ('iPhone 16', 'Apple_iPhone_16_front.jpg'),
            ('iPhone 16 Plus', 'Apple_iPhone_16_Plus_front.jpg'),
            ('iPhone 16 Pro', 'Apple_iPhone_16_Pro_front.jpg'),
            ('iPhone 16 Pro Max', 'Apple_iPhone_16_Pro_Max_front.jpg'),
            ('iPhone SE', 'Apple_iPhone_SE_front.jpg'),
        ]
        
        restored_count = 0
        
        for model, filename in apple_phones:
            local_url = f"http://localhost:5198/images/phones/{filename}"
            cur.execute('UPDATE "Phones" SET "ImageUrl" = %s WHERE "Brand" = %s AND "Model" = %s', 
                       (local_url, 'Apple', model))
            if cur.rowcount > 0:
                logger.info(f"✅ Restored Apple {model}")
                restored_count += 1
        
        # 恢复ASUS ROG Phone的本地图片路径
        asus_phones = [
            ('ROG Phone 3', 'ASUS_ROG_Phone_3_front.jpg'),
            ('ROG Phone 5', 'ASUS_ROG_Phone_5_front.jpg'),
            ('ROG Phone 5 Pro', 'ASUS_ROG_Phone_5_Pro_front.jpg'),
            ('ROG Phone 5 Ultimate', 'ASUS_ROG_Phone_5_Ultimate_front.jpg'),
            ('ROG Phone 6', 'ASUS_ROG_Phone_6_front.jpg'),
            ('ROG Phone 6 Pro', 'ASUS_ROG_Phone_6_Pro_front.jpg'),
            ('ROG Phone 7', 'ASUS_ROG_Phone_7_front.jpg'),
            ('ROG Phone 7 Ultimate', 'ASUS_ROG_Phone_7_Ultimate_front.jpg'),
            ('ROG Phone 8', 'ASUS_ROG_Phone_8_front.jpg'),
            ('ROG Phone 8 Pro', 'ASUS_ROG_Phone_8_Pro_front.jpg'),
        ]
        
        for model, filename in asus_phones:
            local_url = f"http://localhost:5198/images/phones/{filename}"
            cur.execute('UPDATE "Phones" SET "ImageUrl" = %s WHERE "Brand" = %s AND "Model" = %s', 
                       (local_url, 'ASUS', model))
            if cur.rowcount > 0:
                logger.info(f"✅ Restored ASUS {model}")
                restored_count += 1
        
        # 恢复Google Pixel的本地图片路径
        google_phones = [
            ('Pixel 4a', 'Google_Pixel_4a_front.jpg'),
            ('Pixel 5', 'Google_Pixel_5_front.jpg'),
            ('Pixel 5a', 'Google_Pixel_5a_front.jpg'),
            ('Pixel 6', 'Google_Pixel_6_front.jpg'),
            ('Pixel 6 Pro', 'Google_Pixel_6_Pro_front.jpg'),
            ('Pixel 7', 'Google_Pixel_7_front.jpg'),
            ('Pixel 7 Pro', 'Google_Pixel_7_Pro_front.jpg'),
            ('Pixel 7a', 'Google_Pixel_7a_front.jpg'),
            ('Pixel 8', 'Google_Pixel_8_front.jpg'),
            ('Pixel 8 Pro', 'Google_Pixel_8_Pro_front.jpg'),
            ('Pixel 9', 'Google_Pixel_9_front.jpg'),
            ('Pixel 9 Pro', 'Google_Pixel_9_Pro_front.jpg'),
            ('Pixel 9 Pro XL', 'Google_Pixel_9_Pro_XL_front.jpg'),
        ]
        
        for model, filename in google_phones:
            local_url = f"http://localhost:5198/images/phones/{filename}"
            cur.execute('UPDATE "Phones" SET "ImageUrl" = %s WHERE "Brand" = %s AND "Model" = %s', 
                       (local_url, 'Google', model))
            if cur.rowcount > 0:
                logger.info(f"✅ Restored Google {model}")
                restored_count += 1
        
        # 恢复Huawei的本地图片路径
        huawei_phones = [
            ('Mate 30 Pro', 'Huawei_Mate_30_Pro_front.jpg'),
            ('Mate 40', 'Huawei_Mate_40_front.jpg'),
            ('Mate 40 Pro', 'Huawei_Mate_40_Pro_front.jpg'),
            ('Mate 50', 'Huawei_Mate_50_front.jpg'),
            ('Mate 50 Pro', 'Huawei_Mate_50_Pro_front.jpg'),
            ('Mate 60', 'Huawei_Mate_60_front.jpg'),
            ('Mate 60 Pro', 'Huawei_Mate_60_Pro_front.jpg'),
            ('Mate 60 Pro+', 'Huawei_Mate_60_Pro+_front.jpg'),
            ('P40', 'Huawei_P40_front.jpg'),
            ('P40 Pro', 'Huawei_P40_Pro_front.jpg'),
            ('P40 Pro+', 'Huawei_P40_Pro+_front.jpg'),
            ('P50', 'Huawei_P50_front.jpg'),
            ('P50 Pro', 'Huawei_P50_Pro_front.jpg'),
            ('P60', 'Huawei_P60_front.jpg'),
            ('P60 Pro', 'Huawei_P60_Pro_front.jpg'),
            ('Pura 70', 'Huawei_Pura_70_front.jpg'),
        ]
        
        for model, filename in huawei_phones:
            local_url = f"http://localhost:5198/images/phones/{filename}"
            cur.execute('UPDATE "Phones" SET "ImageUrl" = %s WHERE "Brand" = %s AND "Model" = %s', 
                       (local_url, 'Huawei', model))
            if cur.rowcount > 0:
                logger.info(f"✅ Restored Huawei {model}")
                restored_count += 1
        
        # 恢复Honor的本地图片路径
        honor_phones = [
            ('30', 'Honor_30_front.jpg'),
            ('30 Pro', 'Honor_30_Pro_front.jpg'),
            ('30 Pro+', 'Honor_30_Pro+_front.jpg'),
            ('Magic3', 'Honor_Magic3_front.jpg'),
            ('Magic3 Pro', 'Honor_Magic3_Pro_front.jpg'),
            ('Magic3 Pro+', 'Honor_Magic3_Pro+_front.jpg'),
            ('Magic4', 'Honor_Magic4_front.jpg'),
            ('Magic4 Pro', 'Honor_Magic4_Pro_front.jpg'),
            ('Magic4 Ultimate', 'Honor_Magic4_Ultimate_front.jpg'),
            ('Magic5', 'Honor_Magic5_front.jpg'),
            ('Magic5 Pro', 'Honor_Magic5_Pro_front.jpg'),
            ('Magic6', 'Honor_Magic6_front.jpg'),
            ('Magic6 Pro', 'Honor_Magic6_Pro_front.jpg'),
        ]
        
        for model, filename in honor_phones:
            local_url = f"http://localhost:5198/images/phones/{filename}"
            cur.execute('UPDATE "Phones" SET "ImageUrl" = %s WHERE "Brand" = %s AND "Model" = %s', 
                       (local_url, 'Honor', model))
            if cur.rowcount > 0:
                logger.info(f"✅ Restored Honor {model}")
                restored_count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"🎉 Successfully restored {restored_count} original image paths!")
        
    except Exception as e:
        logger.error(f"Error restoring images: {e}")

if __name__ == "__main__":
    restore_original_images()

