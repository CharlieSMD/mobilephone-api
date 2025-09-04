#!/usr/bin/env python3
"""
手动修复iPhone系列的ScreenSize、RAM、Battery数据
使用官方iPhone规格数据，不依赖GSMArena抓取
"""

import psycopg2
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fix_iphone_manual.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# iPhone官方规格数据
IPHONE_SPECS = {
    'iPhone 12 mini': {
        'screen_size': '5.4"',
        'ram': '4GB',
        'battery': '2227mAh',
        'storage': '64GB, 128GB, 256GB'
    },
    'iPhone 12': {
        'screen_size': '6.1"',
        'ram': '4GB', 
        'battery': '2815mAh',
        'storage': '64GB, 128GB, 256GB'
    },
    'iPhone 12 Pro': {
        'screen_size': '6.1"',
        'ram': '6GB',
        'battery': '2815mAh',
        'storage': '128GB, 256GB, 512GB'
    },
    'iPhone 12 Pro Max': {
        'screen_size': '6.7"',
        'ram': '6GB',
        'battery': '3687mAh',
        'storage': '128GB, 256GB, 512GB'
    },
    'iPhone 13 mini': {
        'screen_size': '5.4"',
        'ram': '4GB',
        'battery': '2406mAh',
        'storage': '128GB, 256GB, 512GB'
    },
    'iPhone 13': {
        'screen_size': '6.1"',
        'ram': '4GB',
        'battery': '3240mAh',
        'storage': '128GB, 256GB, 512GB'
    },
    'iPhone 13 Pro': {
        'screen_size': '6.1"',
        'ram': '6GB',
        'battery': '3095mAh',
        'storage': '128GB, 256GB, 512GB, 1TB'
    },
    'iPhone 13 Pro Max': {
        'screen_size': '6.7"',
        'ram': '6GB',
        'battery': '4352mAh',
        'storage': '128GB, 256GB, 512GB, 1TB'
    },
    'iPhone 14': {
        'screen_size': '6.1"',
        'ram': '6GB',
        'battery': '3279mAh',
        'storage': '128GB, 256GB, 512GB'
    },
    'iPhone 14 Plus': {
        'screen_size': '6.7"',
        'ram': '6GB',
        'battery': '4325mAh',
        'storage': '128GB, 256GB, 512GB'
    },
    'iPhone 14 Pro': {
        'screen_size': '6.1"',
        'ram': '6GB',
        'battery': '3200mAh',
        'storage': '128GB, 256GB, 512GB, 1TB'
    },
    'iPhone 14 Pro Max': {
        'screen_size': '6.7"',
        'ram': '6GB',
        'battery': '4323mAh',
        'storage': '128GB, 256GB, 512GB, 1TB'
    },
    'iPhone 15': {
        'screen_size': '6.1"',
        'ram': '6GB',
        'battery': '3349mAh',
        'storage': '128GB, 256GB, 512GB'
    },
    'iPhone 15 Plus': {
        'screen_size': '6.7"',
        'ram': '6GB',
        'battery': '4383mAh',
        'storage': '128GB, 256GB, 512GB'
    },
    'iPhone 15 Pro': {
        'screen_size': '6.1"',
        'ram': '8GB',
        'battery': '3274mAh',
        'storage': '128GB, 256GB, 512GB, 1TB'
    },
    'iPhone 15 Pro Max': {
        'screen_size': '6.7"',
        'ram': '8GB',
        'battery': '4441mAh',
        'storage': '256GB, 512GB, 1TB'
    },
    'iPhone 16': {
        'screen_size': '6.1"',
        'ram': '8GB',
        'battery': '3561mAh',
        'storage': '128GB, 256GB, 512GB'
    },
    'iPhone 16 Plus': {
        'screen_size': '6.7"',
        'ram': '8GB',
        'battery': '4674mAh',
        'storage': '128GB, 256GB, 512GB'
    },
    'iPhone 16 Pro': {
        'screen_size': '6.3"',
        'ram': '8GB',
        'battery': '3582mAh',
        'storage': '128GB, 256GB, 512GB, 1TB'
    },
    'iPhone 16 Pro Max': {
        'screen_size': '6.9"',
        'ram': '8GB',
        'battery': '4685mAh',
        'storage': '256GB, 512GB, 1TB'
    }
}

def get_iphones_to_fix():
    """Get iPhone models that need fixing"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='mobilephone_db',
            user='postgres'
        )
        cur = conn.cursor()
        
        cur.execute('''
            SELECT "Id", "Model" 
            FROM "Phones" 
            WHERE "Brand" = 'Apple'
            AND ("ScreenSize" = 'TBD' OR "Ram" = 'Card slot')
            ORDER BY "Model"
        ''')
        
        phones = cur.fetchall()
        cur.close()
        conn.close()
        
        logger.info(f"Found {len(phones)} iPhones to fix")
        return phones
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        return []

def update_iphone_specs(phone_id, model, specs):
    """Update iPhone with correct specs"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='mobilephone_db',
            user='postgres'
        )
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE "Phones" 
            SET "ScreenSize" = %s, 
                "Ram" = %s, 
                "Battery" = %s, 
                "Storage" = %s
            WHERE "Id" = %s
        ''', (
            specs['screen_size'],
            specs['ram'],
            specs['battery'],
            specs['storage'],
            phone_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"✅ Updated {model}: {specs['screen_size']}, {specs['ram']}, {specs['battery']}")
        return True
        
    except Exception as e:
        logger.error(f"Database update error for {model}: {e}")
        return False

def fix_iphone_specs_manually():
    """Main function to fix iPhone specs manually"""
    phones = get_iphones_to_fix()
    
    if not phones:
        logger.info("No iPhones to fix found")
        return
    
    success_count = 0
    fail_count = 0
    
    for phone_id, model in phones:
        logger.info(f"\n📱 Processing: {model}")
        
        if model in IPHONE_SPECS:
            specs = IPHONE_SPECS[model]
            if update_iphone_specs(phone_id, model, specs):
                success_count += 1
            else:
                fail_count += 1
        else:
            logger.warning(f"❌ No specs data found for {model}")
            fail_count += 1
    
    logger.info(f"\n🎯 iPhone Manual Fix completed!")
    logger.info(f"✅ Success: {success_count}")
    logger.info(f"❌ Failed: {fail_count}")
    logger.info(f"📊 Total: {len(phones)}")

if __name__ == "__main__":
    fix_iphone_specs_manually()

