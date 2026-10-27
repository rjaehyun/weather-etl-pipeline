# Development Notes

## Problems I Hit and How I Fixed Them

### 1. mkdir doesn't accept multiple arguments in PowerShell
`mkdir src data sql tests` fails on Windows PowerShell.
**Fix:** use commas: `mkdir src, data, sql, tests`

### 2. pandas Timestamp not supported by SQLite
SQLite doesn't accept pandas Timestamp objects directly.
**Fix:** convert with `str(row["date"].date())` before inserting.

### 3. ModuleNotFoundError: No module named 'src' in pytest
pytest couldn't find the `src` module when running tests.
**Fix:** added `conftest.py` at the project root with `sys.path.insert(0, ...)`.

### 4. datetime64[ns] vs datetime64[us] in newer pandas
pandas 2.x uses microseconds instead of nanoseconds.
**Fix:** updated the test to use `str(result["date"].dtype).startswith("datetime64")`.

### 5. Empty folders not tracked by Git
Git ignores empty folders, so `data/` and `tests/` didn't show on GitHub.
**Fix:** added `.gitkeep` placeholder files.

### 6. CI couldn't find schema.sql
The `sql/` folder wasn't committed to Git.
**Fix:** ran `git add sql/` and committed the missing files.

### 7. pandas Timestamp not compatible with psycopg2
psycopg2 couldn't bind a pandas Timestamp directly.
**Fix:** convert with `row.date.date()` to get a plain Python date object.

### 8. ROUND() fails on double precision in PostgreSQL
PostgreSQL's ROUND() doesn't accept double precision with a decimal argument.
**Fix:** cast to numeric first: `ROUND(value::numeric, 2)` or
`ROUND((expression)::numeric, 2)` for calculations.

### 9. API timeout on Open-Meteo
The API occasionally times out on one city mid-loop.
**Fix:** added retry logic with up to 3 attempts per city.

### 10. CI couldn't find PostgreSQL tables
The schema wasn't applied before the tests ran in CI.
**Fix:** added `python -m src.init_db` as a step before `pytest` in the workflow.

### 11. `curl` in PowerShell is not curl
`curl -LfO` failed because PowerShell aliases `curl` to a different command.
**Fix:** use `curl.exe`.

### 12. `host.docker.internal` did not resolve inside the Airflow containers
The containers could not translate the hostname.
**Fix:** attached Airflow to the weather database's Docker network and used the
container name (`weather_postgres`) as the host.

### 13. `localhost` inside a container is the container itself
This is why the database host needs a container name, not `localhost`.

### 14. Compose commands depend on the current folder
`docker compose exec airflow-worker ...` failed from the project root because
the Airflow compose file lives in `airflow/`.
**Fix:** run Airflow commands from the `airflow/` folder.

### 15. Password authentication failed after the network fix
The connection reached the database, but the credentials did not match.
**Fix:** made the credentials consistent between the root `.env` and
`airflow/.env`. The password is set when the database volume is first created.

### 16. FERNET_KEY was wrapped in angle brackets
`<...>` is not part of a Fernet key, so the key was invalid.
**Fix:** removed the brackets.