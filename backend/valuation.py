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
        active_ticker = (target_ticker if target_ticker else ticker or "").strip().upper()
        if not active_ticker:
            return valuation_data

        yf_ticker = f"{active_ticker}.JK"
        stock = yf.Ticker(yf_ticker)
        info = stock.info or {}

        # Multiples
        pe = info.get("trailingPE") or info.get("forwardPE")
        pb = info.get("priceToBook")
        ev_ebitda = info.get("enterpriseToEbitda")

        if pe is not None:
            valuation_data["pe_multiple"] = Decimal(str(round(float(pe), 2)))
        if pb is not None:
            valuation_data["pb_multiple"] = Decimal(str(round(float(pb), 2)))
        if ev_ebitda is not None:
            valuation_data["ev_ebitda"] = Decimal(str(round(float(ev_ebitda), 2)))

        # Calculate 1-Day Premium (relative to unaffected share price 1 day before event)
        hist = stock.history(period="5d")
        if not hist.empty and len(hist) >= 2:
            unaffected_close = float(hist["Close"].iloc[-2])
            current_price = float(hist["Close"].iloc[-1])
            if unaffected_close > 0:
                premium = (current_price - unaffected_close) / unaffected_close
                valuation_data["premium_1d"] = Decimal(str(round(premium, 4)))
        elif not hist.empty and len(hist) == 1:
            prev_close = info.get("previousClose")
            curr_price = float(hist["Close"].iloc[0])
            if prev_close and prev_close > 0:
                premium = (curr_price - prev_close) / prev_close
                valuation_data["premium_1d"] = Decimal(str(round(premium, 4)))

    except Exception as e:
        logger.error(f"Error calculating valuation for {ticker}: {e}")

    return valuation_data
