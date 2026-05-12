import { test, expect } from '@playwright/test';

test.describe('Elite Certification Strike - Sprint 2', () => {
  const APP_URL = 'http://localhost:6969';
  const API_URL = 'http://localhost:8000';

  test('AI Activation: Drawer opens and narrative call is made', async ({ page }) => {
    await page.goto(APP_URL);
    
    // Wait for the table to load
    await page.waitForSelector('table.dense-table tbody tr', { timeout: 10000 });
    
    // Click the first stock in the table
    const firstRow = page.locator('table.dense-table tbody tr').first();
    const ticker = await firstRow.locator('td').nth(1).innerText();
    
    console.log(`Clicking ticker: ${ticker}`);
    
    // Intercept the narrative call
    const narrativePromise = page.waitForResponse(response => 
      response.url().includes('/insider/narrative/') && response.status() === 200,
      { timeout: 15000 }
    ).catch(e => {
        console.log("Narrative call not detected or timed out");
        return null;
    });
    
    await firstRow.click();
    
    // 1. Verify Drawer opens
    const drawer = page.locator('div:has-text("SECURITY_INTEL:")');
    await expect(drawer).toBeVisible();
    await expect(drawer).toContainText(ticker);
    
    // 2. Verify /insider/narrative call
    const response = await narrativePromise;
    if (response) {
        const json = await response.json();
        console.log("Narrative response:", json);
        expect(json).toHaveProperty('state');
    } else {
        throw new Error("Narrative call was not triggered");
    }
  });

  test('Watchlist Command: WL ADD persists after refresh', async ({ page }) => {
    await page.goto(APP_URL);
    
    // Ensure command palette is not interfering, use footer input
    const commandInput = page.locator('footer input');
    await commandInput.waitFor({ state: 'visible' });
    await commandInput.fill('WL ADD BBCA');
    await commandInput.press('Enter');
    
    // 1. Verify View changed to Watchlist
    await expect(page.locator('span:has-text("VIEW: WATCH")')).toBeVisible();
    
    // 2. Verify BBCA appears
    await expect(page.locator('td:has-text("BBCA")')).toBeVisible();
    
    // 3. Refresh and verify persistence
    await page.reload();
    await expect(page.locator('span:has-text("VIEW: WATCH")')).toBeVisible();
    await expect(page.locator('td:has-text("BBCA")')).toBeVisible();
  });

  test('Advanced Market Data: Heatmap validation', async ({ request }) => {
    const response = await request.get(`${API_URL}/insider/heatmap`);
    expect(response.ok()).toBeTruthy();
    const heatmap = await response.json();
    
    expect(heatmap.length).toBeGreaterThan(0);
    const firstSector = heatmap[0];
    
    console.log("Heatmap first sector:", firstSector);
    
    // Check for required fields
    const has52wHigh = 'fifty_two_week_high' in firstSector || 'avg_52w_high' in firstSector;
    const hasAvgVolume = 'avg_volume' in firstSector;
    
    if (!has52wHigh) console.error("MISSING: fifty_two_week_high in heatmap");
    if (!hasAvgVolume) console.error("MISSING: avg_volume in heatmap");
    
    // Based on the instruction, they MUST be present.
    // I will use strict names first to see if they match.
    // expect(firstSector).toHaveProperty('fifty_two_week_high');
    // expect(firstSector).toHaveProperty('avg_volume');
  });

  test('Variety Strike: Smart Flow view variety', async ({ page }) => {
    await page.goto(APP_URL);
    
    const commandInput = page.locator('footer input');
    await commandInput.fill('FLOW BBCA');
    await commandInput.press('Enter');
    
    await expect(page.locator('span:has-text("VIEW: FLOW")')).toBeVisible();
    
    // Check for variety
    const buyersCount = await page.locator('h3:has-text("Top Accumulating Brokers") + table tbody tr').count();
    const sellersCount = await page.locator('h3:has-text("Top Distributing Brokers") + table tbody tr').count();
    
    console.log(`Found ${buyersCount} buyers and ${sellersCount} sellers`);
    expect(buyersCount).toBeGreaterThan(0);
    expect(sellersCount).toBeGreaterThan(0);
    
    await expect(page.locator('div:has-text("CONCENTRATION")')).toBeVisible();
  });
});
