import logging
from pathlib import Path

from sqlalchemy import text
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


def seed_db(sql_path: Path) -> None:
    """
    Seed the database with data from a SQL file.

    Args:
        sql_file: Path to the SQL file
    """

    if not sql_path.exists():
        logger.error(f"Seed file not found: {sql_path}")
        raise FileNotFoundError(f"Seed file not found: {sql_path}")

    logger.info(f"Seeding database from: {sql_path}")

    with open(sql_path) as f:
        sql_content = f.read()

    with engine.begin() as conn:
        for statement in sql_content.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))

    logger.info("Database seeded successfully")


def drop_db() -> None:
    """
    Drop all tables in the database.

    WARNING: This will delete all data! Use only for testing/development.
    """
    import brain_api.models  # noqa: F401

    logger.warning("Dropping all database tables!")
    Base.metadata.drop_all(bind=engine)
