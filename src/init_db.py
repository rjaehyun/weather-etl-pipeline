from pathlib import Path

from .db import get_connection


def init_database() -> None:
    """Create the tables in PostgreSQL (safe to rerun)."""
    schema = Path("sql/postgres/01_schema.sql").read_text()

    conn = get_connection()
    try:
        with conn:  # commits on success, rolls back on error
            with conn.cursor() as cur:
                cur.execute(schema)
        print("✓ Database schema is ready")
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()