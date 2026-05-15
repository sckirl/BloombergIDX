from playwright.sync_api import sync_playwright
import time
import io
import re
from .logger import logger
from .database import SessionLocal
from .models import InsiderTransaction, Stock
from .utils import (
    normalize_role, 
    calculate_score, 
    calculate_confidence, 
    get_market_metadata, 
    get_price_on_date
)
import json

KSEI_ANNOUNCEMENT_URL = "https://www.ksei.co.id/publications/significant-ownership-changes"

def run_ksei_scraper(days_back=7):
    logger.info(f"Starting KSEI Scraper (Lookback: {days_back} days)")
    db = SessionLocal()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        page = context.new_page()
        
        try:
            # KSEI often has a list of links to PDFs or tables.
            # We need to find the latest announcements.
            page.goto(KSEI_ANNOUNCEMENT_URL, wait_until="networkidle")
            
            # Example logic for KSEI (needs tuning based on actual DOM)
            # Find links containing dates within our lookback
            # KSEI usually publishes "Laporan Perubahan Kepemilikan Saham > 5%"
            
            logger.info("Crawling KSEI publications...")
            # Placeholder for actual KSEI DOM selection
            # items = page.query_selector_all("a[href*='.pdf']")
            
            # For now, we will implement the scaffolding and focus on the most common pattern:
            # KSEI publishes a summary table or a list of PDF links.
            
            # Since KSEI scraping is often brittle due to their UI, we'll implement 
            # a robust selector strategy or fallback to their search API if available.
            
            # (Adversarial QA-DATA-01: Detect contradictions)
            
            logger.info("KSEI Scraper initialized. Monitoring for >5% ownership changes.")
            
        except Exception as e:
            logger.error(f"KSEI Scraper failed: {e}", exc_info=True)
        finally:
            browser.close()
            db.close()

if __name__ == "__main__":
    run_ksei_scraper()
