#!/usr/bin/env python3
"""
手动填充手机规格数据
基于公开的官方规格信息，手动填充缺失的ScreenSize、Ram、Battery字段
"""

import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 手机规格数据库 - 基于官方公开信息
PHONE_SPECS = {
    # ASUS ROG系列
    'ASUS ROG Phone 7': {
        'screen_size': '6.78"',
        'ram': '12GB/16GB',
        'battery': '6000mAh',
        'storage': '256GB/512GB'
    },
    'ASUS ROG Phone 7 Ultimate': {
        'screen_size': '6.78"',
        'ram': '16GB',
        'battery': '6000mAh',
        'storage': '512GB'
    },
    'ASUS ROG Phone 8 Pro': {
        'screen_size': '6.78"',
        'ram': '16GB/24GB',
        'battery': '6000mAh',
        'storage': '512GB/1TB'
    },
    'ASUS ROG Phone 6': {
        'screen_size': '6.78"',
        'ram': '12GB/16GB',
        'battery': '6000mAh',
        'storage': '256GB/512GB'
    },
    'ASUS ROG Phone 5': {
        'screen_size': '6.78"',
        'ram': '8GB/12GB/16GB',
        'battery': '6000mAh',
        'storage': '128GB/256GB/512GB'
    },
    
    # Google Pixel系列
    'Google Pixel 7': {
        'screen_size': '6.3"',
        'ram': '8GB',
        'battery': '4355mAh',
        'storage': '128GB/256GB'
    },
    'Google Pixel 7 Pro': {
        'screen_size': '6.7"',
        'ram': '12GB',
        'battery': '5000mAh',
        'storage': '128GB/256GB/512GB'
    },
    'Google Pixel 7a': {
        'screen_size': '6.1"',
        'ram': '8GB',
        'battery': '4385mAh',
        'storage': '128GB'
    },
    'Google Pixel 6': {
        'screen_size': '6.4"',
        'ram': '8GB',
        'battery': '4614mAh',
        'storage': '128GB/256GB'
    },
    'Google Pixel 6 Pro': {
        'screen_size': '6.7"',
        'ram': '12GB',
        'battery': '5003mAh',
        'storage': '128GB/256GB/512GB'
    },
    'Google Pixel 6a': {
        'screen_size': '6.1"',
        'ram': '6GB',
        'battery': '4410mAh',
        'storage': '128GB'
    },
    'Google Pixel 8': {
        'screen_size': '6.2"',
        'ram': '8GB',
        'battery': '4575mAh',
        'storage': '128GB/256GB'
    },
    'Google Pixel 8 Pro': {
        'screen_size': '6.7"',
        'ram': '12GB',
        'battery': '5050mAh',
        'storage': '128GB/256GB/512GB/1TB'
    },
    'Google Pixel 8a': {
        'screen_size': '6.1"',
        'ram': '8GB',
        'battery': '4492mAh',
        'storage': '128GB/256GB'
    },
    'Google Pixel 4a': {
        'screen_size': '5.81"',
        'ram': '6GB',
        'battery': '3140mAh',
        'storage': '128GB'
    },
    
    # Honor Magic系列
    'Honor Magic4': {
        'screen_size': '6.81"',
        'ram': '8GB/12GB',
        'battery': '4800mAh',
        'storage': '256GB/512GB'
    },
    'Honor Magic4 Pro': {
        'screen_size': '6.81"',
        'ram': '8GB/12GB',
        'battery': '4600mAh',
        'storage': '256GB/512GB'
    },
    'Honor Magic4 Ultimate': {
        'screen_size': '6.81"',
        'ram': '12GB',
        'battery': '4600mAh',
        'storage': '512GB'
    },
    'Honor Magic5': {
        'screen_size': '6.73"',
        'ram': '8GB/12GB/16GB',
        'battery': '5100mAh',
        'storage': '256GB/512GB'
    },
    'Honor Magic5 Pro': {
        'screen_size': '6.81"',
        'ram': '12GB/16GB',
        'battery': '5100mAh',
        'storage': '256GB/512GB'
    },
    'Honor Magic6': {
        'screen_size': '6.78"',
        'ram': '12GB/16GB',
        'battery': '5600mAh',
        'storage': '256GB/512GB/1TB'
    },
    'Honor Magic6 Pro': {
        'screen_size': '6.8"',
        'ram': '12GB/16GB',
        'battery': '5600mAh',
        'storage': '256GB/512GB/1TB'
    },
    
    # Huawei系列
    'Huawei P60': {
        'screen_size': '6.67"',
        'ram': '8GB/12GB',
        'battery': '4815mAh',
        'storage': '128GB/256GB/512GB'
    },
    'Huawei P60 Pro': {
        'screen_size': '6.67"',
        'ram': '8GB/12GB',
        'battery': '4815mAh',
        'storage': '256GB/512GB'
    },
    'Huawei Mate 60': {
        'screen_size': '6.69"',
        'ram': '12GB',
        'battery': '4750mAh',
        'storage': '256GB/512GB'
    },
    'Huawei Mate 60 Pro': {
        'screen_size': '6.82"',
        'ram': '12GB',
        'battery': '5000mAh',
        'storage': '256GB/512GB/1TB'
    },
    'Huawei P50': {
        'screen_size': '6.5"',
        'ram': '8GB',
        'battery': '4100mAh',
        'storage': '128GB/256GB'
    },
    'Huawei P50 Pro': {
        'screen_size': '6.6"',
        'ram': '8GB/12GB',
        'battery': '4360mAh',
        'storage': '256GB/512GB'
    },
    
    # OPPO Find系列
    'OPPO Find X5': {
        'screen_size': '6.55"',
        'ram': '8GB/12GB',
        'battery': '4800mAh',
        'storage': '256GB'
    },
    'OPPO Find X5 Pro': {
        'screen_size': '6.7"',
        'ram': '8GB/12GB',
        'battery': '5000mAh',
        'storage': '256GB/512GB'
    },
    'OPPO Find X6': {
        'screen_size': '6.74"',
        'ram': '12GB/16GB',
        'battery': '4800mAh',
        'storage': '256GB/512GB'
    },
    'OPPO Find X6 Pro': {
        'screen_size': '6.82"',
        'ram': '12GB/16GB',
        'battery': '5000mAh',
        'storage': '256GB/512GB'
    },
    'OPPO Find X7': {
        'screen_size': '6.78"',
        'ram': '12GB/16GB',
        'battery': '5000mAh',
        'storage': '256GB/512GB'
    },
    
    # OnePlus系列
    'OnePlus 10 Pro': {
        'screen_size': '6.7"',
        'ram': '8GB/12GB',
        'battery': '5000mAh',
        'storage': '128GB/256GB/512GB'
    },
    'OnePlus 10T': {
        'screen_size': '6.7"',
        'ram': '8GB/12GB/16GB',
        'battery': '4800mAh',
        'storage': '128GB/256GB'
    },
    'OnePlus 11': {
        'screen_size': '6.7"',
        'ram': '8GB/12GB/16GB',
        'battery': '5000mAh',
        'storage': '128GB/256GB/512GB'
    },
    'OnePlus 12': {
        'screen_size': '6.82"',
        'ram': '12GB/16GB/24GB',
        'battery': '5400mAh',
        'storage': '256GB/512GB/1TB'
    },
    'OnePlus 12R': {
        'screen_size': '6.78"',
        'ram': '8GB/16GB',
        'battery': '5500mAh',
        'storage': '128GB/256GB'
    },
    'OnePlus 8': {
        'screen_size': '6.55"',
        'ram': '8GB/12GB',
        'battery': '4300mAh',
        'storage': '128GB/256GB'
    },
    'OnePlus 8 Pro': {
        'screen_size': '6.78"',
        'ram': '8GB/12GB',
        'battery': '4510mAh',
        'storage': '128GB/256GB'
    },
    'OnePlus 8T': {
        'screen_size': '6.55"',
        'ram': '8GB/12GB',
        'battery': '4500mAh',
        'storage': '128GB/256GB'
    },
    'OnePlus 9': {
        'screen_size': '6.55"',
        'ram': '8GB/12GB',
        'battery': '4500mAh',
        'storage': '128GB/256GB'
    },
    'OnePlus 9 Pro': {
        'screen_size': '6.7"',
        'ram': '8GB/12GB',
        'battery': '4500mAh',
        'storage': '128GB/256GB'
    },
    'OnePlus 9RT': {
        'screen_size': '6.62"',
        'ram': '8GB/12GB',
        'battery': '4500mAh',
        'storage': '128GB/256GB'
    },
    
    # 基于网络搜索添加的额外规格数据
    # iPhone SE
    'Apple iPhone SE': {
        'screen_size': '4.7"',
        'ram': '4GB',
        'battery': '2018mAh',
        'storage': '64GB/128GB/256GB'
    },
    
    # Google Pixel 5系列
    'Google Pixel 5': {
        'screen_size': '6.0"',
        'ram': '8GB',
        'battery': '4080mAh',
        'storage': '128GB'
    },
    'Google Pixel 5a': {
        'screen_size': '6.34"',
        'ram': '6GB',
        'battery': '4680mAh',
        'storage': '128GB'
    },
    'Google Pixel 6a': {
        'screen_size': '6.1"',
        'ram': '6GB',
        'battery': '4410mAh',
        'storage': '128GB'
    },
    'Google Pixel 8a': {
        'screen_size': '6.1"',
        'ram': '8GB',
        'battery': '4492mAh',
        'storage': '128GB/256GB'
    },
    'Google Pixel 9': {
        'screen_size': '6.3"',
        'ram': '12GB',
        'battery': '4700mAh',
        'storage': '128GB/256GB'
    },
    'Google Pixel 9 Pro': {
        'screen_size': '6.3"',
        'ram': '16GB',
        'battery': '4700mAh',
        'storage': '128GB/256GB/512GB'
    },
    'Google Pixel 9 Pro XL': {
        'screen_size': '6.8"',
        'ram': '16GB',
        'battery': '5060mAh',
        'storage': '128GB/256GB/512GB/1TB'
    },
    
    # Honor 30系列 - 基于中关村在线数据
    'Honor 30': {
        'screen_size': '6.53"',
        'ram': '6GB/8GB',
        'battery': '4000mAh',
        'storage': '128GB/256GB'
    },
    'Honor 30 Pro': {
        'screen_size': '6.57"',
        'ram': '8GB/12GB',
        'battery': '4000mAh',
        'storage': '128GB/256GB'
    },
    'Honor 30 Pro+': {
        'screen_size': '6.57"',
        'ram': '8GB/12GB',
        'battery': '4000mAh',
        'storage': '256GB'
    },
    
    # Honor Magic3系列
    'Honor Magic3': {
        'screen_size': '6.76"',
        'ram': '8GB/12GB',
        'battery': '4600mAh',
        'storage': '128GB/256GB'
    },
    'Honor Magic3 Pro': {
        'screen_size': '6.76"',
        'ram': '8GB/12GB',
        'battery': '4600mAh',
        'storage': '256GB/512GB'
    },
    'Honor Magic3 Pro+': {
        'screen_size': '6.76"',
        'ram': '12GB',
        'battery': '4600mAh',
        'storage': '256GB/512GB'
    },
    
    # ASUS ROG系列
    'ASUS ROG Phone 6': {
        'screen_size': '6.78"',
        'ram': '12GB/16GB',
        'battery': '6000mAh',
        'storage': '256GB/512GB'
    },
    'ASUS ROG Phone 6 Pro': {
        'screen_size': '6.78"',
        'ram': '18GB',
        'battery': '6000mAh',
        'storage': '512GB'
    },
    'ASUS ROG Phone 8': {
        'screen_size': '6.78"',
        'ram': '12GB/16GB',
        'battery': '6000mAh',
        'storage': '256GB/512GB'
    },
    
    # Huawei老款系列
    'Huawei Mate 30 Pro': {
        'screen_size': '6.53"',
        'ram': '8GB',
        'battery': '4500mAh',
        'storage': '256GB/512GB'
    },
    'Huawei Mate 40': {
        'screen_size': '6.5"',
        'ram': '8GB',
        'battery': '4200mAh',
        'storage': '128GB/256GB'
    },
    'Huawei Mate 40 Pro': {
        'screen_size': '6.76"',
        'ram': '8GB',
        'battery': '4400mAh',
        'storage': '256GB/512GB'
    },
    'Huawei Mate 50': {
        'screen_size': '6.7"',
        'ram': '8GB',
        'battery': '4460mAh',
        'storage': '128GB/256GB/512GB'
    },
    'Huawei Mate 50 Pro': {
        'screen_size': '6.74"',
        'ram': '8GB',
        'battery': '4700mAh',
        'storage': '256GB/512GB'
    },
    'Huawei Mate 60 Pro+': {
        'screen_size': '6.82"',
        'ram': '16GB',
        'battery': '5000mAh',
        'storage': '256GB/512GB/1TB'
    },
    'Huawei P40': {
        'screen_size': '6.1"',
        'ram': '8GB',
        'battery': '3800mAh',
        'storage': '128GB/256GB'
    },
    'Huawei P40 Pro': {
        'screen_size': '6.58"',
        'ram': '8GB',
        'battery': '4200mAh',
        'storage': '256GB/512GB'
    },
    'Huawei P40 Pro+': {
        'screen_size': '6.58"',
        'ram': '8GB',
        'battery': '4200mAh',
        'storage': '512GB'
    },
    'Huawei Pura 70': {
        'screen_size': '6.6"',
        'ram': '12GB',
        'battery': '4900mAh',
        'storage': '256GB/512GB'
    },
    
    # OPPO Find X2系列
    'OPPO Find X2': {
        'screen_size': '6.7"',
        'ram': '8GB/12GB',
        'battery': '4200mAh',
        'storage': '128GB/256GB'
    },
    'OPPO Find X2 Pro': {
        'screen_size': '6.7"',
        'ram': '12GB',
        'battery': '4260mAh',
        'storage': '256GB/512GB'
    },
    'OPPO Find X3': {
        'screen_size': '6.7"',
        'ram': '8GB/12GB',
        'battery': '4300mAh',
        'storage': '128GB/256GB'
    },
    'OPPO Find X3 Pro': {
        'screen_size': '6.7"',
        'ram': '8GB/12GB',
        'battery': '4500mAh',
        'storage': '256GB/512GB'
    },
    'OPPO Find X7 Pro': {
        'screen_size': '6.82"',
        'ram': '12GB/16GB',
        'battery': '5400mAh',
        'storage': '256GB/512GB'
    }
}

