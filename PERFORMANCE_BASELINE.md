# Performance Baseline Documentation

## ⚠️ Impracticality of Measurement

Establishing a precise performance baseline through code execution is currently impractical in this environment due to the following constraints:

1.  **Broken Virtual Environment**: The pre-configured virtual environment (`test_venv`) contains absolute path symlinks that point to a different user's home directory (`/Users/alvin/...`), making it unusable in the current sandbox environment.
2.  **Restricted Network Access**: Network access is disabled, preventing the installation of necessary dependencies (e.g., `SQLAlchemy`, `FastAPI`, `Pydantic`) required to run the backend code or standalone benchmark scripts.
3.  **Missing Core Dependencies**: The base environment lacks the required libraries to execute the SQLAlchemy models and queries used in `backend/main.py`.

## 💡 Rationale for Optimization

Despite the inability to provide exact benchmarks, the proposed changes address a classic **N+1 query problem**, which is a well-documented performance anti-pattern.

### Current Inefficiency
For a list of $N$ tickers, the current implementation executes:
- $1$ query for `Stock`
- $1$ query for the latest `PriceTick`
- $1$ query for the previous `PriceTick`
- $1$ query for `InsiderTransaction` count
Total: **$4N$ queries**.

If a user watches 50 stocks, this results in **200 database round-trips** for a single API call.

### Optimized Approach
By using bulk operations:
- $1$ query to fetch all `Stock` objects using an `IN` clause.
- $1$ query to fetch the two most recent `PriceTick` objects for all stocks using a window function or optimized subquery.
- $1$ query to fetch all `InsiderTransaction` counts using `GROUP BY`.
Total: **3 queries**.

### Expected Impact
- **Reduced Latency**: Minimizing database round-trips significantly reduces the total time spent waiting for I/O, especially in environments where the database is not co-located with the application server.
- **Lower Database Load**: Executing fewer, more efficient queries reduces the overhead on the database engine.
- **Improved Scalability**: The execution time will grow much more slowly as the number of tickers in the watchlist increases.
