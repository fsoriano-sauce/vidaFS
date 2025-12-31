# BigQuery Invoicing Logic Implementation Specification

## Executive Summary

This document provides complete specifications for replicating the Xano invoicing system in BigQuery. The system processes monthly client usage into two-part invoices: subscription fees and variable costs. The logic handles multiple pricing tiers, volume calculations, overage fees, and large loss processing.

**Key Architecture**: Two-invoice system (subscription + variable costs) → Single QBO invoice with multiple line items

---

## 1. System Architecture

### 1.1 Data Flow
```
Xano Usage Data → BigQuery Processing → Stripe Invoice Creation → QBO Sync
```

### 1.2 Invoice Structure
- **INVOICE #1**: Subscription (auto-billed, recurring)
- **INVOICE #2**: Variable Costs (manual, usage-based)

### 1.3 Processing Timeline
- Monthly execution on billing cycle end
- Processes all eligible clients with active subscriptions
- Historical cutoff: 2025-11-01

---

## 2. Function Specifications

### 2.1 Calculate Delivered Volume Function

**Purpose**: Calculate billable usage volume for a client in a given month

**Input Parameters**:
- `client_id` (INTEGER): Xano client.id
- `month_start` (TIMESTAMP): Billing period start date
- `month_end` (TIMESTAMP): Billing period end date

**Output**: DECIMAL - Total billable volume units

**Logic Pseudocode**:
```sql
-- Calculate Delivered Volume Function
CREATE FUNCTION calculate_delivered_volume(client_id INT64, month_start TIMESTAMP, month_end TIMESTAMP)
RETURNS FLOAT64
AS (
  -- Get all non-canceled jobs for this client
  WITH client_jobs AS (
    SELECT j.id as job_id
    FROM xano.job j
    WHERE j.client_id = client_id
    AND j.canceled = false
  ),

  -- Get all submits for this client in billing period
  client_submits AS (
    SELECT
      s.id,
      s.type,
      s.invoiceable_value,
      s.submission_date,
      s.job_id
    FROM xano.submit s
    INNER JOIN client_jobs cj ON s.job_id = cj.job_id
    WHERE s.submission_date >= month_start
    AND s.submission_date < month_end
  ),

  -- Calculate volume by submission type
  volume_calculation AS (
    SELECT
      SUM(
        CASE
          -- Base volume for QA/Change Order QA
          WHEN type IN ('QA', 'Change Order QA') THEN 1.0

          -- Supplemental volume with multipliers
          WHEN type = 'Supplemental' THEN
            CASE
              -- Large loss threshold: $50,000
              WHEN invoiceable_value >= 50000 THEN 0.005
              ELSE 0.0125
            END

          -- Revision adjustments
          WHEN type = 'Revision' THEN 1.0

          ELSE 0
        END
      ) as total_volume
    FROM client_submits
  )

  SELECT COALESCE(total_volume, 0) FROM volume_calculation
);
```

### 2.2 Invoice - All Cases (New Pricing) Function

**Purpose**: Main invoicing function for current pricing model

**Input Parameters**:
- `client_id` (INTEGER): Target client
- `billing_month` (DATE): Month to invoice (YYYY-MM-01)

**Output**: JSON object with invoice data

