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
