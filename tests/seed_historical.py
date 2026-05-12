import sys
import os
sys.path.append(os.getcwd())
from backend.database import SessionLocal
from backend.models import InsiderTransaction, Stock, PriceTick
from datetime import date

def seed():
    db = SessionLocal()
    # Ensure stock exists
    stock = db.query(Stock).filter(Stock.ticker == "BBCA").first()
    if not stock:
        stock = Stock(ticker="BBCA", name="Bank Central Asia")
        db.add(stock)
        db.commit()
        db.refresh(stock)
    
    # Add a Feb 2026 transaction
    t = InsiderTransaction(
        ticker="BBCA",
        stock_id=stock.id,
        insider_name="HENDRA LEMBONG",
        role="DIREKTUR",
        transaction_type="BUY",
        shares=1000,
        price=9500,
        value=9500000,
        date=date(2026, 2, 15),
        filing_date=date(2026, 2, 16),
        score=5,
        source_url="https://example.com/filing1"
    )
    db.add(t)
    
    # Add some historical price ticks for Feb 2026
    for i in range(1, 29):
        tick = PriceTick(
            stock_id=stock.id,
            date=date(2026, 2, i),
            open=9400 + i,
            high=9600 + i,
            low=9300 + i,
            close=9500 + i,
            volume=1000000 + i*1000
        )
        db.add(tick)
    
    db.commit()
    print("Seeded Feb 2026 data for BBCA")
    db.close()

if __name__ == "__main__":
    seed()
