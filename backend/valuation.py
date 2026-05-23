import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from decimal import Decimal
from .logger import logger

def calculate_event_valuation(ticker: str, event_date: datetime.date, target_ticker: Optional[str] = None) -> Dict[str, Any]:
    """
    Computes deterministic valuation multiples and premium metrics for Track B.
    Strictly uses yfinance for real-world metrics. No hallucinated data.
    """
    valuation_data = {
        "pe_multiple": None,
        "pb_multiple": None,
        "ev_ebitda": None,
        "premium_1d": None,
    }

    try:
        # Fetch target details using yfinance
        active_ticker = target_ticker if target_ticker else ticker
        if not active_ticker:
            return valuation_data

        yf_ticker = f"{active_ticker}.JK"
        stock = yf.Ticker(yf_ticker)
        info = stock.info

        # Multiples
        pe = info.get("trailingPE")
        pb = info.get("priceToBook")
        ev_ebitda = info.get("enterpriseToEbitda")

        if pe: valuation_data["pe_multiple"] = Decimal(str(pe))
        if pb: valuation_data["pb_multiple"] = Decimal(str(pb))
        if ev_ebitda: valuation_data["ev_ebitda"] = Decimal(str(ev_ebitda))

        # Calculate 1-Day Premium (relative to unaffected share price 1 day before event)
        unaffected_date = event_date - timedelta(days=1)
        # Avoid weekends
        if unaffected_date.weekday() == 5: # Saturday
            unaffected_date -= timedelta(days=1)
        elif unaffected_date.weekday() == 6: # Sunday
            unaffected_date -= timedelta(days=2)

        hist = stock.history(start=unaffected_date.strftime("%Y-%m-%d"), end=event_date.strftime("%Y-%m-%d"))
        if not hist.empty and len(hist) > 0:
            unaffected_close = hist["Close"].iloc[0]
            current_price = info.get("currentPrice") or info.get("previousClose")
            if unaffected_close and current_price and unaffected_close > 0:
                premium = (current_price - unaffected_close) / unaffected_close
                valuation_data["premium_1d"] = Decimal(str(round(premium, 4)))

    except Exception as e:
        logger.error(f"Error calculating valuation for {ticker}: {e}")

    return valuation_data
