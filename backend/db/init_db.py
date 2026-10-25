"""Enable pgvector and create all tables: python -m db.init_db"""
from sqlalchemy import text

from backend.db.connection import get_engine
from backend.db.models import Base


def init_db() -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)
    # create_all does not alter existing tables.
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE analysis_runs ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'pending'"))
        conn.execute(text("ALTER TABLE analysis_runs ADD COLUMN IF NOT EXISTS error TEXT"))
        conn.execute(text("ALTER TABLE analysis_runs ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ"))
    with engine.connect() as conn:
        version = conn.execute(text("SELECT extversion FROM pg_extension WHERE extname='vector'")).scalar()
    print(f"pgvector {version} enabled; tables: {', '.join(Base.metadata.tables)}")


if __name__ == "__main__":
    init_db()
