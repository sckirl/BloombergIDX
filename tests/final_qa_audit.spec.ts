import { test, expect } from "@playwright/test";

test.describe("Final QA Audit", () => {
  const APP_URL = "http://localhost:8100";
  const API_URL = "http://localhost:8000";

  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await page.waitForLoadState("networkidle");
  });

  test("Institutional Drawer opens without 500 errors", async ({ page }) => {
    await page.waitForSelector("table.dense-table tbody tr", { timeout: 15000 });
    
    const responsePromises = [];
    page.on("response", response => {
      if (response.status() >= 500) {
        console.error("500 Error at:", response.url());
        responsePromises.push(response.url());
      }
    });

    const firstRow = page.locator("table.dense-table tbody tr").first();
    await firstRow.click();

    const drawer = page.locator("aside:has-text(\"SECURITY_INTEL:\")");
    await expect(drawer).toBeVisible({ timeout: 5000 });
    
    expect(responsePromises.length).toBe(0);
  });

  test("Momentum Convergence and Bandar Detection load successfully", async ({ page, request }) => {
    const momRes = await request.get(`${API_URL}/insider/momentum/BBCA`);
    expect(momRes.ok()).toBeTruthy();

    const banRes = await request.get(`${API_URL}/insider/bandar/BBCA`);
    expect(banRes.ok()).toBeTruthy();

    await page.waitForSelector("table.dense-table tbody tr", { timeout: 15000 });
    const firstRow = page.locator("table.dense-table tbody tr").first();
    await firstRow.click();
    
    const drawer = page.locator("aside:has-text(\"SECURITY_INTEL:\")");
    await expect(drawer).toBeVisible();

    await expect(page.locator("div:has-text(\"Momentum Convergence\")").last()).toBeVisible({ timeout: 10000 });
    await expect(page.locator("div:has-text(\"Bandar Detection\")").last()).toBeVisible({ timeout: 10000 });
  });

  test("CSV Export is functional", async ({ page }) => {
    await page.waitForSelector("table.dense-table tbody tr", { timeout: 15000 });
    const exportBtn = page.locator("button:has-text(\"Export (CSV)\")");
    await expect(exportBtn).toBeVisible();

    const downloadPromise = page.waitForEvent("download", { timeout: 10000 });
    await exportBtn.click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain(".csv");
  });

  test("Alerts are functional", async ({ page }) => {
    await page.click("button:has-text(\"ALERT ENGINE\")");
    await expect(page.locator("h2:has-text(\"Asymmetric Alert Engine\")")).toBeVisible();

    await page.fill("input[placeholder=\"e.g. BBCA\"]", "BMRI");
    await page.selectOption("select", "BUY");
    await page.fill("input[type=\"number\"]", "10000000000");
    await page.click("button:has-text(\"Deploy Rule\")");

    await expect(page.locator("div.terminal-panel:has-text(\"BMRI\")")).toBeVisible();

    await page.click("button:has-text(\"TERMINATE\")");
    await expect(page.locator("div.terminal-panel:has-text(\"BMRI\")")).not.toBeVisible();
  });
});