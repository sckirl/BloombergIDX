from .database import settings
from .logger import logger
from sqlalchemy import create_engine, text
import re

from .models import Base

def migrate():
    database_url = settings.DATABASE_URL
    print(f"Connecting to database...")
    engine = create_engine(database_url, connect_args={"connect_timeout": 10})
    
    # Create all base tables if not present
    Base.metadata.create_all(bind=engine)
    print("Base metadata tables created/verified.")

    with engine.connect() as conn:
        print("Checking for missing tables...")
        # Create corporate_events table with full Sprint-3 schema
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
                pe_multiple NUMERIC(10, 4),
                pb_multiple NUMERIC(10, 4),
                ev_ebitda NUMERIC(10, 4),
                premium_1d NUMERIC(10, 4),
                status VARCHAR(50),
                event_version INTEGER DEFAULT 1,
                source_hash VARCHAR(255) UNIQUE,
                state_transition_log TEXT,
                description TEXT,
                rationale_ai TEXT,
                source_url VARCHAR(500),
                pre_event_insider_volume NUMERIC(24, 4),
                pre_event_smart_money_score INTEGER,
                acquirer_entity_id INTEGER,
                target_entity_id INTEGER,
                post_event_absorption_ratio NUMERIC(12, 4),
                last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        print("Table corporate_events verified.")

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS event_snapshots (
                id SERIAL PRIMARY KEY,
                event_id INTEGER REFERENCES corporate_events(id),
                version INTEGER,
                status VARCHAR(50),
                data_snapshot TEXT,
                snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        print("Table event_snapshots verified.")

        print("Checking for missing columns in existing tables...")
        
        # Helper to add column if not exists
        def add_column(table_name, col_name, col_type):
            try:
                res = conn.execute(
                    text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='{col_name}';")
                ).fetchone()
                
                if not res:
                    print(f"Adding column {col_name} to {table_name}...")
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};"))
                    conn.commit()
                    print(f"Successfully added {col_name}.")
            except Exception as e:
                conn.rollback()
                print(f"Error adding {col_name}: {e}")

        # Ensure corporate_events has all columns (handle existing table upgrades)
        add_column("corporate_events", "ev_ebitda", "NUMERIC(10, 4)")
        add_column("corporate_events", "acquirer_entity_id", "INTEGER")
        add_column("corporate_events", "target_entity_id", "INTEGER")
        add_column("corporate_events", "post_event_absorption_ratio", "NUMERIC(12, 4)")
        add_column("corporate_events", "last_seen_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        add_column("corporate_events", "rationale_ai", "TEXT")

        # PriceTick upgrades
        add_column("price_ticks", "foreign_buy", "BIGINT DEFAULT 0")
        add_column("price_ticks", "foreign_sell", "BIGINT DEFAULT 0")
        add_column("price_ticks", "foreign_net", "BIGINT DEFAULT 0")

        # Other table upgrades
        add_column("insider_transactions", "filing_hash", "VARCHAR(64)")
        add_column("insider_transactions", "date_inferred", "BOOLEAN DEFAULT FALSE")
        add_column("insider_transactions", "confidence", "NUMERIC(5, 2) DEFAULT 1.0")
        add_column("insider_transactions", "insider_win_rate", "NUMERIC(12, 6)")
        add_column("insider_transactions", "price_history", "TEXT")
        add_column("insider_transactions", "is_buyback", "BOOLEAN DEFAULT FALSE")
        add_column("insider_transactions", "rvol", "NUMERIC(12, 4)")
        
        add_column("stocks", "fifty_two_week_high", "NUMERIC(18, 4)")
        add_column("stocks", "fifty_two_week_low", "NUMERIC(18, 4)")
        add_column("stocks", "avg_volume", "BIGINT")
        add_column("stocks", "trailing_pe", "NUMERIC(12, 4)")
        add_column("stocks", "price_to_book", "NUMERIC(12, 4)")
        
        # Ensure unique index on insider_transactions filing_hash
        try:
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_insider_transactions_filing_hash ON insider_transactions (filing_hash);"))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Index creation notice: {e}")

        print("Schema repair complete.")

if __name__ == "__main__":
    migrate()
