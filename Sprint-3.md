# Sprint 3: Elite Events & Corporate Action Intelligence (Refined)

**Duration:** 7 Days  
**Objective:** Transform the 'EVENTS' module into a Bloomberg-grade temporal transaction database with automated valuation and full lifecycle auditability.

## 🏎️ Orchestrated Execution Tracks

### TRACK A: Event Timeline Engine (PRO)
**Focus:** Versioning, State Transitions, and Incremental Crawling.
- `LIFECYCLE-CORE-01`: Implement the versioned `CorporateEvent` model with `state_transition_log` and source hashing.
- `DIFF-ENGINE-01`: Build an incremental crawler that detects document mutations and triggers state revisions.
- `SYNC-GATE-01`: **MANDATORY GATE.** Certify lifecycle state truth before Track B/C execution.

### TRACK B: Valuation & PDF Extraction (PRO/HEAVY)
**Focus:** Financial logic and structured data extraction.
- `PDF-EXTRACT-01` (**PRO**): Implement robust PDF excerpting and normalization for deal terms.
- `VALUATION-CORE-01` (**HEAVY**): Build deterministic valuation logic for multiples (PE, PB, EV/EBITDA).
- `PREMIUM-ENGINE-01` (**HEAVY**): Implement premium/discount calculations relative to unaffected share prices.

### TRACK C: Market Enrichment & OpenBB (PRO)
**Focus:** Market context and peer benchmarking.
- `OPENBB-ADAPTER-01`: Integrate OpenBB for historical volatility and sector peer multiples.
- `BENCHMARK-CORE-01`: Correlate deal multiples against sector averages to identify 'Cheap' acquisitions.

### TRACK D: Bloomberg Deal-Sheet (FAST)
**Focus:** State Visibility, Auditability, and Drill-down Speed.
- `TIMELINE-UX-01`: Implement the visual event timeline (Announcement -> Revision -> Effective).
- `AUDIT-DRAWER-01`: Build a 'Source-to-State' drawer showing the original PDF snippet alongside the extracted terms.
- `DEGRADATION-UX-01`: Ensure core event data remains visible even if AI rationale fails.

### TRACK E: Temporal & Adversarial QA (HEAVY)
**Focus:** Transition validation and data veracity.
- `QA-TEMPORAL-01`: Validate state transition consistency over 100+ simulated event mutations.
- `QA-DATA-TRUTH-01`: Hostile audit of acquirer/target mapping and premium math.
- `QA-RESILIENCE-01`: Simulate OpenBB/NVIDIA outages to verify module optionality.

---

## 🏛️ Tactical Mandates
1.  **Temporal Integrity:** No event record may be overwritten. Every update creates a new version/snapshot.
2.  **AI Constraint:** AI is restricted to rationale tagging and summarization; it cannot define lifecycle states.
3.  **Synchronization:** Track A certification is required before Track B/C can consume 'Truth' states.
4.  **Performance:** Enforce document hashing to prevent redundant LLM/PDF parsing of unchanged filings.

---

## Technical Specifications
| Mandate | Implementation Detail |
| :--- | :--- |
| **Data Model** | Versioned `CorporateEvent` + `EventSnapshot` |
| **Enrichment** | OpenBB (Market Context) + Nemotron-4b (Rationale) |
| **Logic Authority** | Deterministic (Valuation) > AI (Summarization) |
| **UX Standard** | Audit-first; 10px Mono; Transition Timeline |

## 🔗 Cross-Module Enhancements (The "Missing Datapoints")
To immediately enhance all existing data streams (Insiders, Broker Flows, Market Microstructure) with the new Event Intelligence, the following datapoints must be added to Track B/C:

1. **Signal Convergence Linkage (Pre-Event Accumulation):**
   - *Datapoint:* `pre_event_insider_volume`, `pre_event_smart_money_score`
   - *Value:* Calculates the 30-day/60-day trailing insider and broker accumulation leading up to an event announcement. Directly answers: "Did insiders front-run this M&A?"
2. **Entity / UBO Resolution (Pulling from Phase 4):**
   - *Datapoint:* `acquirer_entity_id`, `target_entity_id`
   - *Value:* Maps raw text `acquirer` and `target` to canonical `entities` table to expose Ultimate Beneficial Owner (UBO), Nominee, and Politically Exposed Person (PEP) networks across events.
3. **Event Liquidity Absorption:**
   - *Datapoint:* `post_event_absorption_ratio`
   - *Value:* Ties Phase 2 Market Microstructure to Phase 3 Events by measuring how the market absorbed volume in the 3 days following the event state transition.

## 🎯 Unsolved Project KPIs (Agent Objectives)
Based on the `Full-Plan.md` vision, the agents must solve the following KPIs as part of the ongoing implementation:

1. **Signal Convergence Rate:** >85% of Corporate Events must successfully check for and link to historical Insider/Broker anomalies (connecting Phase 1/2 to Phase 3).
2. **Entity Resolution Veracity:** >95% accuracy in mapping unstructured Acquirer/Target names from raw PDFs to canonical Entity IDs.
3. **Event Processing Latency:** < 60m delay from IDX PDF publication to a fully enriched, deterministic Valuation state visible on the Terminal.
4. **Temporal State Accuracy:** 100% pass rate on `QA-TEMPORAL-01`, ensuring zero data overwrites and perfect state transition logging over simulated mutations.

## 🛑 STRICT QA DATA INTEGRITY MANDATE
**The following directives override any prior instructions regarding data generation:**
- **Zero Hallucination Tolerance:** ABSOLUTELY NO mocked, generated, or hallucinated financial numbers, IDR prices, multiples, volume data, or entity relationships are permitted in the system or the UI.
- **External Truth Verification:** QA must actively independently verify all numbers presented in the terminal against external, real-world truth sources (e.g., live IDX feeds, Bloomberg, Yahoo Finance/yfinance).
- **Fallback Protocol:** If the current data source (e.g., a specific PDF extraction or static file) is found to be inaccurate or hallucinated compared to real-world data:
    1. QA immediately flags the module as `FAILED_TRUTH_CHECK`.
    2. The BA (Business Analyst) and PM (Project Manager) must immediately research and define the most reliable API or data pipeline to fetch the live, accurate data.
    3. The Dev agent is re-tasked to implement the new, real-world data stream before any further progress is made.
- Every single number in the project must reflect real-world values, as financial inaccuracies will catastrophically cascade through the valuation and scoring logic.
