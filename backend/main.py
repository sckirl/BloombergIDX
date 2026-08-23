from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import asyncio
from datetime import datetime, timezone, timedelta, date
import threading
from decimal import Decimal

from .logger import logger
from .database import get_db, engine, SessionLocal, settings
from .models import InsiderTransaction, Base
from . import models
from .scraper import run_scraper
from .utils import (
    normalize_role, 
    calculate_score, 
    get_30d_adv, 
    get_insider_stats_for_absorption,
    sanitize_float
)
from .market_scraper import enrich_stock_metadata, fetch_market_history, generate_broker_flow_proxy
from .market_indices import get_real_market_indices

import os

app = FastAPI(title="IDX OpenInsider API")
from .narrative_api import router as narrative_router
app.include_router(narrative_router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Terminal Error", "detail": str(exc) if os.getenv("DEBUG") else "An unexpected error occurred."},
    )

# Add CORS middleware to allow requests from the frontend
origins = settings.ALLOWED_ORIGINS.split(",")
if "*" in origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

# Global lock for scraper to prevent concurrent runs
scraper_lock = threading.Lock()

async def run_scraper_async(full_year=False):
    if scraper_lock.locked():
        logger.warning("Scraper is already running. Skipping this trigger.")
        return
    
    try:
        logger.info(f"Background Task: Running scraper (full_year={full_year})...")
        with scraper_lock:
            await asyncio.to_thread(run_scraper, full_year=full_year)
        logger.info("Background Task: Scraper finished.")
    except Exception as e:
        logger.error(f"Background Task Error: {e}", exc_info=True)

async def daily_scheduler():
    import random
    while True:
        now_wib = datetime.now(timezone(timedelta(hours=7)))
        # Random hour between 1 and 4 (inclusive), random minute between 0 and 59
        random_hour = random.randint(1, 4)
        random_minute = random.randint(0, 59)
        
        target_time = now_wib.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
        if now_wib >= target_time:
            target_time += timedelta(days=1)
        
        wait_seconds = (target_time - now_wib).total_seconds()
        logger.info(f"Scheduler: Next run at {target_time} (WIB), waiting {wait_seconds} seconds.")
        
        await asyncio.sleep(wait_seconds)
        await run_scraper_async()

@app.on_event("startup")
async def startup_event():
    logger.info("Startup: Triggering daily scheduler...")
    asyncio.create_task(daily_scheduler())
    # Seed entities
    from .seed_entities import seed_entities
    seed_entities()

@app.get("/health")
def health_check():
    try:
        # Check DB connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected", "timestamp": datetime.now()}
    except Exception as e:
        return {"status": "degraded", "database": str(e), "timestamp": datetime.now()}

@app.get("/")
def read_root():
    return {"message": "Welcome to IDX OpenInsider API", "status": "running"}

@app.get("/insider/scraper-status")
def get_scraper_status():
    return {"is_running": scraper_lock.locked(), "timestamp": datetime.now()}

