#!/usr/bin/env python3
"""
Check ZOL page structure and response
"""

import requests
from bs4 import BeautifulSoup

def check_zol_response():
    """Check what ZOL returns for search requests"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    url = "https://search.zol.com.cn/s/shouji_%E8%8B%B9%E6%9E%9C%20iPhone15.html"
    
    try:
        response = session.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content length: {len(response.content)}")
        print(f"URL after redirects: {response.url}")
        
        # Save response for inspection
        with open('zol_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("Response saved to zol_response.html")
        
        # Check if it's a CAPTCHA or blocking page
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        if title:
            print(f"Page title: {title.get_text()}")
        
        # Look for anti-bot indicators
        scripts = soup.find_all('script')
        for script in scripts:
            text = script.get_text()
            if any(keyword in text.lower() for keyword in ['captcha', 'bot', 'verify', 'challenge']):
                print("⚠️ Possible anti-bot detection")
                break
        
        # Check if page has actual content
        body = soup.find('body')
        if body:
            text_content = body.get_text(strip=True)
            print(f"Body text length: {len(text_content)}")
            if len(text_content) < 100:
                print("⚠️ Very little content - possible blocking")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_zol_response()
