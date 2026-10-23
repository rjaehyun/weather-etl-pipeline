import sqlite3


def query_example(db_path: str = "weather.db") -> None:
    """Run a sample query to verify data loaded correctly."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query 1: Count rows per city
    print("=== Rows per city ===")
    cursor.execute("""
        SELECT c.name, COUNT(*) as record_count
        FROM daily_weather w
        JOIN cities c ON c.city_id = w.city_id
        GROUP BY c.name
    """)
    for city, count in cursor.fetchall():
        print(f"{city}: {count} records")
    
    # Query 2: Sample data
    print("\n=== Sample data ===")
    cursor.execute("""
        SELECT c.name, w.date, w.temp_max, w.temp_min, w.rainfall
        FROM daily_weather w
        JOIN cities c ON c.city_id = w.city_id
        ORDER BY c.name, w.date
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(row)
    
    conn.close()


if __name__ == "__main__":
    query_example()