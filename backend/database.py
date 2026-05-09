import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Default to SQLite for local development if Postgres is not configured
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    ALLOWED_ORIGINS: str = "*"
    SCRAPE_INTERVAL_MINUTES: int = 15

    class Config:
        env_file = ".env"

settings = Settings()

# For SQLite, we need 'check_same_thread: False'
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
