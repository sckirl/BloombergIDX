import { test, expect } from '@playwright/test';

test.describe('BloombergIDX Heavy Senior QA Audit', () => {
  test.beforeEach(async ({ page }) => {
    test.setTimeout(60000);
    await page.goto('http://localhost:8100');
    await expect(page.locator('body')).toBeVisible();
  });

  test('SIT-01: Market Data Veracity (IHSG/USDIDR)', async ({ page }) => {
    // Flexible match for IHSG and USDIDR in header
    await expect(page.locator('header')).toContainText(/6\.370,67/);
    await expect(page.locator('header')).toContainText(/17\.600/);
    
    // Refresh and check again to ensure not randomized
    await page.reload();
    await expect(page.locator('header')).toContainText(/6\.370,67/);
  });

  test('SIT-02: Events Module Connectivity', async ({ page }) => {
    const footerInput = page.locator('footer input');
    await page.keyboard.press('Alt+s');
    await footerInput.fill('EVENTS');
    await page.keyboard.press('Enter');

    // Events view uses .terminal-panel instead of table
    const eventCards = page.locator('.terminal-panel');
    await expect(eventCards.first()).toBeVisible({ timeout: 15000 });
    
    const cardCount = await eventCards.count();
    console.log('Events card count:', cardCount);
    // Backend returned 21.
    expect(cardCount).toBeGreaterThanOrEqual(21); 
  });

  test('UAT-01: Watchlist Persistence (WL ADD BBCA)', async ({ page }) => {
    const footerInput = page.locator('footer input');
    
    // Add BBCA to watchlist
    await page.keyboard.press('Alt+s');
    await footerInput.fill('WL ADD BBCA');
    await page.keyboard.press('Enter');
    
    await page.waitForTimeout(2000); 
    
    // Navigate to Watchlist view
    await page.keyboard.press('Alt+s');
    await footerInput.fill('WL');
    await page.keyboard.press('Enter');
    
    // Watchlist view uses a table
    await expect(page.locator('table')).toContainText('BBCA', { timeout: 10000 });
    
    // Reload and verify persistence
    await page.reload();
    await page.waitForTimeout(2000);
    
    // Go back to WL view 
    await page.keyboard.press('Alt+s');
    await footerInput.fill('WL');
    await page.keyboard.press('Enter');
    
    await expect(page.locator('table')).toContainText('BBCA');
  });

  test('UAT-02: Institutional UI Density (10px Mono)', async ({ page }) => {
    // Wait for the main table to load
    const table = page.locator('table.dense-table');
    await expect(table).toBeVisible({ timeout: 15000 });

    const cells = table.locator('td');
    const count = await cells.count();
    expect(count).toBeGreaterThan(0);
    
    for (let i = 0; i < Math.min(count, 5); i++) {
      const cell = cells.nth(i);
      const fontSize = await cell.evaluate((el) => window.getComputedStyle(el).fontSize);
      const fontFamily = await cell.evaluate((el) => window.getComputedStyle(el).fontFamily);
      
      console.log(`Cell ${i} font:`, fontSize, fontFamily);
      
      expect(fontSize).toBe('10px');
      expect(fontFamily.toLowerCase()).toContain('mono');
    }
  });
});
