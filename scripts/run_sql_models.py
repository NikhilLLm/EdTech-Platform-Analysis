import duckdb
from pathlib import Path

# Get the project root (parent of scripts directory)
PROJECT_ROOT = Path(__file__).parent.parent

# Database file location
DB_PATH = PROJECT_ROOT / "data" / "edtech.duckdb"

# List of SQL files to execute in order
SQL_FILES = [
    PROJECT_ROOT / "sql" / "staging" / "stg_users.sql",
    PROJECT_ROOT / "sql" / "staging" / "stg_enrollments.sql",
    PROJECT_ROOT / "sql" / "staging" / "stg_lesson_events.sql",
    PROJECT_ROOT / "sql" / "staging" / "stg_payments.sql"
]

def main():
    # Use forward slashes for DuckDB compatibility on Windows
    db_path_str = str(DB_PATH).replace("\\", "/")
    print(f"Connecting to DuckDB: {db_path_str}")
    con = duckdb.connect(db_path_str)
    
    # Build absolute data directory path for SQL templates
    data_dir = (PROJECT_ROOT / "data" / "raw").resolve()
    data_dir_str = str(data_dir).replace("\\", "/")

    # 1. Execute each SQL file
    for sql_file in SQL_FILES:
        sql_file_str = str(sql_file).replace("\\", "/")
        print(f"\nRunning: {sql_file_str}...")
        with open(sql_file, "r", encoding="utf-8") as f:
            query = f.read()
        
        # Replace relative data paths with absolute paths
        query = query.replace("'data/raw/", f"'{data_dir_str}/")
        
        con.execute(query)
        print(f"Done: {sql_file_str}")

    # 2. Verify row counts in the created tables
    tables = [
        "stg_users",
        "stg_enrollments",
        "stg_lesson_events",
        "stg_payments"
    ]

    print("\n" + "=" * 40)
    print("PHASE 1 STAGING VALIDATION")
    print("=" * 40)

    for table in tables:
        result = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        count = result[0] if result is not None else 0
        print(f"{table:20s}: {count:>10,d} rows")

    con.close()
    print("\nPipeline execution complete!")

if __name__ == "__main__":
    main()
