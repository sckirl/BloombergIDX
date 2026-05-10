# Sprint 2: NVIDIA Nemotron Intelligence Layer (Orchestrated)

**Objective:** Deploy an asynchronous, resilient summarization layer using NVIDIA Nemotron Nano, orchestrated through model-class parallel tracks.

## 🏛️ Model Classification & Roles
| Class | Purpose | Responsibility |
| :--- | :--- | :--- |
| **FAST** | Velocity | UI, glue logic, scaffolding, non-truth systems. |
| **PRO** | Integrity | Architecture, infra, contracts, integration stability. |
| **HEAVY** | Validation | Adversarial QA, complex reasoning, production gating. |

---

## 🏎️ Parallel Execution Tracks

### TRACK A: Infra & State Systems (PRO)
**Focus:** Lifecycle, resilience, and degraded-state handling.
- `STATE-MACHINE-01`: Implement the 9-state lifecycle (QUEUED to DEGRADED).
- `RETRY-ENGINE-01`: Implement exponential backoff for `FAILED_RETRYABLE` states.
- `REDIS-CORE-01`: Provision and optimize narrative cache and task queue.

### TRACK B: AI Compression Pipeline (PRO/FAST)
**Focus:** Preprocessing and deterministic compression.
- `SSO-PIPE-01` (PRO): Define the **Structured Signal Object** schema in the backend.
- `CCB-PIPE-01` (FAST): Implement the **Compact Context Builder** to flatten signals.
- `TOKEN-GUARD-01` (FAST): Enforce character limits (1,500 target) and payload deduplication.
- `PROMPT-CORE-01` (PRO): Engineer uncertainty-aware prompt templates for the LLM.

### TRACK C: NVIDIA Integration Layer (PRO)
**Focus:** Async generation and provider resilience.
- `NVIDIA-CLIENT-01`: Implement the OpenAI-compatible client with strict env var protection.
- `AI-QUEUE-01`: Integrate FastAPI `BackgroundTasks` for non-blocking triggers.
- `AI-CACHE-01`: Implement read-through caching and TTL lifecycle management.

### TRACK D: Terminal UX (FAST)
**Focus:** Non-blocking AI states and confidence visualization.
- `DRAWER-STATE-01`: Update the Institutional Drawer to support async data loading.
- `AI-STATUS-UX-01`: Implement status-specific UI labels (e.g., "SCANNING LEDGER...").
- `CONFIDENCE-UX-01`: Add visual indicators for probabilistic low-confidence narratives.

### TRACK E: Adversarial QA (HEAVY)
**Focus:** Hostile institutional auditing and production gating.
- `QA-AI-HALLUC-01`: Detect unsupported causality and fabricated smart money narratives.
- `QA-AI-FAIL-01`: Simulate rate limits and provider outages to verify UI optionality.
- `QA-AI-LATENCY-01`: Stress test the async queue and cache hit rates.
- `QA-AI-REGRESS-01`: Ensure AI enrichment does not degrade core terminal performance.

---

## 🛠️ Operational Policies
1.  **Dependency Flow:** SSO-PIPE -> CCB-PIPE -> PROMPT-CORE -> NVIDIA-CLIENT -> AI-CACHE -> DRAWER-STATE.
2.  **Continuous QA:** Track E executes in parallel with実装 from Day 1.
3.  **Pro Gating:** PRO agents must certify all contract and infra changes before merging.
4.  **Heavy Gating:** Production readiness is blocked until HEAVY QA sign-off.
5.  **No Exceptions:** No agent may redefine contracts, bypass cache, or call NVIDIA from the frontend.

---

## Technical Specifications
| Mandate | Implementation Detail |
| :--- | :--- |
| **Model** | `nvidia/nemotron-3-nano-30b-a3b` |
| **Async Engine** | FastAPI `BackgroundTasks` |
| **Input Target** | 1,200 - 1,800 chars (Max 2,500) |
| **Output Target** | 200 - 350 chars (Max 500) |
| **Reasoning Budget**| 512 - 1,024 |
| **Cache Store** | Redis (TTL tied to 15m polling sync) |
