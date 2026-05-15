# Deployment Guide: BloombergIDX on Google Cloud

This guide outlines the fastest and most secure way to deploy the BloombergIDX platform, including the OpenBB integration, onto Google Cloud Platform (GCP).

## Architecture
We use **Google Cloud Run** for serverless, scalable container execution.
- **Frontend:** Next.js deployed on Cloud Run.
- **Backend:** FastAPI deployed on Cloud Run.
- **Database:** Cloud SQL for PostgreSQL.
- **Cache/Queue:** Memorystore for Redis.
- **OpenBB:** Hosted OpenBB Platform API (deployed via a separate Cloud Run service).

---

## Step 1: Database & Cache Setup
1. **Cloud SQL:**
   - Create a PostgreSQL 15 instance in Cloud SQL.
   - Note the `Connection Name` (e.g., `project-id:region:instance-id`).
   - Create a database named `openinsider` and a strong password for the default user.
2. **Memorystore (Redis):**
   - Create a Redis instance in the same region as your Cloud Run services.
   - Note the IP address and port (default 6379).
   - *Ensure you deploy your Cloud Run services into a VPC via Serverless VPC Access to communicate with Redis.*

## Step 2: OpenBB Platform Setup
To keep the main backend lightweight, OpenBB runs as a separate API service.
1. Deploy the OpenBB Platform via Docker to Cloud Run:
   ```bash
   gcloud run deploy openbb-api \
     --image ghcr.io/openbb-finance/openbb-api:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```
2. Note the generated URL (e.g., `https://openbb-api-xxxx-uc.a.run.app`).

## Step 3: Backend Deployment (FastAPI + Playwright)
The backend requires Playwright browsers, so the Docker image is slightly larger.

1. **Build and push the image to Google Artifact Registry:**
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/idx-backend ./backend
   ```
2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy idx-backend \
     --image gcr.io/YOUR_PROJECT_ID/idx-backend \
     --add-cloudsql-instances YOUR_CONNECTION_NAME \
     --set-env-vars DATABASE_URL="postgresql+psycopg2://USER:PASS@/openinsider?host=/cloudsql/YOUR_CONNECTION_NAME" \
     --set-env-vars REDIS_URL="redis://YOUR_REDIS_IP:6379/0" \
     --set-env-vars OPENBB_API_URL="https://openbb-api-xxxx-uc.a.run.app/api/v1" \
     --set-env-vars OPENBB_PAT="your_secure_openbb_pat" \
     --vpc-connector YOUR_VPC_CONNECTOR \
     --memory 2Gi --cpu 2 \
     --region us-central1
   ```
   *(Note: 2Gi memory is recommended because of the headless Chromium/Playwright scraper).*

## Step 4: Frontend Deployment (Next.js)
1. **Build and push the image:**
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/idx-frontend ./frontend
   ```
2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy idx-frontend \
     --image gcr.io/YOUR_PROJECT_ID/idx-frontend \
     --set-env-vars NEXT_PUBLIC_API_URL="https://idx-backend-xxxx-uc.a.run.app" \
     --allow-unauthenticated \
     --region us-central1
   ```

## Step 5: Security & Verification
1. **Verify No Hallucinations:** Navigate to the events tab. Check the deal multiples. If OpenBB fails, the values will be blank/None instead of hallucinated mock data.
2. **Tailscale/VPN:** For institutional security, remove `--allow-unauthenticated` from the Frontend deployment and secure it via Cloud Identity Aware Proxy (IAP) or host it entirely internally using Tailscale Subnet Routers connected to your VPC.
3. **Database Migrations:** Before full use, ensure you run Alembic migrations against the Cloud SQL instance:
   ```bash
   alembic upgrade head
   ```

## Step 6: Running Locally (Docker Compose)
Before deploying to Google Cloud, you can test the entire stack locally using the included Docker Compose setup. This ensures your database migrations, backend API, and frontend connect seamlessly.

1. **Configure Environment Variables:**
   Ensure you have a `.env` file in the root directory (or inside `/backend`). You can start by copying an example if provided, or simply use defaults.
   Example `.env` (optional for basic local run):
   ```ini
   OPENBB_PAT=your_secure_openbb_pat_here
   # Other API keys if needed
   ```

2. **Start the Stack:**
   From the root of the project, run:
   ```bash
   docker compose up --build -d
   ```
   *This command builds the Next.js frontend, FastAPI backend, and spins up PostgreSQL and Redis containers.*

3. **Run Database Migrations (Important):**
   Once the containers are up, you must initialize the database schema. Run this command to execute Alembic migrations inside the backend container:
   ```bash
   docker compose exec backend alembic upgrade head
   ```

4. **Verify the Services:**
   - **Frontend:** Open your browser and navigate to `http://localhost:8100`.
   - **Backend API Docs:** Navigate to `http://localhost:8000/docs` to view the FastAPI Swagger UI and test endpoints directly.

5. **Stop the Stack:**
   When you're done testing, you can shut everything down cleanly:
   ```bash
   docker compose down
   ```
