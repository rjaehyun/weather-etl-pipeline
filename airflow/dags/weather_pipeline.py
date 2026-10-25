import os
from datetime import datetime

from airflow.sdk import dag, task

PROJECT_DIR = "/opt/airflow/project"
DATA_DIR = f"{PROJECT_DIR}/data"


def _setup() -> None:
    """Make relative paths in src/ (like sql/postgres/...) resolve correctly."""
    os.chdir(PROJECT_DIR)
    os.makedirs(DATA_DIR, exist_ok=True)


@dag(
    dag_id="weather_pipeline",
    description="Fetch, clean, validate, and load daily weather data",
    start_date=datetime(2026, 10, 1),
    schedule=None,  # manual runs for now; Day 3 adds the daily schedule
    catchup=False,
    tags=["weather", "etl"],
)
def weather_pipeline():

    @task
    def init_db() -> None:
        _setup()
        from src.init_db import init_database

        init_database()

    @task
    def extract_and_clean() -> str:
        _setup()
        from src.fetch_weather import clean_data, fetch_all_cities, raw_to_dataframe

        df = clean_data(raw_to_dataframe(fetch_all_cities()))
        path = f"{DATA_DIR}/weather_clean.csv"
        df.to_csv(path, index=False)
        print(f"Saved {len(df)} cleaned rows to {path}")
        return path

    @task
    def validate(cleaned_path: str) -> str:
        _setup()
        import pandas as pd

        from src.validate import print_validation_report, validate_data

        df = pd.read_csv(cleaned_path, parse_dates=["date"])
        valid_df, rejected_df = validate_data(df)
        print_validation_report(valid_df, rejected_df)

        valid_path = f"{DATA_DIR}/weather_valid.csv"
        valid_df.to_csv(valid_path, index=False)
        if len(rejected_df) > 0:
            rejected_df.to_csv(f"{DATA_DIR}/weather_rejected.csv", index=False)
        return valid_path

    @task
    def load(valid_path: str) -> None:
        _setup()
        import pandas as pd

        from src.fetch_weather import load_to_database

        df = pd.read_csv(valid_path, parse_dates=["date"])
        load_to_database(df)

    @task
    def run_queries() -> None:
        _setup()
        from src.run_queries import run_all_queries

        run_all_queries()

    init = init_db()
    cleaned_path = extract_and_clean()
    valid_path = validate(cleaned_path)
    loaded = load(valid_path)
    queried = run_queries()

    init >> cleaned_path
    loaded >> queried


weather_pipeline()