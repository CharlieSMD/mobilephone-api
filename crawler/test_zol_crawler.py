#!/usr/bin/env python3
"""
Test ZOL Crawler with a few sample phones
"""

from zol_flagship_crawler import ZOLCrawler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_crawler():
    """Test crawler with sample phones"""
    print("🧪 Testing ZOL Crawler with sample phones")
    
    db_config = {
        'host': 'localhost',
        'database': 'mobilephone_db',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    crawler = ZOLCrawler(db_config)
    
    # Test search functionality
    test_phones = [
        {"brand": "Apple", "model": "iPhone 15 Pro Max"},
        {"brand": "Samsung", "model": "Galaxy S24 Ultra"},
        {"brand": "Xiaomi", "model": "Xiaomi 14 Ultra"}
    ]
    
    for phone in test_phones:
        print(f"\n📱 Testing: {phone['brand']} {phone['model']}")
        
        # Test search
        product_url = crawler.search_phone_on_zol(phone['brand'], phone['model'])
        if product_url:
            print(f"✅ Found product page: {product_url}")
            
            # Test detail extraction
            details = crawler.extract_phone_details(product_url)
            if details:
                print(f"✅ Extracted {len(details)} details:")
                for key, value in details.items():
                    print(f"   {key}: {value}")
            else:
                print("❌ No details extracted")
        else:
            print("❌ No product page found")

if __name__ == "__main__":
    test_crawler()
