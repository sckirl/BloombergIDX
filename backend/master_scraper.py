import sys
import os
import time
from backend.database import SessionLocal
from backend.logger import logger

# Import the existing pipeline functions
from backend.scraper import run_scraper
from backend.market_scraper import enrich_stock_metadata, fetch_market_history, generate_broker_flow_proxy
from backend.event_scraper import run_event_scraper

def run_master_strike(full_year: bool = False):
    """
    The "Master Strike": A fully orchestrated ingestion pipeline.
    Executes all scrapers in the optimal strategic order to ensure 
    no data gaps and maximum relational integrity.
    """
    start_time = time.time()
    logger.info(f"--- 🏛️ BloombergIDX MASTER STRIKE INITIATED (Full Year: {full_year}) ---")
    
    db = SessionLocal()
    try:
        # Phase 1: Stock Metadata (The Foundation)
        # Updates sectors, PE, PB, and Market Cap. 
        # Crucial for Heatmap (MAP) and Anomaly categorization.
        logger.info("PHASE 1: Syncing Stock Metadata & Sectors...")
        enrich_stock_metadata(db)
        
        # Phase 2: Market History (The Context)
        # Fetches 60 days of OHLCV ticks.
        # Wakes up the Anomaly detection and Price Map modules.
        logger.info("PHASE 2: Fetching Market History & Price Ticks...")
        fetch_market_history(db)
        
        # Phase 3: Corporate Events (The Horizon)
        # Scrapes E-IPO and M&A actions.
        # Populates the Deal-Sheet and Event Timeline modules.
        logger.info("PHASE 3: Ingesting Corporate Event Intelligence...")
        run_event_scraper()
        
        # Phase 4: Insider Transactions (The Core)
        # The primary Playwright-based scraper for PDF disclosures.
        # Using undetectable-stealth to bypass exchange detection.
        logger.info("PHASE 4: Ingesting Insider Disclosures (Stealth Mode)...")
        run_scraper(full_year=full_year)
        
        # Phase 5: Smart Money Analysis (The Insight)
        # Generates broker flow proxies based on the freshly scraped insider trades.
        logger.info("PHASE 5: Synchronizing Smart Money Flow Proxies...")
        generate_broker_flow_proxy(db)
        
        duration = (time.time() - start_time) / 60
        logger.info(f"--- ✅ MASTER STRIKE COMPLETE (Duration: {duration:.2f}m) ---")
        logger.info("All modules (INSIDER, MAP, ANOMALY, EVENT) are now synchronized.")
        
    except Exception as e:
        logger.error(f"❌ MASTER STRIKE CRITICAL FAILURE: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    # Check for --full-year flag
    full_year_flag = "--full-year" in sys.argv
    run_master_strike(full_year=full_year_flag)
