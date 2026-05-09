# 🚩 BloombergIDX: Institutional Defect Ledger (May 10, 2026)

**Audit Status:** REJECTED (Zero-Trust Violation)
**QA Agents:** Senior Backend (SIT) & Senior Frontend (UAT) - [20 Years Experience]

---

## 🛠️ BACKEND & DATA PIPELINE DEFECTS (SIT)

| ID | Severity | Component | Description | Impact | Recommendation |
|:---|:---|:---|:---|:---|:---|
| **DEFECT-BACK-01** | **CRITICAL** | API (`main.py`) | **Fatal Missing Imports:** `models`, `run_scraper`, `InsiderTransaction`, and `date` are used but not imported. | Application fails to start or crashes immediately. | Add missing imports to `main.py`. |
| **DEFECT-BACK-02** | **CRITICAL** | Scraper (`scraper.py`) | **Dangerous Number Parsing:** Unsafe cleaning of financial numbers (`replace(".", "").replace(",", ".")`) ignoring Indonesian locale. | Order-of-magnitude errors in share counts. | Implement locale-aware decimal/thousands separator handling. |
| **DEFECT-BACK-03** | **CRITICAL** | Scraper (`scraper.py`) | **Share Hallucination Heuristic:** Uses `max(all_nums)` as a fallback for missing labels. | Captures non-transaction numbers (Tax IDs, Phones) as "Insider Shares." | Remove broad fallbacks; enforce strict label-based extraction. |
| **DEFECT-BACK-04** | **HIGH** | Schema (`models.py`) | **Flawed Unique Constraint:** `InsiderTransaction.source_url` prevents multi-transaction PDFs. | Significant data loss from multi-trade filings. | Remove `unique=True` from `source_url` or use composite key. |
| **DEFECT-BACK-05** | **HIGH** | Scraper (`scraper.py`) | **Race Condition in Ticker Creation:** Multi-threaded stock record creation causes crashes. | Partial ingestion failures due to UniqueConstraintViolation. | Implement `get_or_create` with locking or serial execution. |
| **DEFECT-BACK-06** | **HIGH** | Utils (`utils.py`) | **N+1 Query Explosion:** Scoring logic performs DB queries inside a loop per transaction. | Extreme latency during data ingestion. | Use bulk-load/prefetching for scoring context. |
| **DEFECT-BACK-07** | **HIGH** | API (`main.py`) | **Unprotected Scraper Concurrency:** Lack of locks for concurrent scraper triggers. | DB deadlocks and redundant processing. | Implement singleton lock for background scraping tasks. |
| **DEFECT-BACK-08** | **MED** | Schema (`models.py`) | **Precision Loss (`Float` Type):** Financial values stored as Float instead of Numeric. | Rounding errors in cumulative signals. | Migrate financial fields to `Numeric`. |
| **DEFECT-BACK-11** | **MED** | Utils (`utils.py`) | **yfinance Rate Limiting:** Synchronous calls without retry/backoff. | Scraper hangs or returns 0.0 values when blocked. | Implement asynchronous client with exponential backoff. |
| **DEFECT-BACK-14** | **LOW** | Telemetry (`logger.py`) | **Log Inconsistency:** Mixing `print` statements with structured JSON logging. | Breaks institutional monitoring pipelines. | Universal migration to `logger.info/error`. |

---

## 🖥️ FRONTEND & USER EXPERIENCE DEFECTS (UAT)

| ID | Severity | Component | Description | Impact | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DEFECT-FRONT-01** | **CRITICAL** | Core Layout | **Institutional Feature Loss (Regression)**. The "Institutional Drawer", "Price Map", and "Absorption Ratio" are absent from `page.tsx`. | Total failure to deliver primary "Killer Features". | Re-integrate Drawer and Intelligence components into `page.tsx`. |
| **DEFECT-FRONT-02** | **CRITICAL** | Footer | **Dead Command Input**. The main footer command bar has no event listeners or logic. | Primary UX interaction point is non-functional. | Bind input to `handleCommand` logic. |
| **DEFECT-FRONT-03** | **HIGH** | `page.tsx` | **Refresh Button Data Wipe**. The `REFRESH` button passes a `MouseEvent` to `fetchData`, which treats it as a ticker, wiping the table. | Critical loss of basic functionality. | Fix `onClick` to pass undefined/null by default. |
| **DEFECT-FRONT-04** | **HIGH** | Sidebar | **Dead Navigation**. Sidebar buttons have empty `onNav` handlers. | Users are trapped in the "Insider Feed" view. | Implement view-switching state machine. |
| **DEFECT-FRONT-05** | **HIGH** | `CommandPalette` | **Keyboard Inaccessibility**. Suggestions cannot be navigated with Arrow keys; mouse click required. | Violates institutional keyboard-first mandate. | Implement keyboard focus management for list items. |
| **DEFECT-FRONT-06** | **HIGH** | API Integration | **False Negative Search Results**. Search filters only the "Latest 1000" client-side. | Users will miss valid historical data. | Implement server-side search/ticker filtering. |
| **DEFECT-FRONT-07** | **MED** | `SignalFeed` | **Mock Data Dependency**. The Intelligence Feed uses static hardcoded signals. | No real-time intelligence delivery. | Connect to backend `/signals` endpoint. |
| **DEFECT-FRONT-08** | **MED** | Header | **Static Market Data**. IHSG and USDIDR values are hardcoded in the JSX. | Misleading market context. | Integrate live market index feed. |
| **DEFECT-FRONT-09** | **MED** | `contract.ts` | **Type Inconsistency**. Frontend interfaces differ from backend models. | High risk of runtime crashes. | Unify Type definitions across layers. |
| **DEFECT-FRONT-12** | **LOW** | UI Labels | **Unimplemented Shortcuts**. `ALT+S` and `ALT+Q` are listed but not coded. | Misleading interface. | Implement global keyboard listeners. |

---

## ⚖️ AUDITOR VERDICT
**FAILED.** The application is currently in a "Visual Prototype" state with critical functional regressions and dangerous data-parsing heuristics. Immediate rectification of **DEFECT-FRONT-01** and **DEFECT-BACK-01/02** is mandatory for project survival.