@app.get("/insider/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks, full_year: bool = False):
    if scraper_lock.locked():
        return {"message": "Scraper is already running", "status": "busy"}
    
    background_tasks.add_task(run_scraper_async, full_year=full_year)
    return {"message": f"Scraper task (full_year={full_year}) triggered"}

@app.get("/insider/enrich")
async def trigger_enrich(background_tasks: BackgroundTasks):
    """
    Triggers market metadata enrichment, price history fetching, 
    and synthetic broker flow generation.
    """
    def run_enrichment():
        db_session = SessionLocal()
        try:
            logger.info("Starting background enrichment process...")
            enrich_stock_metadata(db_session)
            fetch_market_history(db_session)
            generate_broker_flow_proxy(db_session)
            
            # Invalidate caches
            invalidate_cache("market_heatmap")
            invalidate_cache("market_anomalies")
            logger.info("Background enrichment process completed.")
        except Exception as e:
            logger.error(f"Enrichment process failed: {e}", exc_info=True)
        finally:
            db_session.close()

    background_tasks.add_task(run_enrichment)
    return {"message": "Market enrichment tasks triggered in background"}

def to_dict(obj):
    """Convert SQLAlchemy model instance to dict with Decimal -> float conversion and NaN/Inf sanitation."""
    d = {}
    for column in obj.__table__.columns:
        val = getattr(obj, column.name)
        if isinstance(val, Decimal):
            d[column.name] = sanitize_float(val)
        elif isinstance(val, (datetime, date)):
            d[column.name] = val.isoformat()
        elif isinstance(val, float):
            d[column.name] = sanitize_float(val)
        else:
            d[column.name] = val
    return d

from .cache import get_cache, set_cache, invalidate_cache
from .intelligence import calculate_momentum, detect_bandar_activity, get_entity_intelligence

@app.get("/insider/momentum/{ticker}")
def get_momentum_api(ticker: str, db: Session = Depends(get_db)):
    data = calculate_momentum(db, ticker)
    # Institutional Mandate: Always return 200, use status field for data availability
    return data

@app.get("/insider/bandar/{ticker}")
def get_bandar_api(ticker: str, db: Session = Depends(get_db)):
    data = detect_bandar_activity(db, ticker)
    # Institutional Mandate: Always return 200, use status field for data availability
    return data

@app.get("/insider/entity/{name}")
def get_entity_api(name: str, db: Session = Depends(get_db)):
    return get_entity_intelligence(db, name)

@app.get("/insider/latest", response_model=List[Dict[str, Any]])
def get_latest_insiders(ticker: str = None, db: Session = Depends(get_db)):
    cache_key = f"insider_latest_{ticker}" if ticker else "insider_latest"
    cached = get_cache(cache_key)
    if cached: return cached

    try:
        query = db.query(InsiderTransaction)
        if ticker:
            query = query.filter(InsiderTransaction.ticker == ticker.upper())
        
        transactions = query.order_by(InsiderTransaction.filing_date.desc()).limit(1000).all()
        result = [to_dict(t) for t in transactions]
        
        set_cache(cache_key, result, ttl=60) # 1 minute cache for feed
        return result
    except Exception as e:
        logger.error(f"Error fetching latest insiders: {e}")
        return []

@app.get("/insider/top-buy", response_model=List[Dict[str, Any]])
def get_top_buys(db: Session = Depends(get_db)):
    cached = get_cache("insider_top_buy")
    if cached: return cached
    
    transactions = db.query(InsiderTransaction).filter(InsiderTransaction.transaction_type == "BUY").order_by(InsiderTransaction.score.desc()).limit(50).all()
    result = [to_dict(t) for t in transactions]
    set_cache("insider_top_buy", result, ttl=300)
    return result

@app.get("/insider/top-sell", response_model=List[Dict[str, Any]])
def get_top_sells(db: Session = Depends(get_db)):
    cached = get_cache("insider_top_sell")
    if cached: return cached

    transactions = db.query(InsiderTransaction).filter(InsiderTransaction.transaction_type == "SELL").order_by(InsiderTransaction.score.asc()).limit(50).all()
    result = [to_dict(t) for t in transactions]
    set_cache("insider_top_sell", result, ttl=300)
    return result

@app.get("/insider/clusters")
def get_insider_clusters(
    min_insiders: int = 2, 
    max_insiders: int = 100, 
    days: int = 30, 
    db: Session = Depends(get_db)
):
    """
    Identifies 'Cluster Buys' where multiple unique insiders are buying 
    the same ticker within a rolling window.
    """
    cache_key = f"insider_clusters_{days}_{min_insiders}"
    cached = get_cache(cache_key)
    if cached: return cached

    cutoff_date = datetime.now().date() - timedelta(days=days)
    
    # 1. Fetch all buys in the window
    buys = db.query(InsiderTransaction).filter(
        InsiderTransaction.transaction_type == "BUY",
        InsiderTransaction.date >= cutoff_date
    ).all()
    
    # 2. Group by ticker
    from collections import defaultdict
    ticker_groups = defaultdict(list)
    for b in buys:
        ticker_groups[b.ticker].append(b)
        
    # 3. Analyze unique insiders per ticker
    clusters = []
    for ticker, transactions in ticker_groups.items():
        unique_insiders = set(t.insider_name for t in transactions)
        count = len(unique_insiders)
        
        if min_insiders <= count <= max_insiders:
            # Sort transactions by date
            transactions.sort(key=lambda x: x.date, reverse=True)
            
            clusters.append({
                "ticker": ticker,
                "insider_count": count,
                "transaction_count": len(transactions),
                "last_date": transactions[0].date.isoformat(),
                "total_value": float(sum(t.value for t in transactions)),
                "insiders": list(unique_insiders),
                "activity": [to_dict(t) for t in transactions]
            })
            
    # Sort clusters by insider count (high to low)
    clusters.sort(key=lambda x: x["insider_count"], reverse=True)
    set_cache(cache_key, clusters, ttl=300)
    return clusters

@app.get("/insider/accumulation/{ticker}")
def get_accumulation_map(ticker: str, db: Session = Depends(get_db)):
    """
    Groups historical insider trades by price and sums up buy/sell shares.
    """
    cache_key = f"insider_acc_map_{ticker.upper()}"
    cached = get_cache(cache_key)
    if cached: return cached

    from sqlalchemy import func
    
    # 1. Fetch transactions for the ticker
    results = db.query(
        InsiderTransaction.price,
        func.sum(InsiderTransaction.shares).label("total_shares"),
        InsiderTransaction.transaction_type
    ).filter(
        InsiderTransaction.ticker == ticker.upper()
    ).group_by(
        InsiderTransaction.price,
        InsiderTransaction.transaction_type
    ).all()
    
    # 2. Format result
    price_map = []
    for price, shares, t_type in results:
        price_map.append({
            "price": float(price or 0),
            "shares": float(shares or 0),
            "type": t_type
        })
    
    # Sort by price descending (top to bottom)
    price_map.sort(key=lambda x: x["price"], reverse=True)
    set_cache(cache_key, price_map, ttl=600)
    return price_map

@app.get("/insider/absorption/{ticker}")
async def get_absorption_ratio(ticker: str, db: Session = Depends(get_db)):
    """
    Calculates the Absorption Ratio: 
    (Total Shares Bought by Insiders / 30-Day Avg Daily Volume)
    """
    cache_key = f"insider_absorption_{ticker.upper()}"
    cached = get_cache(cache_key)
    if cached: return cached

    # 1. Fetch insider stats (last 90 days)
    insider_stats = get_insider_stats_for_absorption(ticker.upper(), db)
    
    # 2. Fetch market volume (30-day ADV)
    adv_30d, current_price = await asyncio.to_thread(get_30d_adv, ticker.upper())
    
    # 3. Calculate ratio
    ratio = 0.0
    if adv_30d > 0:
        ratio = insider_stats["total_shares"] / adv_30d
        
    result = {
        "ticker": ticker.upper(),
        "total_shares_bought": insider_stats["total_shares"],
        "adv_30d": adv_30d,
        "absorption_ratio": float(round(ratio, 4)),
        "current_price": current_price,
        "transaction_count": insider_stats["transaction_count"]
    }
    set_cache(cache_key, result, ttl=600)
    return result

@app.get("/insider/flow/{ticker}")
def get_broker_flow(ticker: str, days: int = 30, db: Session = Depends(get_db)):
    """
    Calculates broker concentration and accumulation flow for a ticker.
    """
    cache_key = f"broker_flow_{ticker.upper()}_{days}"
    cached = get_cache(cache_key)
    if cached: return cached

    from sqlalchemy import func
    from .models import Stock, BrokerTransaction
    
    stock = db.query(Stock).filter(Stock.ticker == ticker.upper()).first()
    if not stock:
        return {"error": "Stock not found"}

    cutoff_date = datetime.now().date() - timedelta(days=days)
    
    # Aggregate transactions by broker
    results = db.query(
        BrokerTransaction.broker_code,
        BrokerTransaction.broker_name,
        func.sum(BrokerTransaction.buy_value).label("total_buy"),
        func.sum(BrokerTransaction.sell_value).label("total_sell"),
        func.sum(BrokerTransaction.net_value).label("total_net")
    ).filter(
        BrokerTransaction.stock_id == stock.id,
        BrokerTransaction.date >= cutoff_date
    ).group_by(
        BrokerTransaction.broker_code,
        BrokerTransaction.broker_name
    ).all()

    brokers = []
    total_net_abs = 0
    for r in results:
        brokers.append({
            "broker_code": r.broker_code,
            "broker_name": r.broker_name,
            "buy_value": int(r.total_buy or 0),
            "sell_value": int(r.total_sell or 0),
            "net_value": int(r.total_net or 0)
        })
        total_net_abs += abs(int(r.total_net or 0))

    # Sort and take top 10
    top_buyers = sorted([b for b in brokers if b["net_value"] > 0], key=lambda x: x["net_value"], reverse=True)[:10]
    top_sellers = sorted([b for b in brokers if b["net_value"] < 0], key=lambda x: x["net_value"])[:10]

    # Concentration Calculation (Top 5 buyers net / Total net of all buyers)
    total_buy_net = sum(b["net_value"] for b in brokers if b["net_value"] > 0)
    top_5_buy_net = sum(b["net_value"] for b in top_buyers[:5])
    concentration = float(round(top_5_buy_net / total_buy_net, 4)) if total_buy_net > 0 else 0.0

    result = {
        "ticker": ticker.upper(),
        "period_days": days,
        "concentration": concentration,
        "top_buyers": top_buyers,
        "top_sellers": top_sellers,
        "summary": {
            "total_brokers": len(brokers),
            "total_buy_value": sum(b["buy_value"] for b in brokers),
            "total_sell_value": sum(b["sell_value"] for b in brokers)
        }
    }
    
    set_cache(cache_key, result, ttl=300)
    return result

@app.get("/insider/anomalies")
def get_anomalies(db: Session = Depends(get_db)):
    """
    Detects volume and price anomalies in the last 7 days.
    """
    cache_key = "market_anomalies"
    cached = get_cache(cache_key)
    if cached: return cached

    from sqlalchemy import func
    from .models import Stock, PriceTick
    
    # 1. Get recent ticks (last 7 days) and historical average (previous 20 days)
    # This is a simplified version. A production version would use more complex SQL.
    
    seven_days_ago = datetime.now().date() - timedelta(days=7)
    
    # Get latest ticks for each stock
    latest_ticks_sub = db.query(
        PriceTick.stock_id,
        func.max(PriceTick.date).label("max_date")
    ).group_by(PriceTick.stock_id).subquery()
    
    latest_ticks = db.query(PriceTick).join(
        latest_ticks_sub, 
        (PriceTick.stock_id == latest_ticks_sub.c.stock_id) & (PriceTick.date == latest_ticks_sub.c.max_date)
    ).all()
    
    anomalies = []
    for tick in latest_ticks:
        stock = db.query(Stock).filter(Stock.id == tick.stock_id).first()
        if not stock: continue
        
        # Calculate 20-day ADV (excluding today)
        adv_20d_res = db.query(func.avg(PriceTick.volume)).filter(
            PriceTick.stock_id == tick.stock_id,
            PriceTick.date < tick.date,
            PriceTick.date >= tick.date - timedelta(days=30)
        ).scalar()
        
        adv_20d = float(adv_20d_res or 0)
        rvol = float(tick.volume / adv_20d) if adv_20d > 0 else 1.0
        
        # Calculate Price Change
        prev_tick = db.query(PriceTick).filter(
            PriceTick.stock_id == tick.stock_id,
            PriceTick.date < tick.date
        ).order_by(PriceTick.date.desc()).first()
        
        price_change = 0.0
        if prev_tick and prev_tick.close > 0:
            price_change = float((tick.close - prev_tick.close) / prev_tick.close)
            
        # Detect Anomaly: RVOL > 3 or |Price Change| > 5%
        if rvol >= 3.0 or abs(price_change) >= 0.05:
            anomalies.append({
                "ticker": stock.ticker,
                "name": stock.name,
                "date": tick.date,
                "close": float(tick.close),
                "volume": int(tick.volume),
                "rvol": float(round(rvol, 2)),
                "price_change": float(round(price_change, 4)),
                "anomaly_score": float(round(rvol * abs(price_change) * 100, 2))
            })
            
    anomalies.sort(key=lambda x: x["anomaly_score"], reverse=True)
    result = anomalies[:50] # Top 50 anomalies
    
    set_cache(cache_key, result, ttl=600)
    return result

@app.get("/insider/heatmap")
def get_heatmap(db: Session = Depends(get_db)):
    """
    Returns sector-wise accumulation data for the heatmap.
    """
    cache_key = "market_heatmap"
    cached = get_cache(cache_key)
    if cached: return cached

    from sqlalchemy import func, case
    from .models import Stock, InsiderTransaction
    
    # Last 30 days of insider activity
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    
    # Query: Sector, Sum(Net Flow)
    # We'll use a CASE statement to handle BUY vs SELL
    sector_flow = db.query(
        Stock.sector,
        func.sum(
            case(
                (InsiderTransaction.transaction_type == "BUY", InsiderTransaction.value),
                (InsiderTransaction.transaction_type == "SELL", -InsiderTransaction.value),
                else_=0
            )
        ).label("net_flow"),
        func.count(InsiderTransaction.id).label("trade_count")
    ).join(Stock, Stock.id == InsiderTransaction.stock_id).filter(
        InsiderTransaction.date >= thirty_days_ago
    ).group_by(Stock.sector).all()
    
    heatmap = []
    for row in sector_flow:
        if not row.sector: continue
        
        # Get top stock in this sector
        top_stock = db.query(
            Stock.ticker,
            func.sum(
                case(
                    (InsiderTransaction.transaction_type == "BUY", InsiderTransaction.value),
                    (InsiderTransaction.transaction_type == "SELL", -InsiderTransaction.value),
                    else_=0
                )
            ).label("stock_net_flow")
        ).join(Stock, Stock.id == InsiderTransaction.stock_id).filter(
            Stock.sector == row.sector,
            InsiderTransaction.date >= thirty_days_ago
        ).group_by(Stock.ticker).order_by(text("stock_net_flow DESC")).first()

        heatmap.append({
            "sector": row.sector,
            "net_flow": float(row.net_flow or 0),
            "trade_count": int(row.trade_count or 0),
            "top_ticker": top_stock.ticker if top_stock else None,
            "sentiment": "BULLISH" if (row.net_flow or 0) > 0 else "BEARISH",
            "avg_52w_high": float(db.query(func.avg(Stock.fifty_two_week_high)).filter(Stock.sector == row.sector).scalar() or 0),
            "avg_52w_low": float(db.query(func.avg(Stock.fifty_two_week_low)).filter(Stock.sector == row.sector).scalar() or 0),
            "avg_volume": float(db.query(func.avg(Stock.avg_volume)).filter(Stock.sector == row.sector).scalar() or 0),
            "total_market_cap": float(db.query(func.sum(Stock.market_cap)).filter(Stock.sector == row.sector).scalar() or 0),
        })
        
    heatmap.sort(key=lambda x: abs(x["net_flow"]), reverse=True)
    set_cache(cache_key, heatmap, ttl=900)
    return heatmap

@app.get("/insider/watchlist-data")
def get_watchlist_data(tickers: str, db: Session = Depends(get_db)):
    """
    Returns latest market data for a list of tickers.
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if not ticker_list:
        return []

    from .models import Stock, PriceTick
    
    result = []
    for ticker in ticker_list:
        stock = db.query(Stock).filter(Stock.ticker == ticker).first()
        if not stock:
            continue
            
        # Get latest tick
        latest_tick = db.query(PriceTick).filter(PriceTick.stock_id == stock.id).order_by(PriceTick.date.desc()).first()
        
        # Get previous tick for change calculation
        prev_tick = None
        if latest_tick:
            prev_tick = db.query(PriceTick).filter(
                PriceTick.stock_id == stock.id,
                PriceTick.date < latest_tick.date
            ).order_by(PriceTick.date.desc()).first()

        # Get insider stats
        insider_buy_count = db.query(InsiderTransaction).filter(
            InsiderTransaction.stock_id == stock.id,
            InsiderTransaction.transaction_type == 'BUY',
            InsiderTransaction.date >= (datetime.now() - timedelta(days=30)).date()
        ).count()

        change_pct = 0.0
        if latest_tick and prev_tick and prev_tick.close > 0:
            change_pct = float((latest_tick.close - prev_tick.close) / prev_tick.close)

        result.append({
            "ticker": ticker,
            "price": float(latest_tick.close) if latest_tick else 0.0,
            "change_pct": float(round(change_pct * 100, 2)),
            "insider_buy_level": "HIGH" if insider_buy_count > 5 else "MED" if insider_buy_count > 1 else "LOW",
            "smart_flow": "BULLISH" if insider_buy_count > 2 else "NEUTRAL", # Simplified proxy
            "signal": "BUY" if insider_buy_count > 3 else "ACCUM" if insider_buy_count > 0 else "WATCH",
            "fifty_two_week_high": float(stock.fifty_two_week_high or 0),
            "fifty_two_week_low": float(stock.fifty_two_week_low or 0),
            "avg_volume": int(stock.avg_volume or 0),
            "trailing_pe": float(stock.trailing_pe or 0),
            "price_to_book": float(stock.price_to_book or 0)
        })
        
    return result

@app.get("/insider/events")
def get_corporate_events(db: Session = Depends(get_db)):
    """
    Returns high-conviction corporate events (E-IPO, Mergers).
    """
    from .models import CorporateEvent
    events = db.query(CorporateEvent).order_by(CorporateEvent.event_date.desc()).all()
    return events

@app.get("/insider/enrich")
async def trigger_enrichment(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Triggers market data enrichment: metadata, history, broker flow proxies, and events.
    """
    from .market_scraper import enrich_stock_metadata, fetch_market_history, generate_broker_flow_proxy
    from .market_indices import get_real_market_indices
    from .event_scraper import seed_initial_events
    
    def run_enrichment():
        db_session = SessionLocal()
        try:
            logger.info("Starting background enrichment process...")
            enrich_stock_metadata(db_session)
            fetch_market_history(db_session)
            generate_broker_flow_proxy(db_session)
            seed_initial_events() # Uses SessionLocal inside
            logger.info("Market enrichment background task completed.")
        except Exception as e:
            logger.error(f"Enrichment background task failed: {e}")
        finally:
            db_session.close()

    background_tasks.add_task(run_enrichment)
    return {"message": "Market enrichment task triggered"}

@app.get("/insider/market-indices")
def get_market_indices_api():
    return get_real_market_indices()
