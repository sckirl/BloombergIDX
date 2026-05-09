import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Production database from openinsider-db container
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@172.19.0.2:5432/openinsider")
    ALLOWED_ORIGINS: str = "*"
    SCRAPE_INTERVAL_MINUTES: int = 15

    class Config:
        env_file = ".env"

settings = Settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
