import sys
import os
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from playwright.sync_api import sync_playwright
from backend.database import SessionLocal
from backend.models import Stock, PriceTick
from backend.logger import logger
from backend.market_scraper import generate_broker_flow_proxy

def surgical_flow_enrichment():
    """
    Surgically enriches the database with TRUE institutional flow 
    using a high-velocity day-first scraping strategy.
    """
    db = SessionLocal()
    try:
        # 1. Get target stocks
        target_tickers = ['AKRA', 'NISP', 'MDKA']
        stocks = db.query(Stock).filter(Stock.ticker.in_(target_tickers)).all()
        stock_map = {s.ticker: s.id for s in stocks}
        
        if not stocks:
            print("No target stocks found in DB.")
            return

        print(f"--- 🏛️ SURGICAL FLOW STRIKE: {target_tickers} ---")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
            page = context.new_page()
            
            # Establish session
            page.goto("https://www.idx.co.id/en/market-data/trading-summary/stock-summary/", wait_until="networkidle")
            
            # Loop through last 30 days
            end_date = datetime.now()
            for i in range(30):
                target_date = (end_date - timedelta(days=i)).date()
                date_str = target_date.strftime("%Y%m%d")
                
                print(f"Fetching IDX Summary for {target_date}...")
                
                script = f"""
                async () => {{
                    try {{
                        const res = await fetch('https://www.idx.co.id/primary/TradingSummary/GetStockSummary?date={date_str}');
                        return await res.json();
                    }} catch (e) {{
                        return null;
                    }}
                }}
                """
                
                result = page.evaluate(script)
                if not result or not result.get("data"):
                    print(f"  - No data found for {target_date} (Weekend/Holiday?)")
                    continue
                
                # Process all data in one go
                data_list = result["data"]
                found_count = 0
                for item in data_list:
                    ticker = item.get("StockCode")
                    if ticker in stock_map:
                        f_buy = int(item.get("ForeignBuy", 0))
                        f_sell = int(item.get("ForeignSell", 0))
                        
                        # Update the tick in DB
                        tick = db.query(PriceTick).filter(
                            PriceTick.stock_id == stock_map[ticker],
                            PriceTick.date == target_date
                        ).first()
                        
                        if tick:
                            tick.foreign_buy = f_buy
                            tick.foreign_sell = f_sell
                            tick.foreign_net = f_buy - f_sell
                            found_count += 1
                
                db.commit()
                print(f"  - Updated {found_count} stocks for {target_date}")
                time.sleep(0.5) # throttle slightly
                
            browser.close()
            
        # 2. Synchronize the Flow Menu
        print("Synchronizing Flow Intelligence...")
        generate_broker_flow_proxy(db)
        print("✅ STRIKE COMPLETE.")

    except Exception as e:
        print(f"❌ STRIKE FAILED: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    surgical_flow_enrichment()
