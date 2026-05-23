from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time

def test_stealth():
    print("--- 🕵️ Stealth Verification Strike ---")
    # Recommended Sync Usage
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to bot detection test...")
        page.goto("https://bot.sannysoft.com/", wait_until="networkidle")
        
        # Success if 'navigator.webdriver' is False
        webdriver_result = page.evaluate("() => navigator.webdriver")
        chrome_result = page.evaluate("() => !!window.chrome")
        
        print(f"Result: WebDriver Detection = {webdriver_result} (Expected: False)")
        print(f"Result: Chrome Object Present = {chrome_result} (Expected: True)")
        
        if webdriver_result is False and chrome_result is True:
            print("✅ STEALTH CERTIFIED: Browser fingerprints are successfully masked.")
        else:
            print("❌ STEALTH FAILED: Detection still active.")
            
        browser.close()

if __name__ == "__main__":
    test_stealth()
