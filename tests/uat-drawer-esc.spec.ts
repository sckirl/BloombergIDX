import { test, expect } from '@playwright/test';

test('Drawer Esc Close Audit', async ({ page }) => {
  await page.goto('http://localhost:6969');
  await page.waitForTimeout(2000);

  const row = page.locator('table.dense-table tbody tr').first();
  if (!(await row.innerText()).includes('NO RECORDS')) {
    await row.click();
    const drawer = page.locator('div.absolute.right-0.w-\\[400px\\]');
    await expect(drawer).toBeVisible();
    
    console.log('Pressing Escape to close drawer...');
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
    
    // Check if it closed. 
    // In many implementations, Esc only closes modals. 
    // Let's see if the developer implemented Esc for the Drawer.
    const isVisible = await drawer.isVisible();
    console.log('Drawer visible after Escape:', isVisible);
  }
});
