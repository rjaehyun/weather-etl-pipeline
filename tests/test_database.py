import pandas as pd
import pytest

from src.db import get_connection
from src.fetch_weather import load_to_database


@pytest.fixture(scope="function")
def db_conn():
    """Give each test a clean database state."""
    conn = get_connection()

    # Create tables fresh for each test
    with conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS daily_weather CASCADE")
            cur.execute("DROP TABLE IF EXISTS cities CASCADE")
            cur.execute("""
                CREATE TABLE cities (
                    city_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE daily_weather (
                    weather_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    city_id INTEGER NOT NULL REFERENCES cities (city_id),
                    date DATE NOT NULL,
                    temp_max DOUBLE PRECISION,
                    temp_min DOUBLE PRECISION,
                    rainfall DOUBLE PRECISION,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (city_id, date)
                )
            """)

    yield conn

    # Tear down after each test
    with conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS daily_weather CASCADE")
            cur.execute("DROP TABLE IF EXISTS cities CASCADE")

    conn.close()


def sample_df() -> pd.DataFrame:
    """A small clean DataFrame for testing."""
    return pd.DataFrame({
        "city": ["Manila", "Manila", "Cebu"],
        "date": [
            pd.Timestamp("2026-10-16"),
            pd.Timestamp("2026-10-17"),
            pd.Timestamp("2026-10-16"),
        ],
        "temp_max": [31.5, 32.0, 30.0],
        "temp_min": [25.2, 25.5, 24.0],
        "rainfall": [0.0, 2.3, 5.0],
    })


class TestLoadToDatabase:
    """Test the load_to_database function."""

    def test_cities_are_inserted(self, db_conn):
        """All unique cities should appear in the cities table."""
        load_to_database(sample_df())

        with db_conn.cursor() as cur:
            cur.execute("SELECT name FROM cities ORDER BY name")
            cities = [row[0] for row in cur.fetchall()]

        assert cities == ["Cebu", "Manila"]

    def test_weather_rows_are_inserted(self, db_conn):
        """All rows should be in daily_weather."""
        load_to_database(sample_df())

        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM daily_weather")
            count = cur.fetchone()[0]

        assert count == 3

    def test_idempotent_load(self, db_conn):
        """Loading the same data twice should not create duplicates."""
        load_to_database(sample_df())
        load_to_database(sample_df())

        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM daily_weather")
            count = cur.fetchone()[0]

        assert count == 3

    def test_null_values_stored_as_null(self, db_conn):
        """NaN values should be stored as NULL in the database."""
        df = pd.DataFrame({
            "city": ["Manila"],
            "date": [pd.Timestamp("2026-10-16")],
            "temp_max": [float("nan")],
            "temp_min": [25.2],
            "rainfall": [0.0],
        })
        load_to_database(df)

        with db_conn.cursor() as cur:
            cur.execute("SELECT temp_max FROM daily_weather")
            value = cur.fetchone()[0]

        assert value is None