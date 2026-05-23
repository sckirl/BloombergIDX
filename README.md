# BloombergIDX: Indonesian Asymmetric Intelligence Terminal

BloombergIDX is an institutional-grade intelligence platform designed to identify asymmetric signals within the Indonesian equity market (IDX). Unlike standard stock dashboards, this system focuses on identifying "Smart Money" activity, insider accumulation, and stealth distribution patterns before they are fully priced in by the broader market.

The platform provides a high-density, command-first interface inspired by the Bloomberg Terminal DNA, optimized for professional traders, quantitative analysts, and institutional desks.

---

## 1. Core Intelligence Modules

### Insider Intelligence
*   **Conviction Scoring**: Real-time analysis of Director and Commissioner disclosures using a weighted scoring model (Role, Value, RVOL, and Cluster Buy signals).
*   **Accumulation Price Map**: Visual volume profile indicating the specific price levels where insiders are concentrating their capital.
*   **Absorption Ratio**: A liquidity metric measuring insider buy volume relative to the 30-day Average Daily Volume (ADV).

### Smart Money & Broker Flow
*   **Bandar Proxy Detection**: Advanced rules-based detection of market-maker activity through broker concentration (HHI) and cross-trade patterns.
*   **Broker Clustering**: Identifying coordinated accumulation across top-tier Indonesian sekuritas (brokers).
*   **Stealth Accumulation Scanner**: Detection of positive net broker flow during periods of low price volatility.

### Corporate Event Intelligence
*   **Temporal Event Lifecycle**: A versioned database tracking the full lifecycle of E-IPOs, Mergers, Acquisitions, and Divestments.
*   **Valuation Engine**: Automated calculation of deal multiples (P/E, P/B, EV/EBITDA) and premiums relative to unaffected share prices.
*   **Audit Transparency**: Direct "Source-to-State" linkage, providing original PDF snippets alongside extracted transaction terms.

### AI Narrative Layer
*   **Asynchronous NLP**: Powered by NVIDIA Nemotron-4b, providing concise, high-density summaries of complex filings.
*   **Confidence Inheritance**: AI narratives strictly adhere to deterministic data confidence, using probabilistic language for lower-scored signals.

---

## 2. Technical Stack

*   **Frontend**: Next.js 14 (App Router), Tailwind CSS, TanStack Table, Recharts.
*   **Backend**: FastAPI (Python 3.11), SQLAlchemy 2.0.
*   **Data Pipeline**: Playwright (Playwright-context fetches), BeautifulSoup4, PDFPlumber.
*   **Intelligence**: NVIDIA Build API (Nemotron-mini-4b-instruct), yfinance.
*   **Persistence**: PostgreSQL (Core Data), Redis (Narrative Cache & Task Queue).
*   **Infrastructure**: Docker, Docker Compose.

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
    Create a `.env` file in the root directory:
    ```bash
    NVIDIA_API_KEY=your_api_key_here
    DATABASE_URL=postgresql://user:password@openinsider-db:5432/openinsider
    REDIS_URL=redis://openinsider-redis:6379/0
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

BloombergIDX is architected for low-cost, high-efficiency execution on Google Cloud Platform.

### Steps
1.  **Containerize**: Build and push images to Google Artifact Registry.
2.  **Database**: Provision a Cloud SQL (PostgreSQL) instance.
3.  **Caching**: Provision a Memorystore (Redis) instance.
4.  **Deployment**:
    *   Deploy the backend to Cloud Run. Ensure you set the `DATABASE_URL` and `REDIS_URL` environment variables.
    *   Deploy the frontend to Cloud Run (or Vercel). Set `NEXT_PUBLIC_API_URL` to your backend's Cloud Run URL.
5.  **Scheduling**: Use Google Cloud Scheduler to trigger the `/insider/scrape` and `/insider/enrich` endpoints every 15 minutes.

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
