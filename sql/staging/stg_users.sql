CREATE OR REPLACE TABLE stg_users AS
SELECT
    TRIM(user_id) AS user_id,
    CAST(signup_date AS DATE) AS signup_date,
    TRIM(signup_channel) AS signup_channel,
    TRIM(country) AS country,
    age AS age_raw,
    CASE 
        WHEN age <= 0 OR age > 100 THEN NULL 
        ELSE age 
    END AS age,
    CASE 
        WHEN age <= 0 OR age > 100 THEN TRUE 
        ELSE FALSE 
    END AS is_age_invalid,
    TRIM(experiment_group) AS experiment_group
FROM read_csv_auto('data/raw/users.csv');
