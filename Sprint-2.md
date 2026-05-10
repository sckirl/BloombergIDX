# Sprint 2: NVIDIA Nemotron Intelligence Layer Integration

**Duration:** 7 Days  
**Objective:** Deploy an asynchronous, token-optimized summarization layer using NVIDIA Nemotron to generate Bloomberg-grade narratives from market signals.

## Core Architectural Mandates
1.  **Asynchronous Processing:** Narratives must be generated in the background using FastAPI `BackgroundTasks` to ensure terminal responsiveness.
2.  **Preprocessing Pipeline:** Raw data must be transformed via the 'Structured Signal Object' (SSO) and 'Compact Context Builder' (CCB) before being sent to the LLM.
3.  **Confidence Inheritance:** AI prompts must explicitly enforce probabilistic language (e.g., "suggests," "possible") for signals with confidence scores < 70.
4.  **Redis Caching:** Implementation of a persistent narrative cache to minimize NVIDIA API costs and latency.
5.  **Institutional Drawer Binding:** The frontend must expose narratives via the terminal's drill-down 'Drawer' component.
6.  **Token Efficiency:** Strict character limits (e.g., 2,500 for context, 500 for output) enforced at the middleware level.

---

## 7-Day Implementation Roadmap

### Day 1: Async Infrastructure & Caching Scaffolding
- **Infrastructure:** Provision Redis in `docker-compose.yml` for narrative caching.
- **Backend:** Initialize Redis client and define the narrative schema (`signal_id`, `model_version`, `narrative_text`, `status`).
- **Orchestration:** Implement FastAPI `BackgroundTasks` for non-blocking summary triggers.
- **Deliverable:** Verified async task queue with persistent Redis connectivity.

### Day 2: Preprocessing & Context Pipeline
- **SSO Implementation:** Define the `Structured Signal Object` (SSO) in `backend/models.py` to normalize filings, flow, and anomalies.
- **Context Builder:** Implement the `Compact Context Builder` (CCB) to flatten SSOs into dense strings.
- **Token Guard:** Implement a strict character-limit validator (max 2,500 chars) for NVIDIA payloads.
- **Deliverable:** Validated pipeline that transforms raw database records into LLM-ready context.

### Day 3: NVIDIA Nemotron Integration & Prompt Engineering
- **Integration:** Connect to `nvidia/nemotron-3-nano-30b-a3b` via `build.nvidia.com`.
- **Confidence Logic:** Engineering the "Institutional Narrator" prompt. 
    - *System Instruction:* "If confidence < 70, use probabilistic qualifiers. Do not declare certainty for weak signals."
- **Testing:** Unit tests to verify that low-confidence signals produce appropriately cautious narratives.
- **Deliverable:** Functional NVIDIA API client with uncertainty-aware prompting.

### Day 4: Narrative Service & Lifecycle Management
- **Task Logic:** Implement the narrative generation service with error handling, retries, and status updates (Pending -> Processing -> Success/Failure).
- **Cache Logic:** Implement "Read-Through" caching (check Redis first; if missing, trigger async generation and return `PENDING`).
- **Deliverable:** End-to-end narrative API with lifecycle tracking and caching.

### Day 5: Frontend Binding (Institutional Drawer)
- **UI Component:** Update the 'Institutional Drawer' (`src/app/Views.tsx`) to display narratives.
- **Data Binding:** Implement React hooks to fetch narratives; handle loading states and background refresh for `PENDING$ statuses.
- **Deliverable:** Real-time summary visualization in the terminal UI.

### Day 6: Token Optimization & Density Audit
- **Audit:** Conduct a "Token Efficiency Audit" to minimize boilerplate in both prompt and response.
- **Optimization:** Refine Nemotron's temperature and max_tokens to ensure high-density, "no-fluff" institutional output.
- **Cache TTL:** Set appropriate Redis expiration based on data freshness (15-minute polling sync).
- **Deliverable:** Optimized, low-latency summarization layer.

### Day 7: Adversarial QA & Validation
- **QA:** Run "Adversarial QA" (per `GEMINI.md`) to find contradictions between narratives and source data.
- **Regression:** Verify that the new summarization layer does not degrade existing terminal performance.
- **Handover:** Finalize `Sprint-2.md` and update `CHANGES.md`.
- **Deliverable:** Production-ready NVIDIA AI Integration.

---

## Technical Specifications (Mandates)

| Mandate | Implementation Detail |
| :--- | :--- |
| **Async Engine** | FastAPI `BackgroundTasks` |
| **Context Pipeline** | `Structured Signal Object` -> `Compact Context Builder` |
| **Confidence Cutoff** | Probabilistic language forced for scores < 70 |
| **Cache Store** | Redis (TTL tied to 15m polling interval) |
| **Model** | NVIDIA Nemotron-4 340B Instruct |
| **Token Limits** | Context: 2,500 chars / Narrative: 500 chars |
