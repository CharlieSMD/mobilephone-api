#!/usr/bin/env python3
"""
Test the two phones that failed
"""

import psycopg2
from gsmarena_flagship_crawler import GSMArenaFlagshipCrawler

def test_failed_phones():
    """Test the two phones that failed in the previous run"""
    print("🧪 Testing previously failed phones")
    
    db_config = {
        'host': 'localhost',
        'database': 'mobilephone_db',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    # Get the specific phones that failed (ASUS ROG Phone 8 and 8 Pro)
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT "Id", "Brand", "Model", "ReleaseYear"
                    FROM "Phones" 
                    WHERE ("Model" = 'ROG Phone 8' OR "Model" = 'ROG Phone 8 Pro')
                    AND "Brand" = 'ASUS'
                    ORDER BY "Model"
                ''')
                
                phones = []
                for row in cur.fetchall():
                    phones.append({
                        'id': row[0],
                        'brand': row[1],
                        'model': row[2],
                        'year': row[3]
                    })
                
                print(f"Found {len(phones)} phones to retest:")
                for i, phone in enumerate(phones, 1):
                    print(f"  {i}. {phone['brand']} {phone['model']} (ID: {phone['id']})")
    
    except Exception as e:
        print(f"Error getting phones: {e}")
        return
    
    if not phones:
        print("No failed phones found")
        return
    
    # Run crawler for these specific phones
    crawler = GSMArenaFlagshipCrawler(db_config)
    
    for phone in phones:
        print(f"\n📱 Processing: {phone['brand']} {phone['model']}")
        
        try:
            # Search for product page
            product_url = crawler.search_phone_on_gsmarena(phone['brand'], phone['model'])
            
            if not product_url:
                print(f"❌ No product page found")
                continue
            
            # Extract details
            details = crawler.extract_phone_details(product_url)
            
            if not details:
                print(f"❌ No details extracted")
                continue
            
            # Update database
            if crawler.update_phone_details(phone['id'], details):
                print(f"✅ Successfully updated with {len(details)} details")
            else:
                print(f"❌ Failed to update database")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_failed_phones()
