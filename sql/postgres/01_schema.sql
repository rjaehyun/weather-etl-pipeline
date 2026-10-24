-- Cities dimension table
CREATE TABLE IF NOT EXISTS cities (
    city_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Daily weather fact table
CREATE TABLE IF NOT EXISTS daily_weather (
    weather_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city_id INTEGER NOT NULL REFERENCES cities (city_id),
    date DATE NOT NULL,
    temp_max DOUBLE PRECISION,
    temp_min DOUBLE PRECISION,
    rainfall DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (city_id, date)
);

-- Faster queries by date
CREATE INDEX IF NOT EXISTS idx_weather_date ON daily_weather (date);