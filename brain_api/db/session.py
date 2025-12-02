import logging
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from ..core.config import settings

logger = logging.getLogger(__name__)

# Singleton - connection pool shared across all requests
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DB_ECHO,  # (debug logging)
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Creates a new session for each request and ensures proper cleanup.

    Usage:
        from fastapi import Depends
        from brain_api.db import get_db

        @router.get("/hubs")
        def list_hubs(db: Session = Depends(get_db)):
            return db.query(Hub).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_health() -> dict:
    """
    Check database connectivity.

    Returns:
        dict: {"status": "healthy"} or {"status": "unhealthy", "error": "..."}
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        return {"status": "healthy"}
    except SQLAlchemyError as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}
