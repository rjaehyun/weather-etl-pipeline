from pathlib import Path

from .db import get_connection


def run_all_queries() -> None:
    """Execute every query in sql/queries_pg/ and print the results."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for query_file in sorted(Path("sql/queries_pg").glob("*.sql")):
                print(f"\n{'=' * 60}\nQuery: {query_file.name}\n{'=' * 60}")
                cur.execute(query_file.read_text())
                rows = cur.fetchall()

                if not rows:
                    print("(No results)")
                    continue

                print(" | ".join(col.name for col in cur.description))
                print("-" * 60)
                for row in rows:
                    print(" | ".join(str(value) for value in row))
    finally:
        conn.close()


if __name__ == "__main__":
    run_all_queries()