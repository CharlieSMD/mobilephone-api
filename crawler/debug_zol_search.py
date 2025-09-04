#!/usr/bin/env python3
"""
Debug ZOL search functionality
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def test_zol_search():
    """Test different search approaches for ZOL"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    # Test searches
    searches = [
        "苹果 iPhone15",
        "iPhone 15",
        "三星 Galaxy S24", 
        "小米14"
    ]
    
    for search_term in searches:
        print(f"\n🔍 Testing search: {search_term}")
        
        # Try different search URLs
        search_urls = [
            f"https://search.zol.com.cn/s/shouji_{quote(search_term.encode('utf-8'))}.html",
            f"https://search.zol.com.cn/s/{quote(search_term.encode('utf-8'))}.html",
            f"https://detail.zol.com.cn/index.php?c=List&subcate=57&keyword={quote(search_term.encode('utf-8'))}"
        ]
        
        for i, url in enumerate(search_urls, 1):
            try:
                print(f"  URL {i}: {url}")
                response = session.get(url, timeout=10)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for product links
                    links = soup.find_all('a', href=True)
                    product_links = []
                    
                    for link in links:
                        href = link.get('href')
                        if href and ('detail.zol.com.cn' in href or '/detail/' in href):
                            text = link.get_text(strip=True)
                            if text:
                                product_links.append((href, text))
                    
                    print(f"  Found {len(product_links)} potential product links")
                    for href, text in product_links[:3]:  # Show first 3
                        print(f"    - {text}: {href}")
                
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    test_zol_search()
