from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import InsiderTransaction, SmartMoneyScore
from .logger import logger

def link_pre_event_anomalies(db: Session, ticker: str, event_date: datetime.date) -> dict:
    """
    Computes trailing accumulation for Track B/C convergence linkages.
    Queries the database for historical 60-day insider volume and scores.
    """
    metrics = {
        "pre_event_insider_volume": 0.0,
        "pre_event_smart_money_score": 0
    }

    try:
        start_date = event_date - timedelta(days=60)

        # 1. Fetch Trailing Insider Buy Volume (60d)
        insider_vol = db.query(func.sum(InsiderTransaction.shares)).filter(
            InsiderTransaction.ticker == ticker,
            InsiderTransaction.transaction_type == "BUY",
            InsiderTransaction.date >= start_date,
            InsiderTransaction.date < event_date
        ).scalar()

        if insider_vol:
            metrics["pre_event_insider_volume"] = float(insider_vol)

        # 2. Fetch Latest Smart Money Score prior to the event
        latest_score = db.query(SmartMoneyScore).filter(
            SmartMoneyScore.stock.has(ticker=ticker),
            func.date(SmartMoneyScore.scored_at) < event_date
        ).order_by(SmartMoneyScore.scored_at.desc()).first()

        if latest_score:
            metrics["pre_event_smart_money_score"] = latest_score.score_total

    except Exception as e:
        logger.error(f"Error computing convergence for {ticker}: {e}")

    return metrics
