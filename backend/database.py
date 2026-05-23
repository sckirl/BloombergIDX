import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuration with institutional fallbacks for local Docker setup
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@openinsider-db:5432/openinsider")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://openinsider-redis:6379/0")
    ALLOWED_ORIGINS: str = "*"
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-mini-4b-instruct")

    SCRAPE_INTERVAL_MINUTES: int = 15

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Add connection timeout for managed databases (e.g. DigitalOcean)
# pool_pre_ping=True helps detect dropped connections
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"connect_timeout": 10},
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
