from .database import SessionLocal
from .models import Stock
import datetime

LQ45_TICKERS = [
    "ACES", "ADRO", "AKRA", "AMRT", "ANTM", "ARTO", "ASII", "BBCA", "BBNI", "BBRI", 
    "BBTN", "BMRI", "BRIS", "BRPT", "BUKA", "CPIN", "EMTK", "ESSA", "EXCL", "GOTO", 
    "HRUM", "ICBP", "INCO", "INDF", "INKP", "INTP", "ITMG", "KLBF", "MAPI", "MBMA", 
    "MDKA", "MEDC", "MIKA", "PGAS", "PTBA", "SIDO", "SMGR", "SRTG", "TLKM", "TPIA", 
    "UNTR", "UNVR"
]

def seed_stocks():
    db = SessionLocal()
    try:
        for ticker in LQ45_TICKERS:
            existing = db.query(Stock).filter(Stock.ticker == ticker).first()
            if not existing:
                stock = Stock(
                    ticker=ticker,
                    name=f"Company {ticker}",
                    is_active=True,
                    listing_date=datetime.date(2000, 1, 1) # Placeholder
                )
                db.add(stock)
                print(f"Added stock: {ticker}")
        db.commit()
        print("Stock seeding complete.")
    except Exception as e:
        print(f"Error seeding stocks: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_stocks()
