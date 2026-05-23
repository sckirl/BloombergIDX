# Sprint 4: Production Hardening — QA Gates, Performance, & Launch

**Duration:** Weeks 14–16  
**Objective:** Execute heavy QA validation, optimize performance across the stack, integrate final legal/compliance requirements, and officially launch the terminal.

## 🏎️ Orchestrated Execution Tracks (Parallelized)

### TRACK A: Heavy QA Gates (HEAVY)
**Focus:** Prove data integrity and model predictive value. *Must complete before LAUNCH-01.*
- `PARSER-QA-01` (**HEAVY**):
  - Validate all 4 data parsers against 90 days of raw scrape artifacts.
  - Assert OHLCV values match IDX official summaries (0.01% price tolerance).
  - Verify deduplication logic and KSEI filing exact matches.
  - Assert broker net flows sum to zero.
- `SCORE-QA-01` (**HEAVY**):
  - Backtest conviction scoring against 10 historical IDX events (positive) and 10 boring stocks (negative).
  - Perform sensitivity analysis on component weights.
- `BANDAR-QA-01` (**HEAVY**):
  - Validate 5 bandar detection rules.
  - Implement suppression rules for legitimate corporate events (buybacks, rights issues, index rebalancing).
  - Ensure false positive rate < 10%.
  - Verify narrative softening (e.g., "unusual pattern" instead of "manipulation").

### TRACK B: Performance & Infrastructure (PRO)
**Focus:** Optimize speed and resource usage.
- `PERF-AUDIT-01` (**PRO**):
  - Run Lighthouse on Frontend (LCP < 2.0s, CLS < 0.1, TBT < 200ms).
  - Add Next.js image optimization, route code splitting, and font preloading.
  - Run `EXPLAIN ANALYZE` on top 10 backend queries, add indexes.
  - Profile Playwright memory usage (peak < 512MB/pod).
- `CACHE-WARM-01` (**PRO**):
  - Implement cron jobs to pre-warm Redis cache before market open (08:30 WIB).
  - Implement intelligent cache invalidation on new filings.

### TRACK C: Launch & Compliance (FAST)
**Focus:** Final mile user experience and legal safety.
- `LEGAL-COMP-01` (**FAST**):
  - Add `/methodology` page.
  - Add disclaimers: "For informational purposes only. Not investment advice."
  - Ensure zero personal data/tracking/cookies.
- `LAUNCH-01` (**FAST**):
  - Execute final smoke test checklist.
  - Once PARSER-QA-01, SCORE-QA-01, and BANDAR-QA-01 pass, trigger deployment to production.

## 🏛️ Tactical Mandates
1. **Zero Hallucination:** QA must fail any process producing fabricated data.
2. **Performance:** Backend responses must be <300ms (cached) or <800ms (uncached p95).
3. **Legal Compliance:** Never imply illegal activity in AI summaries. Use strictly neutral terminology.
4. **Done Definition:** Feature is deployed, tested, and works end-to-end on live data. 90% quality is acceptable for launch; iterate in post-launch waves.
