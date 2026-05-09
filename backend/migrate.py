from .database import engine
from .models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    logger.info("Starting database migration...")
    try:
        # This will create all tables defined in models.py
        # If they already exist, it will skip them.
        # Note: SQLAlchemy's create_all doesn't handle incremental column additions well.
        # For production, Alembic should be used.
        Base.metadata.create_all(bind=engine)
        logger.info("Database migration complete.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
