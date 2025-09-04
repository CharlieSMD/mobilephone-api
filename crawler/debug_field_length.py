#!/usr/bin/env python3
"""
Debug which field is causing the length issue
"""

from gsmarena_flagship_crawler import GSMArenaFlagshipCrawler

def debug_field_lengths():
    """Debug field lengths for problematic phones"""
    print("🔍 Debugging field lengths")
    
    db_config = {
        'host': 'localhost',
        'database': 'mobilephone_db',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    crawler = GSMArenaFlagshipCrawler(db_config)
    
    # Test the problematic phone URLs
    test_urls = [
        "https://www.gsmarena.com/asus_rog_phone_8-12780.php",
        "https://www.gsmarena.com/asus_rog_phone_8_pro-12746.php"
    ]
    
    for url in test_urls:
        print(f"\n📱 Testing: {url}")
        
        details = crawler.extract_phone_details(url)
        
        print(f"Found {len(details)} details:")
        for key, value in details.items():
            value_str = str(value)
            print(f"  {key}: {len(value_str)} chars - {value_str[:100]}{'...' if len(value_str) > 100 else ''}")
            
            # Check which fields exceed typical lengths
            if len(value_str) > 100:
                print(f"    ⚠️  Field '{key}' is {len(value_str)} characters (might be too long)")

if __name__ == "__main__":
    debug_field_lengths()
