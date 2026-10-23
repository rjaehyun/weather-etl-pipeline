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