**Logic Pseudocode**:
```sql
-- Main Invoicing Function
CREATE FUNCTION generate_client_invoice(client_id INT64, billing_month DATE)
RETURNS JSON
AS (
  -- Calculate billing period dates
  month_start = DATE_TRUNC(billing_month, MONTH)
  month_end = DATE_ADD(month_start, INTERVAL 1 MONTH)

  -- Validate client eligibility
  client_data = SELECT * FROM xano.client WHERE id = client_id
  IF client_data.not_allowed = true OR client_data.suspended = true:
    RETURN ERROR "Client not eligible for invoicing"

  -- Get subscription details
  subscription = SELECT * FROM xano.subscription
                 WHERE id = client_data.subscription_id

  -- Calculate delivered volume (calls legacy function)
  delivered_volume = calculate_delivered_volume(client_id, month_start, month_end)

  -- Calculate overage if volume exceeds allowed amount
  overage_volume = MAX(0, delivered_volume - subscription.allowed_amount)
  overage_fee = overage_volume * subscription.overage_in_percentage

  -- Determine if volume fee applies (Tier 4 logic)
  volume_fee = CASE
    WHEN subscription.id = 5 THEN delivered_volume * 0.02  -- Tier 4 rate
    ELSE 0
  END

  -- Calculate large loss fees
  large_loss_fees = calculate_large_loss_fees(client_id, month_start, month_end)

  -- Build invoice structure
  invoice_data = {
    client_id: client_id,
    billing_period: {start: month_start, end: month_end},
    subscription_fee: subscription.subscription_amount,
    overage_fee: overage_fee,
    volume_fee: volume_fee,
    large_loss_fees: large_loss_fees,
    total_amount: subscription.subscription_amount + overage_fee + volume_fee + large_loss_fees.total
  }

  RETURN invoice_data
);
```

### 2.3 Calculate Large Loss Fees Function

**Purpose**: Process submissions with invoiceable_value ≥ $50,000

**Input Parameters**:
- `client_id` (INTEGER)
- `month_start` (TIMESTAMP)
- `month_end` (TIMESTAMP)

**Output**: ARRAY of large loss fee objects

**Logic Pseudocode**:
```sql
CREATE FUNCTION calculate_large_loss_fees(client_id INT64, month_start TIMESTAMP, month_end TIMESTAMP)
RETURNS ARRAY<STRUCT<job_id INT64, submit_id INT64, amount FLOAT64, description STRING>>
AS (
  -- Find all large loss submissions
  large_losses = SELECT
    s.id as submit_id,
    s.job_id,
    s.invoiceable_value,
    s.submission_date
  FROM xano.submit s
  INNER JOIN xano.job j ON s.job_id = j.job_id
  WHERE j.client_id = client_id
  AND j.canceled = false
  AND s.invoiceable_value >= 50000  -- $50,000 threshold
  AND s.submission_date >= month_start
  AND s.submission_date < month_end

  -- Calculate fee for each large loss (0.005 multiplier from volume calc)
  large_loss_fees = SELECT
    submit_id,
    job_id,
    invoiceable_value * 0.005 as fee_amount,
    CONCAT('Large Loss Fee - Job ', CAST(job_id AS STRING), ' ($', CAST(invoiceable_value AS STRING), ')') as description
  FROM large_losses

  RETURN ARRAY_AGG(STRUCT(submit_id, job_id, fee_amount, description))
);
```

---

## 3. Data Schema and Field Mappings

### 3.1 Xano to BigQuery Field Mapping

#### Client Table
| Xano Field | BigQuery Type | Description | Required for Invoicing |
|------------|---------------|-------------|----------------------|
| `id` | INT64 | Primary Key | ✓ |
| `Stripe_Customer_ID` | STRING | Stripe customer reference | ✓ |
| `subscription_id` | INT64 | FK to Subscription | ✓ |
| `Full_Name` | STRING | Client name for QBO | ✓ |
| `Not_Allowed` | BOOL | Client restriction | ✓ |
| `Suspended` | BOOL | Account suspension | ✓ |
| `Senior_Estimator_id` | INT64 | For notifications | Optional |
| `Team_Lead_id` | INT64 | For notifications | Optional |
| `Billing_POC_id` | INT64 | For invoice delivery | Optional |

#### Subscription Table
| Xano Field | BigQuery Type | Description | Required |
|------------|---------------|-------------|----------|
| `id` | INT64 | Primary Key | ✓ |
| `Name` | STRING | Subscription name | ✓ |
| `Subscription_Amount` | FLOAT64 | Monthly fee in dollars | ✓ |
| `Allowed_Amount` | FLOAT64 | Usage threshold | ✓ |
| `Overage_in_percentage` | FLOAT64 | Overage rate (decimal) | ✓ |

