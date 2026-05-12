import asyncio
from playwright.async_api import async_playwright

async def inspect_e_ipo():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to E-IPO...")
        try:
            await page.goto("https://www.e-ipo.co.id/en/ipo/index", wait_until="networkidle", timeout=60000)
            # Wait for any of the common IPO list elements
            await page.wait_for_selector(".col-md-4", timeout=30000)
            
            content = await page.content()
            print(f"Content length: {len(content)}")
            
            items = await page.query_selector_all(".col-md-4")
            print(f"Found {len(items)} items")
            
            for i, item in enumerate(items[:5]):
                text = await item.inner_text()
                print(f"Item {i}: {text[:150].replace('\n', ' ')}...")
                
        except Exception as e:
            print(f"Error: {e}")
            # Try to take a screenshot to see what's happening
            # await page.screenshot(path="e_ipo_debug.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_e_ipo())
