import { test, expect } from '@playwright/test';

test('Diagnostic Screenshot', async ({ page }) => {
  await page.goto('http://localhost:8100');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: 'tests/diagnostic_main.png', fullPage: true });
  
  // Try to find ANY text containing IHSG
  const ihsgText = await page.evaluate(() => {
    return document.body.innerText.match(/IHSG/i);
  });
  console.log('IHSG present:', !!ihsgText);
  if (ihsgText) {
     const bodyText = await page.evaluate(() => document.body.innerText);
     console.log('Body snippet:', bodyText.substring(0, 500));
  }
});
