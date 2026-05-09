import json
from datetime import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import InsiderTransaction, Stock
from .utils import calculate_score, calculate_confidence

def seed_data():
    db = SessionLocal()
    try:
        # Data extracted from idx_data.json
        recent_data = [
            {
                "ticker": "PADA",
                "insider_name": "SIGIT KUNTJAHJO.AK",
                "role": "DIREKTUR",
                "transaction_type": "BUY",
                "shares": 500000,
                "price": 150,
                "date": datetime(2026, 4, 9).date(),
                "source_url": "https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/From_KSEI/LK-09042026-4530-00.pdf-0.pdf"
            },
            {
                "ticker": "BJTM",
                "insider_name": "ARIF SUHIRMAN",
                "role": "DIREKTUR",
                "transaction_type": "BUY",
                "shares": 100000,
                "price": 600,
                "date": datetime(2026, 4, 9).date(),
                "source_url": "https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/From_KSEI/LK-09042026-6185-00.pdf-0.pdf"
            },
            {
                "ticker": "WGSH",
                "insider_name": "WYNFIELD GLOBAL VENTURES",
                "role": "PENGENDALI",
                "transaction_type": "BUY",
                "shares": 2000000,
                "price": 100,
                "date": datetime(2026, 4, 8).date(),
                "source_url": "https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/From_KSEI/LK-08042026-5269-00.pdf-0.pdf"
            },
            {
                "ticker": "TAYS",
                "insider_name": "ANWAR TAY",
                "role": "DIREKTUR UTAMA",
                "transaction_type": "SELL",
                "shares": 1000000,
                "price": 80,
                "date": datetime(2026, 4, 8).date(),
                "source_url": "https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/From_KSEI/LK-08042026-3997-00.pdf-0.pdf"
            },
            {
                "ticker": "UVCR",
                "insider_name": "HADY KUSWANTO",
                "role": "DIREKTUR",
                "transaction_type": "BUY",
                "shares": 300000,
                "price": 120,
                "date": datetime(2026, 4, 8).date(),
                "source_url": "https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/From_KSEI/LK-08042026-2482-00.pdf-0.pdf"
            },
            {
                "ticker": "MEDS",
                "insider_name": "JEMMY KURNIAWAN",
                "role": "KOMISARIS",
                "transaction_type": "BUY",
                "shares": 150000,
                "price": 50,
                "date": datetime(2026, 4, 8).date(),
                "source_url": "https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/From_KSEI/LK-08042026-8944-00.pdf-0.pdf"
            },
            {
                "ticker": "TRUK",
                "insider_name": "SUWITO",
                "role": "PENGENDALI",
                "transaction_type": "BUY",
                "shares": 5000000,
                "price": 90,
                "date": datetime(2026, 4, 8).date(),
                "source_url": "https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/From_KSEI/LK-08042026-1606-00.pdf-0.pdf"
            }
        ]

        for item in recent_data:
            # Check if already exists
            existing = db.query(InsiderTransaction).filter(InsiderTransaction.source_url == item["source_url"]).first()
            if not existing:
                # Resolve stock_id
                ticker = item["ticker"]
                stock = db.query(Stock).filter(Stock.ticker == ticker).first()
                if not stock:
                    stock = Stock(ticker=ticker, name=f"Company {ticker}")
                    db.add(stock)
                    db.flush()
                
                item["stock_id"] = stock.id
                item["value"] = item["shares"] * item["price"]
                item["filing_date"] = item["date"]
                item["issuer_name"] = ""
                item["ownership_before"] = 0
                item["ownership_after"] = 0
                item["ownership_change_pct"] = 0
                item["purpose"] = "Investasi"
                
                score, reasons = calculate_score(item, db=db)
                item["score"] = score
                item["score_reasons"] = json.dumps(reasons)
                item["confidence"] = calculate_confidence(item)
                
                transaction = InsiderTransaction(**item)
                db.add(transaction)
        
        db.commit()
        print(f"Successfully seeded {len(recent_data)} recent transactions.")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
