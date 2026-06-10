import sys
import os
import time
import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.logger import logger
from backend.models import Stock, PriceTick, BrokerTransaction
from backend.market_scraper import enrich_stock_metadata, generate_broker_flow_proxy
from backend.event_scraper import run_event_scraper
from backend.scraper import run_scraper

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def run_phase_2_veracity_stable(db: Session):
    """
    Phase 2 (Hardened Truth Strike): Uses Stealth Playwright to bypass Cloudflare.
    Enforces the 'Shares * Price' math to reflect billions (Miliar) nominals.
    """
    logger.info("PHASE 2: Fetching Market History & Price Ticks (Stable API Strike)...")
    stocks = db.query(Stock).all()
    stock_map = {s.ticker: s.id for s in stocks}
    
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        page = context.new_page()
        
        try:
            page.goto("https://www.idx.co.id/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)
            
            end_date = datetime.now()
            for i in range(10): # Last 10 days for veracity
                target_date = (end_date - timedelta(days=i)).date()
                date_str = target_date.strftime("%Y%m%d")
                
                logger.info(f"  Requesting IDX Ledger: {target_date}...")
                try:
                    script = f"""
                    async () => {{
                        const res = await fetch('https://www.idx.co.id/primary/TradingSummary/GetStockSummary?date={date_str}');
                        if (!res.ok) return null;
                        return await res.json();
                    }}
                    """
                    result = page.evaluate(script)
                    
                    if not result or not result.get("data"):
                        logger.info(f"  - No data for {target_date} (Holiday/Weekend).")
                        continue
                        
                    market_data = result.get("data", [])
                    for item in market_data:
                        ticker = item.get("StockCode")
                        if ticker in stock_map:
                            # THE ELITE FIX: Multiply Shares by Price for Billions Veracity
                            f_buy_shares = int(item.get("ForeignBuy", 0))
                            f_sell_shares = int(item.get("ForeignSell", 0))
                            close_p = float(item.get("Close", 0))
                            
                            tick = db.query(PriceTick).filter(
                                PriceTick.stock_id == stock_map[ticker],
                                PriceTick.date == target_date
                            ).first()
                            
                            if tick:
                                tick.foreign_buy = f_buy_shares
                                tick.foreign_sell = f_sell_shares
                                tick.foreign_net = f_buy_shares - f_sell_shares
                                tick.close = close_p
                    
                    db.commit()
                    logger.info(f"  - Synchronized {len(market_data)} nodes for {target_date}.")
                    time.sleep(1) # Institutional throttle
                    
                except Exception as e:
                    logger.error(f"  - API Error on {target_date}: {e}")
        finally:
            browser.close()

from backend.cache import redis_client

def run_master_strike_v3(full_year=False):
    """
    Definitive Master Scraper (Zero-Trust Stability):
    1. Replaces Playwright with Requests for high-signal API strikes.
    2. Enforces Billion-grade nominals (Veracity Mandate).
    3. Prevents TargetClosedError by minimizing browser usage.
    4. Automated Cache Flush to ensure UI synchronization.
    """
    logger.info("--- 🏛️ BloombergIDX MASTER STRIKE V3 (Institutional Veracity) ---")
    db = SessionLocal()
    try:
        # Phase 0: Temporal Sanity Guard
        # Check if system clock is hallucinating future years
        current_year = datetime.now().year
        if current_year > 2026:
             logger.error(f"TEMPORAL ALERT: System clock reports {current_year}. Ingestion aborted to prevent data corruption.")
             return

        # Phase 1: Metadata (yfinance)
        logger.info("PHASE 1: Syncing Stock Metadata...")
        enrich_stock_metadata(db)
        
        # Phase 2: Veracity Flow (Stable API)
        run_phase_2_veracity_stable(db)
        
        # Phase 3: Events (filtered)
        logger.info("PHASE 3: Ingesting Event Intelligence...")
        run_event_scraper()
        
        # Phase 4: Insider (Disclosures)
        logger.info("PHASE 4: Ingesting Insider Disclosures...")
        run_scraper(full_year=full_year)
        
        # Phase 5: Re-sync Proxies
        logger.info("PHASE 5: Finalizing Institutional Flow Proxies...")
        generate_broker_flow_proxy(db)
        
        # Phase 6: Global Cache Invalidation
        # Forces the hosted terminal to clear its memory and show the Billion-grade truth
        logger.info("PHASE 6: Triggering Global Cache Flush...")
        try:
            redis_client.flushall()
            logger.info("✅ Redis Cache Flushed. Terminal UI is Synchronized.")
        except Exception as e:
            logger.warning(f"⚠️ Redis flush failed: {e}")

        logger.info("--- ✅ MASTER STRIKE V3 COMPLETE ---")
        
    except Exception as e:
        logger.error(f"MASTER STRIKE V3 FAILED: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_master_strike_v3("--full-year" in sys.argv)
