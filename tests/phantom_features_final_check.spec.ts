import { test, expect } from '@playwright/test';

test.describe('Phantom Features Final Verification', () => {
  const BASE_URL = 'http://localhost:6969';

  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForSelector('text=IDX:TERMINAL');
  });

  test('View Switching and Content Check', async ({ page }) => {
    // 1. INSIDER
    await expect(page.locator('text=VIEW: INSIDER')).toBeVisible();
    await page.screenshot({ path: 'tests/view-insider.png' });
    
    // 2. FLOW
    await page.click('text=SMART FLOW');
    await expect(page.locator('text=VIEW: FLOW')).toBeVisible();
    await page.screenshot({ path: 'tests/view-flow-empty.png' });
    
    // FLOW with Ticker
    await page.fill('footer input', 'FLOW BBCA');
    await page.keyboard.press('Enter');
    await expect(page.locator('h2:has-text("BBCA")')).toBeVisible();
    await expect(page.locator('text=CONCENTRATION SCORE')).toBeVisible();
    await page.screenshot({ path: 'tests/view-flow-bbca.png' });
    
    // 3. ANOMALY
    await page.click('text=ANOMALIES');
    await expect(page.locator('text=VIEW: ANOMALY')).toBeVisible();
    await expect(page.locator('text=MARKET ANOMALIES')).toBeVisible();
    // Wait for data or empty message
    await page.waitForTimeout(1000); 
    await page.screenshot({ path: 'tests/view-anomaly.png' });
    
    // 4. HEATMAP
    await page.click('text=HEATMAP');
    await expect(page.locator('text=VIEW: HEATMAP')).toBeVisible();
    await expect(page.locator('text=Sector Accumulation Heatmap')).toBeVisible();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'tests/view-heatmap.png' });
    
    // 5. WATCHLIST
    await page.click('text=WATCHLIST');
    await expect(page.locator('text=VIEW: WATCH')).toBeVisible();
    await expect(page.locator('text=Institutional Watchlist')).toBeVisible();
    await page.screenshot({ path: 'tests/view-watchlist.png' });
  });
});
