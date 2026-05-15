# 🚩 BloombergIDX: Institutional Defect Ledger (May 12, 2026)

**Audit Status:** 🚨 REJECTED - FABRICATION & DRIFT DETECTED
**QA Agents:** Senior Backend (SIT), Senior Frontend (UAT), HEAVY Reliability Engineer
**PM Orchestrator Score:** 82/100

---

## 🏛️ SPRINT-3 ADVERSARIAL AUDIT FINDINGS

### 🚨 CRITICAL: DATA FABRICATION
| ID | Severity | Component | Description | Status |
|:---|:---|:---|:---|:---|
| **DATA-FAB-01** | **CRITICAL** | Frontend | **Market Data Fabrication.** IHSG and USDIDR numbers are hardcoded and randomized using `Math.random()`. Direct violation of "avoid fake data" mandate. | **OPEN** |
| **DRIFT-01** | **HIGH** | Backend | **Migration Drift.** `corporate_events` and `event_snapshots` tables are missing from `database.db`, causing the EVENTS module to show empty states erroneously. | **OPEN** |
| **EVT-LIFE-01** | **MED** | Scraper | **Lifecycle Incompleteness.** `event_scraper.py` lacks mapping for `POSTPONED` or `WAITING` states. | **OPEN** |
| **EVT-COLL-01** | **MED** | Logic | **Collision Risk.** Deduplication based only on name/type; multiple revisions of the same event will collide and overwrite. | **OPEN** |
| **UX-HIER-01** | **LOW** | Visual | **Hierarchy Collapse.** Global `10px !important` reset overrides intended visual cues (headers, big numbers). | **OPEN** |

---

## 🛠️ BACKEND & INTELLIGENCE DEFECTS

| ID | Severity | Component | Description | Status |
|:---|:---|:---|:---|:---|
| **CONF-01** | **HIGH** | AI Logic | **Confidence Decoupling.** AI narratives do not consistently inherit and display the `confidence_score` in the UI. | **OPEN** |
| **OCR-01** | **MED** | Scraper | **OCR Failure Modes.** `test_ocr_accuracy.py` identifies unresolved edge cases in PDF-based disclosure scraping. | **OPEN** |
| **PHANTOM-01** | **HIGH** | Implementation | **Phantom Feature (PEE).** UI shells for "Politically Exposed Entity Mapping" exist without any backend engine. | **OPEN** |
| **RELY-01** | **MED** | Pipeline | **Post-Process Dependency.** Core pipeline is overly dependent on `repair_data.py` to fix malformed ingestion. | **OPEN** |

---

## 🏁 MISSION CERTIFICATION: SPRINT-3

### 📉 STATUS: FAILED (82/100)
The platform fulfills the "Structural Shell" but fails the "Elite Veracity" mandate. 

### ⚖️ AUDITOR VERDICT
**REJECTED.** Implementation of real-time market data for IHSG/USDIDR and stabilization of the event database schema are mandatory before any further progress. 🇮🇩🏁

---

## 📈 SPRINT-3 STRATEGIC RECOMMENDATIONS (PM & BA EVALUATION)

### 1. MAP Module Visualization Assessment
**Finding:** The current Sector Heatmap is functionally active but visually inadequate for rapid institutional decision-making. Users cannot easily discern the relative weight or urgency of the sector action.
**Recommendations for DEV Team:**
- **Visual Weighting (Treemap):** Migrate from a uniform grid to a Treemap layout where the *size* of the box is proportional to the Sector's Market Cap or Total Traded Volume, and the *color intensity* maps to the Net Flow ratio.
- **Contextual Baselines:** "Net Flow of 5 Trillion" is meaningless without a baseline. The UI must display the flow *relative* to the 30-day average. 
- **Defect Logged:** `UX-MAP-02 (MED)` - Heatmap lacks spatial weighting and baseline context.

### 2. Event Intelligence (E-IPO & Mergers) Feasibility & Data Depth
**BA Assessment:** Consolidating E-IPO and M&A data into a single "Corporate Actions" or "Deal-Sheet" section is highly strategic and standard for tier-1 terminals. 
**Data Requirements for Asymmetric Edge:**
To be useful, simply listing the news is insufficient. We need to extract and calculate:
1.  **Valuation Multiples:** Acquirer P/E, Target P/E, Implied EV/EBITDA of the deal. (Identifies "cheap" vs "expensive" acquisitions).
2.  **Premium Analysis:** % Premium of the offer price over the 30-day Volume Weighted Average Price (VWAP) prior to the announcement.
3.  **Signal Convergence:** Did the `insider_transactions` or `broker_flow` tables show abnormal accumulation in the target company 30 days *before* the 'Negotiation' announcement? 
**Volume/Scale:** The IDX sees roughly 50-80 IPOs and 20-40 major M&A events annually. The value is not in high velocity, but in **High Veracity** and deep linkage to existing modules.
**Defect Logged:** `ARCH-EVT-02 (HIGH)` - Event module requires Valuation Engine and Signal Convergence logic to provide an asymmetric edge.

---
**PM Directive to DEV Teams:** Review the updated `Sprint-3.md` and `Full-Plan.md` for the architectural blueprints to resolve these strategic defects. Do not proceed with manual hacks; implement the Temporal Engine and Treemap components.

