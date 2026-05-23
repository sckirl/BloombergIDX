from typing import Dict, Any, List, Tuple
import datetime
import json

def sanitize_float(val: Any) -> float:
    """
    Ensures a value is a valid float for JSON serialization.
    Returns 0.0 for NaN, Inf, or -Inf.
    """
    if val is None:
        return 0.0
    try:
        f_val = float(val)
        if f_val != f_val or f_val == float('inf') or f_val == float('-inf'):
            return 0.0
        return f_val
    except (ValueError, TypeError):
        return 0.0

def normalize_role(role_str: str) -> str:
    if not role_str:
        return "OTHERS"
    role_str = role_str.upper()
    if any(x in role_str for x in ["PRESIDEN DIREKTUR", "DIREKTUR UTAMA", "CEO"]):
        return "DIREKTUR_UTAMA"
    if "DIREKTUR" in role_str:
        return "DIREKTUR"
    if any(x in role_str for x in ["PRESIDEN KOMISARIS", "KOMISARIS UTAMA"]):
        return "KOMISARIS_UTAMA"
    if "KOMISARIS" in role_str:
        return "KOMISARIS"
    if any(x in role_str for x in ["PENGENDALI"]):
        return "PENGENDALI"
    if any(x in role_str for x in ["UTAMA"]):
        return "PEMEGANG_SAHAM_UTAMA"
    return "OTHERS"

from .logger import logger
import time

