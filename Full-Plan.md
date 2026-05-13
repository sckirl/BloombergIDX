# BloombergIDX: Full Strategic Plan & Vision

## 🗺️ Vision Statement
To build the **Single Source of Truth (SSOT)** for Indonesian asymmetric equity intelligence, providing a Bloomberg-grade temporal intelligence terminal for Smart Money, Insider activity, and Corporate Actions.

---

## 🚀 Execution Phases

### Phase 1: Foundational Terminal (COMPLETED)
- **Terminal DNA:** 3-panel UI, 10px Mono font, Command Palette.
- **Insider Intelligence:** Full IDX disclosure ingestion and confidence scoring.
- **Infrastructure:** Docker-first orchestration with Redis caching.

### Phase 2: Intelligence Enrichment (COMPLETED)
- **NVIDIA AI Layer:** Async summarization using Nemotron-4b.
- **Market Microstructure:** Broker flow proxies, RVOL anomalies, and sector heatmaps.
- **Data Veracity:** 4V metrics achieved (Volume, Velocity, Variety, Veracity).

### Phase 3: Temporal Event Intelligence (ACTIVE - Sprint 3)
- **Lifecycle Engine:** 1:1 Bloomberg M&A tracking with full version history and transition timelines.
- **Valuation Layer:** Deterministic deal multiples and premium analytics enriched by OpenBB.
- **Auditability:** Source-to-State transparency with raw PDF excerpts and AI-tagged rationales.

### Phase 4: Quant Flow & Network Mapping (UPCOMING)
- **Broker Clustering:** Identifying 'Bandar' proxies via historical trade correlation.
- **PEP Mapping:** Cross-referencing entity ownership with political/nominee networks.
- **Predictive Engine:** Signal convergence detection (Insider + Anomalies + M&A).

### Phase 5: Institutional API & Handover
- **Predictive Intelligence:** Conviction-weighted price target estimations.
- **Institutional JSON Stream:** High-velocity API for quantitative trading desks.

---

## 🛡️ Foundational Mandates

### 1. Stability First (Freeze & Compose)
Once a module passes Phase-Final QA, it is **FROZEN**. New features are implemented via isolated services or composition.

### 2. Temporal Auditability
Intelligence systems must track *how* and *when* information changed. Snapshot-only data is rejected as non-institutional.

### 3. Institutional UX
- Speed over aesthetics.
- Information density over whitespace.
- Command-first navigation.
- 10px Mono is the terminal law.

---

## 📈 Long-Term KPIs
- **Latency:** < 15m delay for Insider signals; < 60m for Event timelines.
- **Veracity:** 99.9% accuracy on Acquirer/Target mapping and Deal Multiples.
- **Resilience:** 100% platform availability even during AI provider outages.
