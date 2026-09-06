CREATE OR REPLACE TABLE stg_enrollments AS
WITH ranked_enrollments AS (
    SELECT
        TRIM(enrollment_id) AS enrollment_id,
        TRIM(user_id) AS user_id,
        TRIM(course_id) AS course_id,
        TRIM(course_category) AS course_category,
        CAST(enrollment_date AS TIMESTAMP) AS enrollment_date,
        TRIM(enrollment_status) AS enrollment_status,
        ROW_NUMBER() OVER (
            PARTITION BY enrollment_id 
            ORDER BY enrollment_date ASC
        ) AS rn
    FROM read_csv_auto('data/raw/enrollments.csv')
)
SELECT 
    enrollment_id, 
    user_id, 
    course_id, 
    course_category, 
    enrollment_date, 
    enrollment_status
FROM ranked_enrollments
WHERE rn = 1;
