#!/usr/bin/env python3
"""
完整规格补充器 - 基于网络搜索结果补充Camera、Weight、Processor、Dimensions等缺失字段
"""

import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 完整手机规格数据库 - 基于网络搜索的权威信息
COMPLETE_PHONE_SPECS = {
    # Samsung Galaxy系列
    'Samsung Galaxy Z Flip3': {
        'camera': 'Dual',
        'weight': 183,
        'processor': 'Qualcomm Snapdragon 888 5G',
        'dimensions': '166.0 x 72.2 x 6.9 mm'
    },
    'Samsung Galaxy Z Flip4': {
        'camera': 'Dual', 
        'weight': 187,
        'processor': 'Qualcomm Snapdragon 8+ Gen 1',
        'dimensions': '165.2 x 71.9 x 6.9 mm'
    },
    'Samsung Galaxy Z Flip5': {
        'camera': 'Dual',
        'weight': 187,
        'processor': 'Qualcomm Snapdragon 8 Gen 2',
        'dimensions': '165.1 x 71.9 x 6.9 mm'
    },
    'Samsung Galaxy Z Flip6': {
        'camera': 'Dual',
        'weight': 187,
        'processor': 'Qualcomm Snapdragon 8 Gen 3',
        'dimensions': '165.1 x 71.9 x 6.9 mm'
    },
    'Samsung Galaxy Z Fold2': {
        'camera': 'Triple',
        'weight': 282,
        'processor': 'Qualcomm Snapdragon 865+',
        'dimensions': '159.2 x 128.2 x 6.9 mm'
    },
    'Samsung Galaxy Z Fold3': {
        'camera': 'Triple',
        'weight': 271,
        'processor': 'Qualcomm Snapdragon 888',
        'dimensions': '158.2 x 128.1 x 6.4 mm'
    },
    'Samsung Galaxy Z Fold4': {
        'camera': 'Triple',
        'weight': 263,
        'processor': 'Qualcomm Snapdragon 8+ Gen 1',
        'dimensions': '155.1 x 130.1 x 6.3 mm'
    },
    'Samsung Galaxy Z Fold5': {
        'camera': 'Triple',
        'weight': 253,
        'processor': 'Qualcomm Snapdragon 8 Gen 2',
        'dimensions': '154.9 x 129.9 x 6.1 mm'
    },
    'Samsung Galaxy Z Fold6': {
        'camera': 'Triple',
        'weight': 239,
        'processor': 'Qualcomm Snapdragon 8 Gen 3',
        'dimensions': '153.5 x 132.6 x 5.6 mm'
    },
    
    # OnePlus系列 - 基于官方规格
    'OnePlus 10 Pro': {
        'camera': 'Triple',
        'weight': 200.5,
        'processor': 'Qualcomm Snapdragon 8 Gen 1',
        'dimensions': '163.0 x 73.9 x 8.55 mm'
    },
    'OnePlus 10T': {
        'camera': 'Triple',
        'weight': 203.5,
        'processor': 'Qualcomm Snapdragon 8+ Gen 1',
        'dimensions': '160.7 x 75.4 x 8.75 mm'
    },
    'OnePlus 11': {
        'camera': 'Triple',
        'weight': 205,
        'processor': 'Qualcomm Snapdragon 8 Gen 2',
        'dimensions': '163.1 x 74.1 x 8.53 mm'
    },
    'OnePlus 12': {
        'camera': 'Triple',
        'weight': 220,
        'processor': 'Qualcomm Snapdragon 8 Gen 3',
        'dimensions': '164.3 x 75.8 x 9.15 mm'
    },
    'OnePlus 12R': {
        'camera': 'Triple',
        'weight': 207,
        'processor': 'Qualcomm Snapdragon 8 Gen 2',
        'dimensions': '163.3 x 75.3 x 8.8 mm'
    },
    'OnePlus 8': {
        'camera': 'Triple',
        'weight': 180,
        'processor': 'Qualcomm Snapdragon 865',
        'dimensions': '160.2 x 72.9 x 8.0 mm'
    },
    'OnePlus 8 Pro': {
        'camera': 'Quad',
        'weight': 199,
        'processor': 'Qualcomm Snapdragon 865',
        'dimensions': '165.3 x 74.4 x 8.5 mm'
    },
    'OnePlus 8T': {
        'camera': 'Quad',
        'weight': 188,
        'processor': 'Qualcomm Snapdragon 865',
        'dimensions': '160.7 x 74.1 x 8.4 mm'
    },
    'OnePlus 9': {
        'camera': 'Triple',
        'weight': 192,
        'processor': 'Qualcomm Snapdragon 888',
        'dimensions': '160.0 x 74.2 x 8.7 mm'
    },
    'OnePlus 9 Pro': {
        'camera': 'Quad',
        'weight': 197,
        'processor': 'Qualcomm Snapdragon 888',
        'dimensions': '163.2 x 73.6 x 8.7 mm'
    },
    'OnePlus 9RT': {
        'camera': 'Triple',
        'weight': 198.5,
        'processor': 'Qualcomm Snapdragon 888',
        'dimensions': '162.2 x 74.6 x 8.3 mm'
    },
    
    # Apple iPhone系列
    'Apple iPhone 12': {
        'camera': 'Dual',
        'weight': 164,
        'processor': 'Apple A14 Bionic',
        'dimensions': '146.7 x 71.5 x 7.4 mm'
    },
    'Apple iPhone 12 mini': {
        'camera': 'Dual',
        'weight': 135,
        'processor': 'Apple A14 Bionic',
        'dimensions': '131.5 x 64.2 x 7.4 mm'
    },
    'Apple iPhone 12 Pro': {
        'camera': 'Triple',
        'weight': 189,
        'processor': 'Apple A14 Bionic',
        'dimensions': '146.7 x 71.5 x 7.4 mm'
    },
    'Apple iPhone 12 Pro Max': {
        'camera': 'Triple',
        'weight': 228,
        'processor': 'Apple A14 Bionic',
        'dimensions': '160.8 x 78.1 x 7.4 mm'
    },
    'Apple iPhone 13': {
        'camera': 'Dual',
        'weight': 174,
        'processor': 'Apple A15 Bionic',
        'dimensions': '146.7 x 71.5 x 7.65 mm'
    },
    'Apple iPhone 13 mini': {
        'camera': 'Dual',
        'weight': 141,
        'processor': 'Apple A15 Bionic',
        'dimensions': '131.5 x 64.2 x 7.65 mm'
    },
    'Apple iPhone 13 Pro': {
        'camera': 'Triple',
        'weight': 203,
        'processor': 'Apple A15 Bionic',
        'dimensions': '146.7 x 71.5 x 7.65 mm'
    },
    'Apple iPhone 13 Pro Max': {
        'camera': 'Triple',
        'weight': 240,
        'processor': 'Apple A15 Bionic',
        'dimensions': '160.8 x 78.1 x 7.65 mm'
    },
    'Apple iPhone 14': {
        'camera': 'Dual',
        'weight': 172,
        'processor': 'Apple A15 Bionic',
        'dimensions': '146.7 x 71.5 x 7.80 mm'
    },
    'Apple iPhone 14 Plus': {
        'camera': 'Dual',
        'weight': 203,
        'processor': 'Apple A15 Bionic',
        'dimensions': '160.8 x 78.1 x 7.80 mm'
    },
    'Apple iPhone 14 Pro': {
        'camera': 'Triple',
        'weight': 206,
        'processor': 'Apple A16 Bionic',
        'dimensions': '147.5 x 71.5 x 7.85 mm'
    },
    'Apple iPhone 14 Pro Max': {
        'camera': 'Triple',
        'weight': 240,
        'processor': 'Apple A16 Bionic',
        'dimensions': '160.7 x 77.6 x 7.85 mm'
    },
    'Apple iPhone 15': {
        'camera': 'Dual',
        'weight': 171,
        'processor': 'Apple A16 Bionic',
        'dimensions': '147.6 x 71.6 x 7.80 mm'
    },
    'Apple iPhone 15 Plus': {
        'camera': 'Dual',
        'weight': 201,
        'processor': 'Apple A16 Bionic',
        'dimensions': '160.9 x 77.8 x 7.80 mm'
    },
    'Apple iPhone 15 Pro': {
        'camera': 'Triple',
        'weight': 187,
        'processor': 'Apple A17 Pro',
        'dimensions': '146.6 x 70.6 x 8.25 mm'
    },
    'Apple iPhone 15 Pro Max': {
        'camera': 'Triple',
        'weight': 221,
        'processor': 'Apple A17 Pro',
        'dimensions': '159.9 x 76.7 x 8.25 mm'
    },
    'Apple iPhone 16': {
        'camera': 'Dual',
        'weight': 170,
        'processor': 'Apple A18',
        'dimensions': '147.6 x 71.6 x 7.80 mm'
    },
    'Apple iPhone 16 Plus': {
        'camera': 'Dual',
        'weight': 199,
        'processor': 'Apple A18',
        'dimensions': '160.9 x 77.8 x 7.80 mm'
    },
    'Apple iPhone 16 Pro': {
        'camera': 'Triple',
        'weight': 199,
        'processor': 'Apple A18 Pro',
        'dimensions': '149.6 x 71.5 x 8.25 mm'
    },
    'Apple iPhone 16 Pro Max': {
        'camera': 'Triple',
        'weight': 227,
        'processor': 'Apple A18 Pro',
        'dimensions': '163.0 x 77.6 x 8.25 mm'
    },
    'Apple iPhone SE': {
        'camera': 'Single',
        'weight': 148,
        'processor': 'Apple A15 Bionic',
        'dimensions': '138.4 x 67.3 x 7.3 mm'
    },
    
    # Google Pixel系列
    'Google Pixel 4a': {
        'camera': 'Single',
        'weight': 143,
        'processor': 'Qualcomm Snapdragon 730G',
        'dimensions': '144.0 x 69.4 x 8.2 mm'
    },
    'Google Pixel 5': {
        'camera': 'Dual',
        'weight': 151,
        'processor': 'Qualcomm Snapdragon 765G',
        'dimensions': '144.7 x 70.4 x 8.0 mm'
    },
    'Google Pixel 5a': {
        'camera': 'Dual',
        'weight': 183,
        'processor': 'Qualcomm Snapdragon 765G',
        'dimensions': '156.2 x 73.2 x 8.8 mm'
    },
    'Google Pixel 6': {
        'camera': 'Dual',
        'weight': 207,
        'processor': 'Google Tensor',
        'dimensions': '158.6 x 74.8 x 8.9 mm'
    },
    'Google Pixel 6 Pro': {
        'camera': 'Triple',
        'weight': 210,
        'processor': 'Google Tensor',
        'dimensions': '163.9 x 75.9 x 8.9 mm'
    },
    'Google Pixel 6a': {
        'camera': 'Dual',
        'weight': 178,
        'processor': 'Google Tensor',
        'dimensions': '152.2 x 71.8 x 8.9 mm'
    },
    'Google Pixel 7': {
        'camera': 'Dual',
        'weight': 197,
        'processor': 'Google Tensor G2',
        'dimensions': '155.6 x 73.2 x 8.7 mm'
    },
    'Google Pixel 7 Pro': {
        'camera': 'Triple',
        'weight': 210,
        'processor': 'Google Tensor G2',
        'dimensions': '162.9 x 76.6 x 8.9 mm'
    },
    'Google Pixel 7a': {
        'camera': 'Dual',
        'weight': 193.5,
        'processor': 'Google Tensor G2',
        'dimensions': '152.4 x 72.9 x 9.0 mm'
    },
    'Google Pixel 8': {
        'camera': 'Dual',
        'weight': 187,
        'processor': 'Google Tensor G3',
        'dimensions': '150.5 x 70.8 x 8.9 mm'
    },
    'Google Pixel 8 Pro': {
        'camera': 'Triple',
        'weight': 213,
        'processor': 'Google Tensor G3',
        'dimensions': '162.6 x 76.5 x 8.8 mm'
    },
    'Google Pixel 8a': {
        'camera': 'Dual',
        'weight': 193,
        'processor': 'Google Tensor G3',
        'dimensions': '152.1 x 72.7 x 8.9 mm'
    },
    'Google Pixel 9': {
        'camera': 'Dual',
        'weight': 198,
        'processor': 'Google Tensor G4',
        'dimensions': '152.8 x 72.0 x 8.5 mm'
    },
    'Google Pixel 9 Pro': {
        'camera': 'Triple',
        'weight': 199,
        'processor': 'Google Tensor G4',
        'dimensions': '152.8 x 72.0 x 8.5 mm'
    },
    'Google Pixel 9 Pro XL': {
        'camera': 'Triple',
        'weight': 221,
        'processor': 'Google Tensor G4',
        'dimensions': '162.8 x 76.6 x 8.5 mm'
    }
}

