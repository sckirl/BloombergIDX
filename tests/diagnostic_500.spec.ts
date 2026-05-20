import { test, expect } from '@playwright/test';
import fs from 'fs';

test('diagnose 500 error', async ({ page }) => {
  const errors: any[] = [];
  const consoleLogs: any[] = [];

  page.on('pageerror', (exception) => {
    errors.push(exception.message);
  });

  page.on('console', (message) => {
    consoleLogs.push({ type: message.type(), text: message.text() });
  });

  const response = await page.goto('http://localhost:8100');
  
  const report = {
    status: response?.status(),
    statusText: response?.statusText(),
    errors,
    consoleLogs,
    body: await response?.text()
  };

  fs.writeFileSync('tests/diagnostic_report.json', JSON.stringify(report, null, 2));
  await page.screenshot({ path: 'tests/500_diagnostic.png', fullPage: true });
});
