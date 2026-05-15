from typing import Dict, Optional
import os
import requests
from .logger import logger

# By default, use the local OpenBB platform API if deployed,
# or a hosted OpenBB Terminal Pro API endpoint.
OPENBB_API_URL = os.getenv("OPENBB_API_URL", "http://localhost:8000/api/v1")
OPENBB_PAT = os.getenv("OPENBB_PAT", "")

def fetch_sector_multiples(sector: str) -> Dict[str, Optional[float]]:
    """
    Fetches real-world sector multiples using the OpenBB Platform REST API.
    To ensure no hallucinations, it strictly requires a valid API connection.
    If the API fails, it logs the failure and returns None, triggering the QA fallback.
    """
    multiples = {
        "sector_pe_avg": None,
        "sector_pb_avg": None
    }

    if not OPENBB_PAT and not os.getenv("IGNORE_OPENBB_AUTH"):
        logger.warning("OpenBB PAT is not set. Skipping sector multiple fetch to prevent hallucination.")
        return multiples

    headers = {"Authorization": f"Bearer {OPENBB_PAT}"} if OPENBB_PAT else {}

    try:
        # Example endpoint assuming OpenBB Platform Fastapi deployment
        # E.g. GET /api/v1/equity/fundamental/multiples?sector=Financials
        url = f"{OPENBB_API_URL}/equity/fundamental/multiples"
        params = {"sector": sector, "provider": "yfinance"}

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Calculate averages from the returned list of peers
            results = data.get("results", [])
            if results:
                valid_pes = [r.get("pe_ratio") for r in results if r.get("pe_ratio")]
                valid_pbs = [r.get("pb_ratio") for r in results if r.get("pb_ratio")]

                if valid_pes:
                    multiples["sector_pe_avg"] = sum(valid_pes) / len(valid_pes)
                if valid_pbs:
                    multiples["sector_pb_avg"] = sum(valid_pbs) / len(valid_pbs)
        else:
            logger.error(f"OpenBB API returned status {response.status_code}: {response.text}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to OpenBB API: {e}")

    return multiples
