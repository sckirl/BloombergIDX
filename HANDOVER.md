# 📑 BLOOMBERG-IDX: INSTITUTIONAL HANDOVER (May 10, 2026)

## 🎯 MISSION SUMMARY
Build a **Bloomberg-grade Asymmetric Intelligence Terminal** for Indonesian Equities (IDX). 
Focus: Insider Accumulation, Smart Money Flow, and Institutional-grade Signal Analysis.

---

## 🏛️ CURRENT STATE: SPRINT-1 v2.1 (ACTIVE)
We have completed **Day 1: Absorption & Governance**. The project has moved from a greenfield "hackathon" mindset to a high-rigor **Institutional Production Framework**.

### 1. The Execution Model (5-Layer Orchestration)
- **Layer 0:** Governance & Absorption (**COMPLETE**)
- **Layer 1:** Platform Foundations (**PENDING**)
- **Layer 2:** Data Intelligence & Adversarial QA (**PENDING**)
- **Layer 3:** UX Terminal & Visual QA (**PENDING**)
- **Layer 4:** Intelligence & Narrative (**PENDING**)

### 2. Strategic Memory (GEMINI.md)
The core instructions have been hardened with:
- **15 Institutional PM Execution Rules:** Mandatory orchestration discipline, continuous QA, and contract-first development.
- **Legacy System Orchestration Rules:** "Absorption before acceleration." No rewrites without measurable gain.
- **Adversarial QA Mandate:** QA agents are hostile auditors looking for reasons to reject merges.

---

## 🚩 AUDIT FINDINGS (THE "ROTS")
The system was audited by `MAP-01` and `QA-REGRESS-01` and flagged as **UNSTABLE**.
1. **Temporal Delusion:** Scrapers and seeders were hardcoded to 2026 (future).
2. **Brittle Parsing:** PDF parsing relies on fragile regex that will fail on real IDX formatting changes.
3. **Frontend Hallucination:** `package.json` targeted Next.js 16 (unstable). Must use v14.2.3 Stable.
4. **Data Quality Risk:** High reliance on unofficial `yfinance` instead of official/buffered sources.

---

## 📜 ESTABLISHED CONTRACTS (SOURCE OF TRUTH)
The following files were created to insulate new development from legacy rot:
- **`backend/contracts.py`**: Pydantic models for `InsiderTransaction`, `SignalTier` (HIGH/MEDIUM/LOW), and `MarketSummary`.
- **`frontend/src/types/contract.ts`**: TypeScript counterparts for 100% type safety.
- **`Sprint-1.md`**: The definitive 7-day roadmap with agent assignments and latency budgets.

---

## 🤖 NEXT STEPS: DAY 2-3 (FOUNDATION PHASE)
The next instance must deploy these agents in parallel:
1. **`DB-CORE-01` (Pro):** Incremental Supabase migrations for confidence scoring.
2. **`OBS-01` (Fast):** JSON logging + Sentry setup. (No logic before telemetry).
3. **`UI-SHELL-01` (Fast):** 3-panel terminal layout using `MOCK-API-01`.
4. **`SCR-KSEI-01` (Pro):** Playwright scraper with dynamic date logic.

---
*Status: Handover Ready. PM Agent Signing Off.*
