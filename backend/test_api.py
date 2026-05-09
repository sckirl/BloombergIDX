import cloudscraper
import json

def test_idx_api():
    # Final correct IDX API URL
    url = "https://www.idx.co.id/primary/ListedCompany/GetAnnouncement"
    params = {
        "indexFrom": 0,
        "pageSize": 10,
        "dateFrom": "20240101",
        "dateTo": "20241231",
        "lang": "id",
        "keyword": "Laporan Kepemilikan"
    }
    
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get("Results") or data.get("Replies") or []
        print(f"Success! Found {len(items)} announcements.")
        if items:
            print(json.dumps(items[0], indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_idx_api()
