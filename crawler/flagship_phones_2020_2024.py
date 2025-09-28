#!/usr/bin/env python3
"""
Flagship Phone Database Rebuild for 2020-2024
Includes flagship models from Apple, Samsung, Google, Sony, Xiaomi, OPPO, vivo, OnePlus, ASUS, Huawei, Honor
"""

import psycopg2
import json

def get_flagship_phones_2020_2024():
    """Returns flagship phone list for 2020-2024 with standardized brand and model names"""
    return [
        # ===== Apple iPhone (2020-2024) =====
        # 2024
        {"brand": "Apple", "model": "iPhone 16 Pro Max", "year": 2024},
        {"brand": "Apple", "model": "iPhone 16 Pro", "year": 2024},
        {"brand": "Apple", "model": "iPhone 16 Plus", "year": 2024},
        {"brand": "Apple", "model": "iPhone 16", "year": 2024},
        
        # 2023
        {"brand": "Apple", "model": "iPhone 15 Pro Max", "year": 2023},
        {"brand": "Apple", "model": "iPhone 15 Pro", "year": 2023},
        {"brand": "Apple", "model": "iPhone 15 Plus", "year": 2023},
        {"brand": "Apple", "model": "iPhone 15", "year": 2023},
        
        # 2022
        {"brand": "Apple", "model": "iPhone 14 Pro Max", "year": 2022},
        {"brand": "Apple", "model": "iPhone 14 Pro", "year": 2022},
        {"brand": "Apple", "model": "iPhone 14 Plus", "year": 2022},
        {"brand": "Apple", "model": "iPhone 14", "year": 2022},
        
        # 2021
        {"brand": "Apple", "model": "iPhone 13 Pro Max", "year": 2021},
        {"brand": "Apple", "model": "iPhone 13 Pro", "year": 2021},
        {"brand": "Apple", "model": "iPhone 13", "year": 2021},
        {"brand": "Apple", "model": "iPhone 13 mini", "year": 2021},
        
        # 2020
        {"brand": "Apple", "model": "iPhone 12 Pro Max", "year": 2020},
        {"brand": "Apple", "model": "iPhone 12 Pro", "year": 2020},
        {"brand": "Apple", "model": "iPhone 12", "year": 2020},
        {"brand": "Apple", "model": "iPhone 12 mini", "year": 2020},
        {"brand": "Apple", "model": "iPhone SE", "year": 2020},

        # ===== Samsung Galaxy (2020-2024) =====
        # 2024
        {"brand": "Samsung", "model": "Galaxy S24 Ultra", "year": 2024},
        {"brand": "Samsung", "model": "Galaxy S24+", "year": 2024},
        {"brand": "Samsung", "model": "Galaxy S24", "year": 2024},
        {"brand": "Samsung", "model": "Galaxy Z Fold6", "year": 2024},
        {"brand": "Samsung", "model": "Galaxy Z Flip6", "year": 2024},
        
        # 2023
        {"brand": "Samsung", "model": "Galaxy S23 Ultra", "year": 2023},
        {"brand": "Samsung", "model": "Galaxy S23+", "year": 2023},
        {"brand": "Samsung", "model": "Galaxy S23", "year": 2023},
        {"brand": "Samsung", "model": "Galaxy Z Fold5", "year": 2023},
        {"brand": "Samsung", "model": "Galaxy Z Flip5", "year": 2023},
        
        # 2022
        {"brand": "Samsung", "model": "Galaxy S22 Ultra", "year": 2022},
        {"brand": "Samsung", "model": "Galaxy S22+", "year": 2022},
        {"brand": "Samsung", "model": "Galaxy S22", "year": 2022},
        {"brand": "Samsung", "model": "Galaxy Z Fold4", "year": 2022},
        {"brand": "Samsung", "model": "Galaxy Z Flip4", "year": 2022},
        
        # 2021
        {"brand": "Samsung", "model": "Galaxy S21 Ultra", "year": 2021},
        {"brand": "Samsung", "model": "Galaxy S21+", "year": 2021},
        {"brand": "Samsung", "model": "Galaxy S21", "year": 2021},
        {"brand": "Samsung", "model": "Galaxy Z Fold3", "year": 2021},
        {"brand": "Samsung", "model": "Galaxy Z Flip3", "year": 2021},
        {"brand": "Samsung", "model": "Galaxy Note20 Ultra", "year": 2021},
        {"brand": "Samsung", "model": "Galaxy Note20", "year": 2021},
        
        # 2020
        {"brand": "Samsung", "model": "Galaxy S20 Ultra", "year": 2020},
        {"brand": "Samsung", "model": "Galaxy S20+", "year": 2020},
        {"brand": "Samsung", "model": "Galaxy S20", "year": 2020},
        {"brand": "Samsung", "model": "Galaxy Z Fold2", "year": 2020},
        {"brand": "Samsung", "model": "Galaxy Z Flip", "year": 2020},

        # ===== Google Pixel (2020-2024) =====
        # 2024
        {"brand": "Google", "model": "Pixel 9 Pro XL", "year": 2024},
        {"brand": "Google", "model": "Pixel 9 Pro", "year": 2024},
        {"brand": "Google", "model": "Pixel 9", "year": 2024},
        
        # 2023
        {"brand": "Google", "model": "Pixel 8 Pro", "year": 2023},
        {"brand": "Google", "model": "Pixel 8", "year": 2023},
        {"brand": "Google", "model": "Pixel 7a", "year": 2023},
        
        # 2022
        {"brand": "Google", "model": "Pixel 7 Pro", "year": 2022},
        {"brand": "Google", "model": "Pixel 7", "year": 2022},
        
        # 2021
        {"brand": "Google", "model": "Pixel 6 Pro", "year": 2021},
        {"brand": "Google", "model": "Pixel 6", "year": 2021},
        {"brand": "Google", "model": "Pixel 5a", "year": 2021},
        
        # 2020
        {"brand": "Google", "model": "Pixel 5", "year": 2020},
        {"brand": "Google", "model": "Pixel 4a", "year": 2020},

        # ===== Sony Xperia (2020-2024) =====
        # 2024
        {"brand": "Sony", "model": "Xperia 1 VI", "year": 2024},
        {"brand": "Sony", "model": "Xperia 5 V", "year": 2024},
        {"brand": "Sony", "model": "Xperia 10 VI", "year": 2024},
        
        # 2023
        {"brand": "Sony", "model": "Xperia 1 V", "year": 2023},
        {"brand": "Sony", "model": "Xperia 10 V", "year": 2023},
        
        # 2022
        {"brand": "Sony", "model": "Xperia 1 IV", "year": 2022},
        {"brand": "Sony", "model": "Xperia 5 IV", "year": 2022},
        {"brand": "Sony", "model": "Xperia 10 IV", "year": 2022},
        
        # 2021
        {"brand": "Sony", "model": "Xperia 1 III", "year": 2021},
        {"brand": "Sony", "model": "Xperia 5 III", "year": 2021},
        {"brand": "Sony", "model": "Xperia 10 III", "year": 2021},
        
        # 2020
        {"brand": "Sony", "model": "Xperia 1 II", "year": 2020},
        {"brand": "Sony", "model": "Xperia 5 II", "year": 2020},
        {"brand": "Sony", "model": "Xperia 10 II", "year": 2020},

        # ===== Xiaomi Flagship Series (2020-2024) =====
        # 2024
        {"brand": "Xiaomi", "model": "Xiaomi 14 Ultra", "year": 2024},
        {"brand": "Xiaomi", "model": "Xiaomi 14 Pro", "year": 2024},
        {"brand": "Xiaomi", "model": "Xiaomi 14", "year": 2024},
        
        # 2023
        {"brand": "Xiaomi", "model": "Xiaomi 13 Ultra", "year": 2023},
        {"brand": "Xiaomi", "model": "Xiaomi 13 Pro", "year": 2023},
        {"brand": "Xiaomi", "model": "Xiaomi 13", "year": 2023},
        
        # 2022
        {"brand": "Xiaomi", "model": "Xiaomi 12S Ultra", "year": 2022},
        {"brand": "Xiaomi", "model": "Xiaomi 12 Pro", "year": 2022},
        {"brand": "Xiaomi", "model": "Xiaomi 12", "year": 2022},
        
        # 2021
        {"brand": "Xiaomi", "model": "Mi 11 Ultra", "year": 2021},
        {"brand": "Xiaomi", "model": "Mi 11 Pro", "year": 2021},
        {"brand": "Xiaomi", "model": "Mi 11", "year": 2021},
        
        # 2020
        {"brand": "Xiaomi", "model": "Mi 10 Ultra", "year": 2020},
        {"brand": "Xiaomi", "model": "Mi 10 Pro", "year": 2020},
        {"brand": "Xiaomi", "model": "Mi 10", "year": 2020},

        # ===== OPPO Find X Flagship Series (2020-2024) =====
        # 2024
        {"brand": "OPPO", "model": "Find X7 Ultra", "year": 2024},
        {"brand": "OPPO", "model": "Find X7 Pro", "year": 2024},
        {"brand": "OPPO", "model": "Find X7", "year": 2024},
        
        # 2023
        {"brand": "OPPO", "model": "Find X6 Pro", "year": 2023},
        {"brand": "OPPO", "model": "Find X6", "year": 2023},
        
        # 2022
        {"brand": "OPPO", "model": "Find X5 Pro", "year": 2022},
        {"brand": "OPPO", "model": "Find X5", "year": 2022},
        
        # 2021
        {"brand": "OPPO", "model": "Find X3 Pro", "year": 2021},
        {"brand": "OPPO", "model": "Find X3", "year": 2021},
        
        # 2020
        {"brand": "OPPO", "model": "Find X2 Pro", "year": 2020},
        {"brand": "OPPO", "model": "Find X2", "year": 2020},

        # ===== vivo X Flagship Series (2020-2024) =====
        # 2024
        {"brand": "vivo", "model": "X100 Ultra", "year": 2024},
        {"brand": "vivo", "model": "X100 Pro", "year": 2024},
        {"brand": "vivo", "model": "X100", "year": 2024},
        
        # 2023
        {"brand": "vivo", "model": "X90 Pro+", "year": 2023},
        {"brand": "vivo", "model": "X90 Pro", "year": 2023},
        {"brand": "vivo", "model": "X90", "year": 2023},
        
        # 2022
        {"brand": "vivo", "model": "X80 Pro", "year": 2022},
        {"brand": "vivo", "model": "X80", "year": 2022},
        
        # 2021
        {"brand": "vivo", "model": "X70 Pro+", "year": 2021},
        {"brand": "vivo", "model": "X70 Pro", "year": 2021},
        {"brand": "vivo", "model": "X70", "year": 2021},
        
        # 2020
        {"brand": "vivo", "model": "X60 Pro+", "year": 2020},
        {"brand": "vivo", "model": "X60 Pro", "year": 2020},
        {"brand": "vivo", "model": "X60", "year": 2020},

        # ===== OnePlus Flagship Series (2020-2024) =====
        # 2024
        {"brand": "OnePlus", "model": "12", "year": 2024},
        {"brand": "OnePlus", "model": "12R", "year": 2024},
        
        # 2023
        {"brand": "OnePlus", "model": "11", "year": 2023},
        
        # 2022
        {"brand": "OnePlus", "model": "10 Pro", "year": 2022},
        {"brand": "OnePlus", "model": "10T", "year": 2022},
        
        # 2021
        {"brand": "OnePlus", "model": "9 Pro", "year": 2021},
        {"brand": "OnePlus", "model": "9", "year": 2021},
        {"brand": "OnePlus", "model": "9RT", "year": 2021},
        
        # 2020
        {"brand": "OnePlus", "model": "8 Pro", "year": 2020},
        {"brand": "OnePlus", "model": "8", "year": 2020},
        {"brand": "OnePlus", "model": "8T", "year": 2020},

        # ===== ASUS ROG Phone Gaming Flagship (2020-2024) =====
        # 2024
        {"brand": "ASUS", "model": "ROG Phone 8 Pro", "year": 2024},
        {"brand": "ASUS", "model": "ROG Phone 8", "year": 2024},
        
        # 2023
        {"brand": "ASUS", "model": "ROG Phone 7 Ultimate", "year": 2023},
        {"brand": "ASUS", "model": "ROG Phone 7", "year": 2023},
        
        # 2022
        {"brand": "ASUS", "model": "ROG Phone 6 Pro", "year": 2022},
        {"brand": "ASUS", "model": "ROG Phone 6", "year": 2022},
        
        # 2021
        {"brand": "ASUS", "model": "ROG Phone 5 Ultimate", "year": 2021},
        {"brand": "ASUS", "model": "ROG Phone 5 Pro", "year": 2021},
        {"brand": "ASUS", "model": "ROG Phone 5", "year": 2021},
        
        # 2020
        {"brand": "ASUS", "model": "ROG Phone 3", "year": 2020},

        # ===== Huawei Mate/P Flagship Series (2020-2024) =====
        # 2024
        {"brand": "Huawei", "model": "Pura 70 Ultra", "year": 2024},
        {"brand": "Huawei", "model": "Pura 70 Pro", "year": 2024},
        {"brand": "Huawei", "model": "Pura 70", "year": 2024},
        
        # 2023
        {"brand": "Huawei", "model": "Mate 60 Pro+", "year": 2023},
        {"brand": "Huawei", "model": "Mate 60 Pro", "year": 2023},
        {"brand": "Huawei", "model": "Mate 60", "year": 2023},
        {"brand": "Huawei", "model": "P60 Pro", "year": 2023},
        {"brand": "Huawei", "model": "P60", "year": 2023},
        
        # 2022
        {"brand": "Huawei", "model": "Mate 50 Pro", "year": 2022},
        {"brand": "Huawei", "model": "Mate 50", "year": 2022},
        
        # 2021
        {"brand": "Huawei", "model": "P50 Pro", "year": 2021},
        {"brand": "Huawei", "model": "P50", "year": 2021},
        {"brand": "Huawei", "model": "Mate 40 Pro", "year": 2021},
        {"brand": "Huawei", "model": "Mate 40", "year": 2021},
        
        # 2020
        {"brand": "Huawei", "model": "P40 Pro+", "year": 2020},
        {"brand": "Huawei", "model": "P40 Pro", "year": 2020},
        {"brand": "Huawei", "model": "P40", "year": 2020},
        {"brand": "Huawei", "model": "Mate 30 Pro", "year": 2020},

        # ===== Honor Magic Flagship Series (2020-2024) =====
        # 2024
        {"brand": "Honor", "model": "Magic6 Pro", "year": 2024},
        {"brand": "Honor", "model": "Magic6", "year": 2024},
        
        # 2023
        {"brand": "Honor", "model": "Magic5 Pro", "year": 2023},
        {"brand": "Honor", "model": "Magic5", "year": 2023},
        
        # 2022
        {"brand": "Honor", "model": "Magic4 Ultimate", "year": 2022},
        {"brand": "Honor", "model": "Magic4 Pro", "year": 2022},
        {"brand": "Honor", "model": "Magic4", "year": 2022},
        
        # 2021
        {"brand": "Honor", "model": "Magic3 Pro+", "year": 2021},
        {"brand": "Honor", "model": "Magic3 Pro", "year": 2021},
        {"brand": "Honor", "model": "Magic3", "year": 2021},
        
        # 2020
        {"brand": "Honor", "model": "30 Pro+", "year": 2020},
        {"brand": "Honor", "model": "30 Pro", "year": 2020},
        {"brand": "Honor", "model": "30", "year": 2020},
    ]

