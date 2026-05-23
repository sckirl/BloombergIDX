import { test, expect } from '@playwright/test';

test.describe('BloombergIDX Phase 1-4 UAT', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8100');
  });

  test('CSV Export works', async ({ page }) => {
    // Wait for data to load
    await page.waitForSelector('table tbody tr');
    
    // Check if Export button exists
    const exportBtn = page.locator('button:has-text("Export (CSV)")');
    await expect(exportBtn).toBeVisible();

    // Trigger download
    const downloadPromise = page.waitForEvent('download');
    await exportBtn.click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('idx_insider_');
  });

  test('Alert System: Can add and remove alerts', async ({ page }) => {
    // Navigate to Alert View
    await page.click('button:has-text("ALERT ENGINE")');
    await expect(page.locator('h2:has-text("Asymmetric Alert Engine")')).toBeVisible();

    // Add an alert
    await page.fill('input[placeholder="e.g. BBCA"]', 'BBCA');
    await page.selectOption('select', 'BUY');
    await page.fill('input[type="number"]', '5000000000');
    await page.click('button:has-text("Deploy Rule")');

    // Verify alert is listed
    await expect(page.locator('div.terminal-panel:has-text("BBCA")')).toBeVisible();
    await expect(page.locator('div.terminal-panel:has-text("5.000.000.000")')).toBeVisible();

    // Remove alert
    await page.click('button:has-text("TERMINATE")');
    await expect(page.locator('div.terminal-panel:has-text("BBCA")')).not.toBeVisible();
  });

  test('Intelligence Endpoints: Momentum, Bandar, Entity', async ({ request }) => {
    const baseUrl = 'http://localhost:8000';
    
    // Test Momentum
    const momRes = await request.get(`${baseUrl}/insider/momentum/BBCA`);
    expect(momRes.ok()).toBeTruthy();
    const momData = await momRes.json();
    expect(momData).toHaveProperty('convergence_score');

    // Test Bandar
    const banRes = await request.get(`${baseUrl}/insider/bandar/BBCA`);
    expect(banRes.ok()).toBeTruthy();
    const banData = await banRes.json();
    expect(banData).toHaveProperty('bandar_detected');

    // Test Entity Intelligence
    const entRes = await request.get(`${baseUrl}/insider/entity/ANTHONI%20SALIM`);
    expect(entRes.ok()).toBeTruthy();
    const entData = await entRes.json();
    expect(entData).toHaveProperty('pep_flag');
  });

  test('Existing Features: Heatmap and Events', async ({ page }) => {
    // Heatmap
    await page.click('button:has-text("HEATMAP")');
    await expect(page.locator('h2:has-text("Sector Accumulation Treemap")')).toBeVisible();
    // Treemap might take a second to render
    await page.waitForSelector('.recharts-treemap');

    // Events
    await page.click('button:has-text("EVENTS")');
    await expect(page.locator('h2:has-text("Corporate Event Intelligence")')).toBeVisible();
  });
  
  test('Drawer Intelligence: Verify asymmetric signals in drawer', async ({ page }) => {
    // Click on a row to open drawer
    await page.waitForSelector('table tbody tr');
    await page.locator('table tbody tr').first().click();
    
    // Verify drawer is open
    await expect(page.locator('span:has-text("SECURITY_INTEL:")')).toBeVisible();
    
    // Verify Intelligence sections
    await expect(page.locator('h3:has-text("Asymmetric Signals")')).toBeVisible();
    await expect(page.locator('div:has-text("Momentum Convergence")')).toBeVisible();
    await expect(page.locator('div:has-text("Bandar Detection")')).toBeVisible();
  });
});
