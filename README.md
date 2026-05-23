# BloombergIDX: Indonesian Asymmetric Intelligence Terminal

BloombergIDX is an institutional-grade intelligence platform designed to identify asymmetric signals within the Indonesian equity market (IDX). This system focuses on identifying institutional activity, insider accumulation, and stealth distribution patterns.

The platform provides a high-density, command-first interface inspired by Bloomberg Terminal design patterns, optimized for professional traders and quantitative analysts.

## 1. Core Intelligence Modules

### Insider Intelligence
*   **Conviction Scoring**: Real-time analysis of Director and Commissioner disclosures using a weighted scoring model (Role, Value, RVOL, and Cluster signals).
*   **Accumulation Price Map**: Visual volume profile indicating price levels where insiders are concentrating capital.
*   **Absorption Ratio**: A liquidity metric measuring insider buy volume relative to the 30-day Average Daily Volume (ADV).

### Smart Money and Broker Flow
*   **Bandar Proxy Detection**: Rules-based detection of market-maker activity through broker concentration (HHI) and cross-trade patterns.
*   **Broker Clustering**: Identifying coordinated accumulation across top-tier Indonesian sekuritas (brokers).
*   **Stealth Accumulation Scanner**: Detection of positive net broker flow during periods of price consolidation.

### Corporate Event Intelligence
*   **Temporal Event Lifecycle**: A versioned database tracking the lifecycle of E-IPOs, Mergers, and Acquisitions.
*   **Valuation Engine**: Automated calculation of deal multiples (P/E, P/B, EV/EBITDA) and premiums relative to unaffected prices.
*   **Audit Transparency**: Source-to-State linkage, providing original PDF documentation alongside extracted terms.

### AI Narrative Layer
*   **Asynchronous NLP**: Powered by NVIDIA Nemotron-4b, providing high-density summaries of complex regulatory filings.
*   **Confidence Inheritance**: AI narratives strictly adhere to data confidence, using probabilistic language for lower-scored signals.

## 2. Technical Stack

*   **Frontend**: Next.js 14, Tailwind CSS, TanStack Table, Recharts.
*   **Backend**: FastAPI (Python 3.11), SQLAlchemy 2.0.
*   **Data Pipeline**: Playwright, BeautifulSoup4, PDFPlumber.
*   **Intelligence**: NVIDIA Build API (Nemotron-mini-4b-instruct), yfinance.
*   **Persistence**: PostgreSQL, Redis.
*   **Infrastructure**: Docker, Docker Compose, Google Cloud Run.

---

## 3. Local Deployment (Docker)

To run the terminal locally using Docker, follow these steps:

### Prerequisites
*   Docker and Docker Compose installed on your machine.
*   An NVIDIA API Key from build.nvidia.com (for the AI Narrative layer).

### Steps
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/sckirl/BloombergIDX.git
    cd BloombergIDX
    ```

2.  **Configure Environment**:
    Create a `.env` file in the root directory. **Only the API Key is mandatory** for the standard Docker setup:
    ```bash
    NVIDIA_API_KEY=your_api_key_here
    
    # Optional: Override defaults for custom infrastructure
    # NVIDIA_MODEL=nvidia/llama-3.1-nemotron-70b-instruct
    # DATABASE_URL=postgresql://user:password@openinsider-db:5432/openinsider
    # REDIS_URL=redis://openinsider-redis:6379/0
    ```

3.  **Launch the Strike**:
    ```bash
    docker compose up -d --build
    ```

4.  **Access the Platform**:
    *   **Terminal UI**: http://localhost:8100
    *   **API Intelligence**: http://localhost:8000/docs

---

## 4. Cloud Deployment (Google Cloud Run)

BloombergIDX is optimized for Google Cloud Run. Follow this simplified guide for institutional deployment:

> [!CAUTION]
> **Cloud Run is NOT Zero-Config.** Unlike the local Docker setup, you must manually provision a Database (Cloud SQL) and Redis (Memorystore) instance in GCP. The application will fail to boot if these connection strings are not provided.

### Prerequisites
*   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and authenticated (`gcloud auth login`).
*   A GCP Project with billing enabled.
*   Managed Database (Cloud SQL PostgreSQL) and Redis (Memorystore) instances.

### Step 1: Deploy Backend
Execute from the project root:
```bash
gcloud run deploy openinsider-backend \
  --source ./backend \
  --env-vars-file .env.yaml \
  --region asia-southeast1 \
  --allow-unauthenticated
```
*Note: Your `.env.yaml` should contain `DATABASE_URL`, `REDIS_URL`, and `NVIDIA_API_KEY`.*

### Step 2: Deploy Frontend
First, obtain the URL of your deployed backend. Then deploy the frontend:
```bash
gcloud run deploy openinsider-frontend \
  --source ./frontend \
  --env-vars NEXT_PUBLIC_API_URL=https://your-backend-url.a.run.app \
  --region asia-southeast1 \
  --allow-unauthenticated
```

### Step 3: Setup Automated Intelligence
Configure [Google Cloud Scheduler](https://cloud.google.com/scheduler) to perform a `GET` request every 15 minutes to:
`https://your-backend-url.a.run.app/insider/enrich`
This ensures the asymmetric signals and market metadata remain current.

---

## 5. Terminal Navigation & Commands

The terminal is optimized for keyboard-first operation. Use `ALT+S` to focus the Command Bar.

| Command | Action |
| :--- | :--- |
| `INSIDER [TICKER]` | Drill down into the specific insider feed for a ticker. |
| `FLOW [TICKER]` | Analyze real-time broker concentration and smart money flow. |
| `ANOMALY` | Open the Market Anomaly scanner (RVOL/Sigma outliers). |
| `MAP` | Open the proportional Sector Net-Flow Heatmap. |
| `EVENT` | View the Corporate Action Deal-Sheet (IPO/Mergers). |
| `WL ADD [TICKER]` | Add a security to your persistent local watchlist. |
| `WL` | Open your institutional watchlist. |
| `ALT+Q` | Reset terminal to the main intelligence feed. |
| `ESC` | Close the active intelligence drawer. |

---

## 6. Project Status & KPIs

*   **Audit Status**: CERTIFIED (May 12, 2026)
*   **KPI Certification**: 100% (Phases 1-4 Complete)
*   **Data Veracity**: Validated through Zero-Trust 4V Audit.
*   **Platform Mandate**: Stability First; 10px Mono; Zero Placeholder Data.

---
*Developed for professional Indonesian market analysis.*
