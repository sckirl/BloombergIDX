import hashlib
from backend.database import SessionLocal
from backend.models import InsiderTransaction, Narrative
from backend.cache import invalidate_cache
from backend.logger import logger

def prune_duplicate_insider_transactions():
    db = SessionLocal()
    try:
        transactions = db.query(InsiderTransaction).order_by(InsiderTransaction.id.asc()).all()
        logger.info(f"Auditing {len(transactions)} insider transactions for duplicates...")
        
        seen = set()
        to_delete_ids = []
        
        for t in transactions:
            ticker = (t.ticker or "").strip().upper()
            name = (t.insider_name or "").strip().upper()
            t_type = (t.transaction_type or "").strip().upper()
            shares = float(t.shares or 0)
            price = float(t.price or 0)
            t_date = str(t.date)
            
            # Semantic identity key
            key = (ticker, name, t_type, round(shares, 2), round(price, 2), t_date)
            
            if key in seen:
                to_delete_ids.append(t.id)
            else:
                seen.add(key)
                # Ensure clean trimmed values
                t.ticker = ticker
                t.insider_name = " ".join(name.split())
                t.transaction_type = t_type
                # Update filing hash
                fingerprint = f"{ticker}_{name}_{t_type}_{shares:.4f}_{price:.4f}_{t_date}"
                t.filing_hash = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
        
        if to_delete_ids:
            logger.info(f"Found {len(to_delete_ids)} duplicate transactions to prune.")
            # Remove associated narratives first if any
            db.query(Narrative).filter(Narrative.insider_transaction_id.in_(to_delete_ids)).delete(synchronize_session=False)
            db.query(InsiderTransaction).filter(InsiderTransaction.id.in_(to_delete_ids)).delete(synchronize_session=False)
            db.commit()
            logger.info(f"Successfully pruned {len(to_delete_ids)} duplicates. Clean unique records: {len(seen)}.")
            invalidate_cache("insider_*")
        else:
            db.commit()
            logger.info("No duplicates found. Database is 100% clean.")
            
    except Exception as e:
        logger.error(f"Error pruning duplicates: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    prune_duplicate_insider_transactions()
