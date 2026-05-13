import { test, expect } from '@playwright/test';

test.describe('IDX OpenInsider UAT Audit', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8100');
  });

  test('Visual Fidelity: Institutional Dark Mode & Layout', async ({ page }) => {
    await expect(page.locator('header')).toBeVisible();
    await expect(page.locator('aside')).toHaveCount(2); 
    await expect(page.locator('main')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();

    // Check for the "dense-table" class which indicates institutional density
    await expect(page.locator('table.dense-table')).toBeVisible();

    await page.screenshot({ path: 'test-results/visual-audit.png', fullPage: true });
  });

  test('Workflow: Command Bar & Shortcuts', async ({ page }) => {
    const footerInput = page.locator('footer input');
    
    // Test ALT+S focus
    await page.keyboard.press('Alt+s');
    await expect(footerInput).toBeFocused();

    // Test Command Input - Search for a ticker we know exists (from scraper logs)
    // Logs showed NASI, GPSO, IATA, AKRA, NAIK
    await footerInput.fill('INSIDER AKRA');
    await page.keyboard.press('Enter');
    
    // Check if Institutional Drawer appears
    await expect(page.locator('text=SECURITY_INTEL: AKRA')).toBeVisible({ timeout: 10000 });
    
    // Test ALT+Q reset
    await page.keyboard.press('Alt+q');
    await expect(page.locator('text=SECURITY_INTEL: AKRA')).not.toBeVisible();
  });

  test('Workflow: Command Palette (CMD+K)', async ({ page }) => {
    await page.keyboard.press('Control+k');
    // Check if command palette is visible (it should have a specific class or text)
    await expect(page.locator('input[placeholder="Search commands..."]')).toBeVisible();
    await page.screenshot({ path: 'test-results/command-palette.png' });
  });

  test('Data Handling: Records Visible', async ({ page }) => {
    // Wait for the initializing message to disappear
    await expect(page.locator('text=INITIALIZING DATA PIPELINE...')).not.toBeVisible({ timeout: 20000 });
    
    // Check if table has rows (other than the header)
    const rowCount = await page.locator('table.dense-table tbody tr').count();
    console.log('Row count:', rowCount);
    expect(rowCount).toBeGreaterThan(0);
  });

  test('Institutional Drawer: Components', async ({ page }) => {
    // Trigger drawer via search
    await page.keyboard.press('Alt+s');
    await page.locator('footer input').fill('INSIDER AKRA');
    await page.keyboard.press('Enter');

    await expect(page.locator('text=Absorption Ratio')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Accumulation Price Map')).toBeVisible();
    await expect(page.locator('text=NVIDIA_AI_NARRATIVE')).toBeVisible();
    
    await page.screenshot({ path: 'test-results/institutional-drawer.png' });
  });
});
