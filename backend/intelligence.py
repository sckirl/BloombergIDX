from sqlalchemy.orm import Session
from sqlalchemy import func, case, text
from .models import Stock, PriceTick, BrokerTransaction, InsiderTransaction, Entity, SmartMoneyScore
from datetime import datetime, timedelta
import json

from .utils import sanitize_float

def calculate_momentum(db: Session, ticker: str, days: int = 20):
    """
    MOMENTUM-01: Momentum convergence detector.
    Combines Price Momentum, Volume Trend, and Broker Flow Trend.
    """
    stock = db.query(Stock).filter(Stock.ticker == ticker.upper()).first()
    if not stock:
        return {"status": "insufficient_data", "ticker": ticker.upper()}

    # 1. Price Momentum (Current Price / SMA20)
    latest_tick = db.query(PriceTick).filter(PriceTick.stock_id == stock.id).order_by(PriceTick.date.desc()).first()
    if not latest_tick:
        return {"status": "insufficient_data", "ticker": ticker.upper()}

    sma_res = db.query(func.avg(PriceTick.close)).filter(
        PriceTick.stock_id == stock.id,
        PriceTick.date >= (datetime.now() - timedelta(days=days)).date()
    ).scalar()
    
    price_momentum = sanitize_float(latest_tick.close / sma_res) if sma_res else 1.0

    # 2. Volume Trend (Current Volume / Avg Volume)
    avg_vol = float(stock.avg_volume or 1)
    vol_trend = sanitize_float(latest_tick.volume / avg_vol)

    # 3. Broker Flow Trend (Net Flow last 5 days vs last 20 days)
    five_days_ago = (datetime.now() - timedelta(days=5)).date()
    twenty_days_ago = (datetime.now() - timedelta(days=20)).date()

    net_5d = db.query(func.sum(BrokerTransaction.net_value)).filter(
        BrokerTransaction.stock_id == stock.id,
        BrokerTransaction.date >= five_days_ago
    ).scalar() or 0

    net_20d = db.query(func.sum(BrokerTransaction.net_value)).filter(
        BrokerTransaction.stock_id == stock.id,
        BrokerTransaction.date >= twenty_days_ago
    ).scalar() or 0

    flow_trend = sanitize_float(net_5d / (abs(net_20d / 4) + 1)) # Normalized

    # Convergence Score
    convergence = (price_momentum * 0.4) + (min(vol_trend, 3.0) * 0.3) + (min(max(flow_trend, -2.0), 2.0) * 0.3)

    return {
        "ticker": ticker.upper(),
        "price_momentum": round(sanitize_float(price_momentum), 4),
        "vol_trend": round(sanitize_float(vol_trend), 4),
        "flow_trend": round(sanitize_float(flow_trend), 4),
        "convergence_score": round(sanitize_float(convergence), 4),
        "signal": "BULLISH" if convergence > 1.2 else "BEARISH" if convergence < 0.8 else "NEUTRAL",
        "status": "success"
    }

def detect_bandar_activity(db: Session, ticker: str):
    """
    BANDAR-PROXY-01: Bandar (market-maker) detection rules.
    - Broker concentration
    - Stealth accumulation (Price flat, Net Flow high)
    - Cross-trade detection (Not implemented in this simple version, but placeholder)
    """
    stock = db.query(Stock).filter(Stock.ticker == ticker.upper()).first()
    if not stock:
        return {"status": "insufficient_data", "ticker": ticker.upper()}

    # 1. Broker Concentration (Herfindahl-Hirschman Index proxy for top 5)
    top_5_buyers = db.query(
        BrokerTransaction.broker_code,
        func.sum(BrokerTransaction.net_value).label("net_val")
    ).filter(
        BrokerTransaction.stock_id == stock.id,
        BrokerTransaction.net_value > 0,
        BrokerTransaction.date >= (datetime.now() - timedelta(days=14)).date()
    ).group_by(BrokerTransaction.broker_code).order_by(text("net_val DESC")).limit(5).all()

    total_buy_net = db.query(func.sum(BrokerTransaction.net_value)).filter(
        BrokerTransaction.stock_id == stock.id,
        BrokerTransaction.net_value > 0,
        BrokerTransaction.date >= (datetime.now() - timedelta(days=14)).date()
    ).scalar() or 1

    concentration = sanitize_float(sum(float(b.net_val) for b in top_5_buyers) / float(total_buy_net))

    # 2. Stealth Accumulation
    # Price change last 10 days < 5% AND Net Flow > 2x Avg Daily Value
    latest_tick = db.query(PriceTick).filter(PriceTick.stock_id == stock.id).order_by(PriceTick.date.desc()).first()
    ten_days_ago_tick = db.query(PriceTick).filter(
        PriceTick.stock_id == stock.id,
        PriceTick.date <= (datetime.now() - timedelta(days=10)).date()
    ).order_by(PriceTick.date.desc()).first()

    stealth_flag = False
    if latest_tick and ten_days_ago_tick:
        price_change = abs(sanitize_float((latest_tick.close - ten_days_ago_tick.close) / float(ten_days_ago_tick.close)))
        
        net_flow_10d = db.query(func.sum(BrokerTransaction.net_value)).filter(
            BrokerTransaction.stock_id == stock.id,
            BrokerTransaction.date >= (datetime.now() - timedelta(days=10)).date()
        ).scalar() or 0
        
        avg_daily_value = float(stock.avg_volume or 1) * float(latest_tick.close or 1)
        
        if price_change < 0.05 and net_flow_10d > (avg_daily_value * 0.5):
            stealth_flag = True

    return {
        "ticker": ticker.upper(),
        "concentration_score": round(sanitize_float(concentration), 4),
        "stealth_accumulation": stealth_flag,
        "bandar_detected": concentration > 0.7 or stealth_flag,
        "confidence": 0.85 if concentration > 0.8 else 0.6,
        "status": "success"
    }


def get_entity_intelligence(db: Session, name: str):
    """
    ENTITY-MAP-01: Entity resolution and PEP flagging.
    """
    entity = db.query(Entity).filter(
        (Entity.canonical_name.ilike(f"%{name}%")) | (Entity.name_variants.ilike(f"%{name}%"))
    ).first()
    
    if entity:
        return {
            "name": entity.canonical_name,
            "type": entity.entity_type,
            "pep_flag": entity.pep_flag,
            "notes": entity.notes,
            "related": json.loads(entity.related_entities) if entity.related_entities else []
        }
    
    # Heuristic for PEP detection if not in DB
    pep_keywords = ["MINISTER", "DPR", "PRESIDENT", "POLITICIAN", "GOVERNOR"]
    is_likely_pep = any(kw in name.upper() for kw in pep_keywords)
    
    return {
        "name": name,
        "type": "UNKNOWN",
        "pep_flag": is_likely_pep,
        "notes": "Heuristic detection" if is_likely_pep else "No intelligence found",
        "related": []
    }
