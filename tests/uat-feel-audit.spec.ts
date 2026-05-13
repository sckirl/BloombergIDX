import { test, expect } from '@playwright/test';

test('Keyboard Navigation & Feel Audit', async ({ page }) => {
  await page.goto('http://localhost:8100');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);

  // Try both Ctrl+K and Meta+K
  console.log('Attempting to open Command Palette...');
  await page.keyboard.press('Control+k');
  await page.waitForTimeout(500);
  let palette = page.locator('div.fixed.inset-0.z-\\[100\\]');
  
  if (!(await palette.isVisible())) {
    console.log('Ctrl+K failed, trying Meta+k');
    await page.keyboard.press('Meta+k');
    await page.waitForTimeout(500);
  }

  // Fallback: search for unique text inside palette
  const paletteText = page.locator('text=Suggestions');
  await expect(paletteText).toBeVisible();
  console.log('Command Palette opened.');
  
  // 1. Navigation
  await page.keyboard.press('ArrowDown');
  await page.waitForTimeout(100);
  await page.keyboard.press('ArrowDown');
  await page.waitForTimeout(100);
  
  const activeSuggestion = page.locator('button.bg-acc');
  await expect(activeSuggestion).toBeVisible();
  console.log('Arrow key navigation works.');

  await page.keyboard.press('Escape');
  await expect(paletteText).not.toBeVisible();

  // 2. Row Interaction
  const firstRow = page.locator('table.dense-table tbody tr').first();
  const rowText = await firstRow.innerText();
  if (!rowText.includes('NO RECORDS')) {
    await firstRow.click();
    const drawer = page.locator('div.absolute.right-0');
    await expect(drawer).toBeVisible();
    console.log('Institutional Drawer opens on row click.');
    
    // Check Intelligence Density
    const sections = await drawer.locator('section').count();
    console.log('Drawer sections count:', sections);
  }
});
