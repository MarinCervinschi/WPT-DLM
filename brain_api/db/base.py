import logging

from sqlalchemy.orm import declarative_base

from .session import engine

logger = logging.getLogger(__name__)

Base = declarative_base()


def init_db() -> None:
    """
    Create all tables in the database.
    """
    import brain_api.models  # noqa: F401

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_db() -> None:
    """
    Drop all tables in the database.

    WARNING: This will delete all data! Use only for testing/development.
    """
    logger.warning("Dropping all database tables!")
    Base.metadata.drop_all(bind=engine)