def get_phones_to_update():
    """Get phones that need specs update"""
    try:
        conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
        cur = conn.cursor()
        
        cur.execute('''
            SELECT "Id", "Brand", "Model" 
            FROM "Phones" 
            WHERE ("ScreenSize" = 'TBD' 
                   OR "Ram" IN ('TBD', 'Card slot', 'No')
                   OR "Battery" IN ('TBD', 'Type mAh') 
                   OR "Battery" LIKE '%rating%')
            ORDER BY "Brand", "Model"
        ''')
        
        phones = cur.fetchall()
        cur.close()
        conn.close()
        
        logger.info(f"Found {len(phones)} phones needing specs update")
        return phones
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        return []

def update_phone_specs(phone_id, brand, model, specs):
    """Update phone with specs data"""
    try:
        conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
        cur = conn.cursor()
        
        update_fields = []
        values = []
        
        if specs.get('screen_size'):
            update_fields.append('"ScreenSize" = %s')
            values.append(specs['screen_size'])
        
        if specs.get('ram'):
            update_fields.append('"Ram" = %s')
            values.append(specs['ram'])
        
        if specs.get('battery'):
            update_fields.append('"Battery" = %s')
            values.append(specs['battery'])
        
        if specs.get('storage'):
            update_fields.append('"Storage" = %s')
            values.append(specs['storage'])
        
        if update_fields:
            query = f'UPDATE "Phones" SET {", ".join(update_fields)} WHERE "Id" = %s'
            values.append(phone_id)
            
            cur.execute(query, values)
            conn.commit()
            
            logger.info(f"✅ Updated {brand} {model}: {len(update_fields)} fields")
            return True
        
        cur.close()
        conn.close()
        return False
        
    except Exception as e:
        logger.error(f"Database update error for {brand} {model}: {e}")
        return False

def fill_manual_specs():
    """Main function to fill specs manually"""
    phones = get_phones_to_update()
    
    if not phones:
        logger.info("No phones need specs update")
        return
    
    success_count = 0
    no_data_count = 0
    
    for phone_id, brand, model in phones:
        full_name = f"{brand} {model}"
        logger.info(f"\n📱 Processing: {full_name}")
        
        if full_name in PHONE_SPECS:
            specs = PHONE_SPECS[full_name]
            if update_phone_specs(phone_id, brand, model, specs):
                success_count += 1
                logger.info(f"✅ {full_name}: Screen {specs.get('screen_size', 'N/A')}, RAM {specs.get('ram', 'N/A')}, Battery {specs.get('battery', 'N/A')}")
            else:
                logger.error(f"❌ Failed to update {full_name}")
        else:
            logger.warning(f"⚠️ No specs data for {full_name}")
            no_data_count += 1
    
    logger.info(f"\n🎯 Manual Specs Fill completed!")
    logger.info(f"✅ Updated: {success_count}")
    logger.info(f"⚠️ No data: {no_data_count}")
    logger.info(f"📊 Total: {len(phones)}")

if __name__ == "__main__":
    fill_manual_specs()
