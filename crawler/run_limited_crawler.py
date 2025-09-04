#!/usr/bin/env python3
"""
Run GSMArena crawler for a limited number of phones first (testing)
"""

import psycopg2
from gsmarena_flagship_crawler import GSMArenaFlagshipCrawler

def run_limited_crawler(limit=10):
    """Run crawler for first N phones only"""
    print(f"🧪 Running limited crawler for first {limit} phones")
    
    db_config = {
        'host': 'localhost',
        'database': 'mobilephone_db',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    # Get first N phones that need details
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                    SELECT "Id", "Brand", "Model", "ReleaseYear"
                    FROM "Phones" 
                    WHERE ("Processor" IS NULL OR "Processor" = 'TBD')
                    ORDER BY "Brand", "Model"
                    LIMIT {limit}
                ''')
                
                phones = []
                for row in cur.fetchall():
                    phones.append({
                        'id': row[0],
                        'brand': row[1],
                        'model': row[2],
                        'year': row[3]
                    })
                
                print(f"Found {len(phones)} phones to process:")
                for i, phone in enumerate(phones, 1):
                    print(f"  {i}. {phone['brand']} {phone['model']} ({phone['year']})")
    
    except Exception as e:
        print(f"Error getting phones: {e}")
        return
    
    # Run crawler
    crawler = GSMArenaFlagshipCrawler(db_config)
    
    # Temporarily override the get_flagship_phones_from_database method
    original_method = crawler.get_flagship_phones_from_database
    crawler.get_flagship_phones_from_database = lambda: phones
    
    # Run crawling
    crawler.crawl_flagship_phones()
    
    # Restore original method
    crawler.get_flagship_phones_from_database = original_method

if __name__ == "__main__":
    run_limited_crawler(10)  # Test with first 10 phones
