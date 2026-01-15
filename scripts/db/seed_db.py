"""
Database seeding CLI.

Usage:
    uv run scripts/db/seed_db.py                     # Use default seed.sql
    uv run scripts/db/seed_db.py data.sql            # Specify file
    uv run scripts/db/seed_db.py --reset seed.sql    # Drop, recreate, then seed
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import click

from brain_api.db import drop_db, init_db, seed_db


@click.command()
@click.argument("sql_file", default="seed.sql", type=click.Path(exists=False))
@click.option("--reset", is_flag=True, help="Drop and recreate tables before seeding")
def main(sql_file: str, reset: bool):
    """Seed the database with data from a SQL file."""
    try:
        if reset:
            click.echo("Dropping all tables...")
            drop_db()
            click.echo("Recreating tables...")
            init_db()
            click.echo("Tables created.")

        click.echo(f"Seeding from: {sql_file}")
        sql_file_path = Path("scripts") / Path("db") / Path(sql_file)
        seed_db(sql_file_path)
        click.secho("Done!", fg="green")

    except FileNotFoundError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
