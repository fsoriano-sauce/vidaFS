CREATE OR REPLACE VIEW `slack_wescope.rpt_employee_daily_summary` AS
SELECT
  DATE(TIMESTAMP_SECONDS(CAST(CAST(message_ts AS FLOAT64) AS INT64))) AS activity_date,
  user_id,
  employee_name,
  employee_email,
  -- Concatenate all messages for the day into a single text block for analysis
  STRING_AGG(
    FORMAT("On %s in #%s: %s", FORMAT_TIMESTAMP("%H:%M", TIMESTAMP_SECONDS(CAST(CAST(message_ts AS FLOAT64) AS INT64))), channel_name, message_text),
    "\n" ORDER BY message_ts
  ) AS daily_transcript
FROM `slack_wescope.stg_recent_employee_messages`
GROUP BY 1, 2, 3, 4
