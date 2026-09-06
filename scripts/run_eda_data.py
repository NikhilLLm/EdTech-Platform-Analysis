import duckdb
import pandas as pd

con = duckdb.connect("data/edtech.duckdb", read_only=True)

queries = {
    "1. Distribution of signup -> first-enrollment gap (days) (Metric A)": """
        WITH user_first_enroll AS (
            SELECT user_id, MIN(enrollment_date) AS first_enroll_dt
            FROM stg_enrollments 
            GROUP BY user_id
        ),
        gaps AS (
            SELECT DATE_DIFF('day', u.signup_date, CAST(f.first_enroll_dt AS DATE)) AS gap_days
            FROM stg_users u 
            JOIN user_first_enroll f ON u.user_id = f.user_id
        )
        SELECT 
            COUNT(*) AS total_enrolled_users,
            ROUND(AVG(gap_days), 2) AS avg_days,
            QUANTILE_CONT(gap_days, 0.50) AS p50_median,
            QUANTILE_CONT(gap_days, 0.75) AS p75,
            QUANTILE_CONT(gap_days, 0.90) AS p90,
            QUANTILE_CONT(gap_days, 0.95) AS p95,
            MAX(gap_days) AS max_gap
        FROM gaps;
    """,

    "2. Distribution of enrollment -> first-lesson COMPLETED gap (days) (Metric B)": """
        WITH first_lesson_completed AS (
            SELECT 
                enrollment_id, 
                MIN(event_timestamp) AS first_lesson_comp_dt
            FROM stg_lesson_events 
            WHERE event_type = 'completed' AND lesson_number = 1 
            GROUP BY enrollment_id
        ),
        gaps AS (
            SELECT 
                DATE_DIFF('day', CAST(e.enrollment_date AS DATE), CAST(f.first_lesson_comp_dt AS DATE)) AS gap_days
            FROM stg_enrollments e 
            JOIN first_lesson_completed f ON e.enrollment_id = f.enrollment_id
        )
        SELECT 
            COUNT(*) AS total_completed_first_lesson,
            ROUND(AVG(gap_days), 2) AS avg_days,
            QUANTILE_CONT(gap_days, 0.50) AS p50_median,
            QUANTILE_CONT(gap_days, 0.75) AS p75,
            QUANTILE_CONT(gap_days, 0.90) AS p90,
            QUANTILE_CONT(gap_days, 0.95) AS p95,
            MAX(gap_days) AS max_gap
        FROM gaps;
    """,

    "3. Course Length: MAX(lesson_number) per course": """
        SELECT 
            e.course_id, 
            e.course_category, 
            MAX(l.lesson_number) AS total_lessons
        FROM stg_enrollments e 
        JOIN stg_lesson_events l ON e.enrollment_id = l.enrollment_id
        GROUP BY e.course_id, e.course_category 
        ORDER BY e.course_category, e.course_id;
    """,

    "4. Completion Rate by Course Category": """
        SELECT 
            course_category, 
            COUNT(*) AS total_enrollments,
            COUNT(CASE WHEN enrollment_status = 'completed' THEN 1 END) AS completed_count,
            ROUND(COUNT(CASE WHEN enrollment_status = 'completed' THEN 1 END) * 100.0 / COUNT(*), 2) AS completion_pct
        FROM stg_enrollments 
        GROUP BY course_category 
        ORDER BY completion_pct DESC;
    """,

    "5. Payment Conversion Rate by Signup Channel (Completed Users Denominator)": """
        WITH completed_users AS (
            SELECT DISTINCT user_id
            FROM stg_enrollments
            WHERE enrollment_status = 'completed'
        ),
        paid_users_per_channel AS (
            SELECT DISTINCT e.user_id
            FROM stg_enrollments e
            JOIN stg_payments p ON e.enrollment_id = p.enrollment_id
        )
        SELECT 
            u.signup_channel,
            COUNT(DISTINCT c.user_id) AS total_completed_users,
            COUNT(DISTINCT p.user_id) AS paid_users,
            ROUND(COUNT(DISTINCT p.user_id) * 100.0 / COUNT(DISTINCT c.user_id), 2) AS payment_conversion_pct
        FROM stg_users u
        JOIN completed_users c ON u.user_id = c.user_id
        LEFT JOIN paid_users_per_channel p ON u.user_id = p.user_id
        GROUP BY u.signup_channel
        ORDER BY payment_conversion_pct DESC;
    """,

    "6. Quiz Pass Rate per Lesson Number": """
        SELECT 
            lesson_number,
            COUNT(CASE WHEN event_type = 'quiz_passed' THEN 1 END) AS passed,
            COUNT(CASE WHEN event_type = 'quiz_failed' THEN 1 END) AS failed,
            ROUND(
                COUNT(CASE WHEN event_type = 'quiz_passed' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN event_type IN ('quiz_passed', 'quiz_failed') THEN 1 END), 0), 
                2
            ) AS pass_rate_pct
        FROM stg_lesson_events 
        GROUP BY lesson_number 
        ORDER BY lesson_number;
    """,

    "7. Experiment Group Split Sizes": """
        SELECT 
            experiment_group, 
            COUNT(*) AS total_users,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS split_pct
        FROM stg_users 
        GROUP BY experiment_group;
    """,

    "8. Payment Records vs. Distinct Paying Users (Multi-Certification Check)": """
        WITH user_pay_counts AS (
            SELECT 
                e.user_id, 
                COUNT(p.payment_id) AS pay_count
            FROM stg_enrollments e
            JOIN stg_payments p ON e.enrollment_id = p.enrollment_id
            GROUP BY e.user_id
        )
        SELECT 
            (SELECT COUNT(*) FROM stg_payments) AS total_payments_rows,
            COUNT(*) AS distinct_paying_users,
            ROUND((SELECT COUNT(*) FROM stg_payments) * 1.0 / COUNT(*), 2) AS avg_payments_per_user,
            COUNT(CASE WHEN pay_count = 1 THEN 1 END) AS single_cert_payers,
            COUNT(CASE WHEN pay_count > 1 THEN 1 END) AS multi_cert_payers,
            ROUND(COUNT(CASE WHEN pay_count > 1 THEN 1 END) * 100.0 / COUNT(*), 2) AS multi_cert_payer_pct
        FROM user_pay_counts;
    """
}

with open("eda_results.txt", "w", encoding="utf-8") as f:
    for title, q in queries.items():
        f.write(f"=== {title} ===\n")
        df = con.execute(q).df()
        f.write(df.to_string(index=False) + "\n\n")

con.close()
print("Refined EDA results successfully written to eda_results.txt!")
