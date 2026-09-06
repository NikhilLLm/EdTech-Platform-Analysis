CREATE OR REPLACE TABLE mart_cohort_funnel AS
WITH user_milestones AS (
    SELECT 
        u.user_id,
        DATE_TRUNC('week', u.signup_date) AS signup_week,
        u.signup_date,
        MIN(f.enrollment_date) AS first_enroll_dt,
        MIN(f.first_lesson_completed_at) AS first_activation_dt,
        MIN(CASE WHEN f.is_course_completed THEN f.last_event_at END) AS first_completion_dt,
        MIN(f.payment_date) AS first_payment_dt
    FROM stg_users u
    LEFT JOIN mart_funnel f ON u.user_id = f.user_id
    GROUP BY u.user_id, u.signup_date
)
SELECT 
    signup_week,
    COUNT(user_id) AS cohort_size,
    -- Day 1 Milestones
    COUNT(CASE WHEN DATE_DIFF('day', signup_date, CAST(first_enroll_dt AS DATE)) <= 1 THEN 1 END) AS enrolled_d1,
    COUNT(CASE WHEN DATE_DIFF('day', signup_date, CAST(first_activation_dt AS DATE)) <= 1 THEN 1 END) AS activated_d1,
    -- Day 7 Milestones
    COUNT(CASE WHEN DATE_DIFF('day', signup_date, CAST(first_enroll_dt AS DATE)) <= 7 THEN 1 END) AS enrolled_d7,
    COUNT(CASE WHEN DATE_DIFF('day', signup_date, CAST(first_activation_dt AS DATE)) <= 7 THEN 1 END) AS activated_d7,
    COUNT(CASE WHEN DATE_DIFF('day', signup_date, CAST(first_completion_dt AS DATE)) <= 7 THEN 1 END) AS completed_d7,
    -- Day 30 Milestones
    COUNT(CASE WHEN DATE_DIFF('day', signup_date, CAST(first_enroll_dt AS DATE)) <= 30 THEN 1 END) AS enrolled_d30,
    COUNT(CASE WHEN DATE_DIFF('day', signup_date, CAST(first_activation_dt AS DATE)) <= 30 THEN 1 END) AS activated_d30,
    COUNT(CASE WHEN DATE_DIFF('day', signup_date, CAST(first_completion_dt AS DATE)) <= 30 THEN 1 END) AS completed_d30,
    COUNT(CASE WHEN DATE_DIFF('day', signup_date, CAST(first_payment_dt AS DATE)) <= 30 THEN 1 END) AS paid_d30
FROM user_milestones
GROUP BY signup_week
ORDER BY signup_week;
