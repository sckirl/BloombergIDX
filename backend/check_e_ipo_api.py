import requests

def check_e_ipo_api():
    urls = [
        "https://www.e-ipo.co.id/en/ipo/get-data",
        "https://www.e-ipo.co.id/en/ipo/index-data",
        "https://www.e-ipo.co.id/ipo/index-data"
    ]
    for url in urls:
        print(f"Checking {url}...")
        try:
            res = requests.get(url, timeout=10)
            print(f"Status: {res.status_code}")
            print(f"Content: {res.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_e_ipo_api()
