CREATE OR REPLACE VIEW `slack_wescope.stg_recent_employee_messages` AS
SELECT
  m.ts AS message_ts,
  m.message_channel_id AS channel_id,
  CASE
    WHEN m.message_channel_id LIKE 'D%' THEN 'Direct Message'
    WHEN m.message_channel_id LIKE 'G%' THEN 'Group Message'
    ELSE COALESCE(c.name, 'Unknown Channel')
  END AS channel_name,
  m.user_id,
  u.real_name AS employee_name,
  u.profile_email AS employee_email,
  m.text AS message_text,
  m.thread_ts,
  -- Determine if this is a thread start or reply
  COALESCE(CAST(m.thread_ts AS STRING), m.ts) AS conversation_root_id
FROM `slack_wescope.message` m
JOIN `slack_wescope.users` u ON m.user_id = u.id
LEFT JOIN `slack_wescope.channel` c ON m.message_channel_id = c.id
WHERE
  -- Filter for last 3 months
  CAST(TIMESTAMP_SECONDS(CAST(CAST(m.ts AS FLOAT64) AS INT64)) AS DATE) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)
  AND u.is_bot IS FALSE
