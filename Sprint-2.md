# Sprint 2: NVIDIA Nemotron Intelligence Layer Integration (Refined)

**Duration:** 7 Days  
**Objective:** Deploy an asynchronous, resilient, and token-optimized summarization layer using NVIDIA Nemotron Nano to generate Bloomberg-grade narratives from market signals.

## 🛡️ AI Resilience Mandates (Advisor Certified)
1.  **Optionality:** The platform MUST remain fully functional even if the NVIDIA API is offline.
2.  **Zero-Blocking:** AI generation is strictly asynchronous. UI interactions never wait for LLM responses.
3.  **Confidence Inheritance:** Prompts explicitly enforce probabilistic language (e.g., "may indicate") for signals with confidence < 70.
4.  **Adversarial QA:** The layer is not "trusted"; it is audited for hallucinations and data drift by dedicated QA agents.
5.  **State Transparency:** The UI must explicitly report degraded or pending AI states rather than showing generic spinners.

---

## 🏛️ Core Architectural Specifications

### 1. Narrative State Machine
- `QUEUED`: Signal detected, awaiting background worker.
- `PROCESSING`: Payload sent to NVIDIA.
- `SUCCESS`: Narrative cached and ready.
- `FAILED_RETRYABLE`: Network/Rate limit error.
- `FAILED_FINAL`: Content safety or logic error.
- `DEGRADED`: Provider outage; showing "Narrative Unavailable".

### 2. Token & Model Standardization
- **Model:** `nvidia/nemotron-3-nano-30b-a3b`
- **Input Budget:** Target 1,500 chars (Max 2,500).
- **Output Budget:** Target 250 chars (Max 500).
- **Reasoning Budget:** 512 - 1024 (Zero waste policy).

---

## 7-Day Implementation Roadmap

### Day 1: Async Infrastructure & Resilience Scaffolding
- **Infrastructure:** Provision Redis in `docker-compose.yml` for narrative caching.
- **Backend:** Initialize Redis and define the `NarrativeState` enum (QUEUED to DEGRADED).
- **Fallback:** Implement the `DEGRADED` mode toggle to suppress AI components globally if error rates spike.
- **Deliverable:** Verified async queue and failure-aware backend skeleton.

### Day 2: SSO & Compact Context Builder
- **SSO:** Define the `Structured Signal Object` to normalize raw filings into dense JSON.
- **CCB:** Implement the `Compact Context Builder` to flatten SSOs into high-density prompt strings.
- **Deduplication:** Hash payloads (`filing_hash` + `prompt_version`) to prevent redundant API calls.
- **Deliverable:** Validated pipeline that prepares 1,500-char context blocks.

### Day 3: NVIDIA Nemotron Nano Integration
- **Client:** Implement OpenAI-compatible client with `NVIDIA_API_KEY` env var protection.
- **Prompt Engineering:** Standardize the "Bloomberg Terminal" style: dense, filler-free, and probabilistic.
- **Confidence Logic:** Integrate `confidence_score` into the prompt template.
- **Deliverable:** Functional API client with uncertainty-aware prompting.

### Day 4: Narrative Lifecycle Service
- **Service:** Implement the read-through cache service (Check Redis -> Return SUCCESS/PENDING -> Trigger Async).
- **Cleanup:** Implement TTL-based cache expiration tied to the 15m scraping interval.
- **Retry Logic:** Handle `FAILED_RETRYABLE` states with exponential backoff.
- **Deliverable:** Production-ready narrative management service.

### Day 5: Frontend Degradation Handling
- **UI:** Update `InstitutionalDrawer` to handle all 9 state machine statuses.
- **UX:** Replace generic spinners with status-specific labels (e.g., "SCANNING LEDGER...", "AI UNAVAILABLE").
- **Visuals:** Add high-visibility "Low Confidence" styling for probabilistic narratives.
- **Deliverable:** Resilient UI that gracefully handles AI instability.

### Day 6: Performance & Token Audit
- **Audit:** Conduct a "Token Efficiency Audit" to minimize boilerplate.
- **Optimization:** Refine Nemotron's temperature (0.2-0.4) for factual consistency.
- **Latency:** Verify async generation takes < 5 seconds from queue to cache.
- **Deliverable:** Optimized, low-cost intelligence layer.

### Day 7: Adversarial QA Strike
- **QA-AI-HALLUC:** Hostile audit to detect unsupported causality claims.
- **QA-AI-FAIL:** Simulate rate limits and outages to verify UI optionality.
- **QA-AI-LATENCY:** Stress test the async queue with 100+ concurrent signals.
- **Deliverable:** Sprint-2 Certification and Handover.

---

## Technical Specs Summary
| Component | Detail |
| :--- | :--- |
| **Async Engine** | FastAPI `BackgroundTasks` |
| **Model** | `nvidia/nemotron-3-nano-30b-a3b` |
| **Style** | Dense Bloomberg-tier, Probabilistic |
| **Cache Key** | `ticker` + `filing_hash` + `prompt_version` |
| **Safety** | Zero API keys in source, logs, or prompts |
