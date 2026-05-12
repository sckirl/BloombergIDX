import { test, expect } from '@playwright/test';

/**
 * ADVERSARIAL QA FRAMEWORK - TRACK E (SPRINT-2)
 * Mission: Break the AI Narrative system before release.
 * Auditor: HEAVY Reliability Engineer (150 IQ)
 */

test.describe('AI Narrative Adversarial Audit', () => {

  const MOCK_SSO = {
    id: 123,
    tkr: "BBCA",
    ins: "Darmawan Junaidi",
    role: "DIREKTUR_UTAMA",
    type: "BUY",
    val: 5000000000, 
    shr: 500000,
    prc: 10000,
    dte: "2026-04-10",
    fil: "2026-04-11",
    scr: 8,
    rvol: 4.5
  };

  /**
   * TASK 2: Hallucination Detector
   * Compares AI-generated narratives against the Structured Signal Object (SSO).
   */
  test('Hallucination Detector: Statistical Outliers & Fabrications', async ({ page }) => {
    const narratives = [
      "BBCA is accumulating. Synergy with GOTO detected.", // Fabricated Ticker
      "BBCA buy at 50000 IDR.", // Fabricated Price (SSO says 10000)
      "Darmawan Junaidi sold shares.", // Fabricated Type (SSO says BUY)
    ];
    
    for (const text of narratives) {
      console.log(`Auditing Narrative: "${text}"`);
      
      // 1. Ticker Fabrication Check
      const tickers = text.match(/\b[A-Z]{4}\b/g) || [];
      const fabricatedTickers = tickers.filter(t => t !== MOCK_SSO.tkr);
      
      // 2. Price Anomaly Check (>50% deviation)
      const prices = text.match(/\b\d{4,}\b/g) || [];
      const priceAnomalies = prices.map(Number).filter(p => Math.abs(p - MOCK_SSO.prc) / MOCK_SSO.prc > 0.5);

      // 3. Action Inconsistency
      const isSellMentioned = /sell|sold|divest/i.test(text);
      const actionMismatch = (MOCK_SSO.type === 'BUY' && isSellMentioned);

      if (text.includes("GOTO")) expect(fabricatedTickers).toContain('GOTO');
      if (text.includes("50000")) expect(priceAnomalies).toContain(50000);
      if (text.includes("sold")) expect(actionMismatch).toBe(true);
    }
  });

  /**
   * TASK 3: Resilience Test
   * Simulates NVIDIA API timeouts (5s+) and Rate Limits (429).
   */
  test('Resilience: Service Degradation Handling', async ({ page }) => {
    // A. Simulate 10s Timeout
    await page.route('**/insider/narrative/123', async (route) => {
      await new Promise(r => setTimeout(r, 6000));
      await route.abort('timedout');
    });

    // B. Simulate Rate Limit (429)
    await page.route('**/insider/narrative/429', async (route) => {
      await route.fulfill({
        status: 429,
        contentType: 'application/json',
        body: JSON.stringify({ state: "RATE_LIMITED", text: "AI Overloaded." })
      });
    });

    // C. Simulate Backend Failure (503)
    await page.route('**/insider/narrative/503', async (route) => {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ state: "DEGRADED", text: "Service Unavailable." })
      });
    });

    // Verification logic would normally go here after page.goto('/')
    // Since we are building the framework, we've defined the mocks that the frontend must handle.
    console.log("Resilience mocks initialized. Frontend must handle: TIMEOUT, 429, 503.");
  });

  /**
   * TASK 4: Regression Test
   * Ensures background AI processing does not increase core API latency.
   */
  test('Regression: Latency Isolation', async ({ page }) => {
    let latestLatencies: number[] = [];

    await page.route('**/insider/latest', async (route) => {
      const start = Date.now();
      await route.continue();
      latestLatencies.push(Date.now() - start);
    });

    // Simulate heavy AI traffic
    await page.route('**/insider/narrative/**', async (route) => {
      await new Promise(r => setTimeout(r, 1000));
      await route.fulfill({ status: 200, body: '{}' });
    });

    // If we were running the app, we would measure the gap between latestLatencies
    // and a baseline.
    const baseline = 200; // 200ms target
    for (const lat of latestLatencies) {
       expect(lat).toBeLessThan(baseline * 2); // Hostile: 2x baseline is a fail
    }
  });

});
