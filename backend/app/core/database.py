"""Database engine and session management."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from typing import Generator
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=NullPool if settings.database_url.startswith("postgresql") else None,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

# Declarative Base for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for DB session in non-FastAPI contexts."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Enable foreign keys for SQLite (if used)
if "sqlite" in settings.database_url:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def init_db():
    """Initialize database (create all tables)."""
    # Import all models here to ensure they are registered with Base
    # import app.core.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")


def drop_db():
    """Drop all tables (for testing)."""
    Base.metadata.drop_all(bind=engine)
    logger.info("Database dropped")
