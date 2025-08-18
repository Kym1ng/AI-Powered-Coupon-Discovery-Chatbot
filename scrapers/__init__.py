from .simplycodes_scraper import SimplyCodesScraper

def run_scraper(url, headless=True, use_retry=True):
    """
    Convenience function to run the scraper with enhanced features
    
    Args:
        url (str): The URL to scrape
        headless (bool): Whether to run in headless mode
        use_retry (bool): Whether to use retry logic
    """
    scraper = SimplyCodesScraper(headless=headless)
    try:
        if use_retry:
            result = scraper.scrape_with_retry(url)
        else:
            result = scraper.scrape(url)
        
        if result:
            print("✅ Scraping completed successfully!")
            return result
        else:
            print("❌ Scraping failed")
            return None
            
    finally:
        scraper.close()

def discover_categories(headless=True):
    """
    Convenience function to just discover categories without scraping
    
    Args:
        headless (bool): Whether to run in headless mode
    """
    scraper = SimplyCodesScraper(headless=headless)
    try:
        result = scraper.discover_categories()
        
        if result:
            print("✅ Category discovery completed successfully!")
            return result
        else:
            print("❌ Category discovery failed")
            return None
            
    finally:
        scraper.close()

 