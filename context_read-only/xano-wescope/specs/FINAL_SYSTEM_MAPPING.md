# FINAL SYSTEM MAPPING: Xano ↔ Stripe ↔ QBO

**Purpose**: Definitive field mapping for Stripe → QBO sync implementation
**Source**: Actual data from BigQuery (Xano, Stripe, QBO tables)
**Last Updated**: November 2, 2025
**Status**: READY FOR IMPLEMENTATION

---

## 🔑 PRIMARY KEY MAPPINGS

### Invoice Level

| System | Field | Type | Example | Notes |
|--------|-------|------|---------|-------|
| **Stripe** | `invoice.id` | STRING (PK) | `in_1SDZnpL6RKmCZ5rpAZ0cCnuj` | **Source of Truth** |
| **QBO** | `invoice.id` | STRING (PK) | `36877` | QBO-generated |
| **Storage** | QBO `private_note` | TEXT | `Stripe: in_1SDZnpL6...` | Human-readable link |

**Linking Strategy**: Store Stripe invoice.id in QBO private_note field

### Line Item Level

| System | Field | Type | Example | Notes |
|--------|-------|------|---------|-------|
| **Stripe** | `invoice_line_item.id` | STRING (PK) | `il_1SDZnoL6RKmCZ5rpXY97UCrf` | **Globally unique** |
| **QBO** | Composite: `(invoice_id, line_num)` | STRING + INTEGER | `(36877, 1)` | No single PK |
| **Linking** | BigQuery `invoice_line_links` table | | | Maps Stripe line ID → QBO composite |

---

## 👥 CUSTOMER MAPPING (3-Way)

| System | PK Field | Type | Example | FK to Next System |
|--------|----------|------|---------|-------------------|
| **Xano** | `ptl_client.id` | INTEGER | `42` | `stripe_customer_id` → |
| **Stripe** | `customer.id` | STRING | `cus_PURaTTR54CMQOh` | (stored in Xano) |
| **QBO** | `customer.customer_id` | STRING | `3` | `quickbooks_id` ← |
| **Xano (return)** | `ptl_client.quickbooks_id` | STRING | `3` | Populated by Princess |

**Lookup Flow**:
```
1. Stripe invoice.customer_id (cus_...) 
   ↓
2. Query Xano: WHERE stripe_customer_id = 'cus_...'
   ↓
3. Get: xano_client.quickbooks_id
   ↓
4. Use as QBO CustomerRef
```

**Current State**: 
- `quickbooks_id` field EXISTS in Xano ✅
- Currently NOT populated (mostly NULL)
- Will be populated after Princess completes CUSTOMER_MAPPING_FOR_PRINCESS.csv

---

## 🎯 SUBSCRIPTION TIER → QBO CLASS MAPPING

**Source**: Xano `ptl_subscription` table + QBO `class` table

### Complete Mapping Table

| Xano ID | Xano Name | Monthly $ | Stripe Price ID | QBO Class ID | QBO Class Name |
|---------|-----------|-----------|-----------------|--------------|----------------|
| **2** | Tier 1 | $1,500 | `price_1L43RYL6RKmCZ5rpkt8ruWeU` | `7100000000001469972` | Tier 1 |
| **3** | Tier 2 | $2,750 | `price_1L43RYL6RKmCZ5rpwsalp7e6` | `7100000000001469973` | Tier 2 |
| **4** | Tier 3 | $4,375 | `price_1L43RYL6RKmCZ5rpw72NLZrP` | `7100000000001474303` | Tier 3 |
| **5** | Tier 4 | $5,500 | `price_1L43RYL6RKmCZ5rpLWnLHGMd` | `7100000000001474306` | Tier 4 |
| **12** | Essential | $500 | `price_1RHsusL6RKmCZ5rpaxyuUhpM` | `568237` | Essential |
| **13** | Plus | $1,500 | `price_1RHsvKL6RKmCZ5rp0M4HKD2c` | `568238` | Plus |
| **14** | Pro | $3,000 | `price_1RHsvpL6RKmCZ5rphL71b4OD` | `568239` | Pro |
| **8** | Large Loss | $500 | `price_1LsvJ8L6RKmCZ5rpTMfH9oXE` | `7100000000001474638` | Large Loss |
| **9** | Arc - Custom | $0 | (none) | `7100000000001474308` | ARC Services |

