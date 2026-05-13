import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import random
import time

from .models import Stock, PriceTick, BrokerTransaction, InsiderTransaction
from .logger import logger

def enrich_stock_metadata(db: Session):
    """
    Update stock metadata (name, sector, subsector) using yfinance.
    """
    logger.info("Starting stock metadata enrichment...")
    stocks = db.query(Stock).all()
    
    updated_count = 0
    for stock in stocks:
        ticker_jk = f"{stock.ticker}.JK"
        try:
            ticker_info = yf.Ticker(ticker_jk).info
            
            # yfinance uses 'sector' and 'industry'
            # we map industry to subsector
            stock.name = ticker_info.get('longName', stock.name)
            stock.sector = ticker_info.get('sector', stock.sector)
            stock.subsector = ticker_info.get('industry', stock.subsector)
            stock.market_cap = ticker_info.get('marketCap', stock.market_cap)
            stock.trailing_pe = ticker_info.get('trailingPE')
            stock.price_to_book = ticker_info.get('priceToBook')
            stock.fifty_two_week_high = ticker_info.get('fiftyTwoWeekHigh')
            stock.fifty_two_week_low = ticker_info.get('fiftyTwoWeekLow')
            stock.avg_volume = ticker_info.get('averageVolume')
            
            updated_count += 1
            if updated_count % 10 == 0:
                db.commit()
                logger.info(f"Enriched {updated_count} stocks...")
            
            # rate limiting
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error enriching {stock.ticker}: {str(e)}")
            continue
            
    db.commit()
    logger.info(f"Metadata enrichment completed. {updated_count} stocks updated.")

def fetch_market_history(db: Session):
    """
    Fetch last 60 days of daily OHLCV data using yfinance.
    """
    logger.info("Starting market history fetch...")
    stocks = db.query(Stock).all()
    
    total_ticks = 0
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60) # Mandate: 30+ ticks (60 days ensures this)
    
    for stock in stocks:
        ticker_jk = f"{stock.ticker}.JK"
        try:
            df = yf.download(ticker_jk, start=start_date, end=end_date, interval="1d", progress=False)
            if df.empty:
                continue
                
            ticks_added = 0
            for index, row in df.iterrows():
                # check if tick already exists
                existing = db.query(PriceTick).filter(
                    PriceTick.stock_id == stock.id,
                    PriceTick.date == index.date()
                ).first()
                
                if not existing:
                    # Handle Series from yfinance multi-index or single index
                    try:
                        o = float(row['Open'])
                        h = float(row['High'])
                        l = float(row['Low'])
                        c = float(row['Close'])
                        v = int(row['Volume'])
                    except (TypeError, ValueError, KeyError):
                        # Fallback for multi-index DataFrames
                        o = float(row['Open'].iloc[0])
                        h = float(row['High'].iloc[0])
                        l = float(row['Low'].iloc[0])
                        c = float(row['Close'].iloc[0])
                        v = int(row['Volume'].iloc[0])

                    tick = PriceTick(
                        stock_id=stock.id,
                        date=index.date(),
                        open=o,
                        high=h,
                        low=l,
                        close=c,
                        volume=v,
                        value=int(v * c) # approximation
                    )
                    db.add(tick)
                    ticks_added += 1
                    total_ticks += 1
            
            if ticks_added > 0:
                db.commit()
            
            # rate limiting
            time.sleep(0.2)
        except Exception as e:
            logger.error(f"Error fetching history for {stock.ticker}: {str(e)}")
            db.rollback()
            continue
            
    logger.info(f"Market history fetch completed. {total_ticks} ticks added.")

def generate_broker_flow_proxy(db: Session):
    """
    Generate synthetic BrokerTransaction records for the last 30 days.
    Logic: For ALL active tickers, generate 3-5 BrokerTransaction entries
    with significant buy_value from top IDX brokers.
    """
    logger.info("Starting broker flow proxy generation for ALL tickers...")
    
    # top IDX brokers
    top_brokers = [
        ('CC', 'Mandiri Sekuritas'),
        ('DH', 'Sinarmas Sekuritas'),
        ('YP', 'Mirae Asset Sekuritas'),
        ('PD', 'Indo Premier Sekuritas'),
        ('LG', 'Trimegah Sekuritas'),
        ('AK', 'UBS Sekuritas'),
        ('NI', 'BNI Sekuritas'),
        ('GR', 'Panin Sekuritas'),
        ('DR', 'RHB Sekuritas'),
        ('BK', 'J.P. Morgan Sekuritas')
    ]
    
    # Get all active stocks
    stocks = db.query(Stock).all()
    
    # get insider buys in last 30 days for value weighting
    cutoff_date = (datetime.now() - timedelta(days=30)).date()
    
    proxies_created = 0
    for stock in stocks:
        # Check if there's an insider buy to use as a base value
        insider_buy = db.query(InsiderTransaction).filter(
            InsiderTransaction.stock_id == stock.id,
            InsiderTransaction.transaction_type == 'BUY',
            InsiderTransaction.date >= cutoff_date
        ).first()

        # Generate for last 5 trading days at least
        for days_back in range(5):
            target_date = (datetime.now() - timedelta(days=days_back)).date()
            
            # number of broker transactions to generate per day
            num_tx = random.randint(3, 5)
            
            # approximate total value to distribute
            if insider_buy:
                total_value = float(insider_buy.value or (insider_buy.shares * insider_buy.price) or 1_000_000_000)
            else:
                total_value = random.uniform(500_000_000, 5_000_000_000)
                
            # Select random brokers
            selected_brokers = random.sample(top_brokers, num_tx)
            
            for broker_code, broker_name in selected_brokers:
                # check if proxy already exists for this stock, date, and broker
                existing = db.query(BrokerTransaction).filter(
                    BrokerTransaction.stock_id == stock.id,
                    BrokerTransaction.date == target_date,
                    BrokerTransaction.broker_code == broker_code
                ).first()
                
                if not existing:
                    # distributed value with some randomness
                    dist_value = int(total_value * random.uniform(0.5, 2.0) / num_tx)
                    
                    # Get recent price for volume calc
                    recent_tick = db.query(PriceTick).filter(PriceTick.stock_id == stock.id).order_by(PriceTick.date.desc()).first()
                    price = recent_tick.close if recent_tick else 500
                    
                    dist_volume = int(dist_value / price)
                    
                    buy_val = dist_value
                    sell_val = random.randint(0, int(dist_value * 0.4)) # Higher variety
                    
                    proxy = BrokerTransaction(
                        stock_id=stock.id,
                        date=target_date,
                        broker_code=broker_code,
                        broker_name=broker_name,
                        buy_volume=dist_volume,
                        sell_volume=int(dist_volume * (sell_val / buy_val)) if buy_val > 0 else 0,
                        buy_value=buy_val,
                        sell_value=sell_val,
                        net_value=buy_val - sell_val
                    )
                    db.add(proxy)
                    proxies_created += 1
                    
        if proxies_created % 50 == 0:
            db.commit()
            
    db.commit()
    logger.info(f"Broker flow proxy generation completed. {proxies_created} transactions created.")
