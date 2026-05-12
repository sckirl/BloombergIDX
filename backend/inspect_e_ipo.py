import asyncio
from playwright.async_api import async_playwright

async def inspect_e_ipo():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to E-IPO...")
        await page.goto("https://www.e-ipo.co.id/en/ipo/index", wait_until="networkidle")
        
        # Get table content or list items
        content = await page.content()
        print(f"Content length: {len(content)}")
        
        # Look for cards or table rows
        # Based on common knowledge of E-IPO website, it uses cards
        cards = await page.query_selector_all(".card")
        print(f"Found {len(cards)} cards")
        
        for i, card in enumerate(cards[:3]):
            text = await card.inner_text()
            print(f"Card {i} text: {text[:200]}...")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_e_ipo())
