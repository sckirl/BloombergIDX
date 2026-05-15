import os
import sys
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the current directory to sys.path so we can import backend
sys.path.append(os.getcwd())

# Mock environment variables if needed
os.environ["DATABASE_URL"] = "sqlite:///benchmark.db"

from backend.database import Base, engine, SessionLocal
from backend.models import Stock, PriceTick, InsiderTransaction
from backend.main import get_watchlist_data
from datetime import datetime, timedelta

def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Seed data
    tickers = [f"TICK{i}" for i in range(100)]
    for ticker in tickers:
        stock = Stock(
            ticker=ticker,
            name=f"Company {ticker}",
            fifty_two_week_high=100.0,
            fifty_two_week_low=50.0,
            avg_volume=1000000,
            trailing_pe=15.0,
            price_to_book=2.0
        )
        db.add(stock)
        db.flush()

        # Add price ticks
        for j in range(10):
            tick = PriceTick(
                stock_id=stock.id,
                date=(datetime.now() - timedelta(days=j)).date(),
                close=100.0 + j,
                open=100.0 + j,
                high=105.0 + j,
                low=95.0 + j,
                volume=10000
            )
            db.add(tick)

        # Add insider transactions
        for j in range(5):
            trans = InsiderTransaction(
                stock_id=stock.id,
                ticker=ticker,
                transaction_type="BUY",
                date=(datetime.now() - timedelta(days=j)).date(),
                shares=100,
                price=100.0
            )
            db.add(trans)

    db.commit()
    db.close()
    return tickers

def run_benchmark(tickers_list):
    db = SessionLocal()
    tickers_str = ",".join(tickers_list)

    start_time = time.time()
    result = get_watchlist_data(tickers_str, db)
    end_time = time.time()

    db.close()
    return end_time - start_time, len(result)

if __name__ == "__main__":
    if os.path.exists("benchmark.db"):
        os.remove("benchmark.db")

    tickers = setup_db()

    # Warm up
    run_benchmark(tickers[:10])

    # Benchmark
    durations = []
    for _ in range(5):
        duration, count = run_benchmark(tickers)
        durations.append(duration)
        print(f"Run took {duration:.4f} seconds for {count} tickers")

    print(f"Average duration: {sum(durations)/len(durations):.4f} seconds")
