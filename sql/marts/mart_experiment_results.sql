CREATE OR REPLACE TABLE mart_experiment_results AS
SELECT 
    u.user_id,
    u.experiment_group,
    u.signup_date,
    u.signup_channel,
    u.country,
    -- Stage 1: Enrolled within calibrated Metric A window (<= 7 days)
    CASE 
        WHEN MIN(f.enrollment_date) IS NOT NULL 
             AND DATE_DIFF('day', u.signup_date, CAST(MIN(f.enrollment_date) AS DATE)) <= 7
        THEN TRUE 
        ELSE FALSE 
    END AS is_enrolled_7d,
    -- Any enrollment
    CASE WHEN COUNT(f.enrollment_id) > 0 THEN TRUE ELSE FALSE END AS is_enrolled_any,
    -- Stage 2: Activated (Metric B: Lesson 1 completed within 2 days)
    COALESCE(BOOL_OR(f.is_activated_metric_b), FALSE) AS is_activated,
    -- Stage 3: Completed Course
    COALESCE(BOOL_OR(f.is_course_completed), FALSE) AS is_completed_course,
    -- Stage 4: Paid Certification
    COALESCE(BOOL_OR(f.is_paid), FALSE) AS is_paid
FROM stg_users u
LEFT JOIN mart_funnel f ON u.user_id = f.user_id
GROUP BY 
    u.user_id, 
    u.experiment_group, 
    u.signup_date, 
    u.signup_channel, 
    u.country;
