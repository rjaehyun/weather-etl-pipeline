# Weather ETL Pipeline

![CI](https://github.com/rjaehyun/weather-etl-pipeline/actions/workflows/ci.yml/badge.svg)

An end-to-end data pipeline that collects daily weather data for Philippine
cities, validates and cleans it with Python and pandas, stores it in
PostgreSQL, and analyzes it with SQL.

Built as a portfolio project to practice core data engineering skills:
**extract, transform, load, validate, test, and automate.**

## Architecture

```
Open-Meteo API
      │
      ▼
Python (requests + retry logic)    ← fetch_weather.py
      │
      ▼
pandas cleaning                    ← clean_data()
      │
      ▼
Data validation                    ← validate.py
      │              │
      ▼              ▼
 PostgreSQL     rejected.csv       ← load_to_database()
      │
      ▼
SQL analysis                       ← sql/queries_pg/
```

## Tech Stack

| Area | Tool |
|---|---|
| Language | Python 3.12 |
| Data handling | pandas, requests |
| Database | PostgreSQL 16 |
| DB driver | psycopg2 |
| Containerization | Docker + docker-compose |
| Testing | pytest |
| CI | GitHub Actions |

## Project Structure

```
weather-etl-pipeline/
├── src/
│   ├── db.py              # PostgreSQL connection helper
│   ├── fetch_weather.py   # fetch, clean, validate, load
│   ├── validate.py        # data quality checks
│   ├── init_db.py         # database schema setup
│   └── run_queries.py     # run all SQL queries
├── sql/
│   ├── postgres/
│   │   └── 01_schema.sql  # PostgreSQL table definitions
│   └── queries_pg/        # 8 analytical queries
├── tests/
│   ├── test_cleaning.py   # 9 unit tests
│   └── test_database.py   # 4 integration tests
├── docs/
│   └── queries.md
├── data/                  # generated files (gitignored)
├── .github/workflows/
│   └── ci.yml             # GitHub Actions CI with PostgreSQL service
├── docker-compose.yml
├── .env.example
├── conftest.py
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.12+
- Docker Desktop

### Setup

**1. Clone the repo**
```bash
git clone https://github.com/rjaehyun/weather-etl-pipeline.git
cd weather-etl-pipeline
```

**2. Set up the environment**
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configure credentials**
```bash
cp .env.example .env
# Open .env and set your own password
```

**4. Start the database**
```bash
docker compose up -d
```

**5. Initialize the schema**
```bash
python -m src.init_db
```

**6. Run the pipeline**
```bash
python -m src.fetch_weather
```

**7. Run the SQL queries**
```bash
python -m src.run_queries
```

**8. Run the tests**
```bash
pytest tests/ -v
```

## Data Quality

Every run validates:
- Temperature within a realistic range (−20°C to 50°C)
- Max temperature is always ≥ min temperature
- Rainfall is non-negative
- No missing city or date values

Bad rows are saved to `data/weather_rejected.csv` with a reason code
instead of being silently dropped.

## SQL Queries

Eight analytical queries in `sql/queries_pg/`:

| Query | Technique |
|---|---|
| Average temperature per city | GROUP BY, aggregates |
| Hottest and coldest days | CTE, window functions |
| Total and daily rainfall | CASE, aggregates |
| Heavy rain days (> 10mm) | WHERE filter |
| Temperature range per day | Arithmetic, cast |
| City comparison (latest date) | CTE |
| 7-day moving average | Window function (`AVG() OVER`) |
| Data quality check | CASE, COUNT, nulls |

## Tests

13 tests across two files:

| File | What it covers |
|---|---|
| `test_cleaning.py` | Type conversion, sorting, sentinel values, validation rules |
| `test_database.py` | City inserts, row counts, idempotency, NULL handling |

## What I Learned

- How `ON CONFLICT ... DO UPDATE` makes PostgreSQL upserts idempotent
- How `::numeric` casting works in PostgreSQL for `ROUND()`
- How to run a real PostgreSQL service container in GitHub Actions CI
- How `execute_values` batches inserts for better performance
- Why rejected rows should be tracked with reason codes, not silently dropped
- How retry logic prevents one slow API response from crashing the pipeline

## Next Steps

- [ ] Schedule daily runs with Airflow
- [ ] Upload cleaned data to AWS S3 as Parquet
- [ ] Rebuild SQL models in dbt
- [ ] Provision infrastructure with Terraform
- [ ] Add column-level data masking

## Data Source

Weather data from [Open-Meteo](https://open-meteo.com/).
Check their terms for usage and attribution requirements.