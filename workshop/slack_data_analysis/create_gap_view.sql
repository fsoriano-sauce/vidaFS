CREATE OR REPLACE VIEW `slack_wescope.data_gap_analysis` AS
SELECT 
  FORMAT_DATE("%Y-%m", TIMESTAMP_SECONDS(CAST(CAST(ts AS FLOAT64) AS INT64))) as month,
  COUNT(*) as message_count,
  MIN(_fivetran_synced) as first_sync_timestamp,
  MAX(_fivetran_synced) as last_sync_timestamp,
  CASE 
    WHEN COUNT(*) = 0 THEN 'MISSING'
    WHEN MAX(_fivetran_synced) < TIMESTAMP("2025-08-01") THEN 'STALE'
    ELSE 'ACTIVE'
  END as status
FROM slack_wescope.message
GROUP BY 1
ORDER BY 1 DESC
