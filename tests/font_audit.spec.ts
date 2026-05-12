import { test, expect } from '@playwright/test';

test('Font size audit', async ({ page }) => {
  page.on('console', msg => console.log('BROWSER_LOG:', msg.text()));
  await page.goto('http://localhost:6969');
  await expect(page.locator('text=INITIALIZING DATA PIPELINE...')).not.toBeVisible({ timeout: 20000 });

  const elements = await page.evaluate(() => {
    const all = Array.from(document.querySelectorAll('*'));
    return all
      .map(el => {
        const style = window.getComputedStyle(el);
        const fontSize = style.fontSize;
        const text = el.innerText?.trim()?.substring(0, 30);
        const tagName = el.tagName;
        const className = el.className;
        return { fontSize, text, tagName, className };
      })
      .filter(item => {
        if (!item.text) return false;
        const size = parseInt(item.fontSize);
        return size > 10;
      });
  });

  console.log('Total offenders:', elements.length);
  elements.slice(0, 20).forEach(item => {
    console.log(`Offender: ${item.fontSize} - ${item.tagName}.${item.className.split(' ').join('.')} - "${item.text}"`);
  });
  
  expect(elements.length).toBe(0);
});
