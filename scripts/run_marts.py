import duckdb
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = str(PROJECT_ROOT / "data" / "edtech.duckdb").replace("\\", "/")

MARTS = [
    PROJECT_ROOT / "sql" / "marts" / "mart_funnel.sql",
    PROJECT_ROOT / "sql" / "marts" / "mart_lesson_quiz_funnel.sql",
    PROJECT_ROOT / "sql" / "marts" / "mart_experiment_results.sql",
    PROJECT_ROOT / "sql" / "marts" / "mart_churn_risk.sql",
    PROJECT_ROOT / "sql" / "marts" / "mart_payment_conversion.sql",
    PROJECT_ROOT / "sql" / "marts" / "mart_cohort_funnel.sql"
]

def main():
    print(f"Connecting to DuckDB: {DB_PATH}")
    con = duckdb.connect(DB_PATH)

    print("\n" + "=" * 50)
    print("BUILDING PHASE 3 MARTS")
    print("=" * 50)

    for mart_path in MARTS:
        mart_name = mart_path.name
        print(f"\nExecuting: {mart_name}...")
        with open(mart_path, "r", encoding="utf-8") as f:
            sql_code = f.read()
        con.execute(sql_code)
        print(f"Successfully created: {mart_name}")

    tables = [
        "mart_funnel",
        "mart_lesson_quiz_funnel",
        "mart_experiment_results",
        "mart_churn_risk",
        "mart_payment_conversion",
        "mart_cohort_funnel"
    ]

    print("\n" + "=" * 50)
    print("PHASE 3 MARTS VALIDATION")
    print("=" * 50)
    for table in tables:
        result = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        count = result[0] if result is not None else 0
        print(f"{table:26s}: {count:>10,d} rows")

    con.close()
    print("\nAll 6 Marts built successfully!")

if __name__ == "__main__":
    main()
