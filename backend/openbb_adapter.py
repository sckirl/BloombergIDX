from typing import Dict, Optional
from sqlalchemy import func
from .logger import logger
from .database import SessionLocal
from .models import Stock

def fetch_sector_multiples(sector: str) -> Dict[str, Optional[float]]:
    """
    Fetches sector multiples natively from the local database.
    (Replaces the external OpenBB API call since PAT generation changed).
    """
    multiples = {
        "sector_pe_avg": None,
        "sector_pb_avg": None
    }
    
    if not sector:
        return multiples
        
    db = SessionLocal()
    try:
        # Calculate average trailing PE for the given sector (ignoring 0 or null)
        avg_pe = db.query(func.avg(Stock.trailing_pe)).filter(
            Stock.sector == sector, 
            Stock.trailing_pe > 0
        ).scalar()
        
        # Calculate average price to book for the given sector
        avg_pb = db.query(func.avg(Stock.price_to_book)).filter(
            Stock.sector == sector,
            Stock.price_to_book > 0
        ).scalar()
        
        if avg_pe is not None:
            multiples["sector_pe_avg"] = float(avg_pe)
        if avg_pb is not None:
            multiples["sector_pb_avg"] = float(avg_pb)
            
        logger.info(f"Native sector multiples for {sector} calculated: {multiples}")
        
    except Exception as e:
        logger.error(f"Failed to calculate native sector multiples: {e}")
    finally:
        db.close()

    return multiples
