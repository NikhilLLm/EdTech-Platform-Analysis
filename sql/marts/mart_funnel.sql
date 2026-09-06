CREATE OR REPLACE TABLE mart_funnel AS
WITH course_catalog AS (
    SELECT 'CRS_PY_101' AS course_id, 8 AS total_lessons UNION ALL
    SELECT 'CRS_JS_102', 10 UNION ALL
    SELECT 'CRS_WEB_103', 10 UNION ALL
    SELECT 'CRS_SQL_201', 8 UNION ALL
    SELECT 'CRS_BI_202', 8 UNION ALL
    SELECT 'CRS_DS_203', 10 UNION ALL
    SELECT 'CRS_UX_301', 8 UNION ALL
    SELECT 'CRS_FIG_302', 6 UNION ALL
    SELECT 'CRS_SEO_401', 8 UNION ALL
    SELECT 'CRS_DM_402', 8 UNION ALL
    SELECT 'CRS_AWS_501', 10 UNION ALL
    SELECT 'CRS_DOCK_502', 8
),
lesson_aggregates AS (
    SELECT 
        enrollment_id,
        MIN(CASE WHEN lesson_number = 1 AND event_type = 'started' THEN event_timestamp END) AS first_lesson_started_at,
        MIN(CASE WHEN lesson_number = 1 AND event_type = 'completed' THEN event_timestamp END) AS first_lesson_completed_at,
        MAX(event_timestamp) AS last_event_at,
        MAX(lesson_number) AS max_lesson_reached,
        COUNT(CASE WHEN event_type = 'quiz_passed' THEN 1 END) AS quizzes_passed,
        COUNT(CASE WHEN event_type = 'quiz_failed' THEN 1 END) AS quizzes_failed
    FROM stg_lesson_events
    GROUP BY enrollment_id
)
SELECT 
    e.enrollment_id,
    e.user_id,
    e.course_id,
    e.course_category,
    e.enrollment_date,
    e.enrollment_status,
    c.total_lessons AS course_total_lessons,
    l.first_lesson_started_at,
    l.first_lesson_completed_at,
    l.last_event_at,
    COALESCE(l.max_lesson_reached, 0) AS max_lesson_reached,
    COALESCE(l.quizzes_passed, 0) AS quizzes_passed,
    COALESCE(l.quizzes_failed, 0) AS quizzes_failed,
    ROUND(
        COALESCE(l.quizzes_passed, 0) * 1.0 / 
        NULLIF(COALESCE(l.quizzes_passed, 0) + COALESCE(l.quizzes_failed, 0), 0), 
        4
    ) AS quiz_pass_rate,
    -- Calibrated Metric B: Completed Lesson 1 within 2 days of enrollment
    CASE 
        WHEN l.first_lesson_completed_at IS NOT NULL 
             AND DATE_DIFF('day', CAST(e.enrollment_date AS DATE), CAST(l.first_lesson_completed_at AS DATE)) <= 2 
        THEN TRUE 
        ELSE FALSE 
    END AS is_activated_metric_b,
    CASE WHEN e.enrollment_status = 'completed' THEN TRUE ELSE FALSE END AS is_course_completed,
    CASE WHEN p.payment_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_paid,
    p.payment_id,
    p.amount AS payment_amount,
    p.payment_date
FROM stg_enrollments e
LEFT JOIN course_catalog c ON e.course_id = c.course_id
LEFT JOIN lesson_aggregates l ON e.enrollment_id = l.enrollment_id
LEFT JOIN stg_payments p ON e.enrollment_id = p.enrollment_id;
