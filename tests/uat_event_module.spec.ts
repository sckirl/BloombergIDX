import { test, expect } from '@playwright/test';
import * as fs from 'fs';

test('Corporate Event Intelligence UAT', async ({ page }) => {
  let log = '';
  const appendLog = (msg: string) => { log += msg + '\n'; };

  await page.goto('http://localhost:8100');
  await expect(page.locator('text=IDX INSIDER')).toBeVisible();

  const eventsButton = page.locator('button:has-text("EVENTS (IPO/M&A)")');
  await expect(eventsButton).toBeVisible();
  await eventsButton.click();

  await expect(page.locator('text=DECRYPTING EVENT LEDGERS...')).not.toBeVisible({ timeout: 15000 });
  await expect(page.locator('text=Corporate Event Intelligence')).toBeVisible();

  const eventCards = page.locator('.terminal-panel');
  const count = await eventCards.count();
  appendLog('Total event cards found: ' + count);
  expect(count).toBeGreaterThan(0);

  // Variety Audit
  const eIpoLabels = page.locator('span:has-text("E-IPO")');
  const mergerLabels = page.locator('span:has-text("MERGER")');
  
  appendLog('E-IPO count: ' + await eIpoLabels.count());
  appendLog('Merger/Acquisition count: ' + await mergerLabels.count());

  // Check specific tickers
  const mapiVisible = await page.locator('text=MAPI').first().isVisible();
  const smarVisible = await page.locator('text=SMAR').first().isVisible();
  appendLog('MAPI visible: ' + mapiVisible);
  appendLog('SMAR visible: ' + smarVisible);

  // UX Check: Prospectus Link
  const prospectusLink = page.locator('a:has-text("View Prospectus")').first();
  await expect(prospectusLink).toBeVisible();
  const href = await prospectusLink.getAttribute('href');
  appendLog('Sample Prospectus Link: ' + href);

  // Check for Visual Shell Residue
  const naValues = page.locator('text=N/A');
  const naCount = await naValues.count();
  appendLog('N/A value count: ' + naCount);
  
  // Ticker Navigation Check
  const tickerLabel = page.locator('span.text-acc:has-text("[")').first();
  if (await tickerLabel.isVisible()) {
    appendLog('Found ticker label, testing click...');
    await tickerLabel.click();
    
    await page.waitForTimeout(1000);
    const viewHeader = page.locator('text=VIEW: INSIDER');
    const isInsiderView = await viewHeader.isVisible();
    appendLog('Is Insider View after click? ' + isInsiderView);
  } else {
    appendLog('No ticker label found to test navigation.');
  }

  fs.writeFileSync('uat_audit_results.txt', log);
});
