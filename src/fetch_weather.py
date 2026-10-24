import requests
import pandas as pd
import sqlite3
from pathlib import Path
from .validate import validate_data, print_validation_report
from psycopg2.extras import execute_values
from .db import get_connection

def fetch_city(name: str, lat: float, lon: float) -> dict:
    """Fetch the last 7 days of daily weather for one city.
    Retries up to 3 times on timeout or server errors.
    """
    API_URL = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "past_days": 7,
        "forecast_days": 1,
        "timezone": "Asia/Manila",
    }

    for attempt in range(1, 4):  # try up to 3 times
        try:
            print(f"  Attempt {attempt}...")
            response = requests.get(API_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print(f"  Timeout on attempt {attempt} for {name}")
            if attempt == 3:
                raise
        except requests.exceptions.RequestException as e:
            print(f"  Error on attempt {attempt} for {name}: {e}")
            if attempt == 3:
                raise


def fetch_all_cities() -> list[dict]:
    """Fetch weather for all cities and return raw data."""
    cities = {
        "Manila": (14.5995, 120.9842),
        "Cebu": (10.3157, 123.8854),
        "Davao": (7.1907, 125.4553),
    }
    
    all_data = []
    for city_name, (lat, lon) in cities.items():
        print(f"Fetching {city_name}...")
        data = fetch_city(city_name, lat, lon)
        all_data.append({"city": city_name, "data": data})
    
    return all_data


def raw_to_dataframe(all_data: list[dict]) -> pd.DataFrame:
    """Convert raw API responses into a single pandas DataFrame."""
    rows = []
    
    for city_dict in all_data:
        city_name = city_dict["city"]
        daily = city_dict["data"]["daily"]
        
        # daily is a dict with "time", "temperature_2m_max", etc.
        # Zip them together to create rows
        for date, temp_max, temp_min, rainfall in zip(
            daily["time"],
            daily["temperature_2m_max"],
            daily["temperature_2m_min"],
            daily["precipitation_sum"],
        ):
            rows.append({
                "city": city_name,
                "date": date,
                "temp_max": temp_max,
                "temp_min": temp_min,
                "rainfall": rainfall,
            })
    
    return pd.DataFrame(rows)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize the DataFrame."""
    df = df.copy()  # avoid modifying the original
    
    # Convert date to datetime type
    df["date"] = pd.to_datetime(df["date"])
    
    # Ensure numeric columns are floats
    df["temp_max"] = pd.to_numeric(df["temp_max"], errors="coerce")
    df["temp_min"] = pd.to_numeric(df["temp_min"], errors="coerce")
    df["rainfall"] = pd.to_numeric(df["rainfall"], errors="coerce")
    
    # Replace -9999 or other sentinel values with NaN (if the API uses them)
    df = df.replace([-9999, -999], pd.NA)
    
    # Sort by city and date
    df = df.sort_values(["city", "date"]).reset_index(drop=True)
    
    return df

def _to_none(value):
    """Convert pandas NaN/NA to None so PostgreSQL stores NULL."""
    return None if pd.isna(value) else float(value)


def load_to_database(df: pd.DataFrame) -> None:
    """Load cleaned data into PostgreSQL.

    Idempotent: rerunning updates existing (city, date) rows instead of
    creating duplicates. Updating (rather than ignoring) means forecast values
    get refreshed once the real measurements are available.
    """
    conn = get_connection()
    try:
        with conn:  # one transaction: all rows load, or none do
            with conn.cursor() as cur:
                # 1. Make sure every city exists
                for city in df["city"].unique():
                    cur.execute(
                        "INSERT INTO cities (name) VALUES (%s) "
                        "ON CONFLICT (name) DO NOTHING",
                        (city,),
                    )

                # 2. Look up city IDs
                cur.execute("SELECT city_id, name FROM cities")
                city_ids = {name: city_id for city_id, name in cur.fetchall()}

                # 3. Build all rows, then insert them in one batch
                records = [
                    (
                        city_ids[row.city],
                        row.date.date(),
                        _to_none(row.temp_max),
                        _to_none(row.temp_min),
                        _to_none(row.rainfall),
                    )
                    for row in df.itertuples(index=False)
                ]

                execute_values(
                    cur,
                    """
                    INSERT INTO daily_weather
                        (city_id, date, temp_max, temp_min, rainfall)
                    VALUES %s
                    ON CONFLICT (city_id, date) DO UPDATE SET
                        temp_max = EXCLUDED.temp_max,
                        temp_min = EXCLUDED.temp_min,
                        rainfall = EXCLUDED.rainfall
                    """,
                    records,
                )

                cur.execute("SELECT COUNT(*) FROM daily_weather")
                weather_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM cities")
                city_count = cur.fetchone()[0]

        print(f"✓ Loaded {weather_count} weather records for {city_count} cities")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting fetch...")
    
    # Fetch
    raw = fetch_all_cities()
    print(f"Fetched {len(raw)} cities")
    
    # Transform
    df = raw_to_dataframe(raw)
    print(f"\nRaw data shape: {df.shape}")
    
    # Clean
    df_clean = clean_data(df)
    print(f"Cleaned data shape: {df_clean.shape}")
    
    # Validate
    df_valid, df_rejected = validate_data(df_clean)
    print_validation_report(df_valid, df_rejected)
    
    # Save to CSV
    output_path = "data/weather_clean.csv"
    df_valid.to_csv(output_path, index=False)
    print(f"\n✓ Saved {len(df_valid)} valid records to {output_path}")
    
    # Save rejected rows if any
    if len(df_rejected) > 0:
        rejected_path = "data/weather_rejected.csv"
        df_rejected.to_csv(rejected_path, index=False)
        print(f"✓ Saved {len(df_rejected)} rejected records to {rejected_path}")
    
    # Load to database
    load_to_database(df_valid)