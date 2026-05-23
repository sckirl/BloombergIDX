from sqlalchemy import text
from backend.database import SessionLocal, engine
from backend.logger import logger

def purge_wrongful_data():
    """
    Surgically removes all intelligence nodes to prepare for a truthful re-scrape.
    Preserves the 'stocks' table to save API credits on metadata.
    """
    print("--- 🏛️ BloombergIDX Data Purge Strike ---")
    print("Targeting: Hallucinated 2026 Intelligence Nodes")
    
    db = SessionLocal()
    try:
        # Use a transaction block for safety
        # TRUNCATE is faster and resets IDs. CASCADE handles foreign keys.
        tables = [
            "narratives",
            "insider_transactions",
            "broker_clusters",
            "smart_money_scores",
            "signals",
            "corporate_events",
            "event_snapshots"
        ]
        
        for table in tables:
            print(f"Purging {table}...")
            db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
        
        db.commit()
        print("✅ SUCCESS: Intelligence tables are now EMPTY and READY for seeding.")
        
    except Exception as e:
        print(f"❌ FATAL ERROR during purge: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    confirm = input("CRITICAL: This will wipe all transaction and event data. Proceed? (y/N): ")
    if confirm.lower() == 'y':
        purge_wrongful_data()
    else:
        print("Purge aborted.")
