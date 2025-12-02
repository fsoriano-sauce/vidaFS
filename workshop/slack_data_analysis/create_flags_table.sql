CREATE TABLE IF NOT EXISTS `slack_wescope.compliance_flags` (
  flag_id STRING,
  activity_date DATE,
  user_id STRING,
  employee_email STRING,
  risk_level STRING,
  category STRING,
  quote STRING,
  context STRING,
  confidence_score FLOAT64,
  analysis_ts TIMESTAMP
)