**Key Insight**: Xano has `stripe_price_id` field!
- This can be used as the linking key instead of Xano subscription_id
- When QBO sync runs, look up Stripe price → QBO class

**Recommended Mapping Strategy**:
```
Option B: Create mapping table in BigQuery (BEST for this case)

Table: subscription_tier_class_mapping
  - stripe_price_id (STRING PK)
  - xano_subscription_id (INTEGER)
  - qbo_class_id (STRING)
  - tier_name (STRING)
  - monthly_amount (INTEGER)

Why BigQuery instead of Xano?
✓ Xano already mirrors to BigQuery via Fivetran
✓ Sync function reads from BigQuery anyway
✓ No need to add field to Xano Subscription table
✓ Easier to update (SQL update vs Xano UI)
✓ Version controlled with change history
```

---

## 📝 LINE ITEM METADATA MAPPING

### Stripe metadata.type → QBO Item + Account

| Stripe `metadata.type` | QBO `sales_item_item_id` | QBO `sales_item_account_id` | Description |
|------------------------|--------------------------|------------------------------|-------------|
| `NULL` or `{}` (subscription) | `45` | `209` | Subscription fees (AR) |
| `"Large Loss"` | `46` | `126` | Large loss project fees (AR) |
| `"Volume"` | `48` | `200` | Volume/Tier 4 fees (AR) |
| `"Overage"` | `47` | `221` | Overage fees (AR) |
| `"Discount"` | `44` | `203` | Discounts/credits |

**Note**: This mapping is DETERMINISTIC and will be hardcoded in sync function

---

## 💾 QBO INVOICE FIELDS FOR STRIPE ID STORAGE

**Available Fields**:
1. ✅ **`private_note`** (TEXT) - **RECOMMENDED**
   - Internal only (not customer-facing)
   - Can store: `Stripe: in_1SDZnpL6... | Period: 2025-10-01 to 2025-11-01`
   - Already used by Princess in manual process

2. ⚠️ `customer_memo` (STRING) - **NOT recommended**
   - Customer-facing (appears on invoice)
   - Should be used for customer communications

3. ⚠️ `custom_p_o_number` (STRING) - **NOT recommended**
   - Intended for PO numbers
   - Misuse of field semantics

4. ⚠️ `tracking_number` (STRING) - **NOT recommended**
   - Intended for shipment tracking
   - Not relevant for service invoices

**Decision**: Use `private_note` for Stripe invoice.id ✅

---

## ❓ QUESTION FOR PRINCESS & LOGAN

**Should we change QBO doc_number format to use Stripe invoice.id or number?**

### Current Format
- `BI251031001` (BI + YYMMDD + sequence)
- Human-readable, encodes date
- Princess's current process

### Option A: Use Stripe invoice.id
- Example: `in_1SDZnpL6RKmCZ5rpAZ0cCnuj`
- Pros: Direct 1:1 mapping, no separate storage needed
- Cons: Long, not human-readable, no date encoding

### Option B: Use Stripe invoice.number
- Example: `391BEB0D-0`
- Pros: Shorter, unique
- Cons: Still not human-readable, UUID-like format

### Option C: Keep current format + store Stripe ID in private_note
- Example doc_number: `BI251031001`
- private_note: `Stripe: in_1SDZnpL6RKmCZ5rpAZ0cCnuj`
- Pros: Human-readable, date-encoded, still linkable
- Cons: Requires private_note parsing for reverse lookup

**RECOMMENDATION**: Option C (keep current format, use private_note)
- Maintains Princess's existing workflow
- Human-readable for accounting team
- Stripe ID available in private_note for technical lookup
- Best of both worlds

**Question for Princess**: Do you prefer to keep `BI251031001` format or switch to Stripe IDs?

---

## 📊 COMPLETE FIELD MAPPING SUMMARY

### Xano → Stripe → QBO (Critical Fields Only)

