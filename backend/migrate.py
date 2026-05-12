from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Use OpenInsider container hostname if running via Docker, else localhost
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@openinsider-db:5432/openinsider")

def migrate():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Checking for missing columns in insider_transactions...")
        
        # Helper to add column if not exists
        def add_column(col_name, col_type):
            try:
                # Check if column exists
                res = conn.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='insider_transactions' AND column_name='{col_name}';
                """)).fetchone()
                
                if not res:
                    print(f"Adding column {col_name}...")
                    conn.execute(text(f"ALTER TABLE insider_transactions ADD COLUMN {col_name} {col_type};"))
                    conn.commit()
                    print(f"Successfully added {col_name}.")
                else:
                    print(f"Column {col_name} already exists.")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")

        # List of institutional columns added in Sprint-2
        add_column("filing_hash", "VARCHAR(64)")
        add_column("date_inferred", "BOOLEAN DEFAULT FALSE")
        add_column("confidence", "NUMERIC(5, 2) DEFAULT 1.0")
        add_column("insider_win_rate", "NUMERIC(12, 6)")
        add_column("price_history", "TEXT")
        add_column("is_buyback", "BOOLEAN DEFAULT FALSE")
        add_column("rvol", "NUMERIC(12, 4)")
        
        print("Schema repair complete.")

if __name__ == "__main__":
    migrate()
