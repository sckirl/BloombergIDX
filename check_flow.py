import requests
API_BASE = "http://localhost:8000"
latest = requests.get(f"{API_BASE}/insider/latest?limit=100").json()
tickers = set(t['ticker'] for t in latest)
for ticker in tickers:
    flow = requests.get(f"{API_BASE}/insider/flow/{ticker}").json()
    if flow.get('top_buyers') or flow.get('top_sellers'):
        print(f"Ticker {ticker} has flow data!")
    else:
        print(f"Ticker {ticker} has NO flow data.")
