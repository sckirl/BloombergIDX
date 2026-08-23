import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Force load .env from the project root relative to this file
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(ENV_PATH)

class Settings(BaseSettings):
    # Pydantic will automatically look for these keys in the environment.
    # The values here are ONLY used if the environment variable is not found.
    # Note: On host machine (Linux), 'openinsider-db' hostname is unreachable.
    # If .env fails to load, we default to localhost for development.
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/openinsider"
    REDIS_URL: str = "redis://localhost:6379/0"
    ALLOWED_ORIGINS: str = "*"
    NVIDIA_MODEL: str = "nvidia/nemotron-mini-4b-instruct"
    SCRAPE_INTERVAL_MINUTES: int = 15

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()

# Debug for Linux/Host Diagnosis
if "do-user" in settings.DATABASE_URL:
    db_target = "PROD (DigitalOcean)"
elif "localhost" in settings.DATABASE_URL:
    db_target = "DEV (Localhost)"
else:
    db_target = f"CUSTOM ({settings.DATABASE_URL.split('@')[-1].split(':')[0]})"

print(f"DATABASE_TARGET: Connecting to {db_target}")

# Ensure timeout is appropriate for remote DBs
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