| Purpose | Xano | Stripe | QBO | Notes |
|---------|------|--------|-----|-------|
| **Customer** | `ptl_client.id` (INT) | `invoice.customer_id` (STRING) | `invoice.customer_id` (STRING) | Via ptl_client.quickbooks_id |
| **Subscription Tier** | `ptl_client.subscription_id` (INT) | `subscription.price_id` (STRING) | `invoice_line.sales_item_class_id` (STRING) | Via mapping table |
| **Invoice ID** | N/A | `invoice.id` (STRING PK) | `invoice.private_note` (TEXT) | Store for reference |
| **Line Item ID** | N/A | `invoice_line_item.id` (STRING PK) | Composite: `(invoice_id, line_num)` | Via invoice_line_links |
| **Accrual Date** | N/A | `invoice.period_start` (TIMESTAMP) | `invoice.transaction_date` (DATE) | LAST_DAY(MONTH(period_start)) |
| **Amount** | N/A | `invoice.total` (INT cents) | `invoice.total_amount` (NUMERIC $) | Divide by 100 |
| **Line Amount** | N/A | `line_item.amount` (INT cents) | `invoice_line.amount` (NUMERIC $) | Divide by 100 |
| **Line Type** | N/A | `line_item.metadata.type` (STRING) | `invoice_line.sales_item_item_id` (STRING) | Via deterministic mapping |

---

## 🗄️ BIGQUERY TABLES TO CREATE

### 1. `subscription_tier_class_mapping` (NEW)

```sql
CREATE TABLE xano-fivetran-bq.subscription_tier_class_mapping (
  stripe_price_id STRING PRIMARY KEY,
  xano_subscription_id INTEGER NOT NULL,
  qbo_class_id STRING NOT NULL,
  tier_name STRING,
  monthly_amount INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Populate from FINAL_XANO_TO_QBO_CLASS_MAPPING.csv
INSERT INTO subscription_tier_class_mapping VALUES
  ('price_1L43RYL6RKmCZ5rpkt8ruWeU', 2, '7100000000001469972', 'Tier 1', 1500, CURRENT_TIMESTAMP()),
  ('price_1L43RYL6RKmCZ5rpwsalp7e6', 3, '7100000000001469973', 'Tier 2', 2750, CURRENT_TIMESTAMP()),
  ('price_1L43RYL6RKmCZ5rpw72NLZrP', 4, '7100000000001474303', 'Tier 3', 4375, CURRENT_TIMESTAMP()),
  ('price_1L43RYL6RKmCZ5rpLWnLHGMd', 5, '7100000000001474306', 'Tier 4', 5500, CURRENT_TIMESTAMP()),
  ('price_1RHsusL6RKmCZ5rpaxyuUhpM', 12, '568237', 'Essential', 500, CURRENT_TIMESTAMP()),
  ('price_1RHsvKL6RKmCZ5rp0M4HKD2c', 13, '568238', 'Plus', 1500, CURRENT_TIMESTAMP()),
  ('price_1RHsvpL6RKmCZ5rphL71b4OD', 14, '568239', 'Pro', 3000, CURRENT_TIMESTAMP()),
  ('price_1LsvJ8L6RKmCZ5rpTMfH9oXE', 8, '7100000000001474638', 'Large Loss', 500, CURRENT_TIMESTAMP()),
  ('', 9, '7100000000001474308', 'ARC Services', 0, CURRENT_TIMESTAMP());
```

### 2. `invoicing_links` (Invoice Level)

```sql
CREATE TABLE xano-fivetran-bq.invoicing_links (
  link_id STRING PRIMARY KEY,
  stripe_invoice_id STRING NOT NULL UNIQUE,
  qbo_invoice_id STRING NOT NULL,
  qbo_doc_number STRING NOT NULL,
  xano_client_id INTEGER NOT NULL,
  accrual_date DATE NOT NULL,
  stripe_total_cents INTEGER,
  qbo_total_dollars NUMERIC,
  synced_at TIMESTAMP NOT NULL,
  status STRING
);

CREATE INDEX idx_stripe_invoice ON invoicing_links(stripe_invoice_id);
CREATE INDEX idx_qbo_invoice ON invoicing_links(qbo_invoice_id);
```

