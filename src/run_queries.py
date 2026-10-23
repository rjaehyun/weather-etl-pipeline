import sqlite3
from pathlib import Path


def run_all_queries(db_path: str = "weather.db") -> None:
    """Execute all queries in sql/queries/ and print results."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find all .sql files in queries folder
    queries_dir = Path("sql/queries")
    query_files = sorted(queries_dir.glob("*.sql"))
    
    for query_file in query_files:
        print(f"\n{'='*60}")
        print(f"Query: {query_file.name}")
        print('='*60)
        
        # Read and execute the query
        sql = query_file.read_text()
        cursor.execute(sql)
        
        # Fetch and print results
        rows = cursor.fetchall()
        if not rows:
            print("(No results)")
        else:
            # Print header
            if cursor.description:
                headers = [desc[0] for desc in cursor.description]
                print(" | ".join(headers))
                print("-" * 60)
            # Print rows
            for row in rows:
                print(" | ".join(str(val) for val in row))
    
    conn.close()


if __name__ == "__main__":
    run_all_queries()