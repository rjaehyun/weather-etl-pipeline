import requests
import pandas as pd
import sqlite3
from pathlib import Path
from .validate import validate_data, print_validation_report

def fetch_city(name: str, lat: float, lon: float) -> dict:
    """Fetch the last 7 days of daily weather for one city.
    
    Args:
        name: City name (for logging)
        lat, lon: Coordinates
        
    Returns:
        dict: API response with 'daily' key containing dates, temps, rainfall
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
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


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

def load_to_database(df: pd.DataFrame, db_path: str = "weather.db") -> None:
    """Load cleaned data into SQLite, handling duplicates safely.
    
    The UNIQUE constraint on (city_id, date) ensures no duplicates.
    If a row already exists, it is ignored.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure database exists
    if not Path(db_path).exists():
        print(f"Database {db_path} not found. Run init_db.py first.")
        return
    
    try:
        # Insert or replace cities
        for city_name in df["city"].unique():
            cursor.execute(
                "INSERT OR IGNORE INTO cities (name) VALUES (?)",
                (city_name,)
            )
        conn.commit()
        
        # Get city IDs
        city_ids = cursor.execute("SELECT city_id, name FROM cities").fetchall()
        city_name_to_id = {name: city_id for city_id, name in city_ids}
        
        # Insert weather data with conflict handling
        for _, row in df.iterrows():
            city_id = city_name_to_id[row["city"]]
            # Convert datetime to string for SQLite
            date_str = str(row["date"].date())
            cursor.execute(
                """
                INSERT OR IGNORE INTO daily_weather 
                (city_id, date, temp_max, temp_min, rainfall)
                VALUES (?, ?, ?, ?, ?)
                """,
                (city_id, date_str, row["temp_max"], row["temp_min"], row["rainfall"])
            )
        
        conn.commit()
        
        # Print summary
        weather_count = cursor.execute("SELECT COUNT(*) FROM daily_weather").fetchone()[0]
        city_count = cursor.execute("SELECT COUNT(*) FROM cities").fetchone()[0]
        print(f"✓ Loaded {weather_count} weather records for {city_count} cities")
        
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        conn.rollback()
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