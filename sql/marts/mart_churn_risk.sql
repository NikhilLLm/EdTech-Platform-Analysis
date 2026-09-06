CREATE OR REPLACE TABLE mart_churn_risk AS
WITH user_aggregates AS (
    SELECT 
        user_id,
        COUNT(enrollment_id) AS total_enrolled_courses,
        COUNT(CASE WHEN is_course_completed THEN 1 END) AS total_completed_courses,
        COUNT(CASE WHEN is_paid THEN 1 END) AS total_paid_certificates,
        MAX(last_event_at) AS last_activity_at,
        SUM(quizzes_passed) AS total_quizzes_passed,
        SUM(quizzes_failed) AS total_quizzes_failed
    FROM mart_funnel
    GROUP BY user_id
)
SELECT 
    u.user_id,
    u.signup_date,
    u.signup_channel,
    u.country,
    COALESCE(a.total_enrolled_courses, 0) AS total_enrolled_courses,
    COALESCE(a.total_completed_courses, 0) AS total_completed_courses,
    COALESCE(a.total_paid_certificates, 0) AS total_paid_certificates,
    ROUND(
        COALESCE(a.total_completed_courses, 0) * 1.0 / 
        NULLIF(COALESCE(a.total_enrolled_courses, 0), 0), 
        4
    ) AS completion_ratio,
    a.last_activity_at,
    -- Recency relative to platform snapshot end date (2024-12-31)
    DATE_DIFF('day', CAST(COALESCE(a.last_activity_at, u.signup_date) AS DATE), DATE '2024-12-31') AS days_since_last_activity,
    CASE 
        WHEN a.total_completed_courses > 0 AND a.total_completed_courses = a.total_enrolled_courses THEN 'Completed All'
        WHEN DATE_DIFF('day', CAST(COALESCE(a.last_activity_at, u.signup_date) AS DATE), DATE '2024-12-31') > 30 THEN 'High Churn Risk'
        WHEN DATE_DIFF('day', CAST(COALESCE(a.last_activity_at, u.signup_date) AS DATE), DATE '2024-12-31') BETWEEN 14 AND 30 THEN 'Medium Churn Risk'
        ELSE 'Active / Low Risk'
    END AS churn_risk_segment
FROM stg_users u
LEFT JOIN user_aggregates a ON u.user_id = a.user_id;