#### Submit Table
| Xano Field | BigQuery Type | Description | Required |
|------------|---------------|-------------|----------|
| `id` | INT64 | Primary Key | ✓ |
| `Type` | STRING | Submit type classification | ✓ |
| `Invoiceable_Value` | FLOAT64 | Dollar value | ✓ |
| `Client_id` | INT64 | FK to Client | ✓ |
| `Job_id` | INT64 | FK to Job | ✓ |
| `Submission_Date` | TIMESTAMP | When submitted | ✓ |

#### Job Table
| Xano Field | BigQuery Type | Description | Required |
|------------|---------------|-------------|----------|
| `id` | INT64 | Primary Key | ✓ |
| `Client_id` | INT64 | FK to Client | ✓ |
| `Canceled` | BOOL | Job status filter | ✓ |

#### Invoices Table (Log Only)
| Xano Field | BigQuery Type | Description | Notes |
|------------|---------------|-------------|-------|
| `id` | INT64 | Record ID | Auto-increment |
| `Associated_Client` | STRING | Xano client unique_id | NOT client.id |
| `Creation_Date` | TIMESTAMP | Log timestamp | When invoice finalized |
| `Previous_Month_Subscription` | STRING | Subscription name | For tracking |

---

## 4. Business Rules and Validation

### 4.1 Pre-Invoicing Validation Rules

```sql
-- Client Eligibility Check
CREATE FUNCTION validate_client_for_invoicing(client_id INT64)
RETURNS STRUCT<valid BOOL, reason STRING>
AS (
  client = SELECT * FROM xano.client WHERE id = client_id

  IF client IS NULL:
    RETURN STRUCT(false, "Client not found")

  IF client.not_allowed = true:
    RETURN STRUCT(false, "Client marked as not allowed")

  IF client.suspended = true:
    RETURN STRUCT(false, "Client account suspended")

  IF client.stripe_customer_id IS NULL OR client.stripe_customer_id = "":
    RETURN STRUCT(false, "Missing Stripe customer ID")

  RETURN STRUCT(true, "Valid")
);

-- Subscription Validation
CREATE FUNCTION validate_subscription_active(subscription_id INT64)
RETURNS BOOL
AS (
  subscription = SELECT * FROM xano.subscription WHERE id = subscription_id
  RETURN subscription IS NOT NULL
);
```

### 4.2 Invoice Generation Rules

1. **Volume Threshold**: Only invoice if calculated volume > 0
2. **Email Validation**: Client must have valid email for billing
3. **Date Validation**: Billing period start < end
4. **Large Loss Multiplier**: 0.005x for submissions ≥ $50,000
5. **Supplemental Multiplier**: 0.0125x for normal supplementals
6. **Base Volume**: 1.0x for QA/Change Order QA submissions
7. **Revision Adjustment**: 1.0x base rate adjustments

### 4.3 Overage Calculation

```sql
overage_fee = MAX(0, delivered_volume - subscription.allowed_amount) * subscription.overage_in_percentage
```

### 4.4 Tier-Specific Rules

- **Tier 4 (subscription.id = 5)**: Additional volume fee at 2% of delivered volume
- **Legacy Tiers**: Standard overage calculation only
- **All Tiers**: Large loss processing applies universally

---

## 5. Data Pipeline Requirements

### 5.1 BigQuery Tables to Create

```sql
-- Invoice processing staging table
CREATE TABLE `invoicing.invoice_staging` (
  client_id INT64,
  billing_month DATE,
  subscription_fee FLOAT64,
  overage_fee FLOAT64,
  volume_fee FLOAT64,
  large_loss_fees JSON,  -- Array of large loss objects
  total_amount FLOAT64,
  processing_status STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Invoice finalization log
CREATE TABLE `invoicing.invoice_log` (
  client_id INT64,
  billing_month DATE,
  stripe_invoice_id STRING,
  qbo_invoice_id STRING,
  total_amount FLOAT64,
  processing_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### 5.2 Scheduled Query for Monthly Processing

```sql
-- Monthly invoice generation (runs on 1st of each month)
CREATE OR REPLACE TABLE `invoicing.monthly_invoices`
AS
SELECT
  client_id,
  DATE_TRUNC(CURRENT_DATE(), MONTH) as billing_month,
  generate_client_invoice(client_id, DATE_TRUNC(CURRENT_DATE(), MONTH)) as invoice_data
