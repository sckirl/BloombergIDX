from sqlalchemy import create_engine, text
import os
import re
from dotenv import load_dotenv

# Use OpenInsider container hostname if running via Docker, else localhost
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@openinsider-db:5432/openinsider")

def migrate():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Checking for missing tables...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS corporate_events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(50),
                ticker VARCHAR(10),
                company_name VARCHAR(255),
                event_date DATE,
                underwriter VARCHAR(255),
                offering_price_range VARCHAR(100),
                total_shares BIGINT,
                acquirer VARCHAR(255),
                target VARCHAR(255),
                fair_value NUMERIC(20, 2),
                status VARCHAR(50),
                description TEXT,
                source_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        print("Table corporate_events verified.")

        print("Checking for missing columns...")
        
        # Helper to add column if not exists
        def add_column(table_name, col_name, col_type):
            # Validate identifiers to prevent SQL injection
            if not re.match(r'^[A-Za-z0-9_]+$', table_name):
                print(f"Error: Invalid table name '{table_name}'")
                return
            if not re.match(r'^[A-Za-z0-9_]+$', col_name):
                print(f"Error: Invalid column name '{col_name}'")
                return

            try:
                # Check if column exists
                res = conn.execute(
                    text("""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name=:table_name AND column_name=:col_name;
                    """),
                    {"table_name": table_name, "col_name": col_name}
                ).fetchone()
                
                if not res:
                    print(f"Adding column {col_name} to {table_name}...")
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};"))
                    conn.commit()
                    print(f"Successfully added {col_name} to {table_name}.")
                else:
                    print(f"Column {col_name} already exists in {table_name}.")
            except Exception as e:
                print(f"Error adding {col_name} to {table_name}: {e}")

        # List of institutional columns added in Sprint-2
        add_column("insider_transactions", "filing_hash", "VARCHAR(64)")
        add_column("insider_transactions", "date_inferred", "BOOLEAN DEFAULT FALSE")
        add_column("insider_transactions", "confidence", "NUMERIC(5, 2) DEFAULT 1.0")
        add_column("insider_transactions", "insider_win_rate", "NUMERIC(12, 6)")
        add_column("insider_transactions", "price_history", "TEXT")
        add_column("insider_transactions", "is_buyback", "BOOLEAN DEFAULT FALSE")
        add_column("insider_transactions", "rvol", "NUMERIC(12, 4)")
        
        # Add columns to stocks table
        add_column("stocks", "fifty_two_week_high", "NUMERIC(18, 4)")
        add_column("stocks", "fifty_two_week_low", "NUMERIC(18, 4)")
        add_column("stocks", "avg_volume", "BIGINT")
        add_column("stocks", "trailing_pe", "NUMERIC(12, 4)")
        add_column("stocks", "price_to_book", "NUMERIC(12, 4)")
        
        print("Schema repair complete.")

if __name__ == "__main__":
    migrate()
