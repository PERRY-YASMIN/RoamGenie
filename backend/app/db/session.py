from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


@lru_cache
def get_engine() -> Engine | None:
    settings = get_settings()
    url = settings.effective_database_url
    if not url:
        return None

    connect_args = {}
    engine_kwargs = {"pool_pre_ping": True}

    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    elif "postgresql" in url:
        connect_args = {"connect_timeout": settings.db_connect_timeout_seconds}
        engine_kwargs["pool_recycle"] = 300
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20

    return create_engine(
        url,
        connect_args=connect_args,
        **engine_kwargs,
    )


def get_db() -> Generator[Session, None, None]:
    """Provide one SQLAlchemy session and roll back failed request work."""
    try:
        engine = get_engine()
    except (SQLAlchemyError, ValueError) as exc:
        raise RuntimeError("Database configuration is invalid or unavailable") from exc
    if engine is None:
        raise RuntimeError("DATABASE_URL is not configured")
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def database_status() -> str:
    """Return only a safe state; never expose driver errors or connection data."""
    try:
        engine = get_engine()
        if engine is None:
            return "not_configured"
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "connected"
    except (SQLAlchemyError, ValueError):
        return "unavailable"