### 3. `invoice_line_links` (Line Item Level)

```sql
CREATE TABLE xano-fivetran-bq.invoice_line_links (
  link_id STRING PRIMARY KEY,
  stripe_line_item_id STRING NOT NULL UNIQUE,
  qbo_invoice_id STRING NOT NULL,
  qbo_line_num INTEGER NOT NULL,
  stripe_invoice_id STRING NOT NULL,
  metadata_type STRING,
  qbo_item_id STRING,
  qbo_account_id STRING,
  qbo_class_id STRING,
  stripe_amount_cents INTEGER,
  qbo_amount_dollars NUMERIC,
  synced_at TIMESTAMP NOT NULL,
  UNIQUE (qbo_invoice_id, qbo_line_num)
);

CREATE INDEX idx_stripe_line ON invoice_line_links(stripe_line_item_id);
```

### 4. `stripe_qbo_sync_log` (Audit Trail)

```sql
CREATE TABLE xano-fivetran-bq.stripe_qbo_sync_log (
  log_id STRING PRIMARY KEY,
  sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  stripe_invoice_id STRING,
  qbo_invoice_id STRING,
  qbo_doc_number STRING,
  xano_client_id INTEGER,
  line_count INTEGER,
  stripe_total_cents INTEGER,
  qbo_total_dollars NUMERIC,
  status STRING,  -- 'success', 'error', 'duplicate', 'validation_failed'
  error_message TEXT,
  error_code STRING,
  retry_count INTEGER DEFAULT 0
);
```

---

## 🔄 SYNC LOGIC: FIELD-BY-FIELD

### Step 1: Query Unsynced Invoices

```sql
SELECT 
  i.id as stripe_invoice_id,
  i.customer_id as stripe_customer_id,
  i.total as stripe_total_cents,
  i.period_start,
  i.period_end,
  i.created,
  i.due_date
FROM stripe.invoice i
WHERE i.created >= '2025-11-01'
  AND i.status IN ('open', 'paid')
  AND i.id NOT IN (SELECT stripe_invoice_id FROM invoicing_links)
ORDER BY i.created
LIMIT 100;
```

### Step 2: Look Up Customer

```sql
-- Get Xano client
SELECT id, quickbooks_id, subscription_id, full_name
FROM staging_xano.ptl_client
WHERE stripe_customer_id = '<stripe_customer_id>';

-- If quickbooks_id is NULL:
--   STOP - Customer not mapped yet
--   Log error for Princess to resolve
```

### Step 3: Look Up Subscription Tier → QBO Class

```sql
-- Get Xano subscription
SELECT id, stripe_price_id
FROM staging_xano.ptl_subscription
WHERE id = <client.subscription_id>;

-- Map to QBO Class
SELECT qbo_class_id
FROM subscription_tier_class_mapping
WHERE stripe_price_id = '<subscription.stripe_price_id>';
```

### Step 4: Process Line Items (1:1 Mapping)

For each Stripe `invoice_line_item`:

```javascript
{
  stripe_line_item_id: "il_1SDZnoL6RKmCZ5rpXY97UCrf",
  metadata_type: line_item.metadata["type"] || "Subscription",
  
  // Map to QBO Item/Account
  qbo_item_id: mapping[metadata_type].item_id,  // 45, 46, 47, 48, or 44
  qbo_account_id: mapping[metadata_type].account_id,  // 209, 126, 200, 221, or 203
  qbo_class_id: <from step 3>,  // Customer's subscription tier
  
  description: line_item.description,  // Copy as-is
  amount: line_item.amount / 100,  // Cents → dollars
}
```

### Step 5: Calculate Accrual Date

```sql
-- Extract period month
SET accrual_month = EXTRACT(MONTH FROM invoice.period_start);
SET accrual_year = EXTRACT(YEAR FROM invoice.period_start);

-- Get last day of that month
SET accrual_date = LAST_DAY(DATE(accrual_year, accrual_month, 1));

-- Example: period_start = 2025-10-01 → accrual_date = 2025-10-31
```

