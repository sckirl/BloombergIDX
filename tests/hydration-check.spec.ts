import { test, expect } from '@playwright/test';

test('verify no hydration mismatch error', async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  await page.goto('http://localhost:6969');
  
  // Wait for some time to allow hydration and potential errors to show up
  await page.waitForTimeout(2000);

  const hydrationErrors = consoleErrors.filter(err => 
    err.includes('Hydration') || 
    err.includes('Text content does not match') ||
    err.includes('Server-rendered HTML')
  );

  expect(hydrationErrors).toEqual([]);
});
