"""Structural tests for the Airflow DAG.

These parse the DAG file without importing Airflow, so they run fast in CI.
The full import check is `airflow dags list-import-errors` inside the container.
"""

import ast
from pathlib import Path

DAG_FILE = Path(__file__).resolve().parents[1] / "airflow" / "dags" / "weather_pipeline.py"

EXPECTED_TASKS = {"init_db", "extract_and_clean", "validate", "load", "run_queries"}


def _tree() -> ast.Module:
    return ast.parse(DAG_FILE.read_text(encoding="utf-8"))


def _dag_kwargs() -> dict:
    """Return the keyword arguments passed to the @dag(...) decorator."""
    for node in ast.walk(_tree()):
        if isinstance(node, ast.FunctionDef) and node.name == "weather_pipeline":
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and getattr(dec.func, "id", None) == "dag":
                    return {kw.arg: kw.value for kw in dec.keywords}
    raise AssertionError("@dag-decorated weather_pipeline function not found")


def _default_args() -> dict:
    """Return the default_args dict, keyed by name."""
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Assign) and any(
            getattr(t, "id", None) == "default_args" for t in node.targets
        ):
            return {
                ast.literal_eval(k): v
                for k, v in zip(node.value.keys, node.value.values)
            }
    raise AssertionError("default_args not found")


def test_dag_file_is_valid_python():
    """A syntax error in the DAG file should fail CI."""
    assert _tree() is not None


def test_dag_id_schedule_and_safety_settings():
    """The DAG runs daily, never backfills, and never overlaps."""
    kwargs = _dag_kwargs()
    assert ast.literal_eval(kwargs["dag_id"]) == "weather_pipeline"
    assert ast.literal_eval(kwargs["schedule"]) == "0 7 * * *"
    assert ast.literal_eval(kwargs["catchup"]) is False
    assert ast.literal_eval(kwargs["max_active_runs"]) == 1


def test_default_args_have_retries_and_failure_alert():
    """Tasks must retry, and a failure callback must be configured."""
    args = _default_args()
    assert ast.literal_eval(args["retries"]) >= 1
    assert "on_failure_callback" in args


def test_expected_tasks_exist():
    """All five pipeline steps are defined as tasks."""
    names = set()
    for node in ast.walk(_tree()):
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                if getattr(dec, "id", None) == "task":
                    names.add(node.name)
    assert names == EXPECTED_TASKS