### Step 6: Create QBO Invoice

```json
POST /v2/company/{realmId}/invoice
{
  "CustomerRef": {"value": "<xano_client.quickbooks_id>"},
  "DocNumber": "<generated_bi_number>",
  "TxnDate": "<accrual_date>",
  "DueDate": "<accrual_date + 30 days>",
  "PrivateNote": "Stripe: <invoice.id> | Period: <period_start> to <period_end>",
  "Line": [
    {
      "DetailType": "SalesItemLineDetail",
      "Amount": <line.amount / 100>,
      "Description": "<line.description>",
      "SalesItemLineDetail": {
        "ItemRef": {"value": "<qbo_item_id>"},
        "ClassRef": {"value": "<qbo_class_id>"}
        // NOTE: Test if AccountRef is required or auto-populated
      }
    }
  ]
}
```

### Step 7: Store Links

```sql
-- Invoice level
INSERT INTO invoicing_links (
  link_id, stripe_invoice_id, qbo_invoice_id, qbo_doc_number,
  xano_client_id, accrual_date, synced_at, status
) VALUES (
  UUID(), '<invoice.id>', '<qbo_response.Id>', '<qbo_response.DocNumber>',
  <xano_client.id>, '<accrual_date>', CURRENT_TIMESTAMP(), 'linked'
);

-- Line item level
INSERT INTO invoice_line_links (
  link_id, stripe_line_item_id, qbo_invoice_id, qbo_line_num,
  stripe_invoice_id, metadata_type, qbo_item_id, qbo_account_id,
  qbo_class_id, synced_at
) VALUES (
  UUID(), '<line_item.id>', '<qbo_invoice.Id>', <line_num>,
  '<invoice.id>', '<metadata.type>', '<item_id>', '<account_id>',
  '<class_id>', CURRENT_TIMESTAMP()
);
```

---

## ⚠️ OPEN QUESTIONS FOR PRINCESS

1. **Invoice Number Format**:
   - Keep current: `BI251031001` (BI + date + sequence) ✓
   - OR switch to: Stripe invoice.id (`in_1SDZnp...`) or number (`391BEB0D-0`)?
   - **Recommendation**: Keep current + store Stripe ID in private_note

2. **Customer Mapping**:
   - Complete `CUSTOMER_MAPPING_FOR_PRINCESS.csv` (65 Stripe customers)
   - This will populate Xano `ptl_client.quickbooks_id` field

3. **Future Customer Creation**:
   - Should we auto-create QBO customers from Stripe going forward?
   - This would ensure name consistency across systems

---

## ⚠️ OPEN QUESTIONS FOR LOGAN

1. **AccountRef in QBO API**:
   - QBO Items have default accounts pre-configured
   - Test if AccountRef can be OMITTED (likely not required)
   - If successful: Cleaner API payload
   - If fails: Keep AccountRef (redundant but safe)

2. **Accrual Edge Cases**:
   - Mid-month start (Oct 15-Nov 15) → Use Oct 31? ✓
   - Period spans months (Oct 20-Nov 20) → Use Oct 31? ✓
   - Confirmed: Always use LAST_DAY(MONTH(period_start))

---

## ✅ FINALIZED DECISIONS

1. ✅ **Stripe invoice.id** → Store in QBO `private_note`
2. ✅ **Stripe line_item.id** → Link via BigQuery `invoice_line_links` table
3. ✅ **Customer mapping** → Use Xano `ptl_client.quickbooks_id` (Princess to populate)
4. ✅ **Subscription tier** → Map via `subscription_tier_class_mapping` table in BigQuery
5. ✅ **Line item mapping** → 1:1 deterministic (metadata.type → Item/Account)
6. ✅ **Accrual date** → LAST_DAY(MONTH(period_start))
7. ✅ **Amount conversion** → Stripe cents ÷ 100 = QBO dollars
8. ✅ **Start date** → 11/1/2025 (no historical backfill)

---

**Status**: FINAL MAPPING COMPLETE - Ready for implementation review

