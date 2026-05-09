# 🏛️ SPRINT-1: Institutional Production Framework (v2.1)
**Strategy:** 5-Layer Orchestration | Adversarial QA | Legacy Absorption
**Goal:** High-confidence IDX Intelligence Terminal (LQ45 Scope)

---

## 🏗️ 1. THE 5-LAYER EXECUTION MODEL

### LAYER 0: GOVERNANCE, CONTRACTS & ABSORPTION (Day 1)
| Agent ID | Task | Model | Dependency |
| :--- | :--- | :--- | :--- |
| **MAP-01** | **The Explorer:** Audit existing architecture, DB, and APIs. Map integration boundaries. | Pro 3 | None |
| **CONTRACT-01** | **The Source:** OpenAPI schemas & Pydantic models (Must respect existing DB). | Pro 3 | MAP-01 |
| **QA-REGRESS-01**| **Legacy Auditor:** Hostile audit of existing features to establish stability baseline. | Pro 3 | MAP-01 |

### LAYER 1: PLATFORM FOUNDATIONS & TELEMETRY
| Agent ID | Task | Model | Dependency |
| :--- | :--- | :--- | :--- |
| **DB-CORE-01** | **The Ledger:** Supabase migrations (Additive/Incremental, NO drops). | Pro 3 | CONTRACT-01 |
| **OBS-01** | **The Eye:** JSON logging + telemetry. Mandatory BEFORE logic implementation. | Flash 3 | CONTRACT-01 |
| **CACHE-01** | **The Shield:** Redis TTL & Invalidation based on data freshness requirements. | Pro 3 | CONTRACT-01 |

### LAYER 2: DATA INTELLIGENCE & ADVERSARIAL QA
| Agent ID | Task | Model | Dependency |
| :--- | :--- | :--- | :--- |
| **SCR-KSEI-01** | **The Insider:** KSEI Playwright scraper. Must handle site-change detection. | Pro 3 | DB-CORE-01 |
| **VALID-01** | **Truth Master:** Signal Truth Hierarchy + Confidence (0-100) scoring. | Pro 3 | SCR-KSEI-01 |
| **QA-DATA-01** | **Hostile Auditor:** Search for data contradictions, nulls, and duplicate leaks. | Pro 3 | VALID-01 |

### LAYER 3: UX TERMINAL & VISUAL QA
| Agent ID | Task | Model | Dependency |
| :--- | :--- | :--- | :--- |
| **UI-SHELL-01** | **The Matrix:** Next.js layout, 3-panel system, institutional density. | Flash 3 | MOCK-API-01 |
| **CMD-PAL-01** | **The Lexicon:** Command Palette (⌘K) with rigid regex routing. | Flash 3 | UI-SHELL-01 |
| **QA-UI-01** | **Visual Auditor:** Break the UI. Test resizing, latencies, and keyboard-only flows. | Flash 3 | UI-SHELL-01 |

### LAYER 4: INTELLIGENCE & PROBABILISTIC NARRATIVE
| Agent ID | Task | Model | Dependency |
| :--- | :--- | :--- | :--- |
| **SCORER-01** | **The Judge:** ConvictionScorer (Insider Delta + Volume Sigma). | Codex 5.3 | VALID-01 |
| **AI-NARR-01** | **The Narrator:** Conditional AI narratives (Must inherit confidence score). | Codex 5.3 | SCORER-01 |
| **QA-INTEL-01** | **Logic Auditor:** Expose false confidence and rank-stability issues. | Codex 5.3 | SCORER-01 |

---

## 📅 4. DELIVERY WORKFLOW (Non-Greenfield)

| Day | Phase | Key Milestone | Status |
| :--- | :--- | :--- | :--- |
| **D1** | **Absorption** | `MAP-01` completes system audit. Contracts finalized. | **COMPLETE** |
| **D2-D3**| **Foundation** | DB and Mocks live. Scrapers start with telemetry. | **PENDING** |
| **D4** | **Scoring** | Confidence scoring live. Scorer v1 logic verified. | **PENDING** |
| **D5** | **Integration** | Mock-to-Live swap. Regression check against existing UI. | **PENDING** |
| **D6** | **Stabilization**| **MANDATORY:** Adversarial load testing & telemetry validation. | **PENDING** |
| **D7** | **Launch** | Adversarial QA sign-off + Production Promote. | **PENDING** |

---

## 🛡️ 5. OPERATIONAL POLICIES & RISKS
*   **Adversarial Mandate:** QA agents are task to find reasons to REJECT merges, not to confirm them.
*   **Truth Policy:** Silence is better than fabrication. If data is stale, show `STALE`. If missing, show `MISSING`.
*   **Legacy Rule:** No re-implementation of existing logic unless it fails `QA-REGRESS-01` audit.

### 🚩 HOSTILE AUDIT FINDINGS (May 10, 2026)
1. **Temporal Delusion:** Hardcoded dates for 2026 in scrapers/seeders. Fix: Parameterize dates.
2. **Brittle Parsing:** Regex-based PDF parser is highly fragile. Fix: Implement structure-aware parsing (QA-DATA-01).
3. **Frontend Hallucination:** Next.js version 16 in package.json (unstable). Fix: Downgrade to 14.2.3 Stable.
4. **Hardcoded Infra:** Fixed DB IPs in code. Fix: Use environment variables via `pydantic-settings`.
5. **Low-Quality Data:** Reliance on unofficial `yfinance`. Fix: Establish OpenBB/Official fallback buffers.


---
*Status: SPRINT-1 v2.1 (BLOOMBERG-GRADE) ACTIVE.*