def get_phones_needing_completion():
    """Get phones that need additional specs completion"""
    try:
        conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
        cur = conn.cursor()
        
        cur.execute('''
            SELECT "Id", "Brand", "Model" 
            FROM "Phones" 
            WHERE ("Camera" = 'TBD'
                   OR "Weight" IS NULL
                   OR "Processor" IS NULL 
                   OR "Processor" = ''
                   OR "Dimensions" IS NULL
                   OR "Dimensions" = '')
            ORDER BY "Brand", "Model"
        ''')
        
        phones = cur.fetchall()
        cur.close()
        conn.close()
        
        logger.info(f"Found {len(phones)} phones needing completion")
        return phones
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        return []

def update_complete_specs(phone_id, brand, model, specs):
    """Update phone with complete specs data"""
    try:
        conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
        cur = conn.cursor()
        
        update_fields = []
        values = []
        
        if specs.get('camera'):
            update_fields.append('"Camera" = %s')
            values.append(specs['camera'])
        
        if specs.get('weight') is not None:
            update_fields.append('"Weight" = %s')
            values.append(specs['weight'])
        
        if specs.get('processor'):
            update_fields.append('"Processor" = %s')
            values.append(specs['processor'])
        
        if specs.get('dimensions'):
            update_fields.append('"Dimensions" = %s')
            values.append(specs['dimensions'])
        
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

def complete_all_specs():
    """Main function to complete all missing specs"""
    phones = get_phones_needing_completion()
    
    if not phones:
        logger.info("No phones need completion")
        return
    
    success_count = 0
    no_data_count = 0
    
    for phone_id, brand, model in phones:
        full_name = f"{brand} {model}"
        logger.info(f"\n📱 Processing: {full_name}")
        
        if full_name in COMPLETE_PHONE_SPECS:
            specs = COMPLETE_PHONE_SPECS[full_name]
            if update_complete_specs(phone_id, brand, model, specs):
                success_count += 1
                logger.info(f"✅ {full_name}: Camera {specs.get('camera', 'N/A')}, Weight {specs.get('weight', 'N/A')}g, Processor {specs.get('processor', 'N/A')[:30]}...")
            else:
                logger.error(f"❌ Failed to update {full_name}")
        else:
            logger.warning(f"⚠️ No complete specs for {full_name}")
            no_data_count += 1
    
    logger.info(f"\n🎯 Complete Specs Fill completed!")
    logger.info(f"✅ Updated: {success_count}")
    logger.info(f"⚠️ No data: {no_data_count}")
    logger.info(f"📊 Total: {len(phones)}")

if __name__ == "__main__":
    complete_all_specs()

