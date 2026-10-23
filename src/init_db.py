import sqlite3
from pathlib import Path


def init_database(db_path: str = "weather.db") -> None:
    """Create the database and schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read schema from file
    schema_file = Path("sql/schema.sql")
    schema = schema_file.read_text()

    # Execute all statements in the schema
    cursor.executescript(schema)
    conn.commit()
    conn.close()

    print(f"✓ Database initialized at {db_path}")


if __name__ == "__main__":
    init_database()