def get_market_metadata(ticker: str) -> Dict[str, Any]:
    """
    Fetch market data (RVOL and Price History) for a ticker via yfinance.
    """
    import yfinance as yf
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # IDX tickers need .JK suffix
            symbol = f"{ticker.upper()}.JK"
            stock = yf.Ticker(symbol)
            
            # Get history for the last 30 days to calculate 20-day average volume
            hist = stock.history(period="1mo")
            if hist.empty:
                return {"rvol": 1.0, "price_history": []}
                
            # 20-day average volume
            avg_vol_20 = hist['Volume'].tail(20).mean()
            current_vol = hist['Volume'].iloc[-1]
            rvol = current_vol / avg_vol_20 if avg_vol_20 > 0 else 1.0
            
            # Last 5 days close prices
            price_history = hist['Close'].tail(5).tolist()
            
            return {
                "rvol": float(round(rvol, 2)),
                "price_history": [float(round(p, 2)) for p in price_history]
            }
        except Exception as e:
            logger.error(f"Error fetching market data for {ticker} (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt) # Exponential backoff
    return {"rvol": 1.0, "price_history": []}

def get_30d_adv(ticker: str) -> Tuple[float, float]:
    """
    Fetch 30-day Average Daily Volume (ADV) and Current Price for a ticker.
    Returns (30d_adv, current_price)
    """
    import yfinance as yf
    max_retries = 3
    for attempt in range(max_retries):
        try:
            symbol = f"{ticker.upper()}.JK"
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1mo")
            if hist.empty:
                return 0.0, 0.0
            
            adv = hist['Volume'].mean()
            current_price = hist['Close'].iloc[-1]
            return float(adv), float(current_price)
        except Exception as e:
            logger.error(f"Error fetching ADV for {ticker} (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return 0.0, 0.0

def get_insider_stats_for_absorption(ticker: str, db) -> Dict[str, Any]:
    """
    Calculate total shares bought by insiders in the last 90 days.
    """
    from .models import InsiderTransaction
    from sqlalchemy import func
    import datetime
    
    ninety_days_ago = datetime.date.today() - datetime.timedelta(days=90)
    
    stats = db.query(
        func.sum(InsiderTransaction.shares).label("total_shares"),
        func.count(InsiderTransaction.id).label("transaction_count")
    ).filter(
        InsiderTransaction.ticker == ticker,
        InsiderTransaction.transaction_type == "BUY",
        InsiderTransaction.date >= ninety_days_ago
    ).first()
    
    return {
        "total_shares": float(stats.total_shares or 0),
        "transaction_count": int(stats.transaction_count or 0)
    }

def get_price_on_date(ticker: str, date: datetime.date) -> float:
    """
    Fetch the historical closing price of a stock on a specific date using yfinance.
    Enhanced with better fallbacks for weekend/holiday dates and retries.
    """
    import yfinance as yf
    if not ticker or ticker == "UNKNOWN":
        return 0.0
        
    symbol = f"{ticker.upper()}.JK"
    max_retries = 3
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(symbol)
            
            # Fetch history for a small range around the target date
            start_date = date - datetime.timedelta(days=7)
            end_date = date + datetime.timedelta(days=2)
            hist = stock.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
            
            if hist.empty:
                # Try fetching a larger range if empty
                hist = stock.history(period="1mo")
                if hist.empty: return 0.0
                
            # Get the latest price before or on the target date
            valid_hist = hist[hist.index.date <= date]
            if not valid_hist.empty:
                return float(valid_hist['Close'].iloc[-1])
            
            # If no price before, take the first available price (after)
            return float(hist['Close'].iloc[0])
        except Exception as e:
            logger.error(f"Error fetching price for {ticker} on {date} (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return 0.0

def calculate_ownership_change(before: float, after: float) -> float:
    """
    Calculates the percentage change in ownership.
    """
    if not before or before == 0:
        return 0.0
    try:
        change = ((after - before) / before) * 100
        return float(round(change, 4))
    except:
        return 0.0

def calculate_confidence(transaction: Dict[str, Any]) -> float:
    """
    Calculates a confidence score (0.0 to 1.0) based on data source and parsing quality.
    (VALID-01: Truth Hierarchy)
    """
    confidence = 1.0
    
    # 1. Source Hierarchy
    source_url = transaction.get("source_url", "")
    if "idx.co.id" in source_url:
        confidence *= 1.0 # Official IDX
    elif "ksei.co.id" in source_url:
        confidence *= 0.9 # Official KSEI (often slightly delayed/different format)
    else:
        confidence *= 0.5 # Unknown/Third-party
        
    # 2. Field Completeness
    required_fields = ["shares", "price", "date", "insider_name"]
    missing = [f for f in required_fields if not transaction.get(f)]
    if missing:
        confidence *= (1.0 - (0.2 * len(missing)))
        
    # 3. Inference Penalties
    if transaction.get("date_inferred", False):
        confidence *= 0.8
        
    # 4. Value Sanity
    price = float(transaction.get("price") or 0)
    if price <= 0:
        confidence *= 0.5
        
    return float(round(max(0.0, confidence), 2))

def calculate_score(transaction: Dict[str, Any], db=None, context: Dict[str, Any] = None) -> Tuple[int, List[str]]:
    """
    Implements the Smart Scoring System with reason breakdown.
    Optional context dictionary can be used to avoid N+1 DB queries.
    """
    score = 0
    reasons = []
    t_type = str(transaction.get("transaction_type", "BUY")).upper()
    role = normalize_role(transaction.get("role", ""))
    value = float(transaction.get("value") or 0)
    ticker = transaction.get("ticker", "")
    t_date = transaction.get("date")

    if t_type in ["GIFT", "INHERITANCE", "BONUS", "DIVIDEND", "SPLIT", "REVERSE_SPLIT", "REPO"]:
        return 0, [f"{t_type.capitalize()} (0)"]

    if t_type in ["BUY", "EXERCISE"]:
        # Role Weight
        role_weights = {
            "DIREKTUR_UTAMA": 5,
            "KOMISARIS_UTAMA": 4,
            "DIREKTUR": 3,
            "PENGENDALI": 3,
            "KOMISARIS": 2,
            "PEMEGANG_SAHAM_UTAMA": 1,
            "OTHERS": 0
        }
        r_weight = role_weights.get(role, 0)
        if r_weight > 0:
            score += r_weight
            reasons.append(f"{role.replace('_', ' ')} Buy (+{r_weight})")
        
        if t_type == "EXERCISE":
            score += 1
            reasons.append("Option Exercise (+1)")

        # Value Weight
        if value >= 10_000_000_000:
            score += 5
            reasons.append("Ultra Large Value (+5)")
        elif value >= 5_000_000_000:
            score += 4
            reasons.append("Very Large Value (+4)")
        elif value >= 1_000_000_000:
            score += 3
            reasons.append("Large Value (+3)")
        elif value >= 500_000_000:
            score += 2
            reasons.append("Significant Value (+2)")
        elif value >= 100_000_000:
            score += 1
            reasons.append("Standard Value (+1)")
        
        # Bonus Modifiers
        if transaction.get("direct_ownership", True):
            score += 1
            reasons.append("Direct Ownership (+1)")
            
        ownership_pct = transaction.get("ownership_change_pct") or 0
        if ownership_pct > 10.0:
            score += 2
            reasons.append("Significant Stake Increase >10% (+2)")
        
        # Double-Conviction (Buyback)
        if transaction.get("is_buyback", False):
            score += 3
            reasons.append("Double-Conviction: Coincides with Buyback (+3)")
            
        # RVOL Modifiers (Volume Sigma)
        rvol = transaction.get("rvol") or 1.0
        if rvol >= 3.0:
            score += 4
            reasons.append(f"Extreme Volume Sigma {rvol}x (+4)")
        elif rvol >= 2.0:
            score += 2
            reasons.append(f"Significant Volume Sigma {rvol}x (+2)")
        
        # Repeated Buyer Logic
        prev_buys = context.get("previous_buys_count") if context else None
        if prev_buys is None and db and ticker and t_date:
            from .models import InsiderTransaction
            thirty_days_ago = t_date - datetime.timedelta(days=30)
            prev_buys = db.query(InsiderTransaction).filter(
                InsiderTransaction.ticker == ticker,
                InsiderTransaction.insider_name == transaction.get("insider_name"),
                InsiderTransaction.transaction_type == "BUY",
                InsiderTransaction.date >= thirty_days_ago,
                InsiderTransaction.date < t_date
            ).count()
            
        if prev_buys:
            if prev_buys >= 2:
                score += 3
                reasons.append(f"Repeated Buyer: {prev_buys + 1}th buy in 30d (+3)")
            elif prev_buys == 1:
                score += 1
                reasons.append("Follow-on Accumulation (+1)")

        # Cluster Buy Logic (BUY or EXERCISE)
        cluster_count = context.get("other_insiders_count") if context else None
        if cluster_count is None and db and ticker and t_date:
            from .models import InsiderTransaction
            seven_days_ago = t_date - datetime.timedelta(days=7)
            cluster_count = db.query(InsiderTransaction.insider_name).filter(
                InsiderTransaction.ticker == ticker,
                InsiderTransaction.transaction_type.in_(["BUY", "EXERCISE"]),
                InsiderTransaction.date >= seven_days_ago,
                InsiderTransaction.date <= t_date,
                InsiderTransaction.insider_name != transaction.get("insider_name")
            ).distinct().count()
            
        total_insiders = (cluster_count or 0) + 1
        if total_insiders >= 3:
            score += 5
            reasons.append(f"Strong Cluster: {total_insiders} Insiders (+5)")
        elif total_insiders == 2:
            score += 3
            reasons.append("Small Cluster: 2 Insiders (+3)")
            
    elif t_type == "SELL":
        score -= 2
        reasons.append("Insider Sell (-2)")
        if role in ["DIREKTUR_UTAMA", "PENGENDALI"]:
            score -= 1
            reasons.append("Key Management Sell (-1)")
        if value >= 5_000_000_000:
            score -= 2
            reasons.append("Large Value Sell (-2)")

    return score, reasons
