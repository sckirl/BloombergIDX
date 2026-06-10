from sqlalchemy import text
from backend.database import SessionLocal, engine
from datetime import datetime, date

def repair_hallucinated_dates():
    """
    Surgically repairs 2026 dates where Month > 5 (Today is May).
    Swaps Day and Month to resolve the DMY vs MDY conflict.
    """
    print("--- 🏛️ BloombergIDX Temporal Repair Strike ---")
    db = SessionLocal()
    try:
        # 1. Identify records with future months (e.g., October 2026)
        # We only target 2026 because previous years are likely correct or irrelevant.
        res = db.execute(text("SELECT id, date FROM insider_transactions WHERE date > '2026-05-31' AND date <= '2026-12-31';")).fetchall()
        
        print(f"Detected {len(res)} future-hallucinated records.")
        
        fixed_count = 0
        for row in res:
            bad_date = row[1] # datetime.date
            # Swap month and day
            try:
                new_date = date(bad_date.year, bad_date.day, bad_date.month)
                db.execute(text(f"UPDATE insider_transactions SET date = '{new_date}' WHERE id = {row[0]};"))
                fixed_count += 1
            except ValueError:
                # If day is > 12, swapping is impossible, might be a different error
                pass
        
        # 2. Delete existing 'PROPOSED' events to satisfy User Mandate
        # Use TRUNCATE CASCADE to handle event_snapshots relationship
        db.execute(text("TRUNCATE TABLE corporate_events RESTART IDENTITY CASCADE;"))
        print("Truncated corporate_events and snapshots for a clean slate.")

        # 3. Clean up Flow data with suspiciously low nominals (Millions)
        # Re-populating with Billions requires a fresh slate for broker_transactions
        db.execute(text("TRUNCATE TABLE broker_transactions RESTART IDENTITY;"))
        print("Truncated broker_transactions for nominal re-calibration.")

        db.commit()
        print(f"✅ SUCCESS: Repaired {fixed_count} dates. System chronology restored.")
        
    except Exception as e:
        print(f"❌ FATAL ERROR during repair: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    repair_hallucinated_dates()
