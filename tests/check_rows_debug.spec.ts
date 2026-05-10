import { test, expect } from '@playwright/test';
test('debug fetch', async ({ page }) => {
  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text()));
  page.on('requestfailed', request => {
    console.log('REQUEST FAILED:', request.url(), request.failure()?.errorText);
  });
  await page.goto('http://localhost:6969');
  await page.waitForTimeout(5000);
  const rowCount = await page.locator('table tbody tr').count();
  console.log('UI ROW COUNT:', rowCount);
});
