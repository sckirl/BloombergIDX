import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuration is loaded from environment variables or .env file
    DATABASE_URL: str
    REDIS_URL: str
    ALLOWED_ORIGINS: str = "*"
    SCRAPE_INTERVAL_MINUTES: int = 15

    class Config:
        env_file = ".env"
        extra = "ignore"

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
