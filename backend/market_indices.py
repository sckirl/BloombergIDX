import yfinance as yf
from .cache import get_cache, set_cache

def get_real_market_indices():
    cache_key = "real_market_indices"
    cached = get_cache(cache_key)
    if cached:
        return cached

    # ^JKSE = IHSG, IDR=X = USD/IDR
    tickers = ["^JKSE", "IDR=X"]
    data = {"ihsg": 0.0, "ihsgChg": 0.0, "usdidr": 0.0, "usdidrChg": 0.0}
    try:
        # We try to get today's and yesterday's to calculate change
        hist = yf.download(tickers, period="5d", progress=False) # Increased period to be safer with weekends
        
        def sanitize_float(v):
            try:
                fv = float(v)
                if fv != fv or fv == float('inf') or fv == float('-inf'):
                    return 0.0
                return fv
            except:
                return 0.0

        # IHSG
        if "^JKSE" in hist["Close"]:
            jkse_closes = hist["Close"]["^JKSE"].dropna()
            if len(jkse_closes) >= 2:
                data["ihsg"] = sanitize_float(jkse_closes.iloc[-1])
                data["ihsgChg"] = sanitize_float(round(((jkse_closes.iloc[-1] - jkse_closes.iloc[-2]) / jkse_closes.iloc[-2]) * 100, 2))
            elif len(jkse_closes) == 1:
                data["ihsg"] = sanitize_float(jkse_closes.iloc[-1])

        # USDIDR
        if "IDR=X" in hist["Close"]:
            idr_closes = hist["Close"]["IDR=X"].dropna()
            if len(idr_closes) >= 2:
                data["usdidr"] = sanitize_float(idr_closes.iloc[-1])
                data["usdidrChg"] = sanitize_float(round(((idr_closes.iloc[-1] - idr_closes.iloc[-2]) / idr_closes.iloc[-2]) * 100, 2))
            elif len(idr_closes) == 1:
                data["usdidr"] = sanitize_float(idr_closes.iloc[-1])
    except Exception as e:
        print(f"Error fetching market indices: {e}")
        # Return 0.0 indicates missing data rather than fake data
        return data

    if data["ihsg"] > 0: # Only cache if we got some real data
        set_cache(cache_key, data, ttl=3600) # Cache for 1 hour instead of 1 day to be more "Live"
    return data
