#!/usr/bin/env python3
"""
Test GSMArena Flagship Crawler with sample phones
"""

from gsmarena_flagship_crawler import GSMArenaFlagshipCrawler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_flagship_crawler():
    """Test crawler with flagship phone samples"""
    print("🧪 Testing GSMArena Flagship Crawler")
    
    db_config = {
        'host': 'localhost',
        'database': 'mobilephone_db',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    crawler = GSMArenaFlagshipCrawler(db_config)
    
    # Test with representative flagship phones
    test_phones = [
        {"brand": "Apple", "model": "iPhone 15 Pro Max"},
        {"brand": "Samsung", "model": "Galaxy S24 Ultra"},
        {"brand": "Google", "model": "Pixel 8 Pro"},
        {"brand": "Xiaomi", "model": "Xiaomi 14 Ultra"},
        {"brand": "OnePlus", "model": "12"}
    ]
    
    for phone in test_phones:
        print(f"\n📱 Testing: {phone['brand']} {phone['model']}")
        
        # Test search
        product_url = crawler.search_phone_on_gsmarena(phone['brand'], phone['model'])
        if product_url:
            print(f"✅ Found product page: {product_url}")
            
            # Test detail extraction (just first few fields to avoid overwhelming output)
            details = crawler.extract_phone_details(product_url)
            if details:
                print(f"✅ Extracted {len(details)} details:")
                for key, value in list(details.items())[:5]:  # Show first 5 details
                    print(f"   {key}: {value}")
                if len(details) > 5:
                    print(f"   ... and {len(details) - 5} more details")
            else:
                print("❌ No details extracted")
        else:
            print("❌ No product page found")
        
        print("-" * 50)

if __name__ == "__main__":
    test_flagship_crawler()
