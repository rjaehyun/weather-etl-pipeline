-- Cities dimension table
CREATE TABLE IF NOT EXISTS cities (
    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily weather fact table
CREATE TABLE IF NOT EXISTS daily_weather (
    weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id INTEGER NOT NULL,
    date DATE NOT NULL,
    temp_max REAL,
    temp_min REAL,
    rainfall REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities (city_id),
    UNIQUE (city_id, date)
);

-- Create an index for faster queries by date
CREATE INDEX IF NOT EXISTS idx_weather_date ON daily_weather (date);