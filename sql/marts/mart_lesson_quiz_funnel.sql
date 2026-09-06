CREATE OR REPLACE TABLE mart_lesson_quiz_funnel AS
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
-- Cartesian grid of every enrollment x every lesson in its course (1,268,782 rows)
enrollment_lesson_grid AS (
    SELECT 
        e.enrollment_id,
        e.user_id,
        e.course_id,
        e.course_category,
        e.enrollment_status,
        unnest(range(1, c.total_lessons + 1)) AS lesson_number,
        c.total_lessons AS course_total_lessons
    FROM stg_enrollments e
    JOIN course_catalog c ON e.course_id = c.course_id
),
lesson_events_agg AS (
    SELECT 
        enrollment_id,
        lesson_number,
        MIN(CASE WHEN event_type = 'started' THEN event_timestamp END) AS lesson_started_at,
        MAX(CASE WHEN event_type = 'completed' THEN event_timestamp END) AS lesson_completed_at,
        COUNT(CASE WHEN event_type = 'quiz_passed' THEN 1 END) AS quizzes_passed,
        COUNT(CASE WHEN event_type = 'quiz_failed' THEN 1 END) AS quizzes_failed
    FROM stg_lesson_events
    GROUP BY enrollment_id, lesson_number
),
enrollment_max_attempted AS (
    SELECT 
        enrollment_id,
        MAX(lesson_number) AS max_lesson_attempted
    FROM stg_lesson_events
    GROUP BY enrollment_id
)
SELECT 
    g.enrollment_id,
    g.user_id,
    g.course_id,
    g.course_category,
    g.lesson_number,
    g.course_total_lessons,
    l.lesson_started_at,
    l.lesson_completed_at,
    CASE WHEN l.lesson_started_at IS NOT NULL THEN TRUE ELSE FALSE END AS is_started,
    CASE WHEN l.lesson_completed_at IS NOT NULL THEN TRUE ELSE FALSE END AS is_completed,
    COALESCE(l.quizzes_passed, 0) AS quizzes_passed,
    COALESCE(l.quizzes_failed, 0) AS quizzes_failed,
    ROUND(
        COALESCE(l.quizzes_passed, 0) * 1.0 / 
        NULLIF(COALESCE(l.quizzes_passed, 0) + COALESCE(l.quizzes_failed, 0), 0), 
        4
    ) AS quiz_pass_rate,
    -- Drop-off lesson: The exact lesson where an incomplete learner stopped
    CASE 
        WHEN g.enrollment_status != 'completed' 
             AND g.lesson_number = m.max_lesson_attempted 
        THEN TRUE 
        -- Also marks lesson 1 for zero-event bounces
        WHEN g.enrollment_status != 'completed' 
             AND m.max_lesson_attempted IS NULL 
             AND g.lesson_number = 1 
        THEN TRUE 
        ELSE FALSE 
    END AS is_drop_off_lesson
FROM enrollment_lesson_grid g
LEFT JOIN lesson_events_agg l ON g.enrollment_id = l.enrollment_id AND g.lesson_number = l.lesson_number
LEFT JOIN enrollment_max_attempted m ON g.enrollment_id = m.enrollment_id;
