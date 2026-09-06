CREATE OR REPLACE TABLE mart_payment_conversion AS
SELECT 
    f.enrollment_id,
    f.user_id,
    f.course_id,
    f.course_category,
    u.signup_channel,
    u.country,
    u.age,
    f.enrollment_date,
    f.last_event_at AS completion_date,
    DATE_DIFF('day', CAST(f.enrollment_date AS DATE), CAST(f.last_event_at AS DATE)) AS days_to_complete,
    f.quizzes_passed,
    f.quizzes_failed,
    f.quiz_pass_rate,
    f.is_paid,
    f.payment_amount,
    f.payment_date
FROM mart_funnel f
JOIN stg_users u ON f.user_id = u.user_id
WHERE f.is_course_completed = TRUE;
