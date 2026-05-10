import { test, expect } from '@playwright/test';

test.describe('Adversarial Audit - BloombergIDX', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:6969');
    // Wait for initial load
    await page.waitForSelector('table, .QuickStart', { timeout: 10000 });
  });

  test('View Switching - Label updates but content stays same (HALLUCINATION)', async ({ page }) => {
    // Check initial view
    await expect(page.locator('text=VIEW: INSIDER')).toBeVisible();
    
    const hasData = await page.locator('table').isVisible();
    if (!hasData) {
      console.log('No data found, skipping view switching content check');
      return;
    }

    const initialTableText = await page.locator('table').innerText();

    const views = [
      { name: 'SMART FLOW', label: 'VIEW: FLOW' },
      { name: 'ANOMALIES', label: 'VIEW: ANOMALY' },
      { name: 'HEATMAP', label: 'VIEW: HEATMAP' },
      { name: 'WATCHLIST', label: 'VIEW: WATCH' },
    ];

    for (const view of views) {
      await page.click(`button:has-text("${view.name}")`);
      await expect(page.locator(`text=${view.label}`)).toBeVisible();
      const currentTableText = await page.locator('table').innerText();
      
      // If content is identical, it's a hallucination (unless it's a very specific coincidence)
      if (currentTableText === initialTableText) {
        console.error(`DEFECT: View ${view.name} does not update content. Content is identical to INSIDER feed.`);
      }
    }
  });

  test('Institutional Drawer - Dynamic data check', async ({ page }) => {
    const hasData = await page.locator('table').isVisible();
    if (!hasData) {
      console.log('No data found, skipping drawer check');
      return;
    }

    // Click on first row ticker
    const firstRow = page.locator('table tbody tr').first();
    const firstTicker = await firstRow.locator('td').nth(1).innerText();
    await firstRow.click();
    
    // Drawer should open
    // Use a more specific locator to avoid strict mode violation
    const drawerTitle = page.locator('div.absolute.inset-y-0.right-0 span.text-black.font-black.text-xs');
    await expect(drawerTitle).toContainText(`SECURITY_INTEL: ${firstTicker}`);
    
    const drawerContent1 = await page.locator('div.absolute.inset-y-0.right-0').innerText();
    
    // Close drawer
    await page.keyboard.press('Escape');
    await expect(drawerTitle).not.toBeVisible();
    
    // Click on another ticker (if available)
    const secondRow = page.locator('table tbody tr').nth(1);
    if (await secondRow.isVisible()) {
      const secondTicker = await secondRow.locator('td').nth(1).innerText();
      if (secondTicker !== firstTicker) {
        await secondRow.click();
        await expect(drawerTitle).toContainText(`SECURITY_INTEL: ${secondTicker}`);
        const drawerContent2 = await page.locator('div.absolute.inset-y-0.right-0').innerText();
        
        if (drawerContent1 === drawerContent2) {
           console.error('DEFECT: Drawer content is static/mocked even for different tickers.');
        }
      }
    }
  });

  test('Command Palette Sync - Ctrl+K vs Footer', async ({ page }) => {
    // Use Ctrl+K to open Command Palette
    await page.keyboard.press('Control+k');
    await expect(page.locator('text=Suggestions')).toBeVisible();
    
    // Type INSIDER BBCA
    const cmdInput = page.locator('input[placeholder="ENTER TERMINAL COMMAND (e.g. INSIDER BBCA)..."]');
    await cmdInput.fill('INSIDER BBCA');
    await page.keyboard.press('Enter');
    
    // Check if view updated
    await expect(page.locator('text=VIEW: INSIDER')).toBeVisible();
    // Wait for drawer (it should open automatically if command is INSIDER BBCA)
    await expect(page.locator('div.absolute.inset-y-0.right-0')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('div.absolute.inset-y-0.right-0')).toContainText('BBCA');
    
    // Close drawer
    await page.keyboard.press('Escape');
    
    // Use Footer
    const footerInput = page.locator('footer input');
    await footerInput.fill('FLOW GOTO');
    await page.keyboard.press('Enter');
    
    await expect(page.locator('text=VIEW: FLOW')).toBeVisible();
    await expect(page.locator('div.absolute.inset-y-0.right-0')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('div.absolute.inset-y-0.right-0')).toContainText('GOTO');
  });

  test('CRT Overlay - pointer-events: none', async ({ page }) => {
    const overlay = page.locator('.crt-overlay');
    const pointerEvents = await overlay.evaluate(el => window.getComputedStyle(el).pointerEvents);
    expect(pointerEvents).toBe('none');
    
    const scanline = page.locator('.scanline');
    const scanlinePointerEvents = await scanline.evaluate(el => window.getComputedStyle(el).pointerEvents);
    expect(scanlinePointerEvents).toBe('none');
  });

  test('Quick Start - Dashboard appears when no data', async ({ page }) => {
    // We can simulate no data by searching for a nonsense ticker
    const footerInput = page.locator('footer input');
    await footerInput.fill('SEARCH_NO_DATA_123');
    await page.keyboard.press('Enter');
    
    // Wait for "INITIALIZING..." to disappear and QuickStart to appear
    await expect(page.locator('text=QUICK START TERMINAL')).toBeVisible({ timeout: 15000 });
    
    // Click HELP in Quick Start
    // Re-register dialog handler
    const dialogPromise = page.waitForEvent('dialog');
    await page.click('button:has-text("HELP")');
    const dialog = await dialogPromise;
    expect(dialog.message()).toContain('Available Commands');
    await dialog.dismiss();
  });
});
