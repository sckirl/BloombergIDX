import { test, expect } from '@playwright/test';
test('count rows', async ({ page }) => {
  await page.goto('http://localhost:8100');
  // Wait for loading to finish
  await page.waitForSelector('text=NO RECORDS FOUND', { state: 'detached', timeout: 20000 });
  const rowCount = await page.locator('table tbody tr').count();
  console.log('UI ROW COUNT:', rowCount);
  expect(rowCount).toBeGreaterThan(0);
});
