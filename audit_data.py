import requests
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"
DB_PATH = "backend/database.db"

def test_veracity_flow():
    print("--- 1. Veracity Check: /insider/flow/{ticker} ---")
    # Find a ticker with data
    latest = requests.get(f"{API_BASE}/insider/latest?limit=10").json()
    if not latest:
        print("FAIL: No latest transactions found.")
        return
    
    ticker = latest[0]['ticker']
    print(f"Auditing ticker: {ticker}")
    
    resp = requests.get(f"{API_BASE}/insider/flow/{ticker}").json()
    if "error" in resp:
        print(f"FAIL: {resp['error']}")
        return
        
    concentration = resp['concentration']
    top_buyers = resp['top_buyers']
    
    # Recalculate concentration
    # We need the full broker list to calculate total_buy_net, 
    # but the API only returns top_buyers/top_sellers.
    # Wait, the summary has total_buy_value and total_sell_value, but not total_buy_net.
    # However, I can check if top_5_buy_net / sum(all buyers net) == concentration.
    # Since I don't have all buyers, I'll at least check if concentration is 
    # mathematically possible (e.g. >= 0 and <= 1).
    # And check if top_buyers are indeed sorted.
    
    print(f"Concentration reported: {concentration}")
    net_values = [b['net_value'] for b in top_buyers]
    is_sorted = all(net_values[i] >= net_values[i+1] for i in range(len(net_values)-1))
    print(f"Top buyers sorted by net_value: {is_sorted}")
    
    if concentration < 0 or concentration > 1:
        print(f"FAIL: Concentration {concentration} out of bounds [0, 1]")
    
    if not is_sorted:
        print("FAIL: Top buyers not sorted correctly.")

def test_volume_ticks():
    print("\n--- 2. Volume Check: PriceTick counts ---")
    conn = sqlite3.connect(DB_PATH)
    df_stocks = pd.read_sql_query("SELECT id, ticker FROM stocks", conn)
    df_ticks = pd.read_sql_query("SELECT stock_id, COUNT(*) as count FROM price_ticks GROUP BY stock_id", conn)
    conn.close()
    
    merged = df_stocks.merge(df_ticks, left_on='id', right_on='stock_id', how='left').fillna(0)
    
    low_volume = merged[merged['count'] < 30]
    print(f"Total stocks: {len(merged)}")
    print(f"Stocks with < 30 ticks: {len(low_volume)}")
    if not low_volume.empty:
        print("Samples of low volume stocks:")
        print(low_volume.head(10))
    else:
        print("SUCCESS: All stocks have >= 30 ticks.")

def test_variety_heatmap():
    print("\n--- 3. Variety Check: /insider/heatmap ---")
    resp = requests.get(f"{API_BASE}/insider/heatmap").json()
    if not resp:
        print("FAIL: Heatmap is empty.")
        return
        
    sectors = [r['sector'] for r in resp]
    flows = [r['net_flow'] for r in resp]
    
    print(f"Sectors found: {len(sectors)}")
    print(f"Sectors list: {sectors}")
    
    zero_flow = [s for s, f in zip(sectors, flows) if f == 0.0]
    if zero_flow:
        print(f"FAIL: Sectors with 0.0 flow: {zero_flow}")
    else:
        print("SUCCESS: All sectors have non-zero flow.")
        
    # Check for major sectors
    major_sectors = ["Finance", "Energy", "Basic Materials", "Consumer Cyclical"]
    # (Checking if at least some of these are present - names might differ slightly)
    found_major = any(any(m.lower() in s.lower() for s in sectors) for m in major_sectors)
    print(f"Found major sectors (Finance/Energy/etc): {found_major}")

def test_variety_latest():
    print("\n--- 4. Variety Check: /insider/latest ---")
    resp = requests.get(f"{API_BASE}/insider/latest?limit=1000").json()
    if not resp:
        print("FAIL: No transactions found.")
        return
        
    df = pd.DataFrame(resp)
    # Check date range
    df['date'] = pd.to_datetime(df['date'])
    year_2026 = df[df['date'].dt.year == 2026]
    print(f"Total transactions: {len(df)}")
    print(f"Transactions in 2026: {len(year_2026)}")
    
    counts = year_2026['transaction_type'].value_counts()
    print("Transaction types in 2026:")
    print(counts)
    
    if 'BUY' not in counts or 'SELL' not in counts:
        print("FAIL: Missing BUY or SELL variety in 2026 data.")
    else:
        buy_sell_ratio = counts['BUY'] / counts['SELL']
        print(f"BUY/SELL Ratio: {buy_sell_ratio:.2f}")

if __name__ == "__main__":
    test_veracity_flow()
    test_volume_ticks()
    test_variety_heatmap()
    test_variety_latest()
