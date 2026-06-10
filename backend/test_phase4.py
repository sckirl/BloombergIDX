from backend.scraper import run_scraper
from backend.database import SessionLocal
import sys

def test_insider():
    print("--- 🕵️ Isolated Phase 4 Test: Insider Scraper ---")
    try:
        run_scraper(full_year=True)
        print("✅ Phase 4 Completed Successfully")
    except Exception as e:
        import traceback
        print("❌ Phase 4 Failed:")
        traceback.print_exc()

if __name__ == "__main__":
    test_insider()
