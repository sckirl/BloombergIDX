import requests
import time

API_URL = "http://localhost:8000"

def audit_narrative():
    print("--- Narrative Audit Start ---")
    
    # 1. Get a transaction ID
    res = requests.get(f"{API_URL}/insider/latest")
    if not res.ok or not res.json():
        print("FAIL: Could not fetch transactions")
        return
    
    txn_id = res.json()[0]['id']
    print(f"Testing Narrative for Transaction ID: {txn_id}")
    
    # 2. Trigger narrative
    res = requests.get(f"{API_URL}/insider/narrative/{txn_id}")
    print(f"Initial State: {res.json()}")
    
    if res.json().get('state') != 'QUEUED':
        print(f"FAIL: Expected initial state QUEUED, got {res.json().get('state')}")
    
    # 3. Poll for transition
    print("Polling for state transition (timeout 10s)...")
    start_time = time.time()
    while time.time() - start_time < 10:
        res = requests.get(f"{API_URL}/insider/narrative/{txn_id}")
        state = res.json().get('state')
        print(f"Current State: {state}")
        if state != 'QUEUED':
            print(f"SUCCESS: State transitioned to {state}")
            break
        time.sleep(2)
    else:
        print("FAIL: State stuck in QUEUED - Narrative logic is likely a hollow mock.")

if __name__ == "__main__":
    audit_narrative()
