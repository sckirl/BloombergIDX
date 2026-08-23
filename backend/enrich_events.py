from backend.database import SessionLocal
from backend.models import CorporateEvent, Stock
from backend.valuation import calculate_event_valuation
from backend.convergence import link_pre_event_anomalies
from backend.logger import logger
from datetime import date

def clean_and_enrich_all_events():
    db = SessionLocal()
    try:
        # First, remove obsolete duplicates with padded names
        events = db.query(CorporateEvent).all()
        logger.info(f"Enriching {len(events)} corporate events...")
        
        seen = set()
        to_delete = []
        
        for e in events:
            # Clean string fields
            e.ticker = (e.ticker or "").strip().upper() if e.ticker else None
            e.company_name = " ".join((e.company_name or "").split())
            e.event_type = (e.event_type or "").strip()
            e.description = (e.description or "").strip()
            
            key = (e.ticker, e.company_name, e.event_type, e.description)
            if key in seen:
                to_delete.append(e)
                continue
            seen.add(key)
            
            # Compute valuation and metrics
            if e.ticker:
                val_data = calculate_event_valuation(e.ticker, e.event_date or date.today())
                if val_data.get("pe_multiple") is not None:
                    e.pe_multiple = val_data["pe_multiple"]
                if val_data.get("pb_multiple") is not None:
                    e.pb_multiple = val_data["pb_multiple"]
                if val_data.get("ev_ebitda") is not None:
                    e.ev_ebitda = val_data["ev_ebitda"]
                if val_data.get("premium_1d") is not None:
                    e.premium_1d = val_data["premium_1d"]
                    
                conv_data = link_pre_event_anomalies(db, e.ticker, e.event_date or date.today())
                if conv_data.get("pre_event_insider_volume") is not None:
                    e.pre_event_insider_volume = conv_data["pre_event_insider_volume"]
                if conv_data.get("pre_event_smart_money_score") is not None:
                    e.pre_event_smart_money_score = conv_data["pre_event_smart_money_score"]
        
        for d in to_delete:
            db.delete(d)
            
        db.commit()
        logger.info(f"Successfully cleaned and enriched events. Deleted {len(to_delete)} duplicates.")
        
    except Exception as e:
        logger.error(f"Error enriching events: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_and_enrich_all_events()
