# Weather ETL Pipeline

![CI](https://github.com/rjaehyun/weather-etl-pipeline/actions/workflows/ci.yml/badge.svg)

An end-to-end data pipeline that collects daily weather data for Philippine
cities, cleans and validates it with Python and pandas, stores it in a
relational database, and analyzes it with SQL.

Built as a portfolio project to practice core data engineering skills:
**extract, transform, load, validate, test, and automate.**

## Architecture

```
Open-Meteo API
      │
      ▼
Python (requests)        ← fetch_weather.py
      │
      ▼
pandas cleaning          ← clean_data()
      │
      ▼
Data validation          ← validate.py
      │         │
      ▼         ▼
  SQLite     rejected.csv (bad rows with reason codes)
      │
      ▼
SQL analysis             ← sql/queries/
```

## Tech Stack

| Area | Tool |
|---|---|
| Language | Python 3.12 |
| Data handling | pandas, requests |
| Database | SQLite |
| Testing | pytest |
| CI | GitHub Actions |

## Project Structure

```
weather-etl-pipeline/
├── src/
│   ├── fetch_weather.py   # fetch, clean, load
│   ├── validate.py        # data quality checks
│   ├── init_db.py         # database setup
│   └── run_queries.py     # run all SQL queries
├── sql/
│   ├── schema.sql         # table definitions
│   └── queries/           # 8 analytical queries
├── tests/
│   └── test_cleaning.py   # 9 pytest unit tests
├── docs/
│   └── queries.md         # query documentation
├── data/                  # generated files (gitignored)
├── .github/workflows/
│   └── ci.yml             # GitHub Actions CI
├── conftest.py
├── requirements.txt
└── README.md
```

## Getting Started

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

**3. Initialize the database**
```bash
python src/init_db.py
```

**4. Run the pipeline**
```bash
python -m src.fetch_weather
```

**5. Run the SQL queries**
```bash
python src/run_queries.py
```

**6. Run the tests**
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

Eight analytical queries in `sql/queries/`:

| Query | Technique |
|---|---|
| Average temperature per city | GROUP BY, aggregates |
| Hottest and coldest days | Subqueries |
| Total and daily rainfall | CASE, aggregates |
| Heavy rain days (> 10mm) | WHERE filter |
| Temperature range per day | Arithmetic |
| City comparison (latest date) | CTE (`WITH` clause) |
| 7-day moving average | Window function (`AVG() OVER`) |
| Data quality check | CASE, COUNT, nulls |

## What I Learned

- How to design an idempotent load (rerunning never creates duplicates)
- How window functions like `AVG() OVER` work on real data
- How GitHub Actions CI runs tests automatically on every PR
- Why rejected rows should be tracked, not silently dropped
- How `conftest.py` and `__init__.py` make pytest work in a src layout

## Next Steps

- [ ] Schedule daily runs with Airflow
- [ ] Upload cleaned data to AWS S3
- [ ] Rebuild SQL models in dbt
- [ ] Provision infrastructure with Terraform
- [ ] Add column-level data masking

## Data Source

Weather data from [Open-Meteo](https://open-meteo.com/).
Check their terms for usage and attribution requirements.