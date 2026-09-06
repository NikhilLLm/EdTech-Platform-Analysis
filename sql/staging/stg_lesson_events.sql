CREATE OR REPLACE TABLE stg_lesson_events AS
SELECT
    TRIM(event_id) AS event_id,
    TRIM(enrollment_id) AS enrollment_id,
    lesson_number,
    TRIM(event_type) AS event_type,
    COALESCE(
        TRY_STRPTIME(event_timestamp, '%Y-%m-%d %H:%M:%S'),
        TRY_STRPTIME(event_timestamp, '%Y/%m/%d %H:%M:%S'),
        TRY_STRPTIME(event_timestamp, '%d-%m-%Y %H:%M:%S'),
        TRY_STRPTIME(event_timestamp, '%Y-%m-%dT%H:%M:%SZ')
    ) AS event_timestamp
FROM read_csv_auto('data/raw/lesson_events.csv');
