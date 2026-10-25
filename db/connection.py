import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from utils.settings import ROOT_FOLDER

load_dotenv(ROOT_FOLDER / "credentials" / ".env")
load_dotenv()


def _database_url() -> str:
    url = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Set NEON_DATABASE_URL (Neon connection string) in credentials/.env")
    # Use the psycopg (v3) driver with SQLAlchemy.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    # Lazy so importing this module never opens a connection.
    return create_engine(_database_url(), pool_pre_ping=True, pool_recycle=300)


def get_session() -> Session:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)()
