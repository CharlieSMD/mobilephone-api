#!/usr/bin/env python3
"""
尝试修复Google Pixel和Honor手机的规格数据
"""

import requests
import time
import psycopg2
from bs4 import BeautifulSoup
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gsmarena_access():
    """Test if we can access GSMArena"""
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Try to access the main page first
        response = session.get('https://www.gsmarena.com', timeout=10)
        logger.info(f"GSMArena main page status: {response.status_code}")
        
        if response.status_code == 200:
            # Try a simple search
            search_url = "https://www.gsmarena.com/results.php3?sQuickSearch=yes&sName=Google+Pixel+7"
            response = session.get(search_url, timeout=10)
            logger.info(f"Search test status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("✅ GSMArena access successful!")
                return True
            else:
                logger.error(f"❌ Search blocked: {response.status_code}")
                return False
        else:
            logger.error(f"❌ Main page blocked: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ GSMArena access failed: {e}")
        return False

def main():
    logger.info("🔍 Testing GSMArena access...")
    
    if test_gsmarena_access():
        logger.info("✅ GSMArena is accessible. We can proceed with crawling.")
        logger.info("You can now run the main crawler scripts.")
    else:
        logger.info("❌ GSMArena is currently blocking requests.")
        logger.info("Please wait or try from a different IP address.")
        logger.info("Alternative: We can use manual data entry for critical phones.")
    
    # Show current missing data status
    try:
        conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
        cur = conn.cursor()
        
        cur.execute('''
            SELECT "Brand", COUNT(*) as total, 
                   COUNT(CASE WHEN "ScreenSize" = 'TBD' THEN 1 END) as missing_screen,
                   COUNT(CASE WHEN "Ram" IN ('TBD', 'Card slot', 'No') THEN 1 END) as missing_ram
            FROM "Phones" 
            WHERE "Brand" NOT IN ('Samsung', 'Apple')
            GROUP BY "Brand" 
            ORDER BY "Brand"
        ''')
        
        results = cur.fetchall()
        
        logger.info("\n📊 Current missing data status (excluding Samsung & Apple):")
        for brand, total, missing_screen, missing_ram in results:
            logger.info(f"{brand}: {total} phones, {missing_screen} missing screen, {missing_ram} missing RAM")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Database query error: {e}")

if __name__ == "__main__":
    main()