def rebuild_flagship_database(connection_string: str):
    """Rebuild database with flagship phones from the past 5 years"""
    phones = get_flagship_phones_2020_2024()
    
    print(f"🎯 Rebuilding database with 2020-2024 flagship phones")
    print(f"📱 Total models: {len(phones)}")
    
    # Calculate brand and year distribution
    brands = {}
    years = {}
    
    for phone in phones:
        # Brand statistics
        brand = phone['brand']
        brands[brand] = brands.get(brand, 0) + 1
        
        # Year statistics
        year = phone['year']
        years[year] = years.get(year, 0) + 1
    
    print(f"\n📊 Brand distribution:")
    for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True):
        print(f"   {brand}: {count} models")
    
    print(f"\n📅 Year distribution:")
    for year in sorted(years.keys(), reverse=True):
        print(f"   {year}: {years[year]} models")
    
    try:
        with psycopg2.connect(connection_string) as conn:
            with conn.cursor() as cur:
                # Clear existing data
                cur.execute('DELETE FROM "Phones"')
                print(f"\n✅ Cleared existing data")
                
                # Insert flagship phones
                inserted = 0
                failed = 0
                
                for phone in phones:
                    try:
                        # Generate placeholder image URL
                        placeholder_url = f"https://via.placeholder.com/400x600/4A90E2/FFFFFF?text={phone['brand']}+{phone['model'].replace(' ', '+')}"
                        
                        cur.execute('''
                            INSERT INTO "Phones" ("Brand", "Model", "Storage", "Ram", "ScreenSize", 
                                                 "Camera", "Battery", "ImageUrl", "ReleaseYear")
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            phone['brand'],
                            phone['model'],
                            'TBD',  # To be filled by crawler
                            'TBD',
                            'TBD', 
                            'TBD',
                            'TBD',
                            placeholder_url,
                            phone['year']
                        ))
                        inserted += 1
                    except Exception as e:
                        failed += 1
                        print(f"  ❌ Insert failed: {phone['brand']} {phone['model']} ({phone['year']}) - {e}")
                
                conn.commit()
                
                print(f"✅ Successfully inserted: {inserted} phones")
                if failed > 0:
                    print(f"❌ Failed: {failed} phones")
                
                # 验证最终数量
                cur.execute('SELECT COUNT(*) FROM "Phones"')
                final_count = cur.fetchone()[0]
                print(f"🎯 最终数据库: {final_count}款旗舰手机")
                
                return final_count
                
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        return 0

def main():
    """主函数"""
    print("🚀 2020-2024年旗舰手机数据库重建工具")
    print("包含11个品牌的旗舰机型，品牌名称标准化")
    
    connection_string = "host=localhost dbname=mobilephone_db user=postgres password=postgres"
    
    final_count = rebuild_flagship_database(connection_string)
    
    if 100 <= final_count <= 200:
        print(f"\n🎉 重建成功！数据库现在包含{final_count}款旗舰手机")
        print(f"✅ 符合目标范围: 100-200款")
        print(f"📱 覆盖年份: 2020-2024 (近5年)")
        print(f"🏆 全部为旗舰机型")
    else:
        print(f"\n⚠️ 数量超出预期: {final_count}款")
    
    # 保存机型列表
    phones = get_flagship_phones_2020_2024()
    with open('flagship_phones_2020_2024.json', 'w', encoding='utf-8') as f:
        json.dump(phones, f, indent=2, ensure_ascii=False)
    
    print(f"💾 旗舰机型列表已保存到: flagship_phones_2020_2024.json")

if __name__ == "__main__":
    main()
