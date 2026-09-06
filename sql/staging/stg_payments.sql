CREATE OR REPLACE TABLE stg_payments AS
SELECT
    TRIM(payment_id) AS payment_id,
    TRIM(enrollment_id) AS enrollment_id,
    amount,
    CAST(payment_date AS TIMESTAMP) AS payment_date,
    TRIM(certification_issued) AS certification_issued
FROM read_csv_auto('data/raw/payments.csv');
