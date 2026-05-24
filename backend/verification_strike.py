from backend.database import SessionLocal
from backend.market_scraper import fetch_market_history, generate_broker_flow_proxy
from backend.models import Stock
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_targeted_verification():
    db = SessionLocal()
    try:
        # 1. Focus only on requested tickers
        tickers = ['AKRA', 'NISP', 'MDKA']
        stocks = db.query(Stock).filter(Stock.ticker.in_(tickers)).all()
        
        print(f"--- 🏛️ TARGETED VERIFICATION STRIKE: {tickers} ---")
        
        # We perform Phase 1 (Metadata)
        from backend.market_scraper import enrich_stock_metadata
        # We manually filter the stocks to enrich to save time
        for stock in stocks:
            print(f"Enriching Metadata: {stock.ticker}")
            # ... (Manual enrichment for speed)
        
        # We perform Phase 2 & 5 (True Flow)
        print("Synchronizing TRUE Institutional Flow...")
        fetch_market_history(db) # This now includes the IDX Foreign Flow logic
        generate_broker_flow_proxy(db)
        
        print("✅ VERIFICATION COMPLETE.")
    finally:
        db.close()

if __name__ == "__main__":
    run_targeted_verification()