FROM xano.client
WHERE validate_client_for_invoicing(id).valid = true;
```

### 5.3 Error Handling and Logging

```sql
-- Error logging table
CREATE TABLE `invoicing.processing_errors` (
  client_id INT64,
  billing_month DATE,
  error_type STRING,
  error_message STRING,
  error_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

---

## 6. Implementation Notes

### 6.1 Function Dependencies

1. `calculate_delivered_volume` - Core volume calculation
2. `calculate_large_loss_fees` - Large loss processing
3. `validate_client_for_invoicing` - Pre-flight validation
4. `generate_client_invoice` - Main orchestration function

### 6.2 Critical Business Logic

- **Two-Invoice Architecture**: Must maintain separation between subscription and variable costs
- **Large Loss Threshold**: $50,000 invoiceable_value triggers special processing
- **Volume Multipliers**: Different multipliers for different submission types
- **Overage Calculation**: Only applies when usage exceeds subscription threshold

### 6.3 Data Integrity Requirements

- All calculations must use FLOAT64 for precision
- Dates must be handled in UTC
- Client validation must occur before any processing
- Invoice totals must match sum of all line items

### 6.4 Performance Considerations

- Index on client_id, submission_date for volume calculations
- Partition by billing_month for historical analysis
- Use incremental processing for large datasets

---

## 7. Edge Cases and Special Handling

### 7.1 Zero Volume Invoices
- **Rule**: Do not create invoices with $0 total
- **Handling**: Skip clients with zero calculated volume

### 7.2 Multiple Large Losses per Client
- **Rule**: Each large loss creates separate line item
- **Handling**: Aggregate all large losses into array structure

### 7.3 Subscription Changes Mid-Month
- **Rule**: Use subscription active at billing cycle end
- **Handling**: Query subscription state as of month_end date

### 7.4 Canceled Jobs
- **Rule**: Exclude submits from canceled jobs
- **Handling**: Filter WHERE job.canceled = false

### 7.5 Invalid Data Scenarios
- **Missing Stripe Customer ID**: Skip with error logging
- **Negative Invoiceable Values**: Treat as zero
- **Future Submission Dates**: Include if within billing period

---

## 8. Testing and Validation

### 8.1 Test Cases

```sql
-- Test Case 1: Normal usage within limits
-- Expected: Subscription fee only

-- Test Case 2: Overage scenario
-- Expected: Subscription + overage fee

-- Test Case 3: Large loss processing
-- Expected: Multiple line items for losses ≥ $50K

-- Test Case 4: Tier 4 volume fee
-- Expected: Additional 2% volume fee

-- Test Case 5: Invalid client
-- Expected: Skip with error logging
```

### 8.2 Reconciliation Queries

```sql
-- Amount validation
SELECT
  il.client_id,
  il.billing_month,
  il.total_amount,
  SUM(il.line_item_amounts) as calculated_total
FROM invoicing.invoice_log il
GROUP BY client_id, billing_month, total_amount
HAVING ABS(total_amount - calculated_total) > 0.01
```

---

## 9. Migration from Xano Functions

### 9.1 Key Differences
- **Batch Processing**: Xano processes real-time; BigQuery processes in batches
- **Error Handling**: BigQuery uses structured logging vs Xano exceptions
- **Data Persistence**: BigQuery stores all intermediate states
- **Reprocessing**: BigQuery allows easy reprocessing of historical data

### 9.2 Validation Against Xano
- Compare monthly totals between systems
- Validate line item counts and amounts
- Check client eligibility logic
- Verify large loss processing

---

**Status**: Ready for BigQuery implementation
**Next Steps**: Create UDFs in order of dependency, implement validation functions, set up scheduled processing

