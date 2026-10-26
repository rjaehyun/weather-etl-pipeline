"""Daily weather ETL pipeline.

Runs every day at 07:00 Manila time:
init_db -> extract_and_clean -> validate -> load -> run_queries

Each task retries on failure. If a task still fails after all retries,
an alert is logged and appended to data/pipeline_alerts.log.
"""

import logging
import os
from datetime import datetime, timedelta

import pendulum
from airflow.sdk import dag, task

log = logging.getLogger(__name__)

PROJECT_DIR = "/opt/airflow/project"
DATA_DIR = f"{PROJECT_DIR}/data"


def _setup() -> None:
    """Make relative paths in src/ resolve correctly."""
    os.chdir(PROJECT_DIR)
    os.makedirs(DATA_DIR, exist_ok=True)


def notify_failure(context) -> None:
    """Runs only when a task has failed AFTER using up all its retries."""
    ti = context.get("task_instance") or context.get("ti")
    message = (
        f"PIPELINE ALERT | dag={getattr(ti, 'dag_id', '?')} "
        f"task={getattr(ti, 'task_id', '?')} "
        f"run={getattr(ti, 'run_id', '?')} "
        f"attempt={getattr(ti, 'try_number', '?')} "
        f"| error={context.get('exception')}"
    )
    log.error(message)

    # Keep a permanent record you can read without opening the UI
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(f"{DATA_DIR}/pipeline_alerts.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} {message}\n")


default_args = {
    "owner": "data-engineering",
    "retries": 3,                               # up to 3 retries per task
    "retry_delay": timedelta(minutes=2),        # wait between attempts
    "execution_timeout": timedelta(minutes=10), # kill a task that hangs
    "on_failure_callback": notify_failure,
}


@dag(
    dag_id="weather_pipeline",
    description="Fetch, clean, validate, and load daily weather data",
    start_date=pendulum.datetime(2026, 10, 1, tz="Asia/Manila"),
    schedule="0 7 * * *",   # every day at 07:00 Manila time
    catchup=False,          # don't backfill missed days
    max_active_runs=1,      # never run two copies at once
    default_args=default_args,
    tags=["weather", "etl"],
    doc_md=__doc__,
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