# Stripe → QBO Sync: Proposal for Logan

**To**: Logan (WeScope leadership)
**From**: Frankie + Taz (Analysis & Architecture)
**Date**: November 1, 2025
**Status**: Ready for approval before development

---

## Executive Summary

**Objective**: Automate the manual data entry process that Princess performs monthly when syncing Stripe invoices to QuickBooks Online.

**Current State**: 
- ~65 Stripe invoices created per month
- Princess manually creates ~65 QBO invoices (10-15 hours/month)
- ~1-3 day delay from invoice creation to QBO recording
- ~2% error rate (duplicate line items, wrong amounts)

**Proposed Solution**: Build a sync service in Xano that automatically creates QBO invoices from Stripe data.

**Expected Impact**:
- ⏱️ Reduce manual work: 10-15 hours → <1 hour/month (verification only)
- 🎯 Error reduction: 98% accuracy → 99.9%
- ⚡ Speed: 1-3 day delay → <5 minutes
- 📋 Audit trail: Complete immutable record for compliance

**Timeline**: 4-5.5 days development + 1-2 days testing = ~1 week to go-live
**Cost**: $0/month recurring (uses existing Xano infrastructure)
**Risk Level**: 🟢 LOW (tested patterns, no new infrastructure)

---

## Architecture Decision: Build in Xano

### Why Xano (vs. Zapier or Custom Cloud Run)?

| Factor | Xano | Zapier | Custom |
|--------|------|--------|--------|
| **Development Time** | 4-5.5 days | 1-2 hours | 5.5-6.5 days |
| **Monthly Cost** | $0 | $50-100 | $5-10 |
| **Audit Trail** | Excellent | Poor | Excellent |
| **Control** | Full | Limited | Full |
| **Maintenance** | Low | None | Medium |
| **Team Familiarity** | High (existing) | None | New infrastructure |

**Decision Rationale**:
1. **Integrated**: Your invoicing logic already lives in Xano
2. **Cost-effective**: $0/month vs. $50-100 for Zapier
3. **Audit trail**: Logs stored in Xano (your database), not vendor's
4. **Control**: Full visibility when Princess asks "why wasn't invoice #42 synced?"
5. **Maintainability**: Team already understands Xano; no new infrastructure to support

---

## Build Workflow: How Taz Will Implement This in Xano

### Technology Stack
```
Frontend/Orchestration: Xano Backend API Endpoint
├─ Language: XanoScript (.xs files)
├─ Execution: Xano Function
├─ Scheduling: Xano Scheduled Task
└─ Authentication: GCP Service Account (taz-assistant)

Data Access:
├─ Source: BigQuery (Stripe invoices synced by Fivetran)
├─ Query Language: SQL via BigQuery Connector
└─ Rate Limiting: Native BigQuery pagination

External APIs:
├─ Stripe API: Read invoice status & line items
├─ QBO API: Create invoices with line items
└─ GCP Secrets Manager: Retrieve API credentials

Logging & Audit:
├─ Primary: BigQuery table (stripe_qbo_sync_log)
├─ Secondary: Xano Functions execution logs
└─ Retention: 7 years (GCP native)
```

### Step-by-Step Build Workflow

#### Phase 1: Infrastructure Setup (0.5-1 day)

**1.1 Create BigQuery Tables**
```
Tools: BigQuery console
Files: N/A (DDL scripts written inline)

Tables to create:
├─ xano-fivetran-bq.subscription_tier_class_mapping
│  └─ Maps Stripe Price ID → QBO Class ID (9 tiers)
├─ xano-fivetran-bq.invoicing_links
│  └─ Tracks Stripe ↔ QBO invoice mappings
├─ xano-fivetran-bq.invoice_line_links
│  └─ Tracks Stripe ↔ QBO line item mappings (1:1)
├─ xano-fivetran-bq.stripe_qbo_sync_log
│  └─ Audit log of all sync operations
└─ xano-fivetran-bq.synced_invoices (view)
   └─ Query-friendly view for status checks
```

// (Section removed as we are not setting up Xano tables.)

**1.3 Configure GCP Secrets**
```
Tools: gcloud CLI or GCP Console
Action: Verify credentials exist for:
├─ stripe-api-key (already exists)
├─ qbo-api-client-id (already exists)
├─ qbo-api-client-secret (already exists)
└─ bigquery-access (via taz service account for ONE-TIME setup only)
   Note: After Phase 1 setup, ongoing syncs will use system SA (TBD in Phase 1)
```

#### Phase 2: Build Xano Sync Function (2-3 days)

**2.1 Create Main API Endpoint**
```
File: /xano/functions/sync_stripe_to_qbo.xs
Language: XanoScript
Type: API Endpoint

Pattern:
function "sync_stripe_to_qbo" {
  input {
    // Optional parameters for manual trigger
    int? limit_invoices = 100
    bool? force_resync = false
  }
  
  stack {
    // Phase 2.2 - Query Stripe invoices
    // Phase 2.3 - Determine invoice type
    // Phase 2.4 - Map to QBO
    // Phase 2.5 - Create/update QBO
    // Phase 2.6 - Log and link
  }
  
  response = {
    synced_count: <int>,
    error_count: <int>,
    errors: [<error objects>]
  }
}
```

**2.2 Query Stripe Invoices from BigQuery**
```
SubStep: Query & Filter
├─ Use: BigQuery Connector in Xano
├─ Query: Get unsynced invoices (check invoicing_links table)
├─ Filter Logic:
│  ├─ created >= '2025-11-01' (DATA CUTOFF: Only invoices after 11/1/2025)
│  ├─ status = 'open' OR 'paid' (sync any new activity regardless of when it happens)
│  ├─ stripe_invoice_id NOT IN (SELECT stripe_invoice_id FROM invoicing_links)
│  └─ Output: Unsynced invoices from 11/1/2025 onwards + any new activity
└─ Idempotency: Check invoicing_links table, skip if already linked

Note: Outstanding invoices before 11/1/2025 will NOT be backfilled
      However, NEW activity (payments, updates) on old invoices will sync live

XanoScript Skeleton:
  db.query BigQuery {
    table = "stripe.invoice"
    where = (created >= '2025-11-01' AND status IN ('open', 'paid') AND id NOT IN invoicing_links.stripe_invoice_id)
    return = {type: "list"}
  }
  
  // For each invoice, lookup customer
  foreach ($invoices) {
    each as $invoice {
      // Get Xano client (has QBO customer ID)
      db.query BigQuery {
        table = "staging_xano.ptl_client"
        where = (stripe_customer_id == $invoice.customer_id)
        return = {type: "single"}
      } as $xano_client
      
      // Validate QBO customer ID exists
      if ($xano_client.quickbooks_id == null) {
        // Skip - customer not mapped yet
        log_error("Customer not mapped: " + $invoice.customer_id)
        continue
      }
      
      // Get subscription for QBO Class lookup
      db.query BigQuery {
        table = "staging_xano.ptl_subscription"
        where = (id == $xano_client.subscription_id)
        return = {type: "single"}
      } as $subscription
      
      // Get QBO Class ID from mapping table
      db.query BigQuery {
        table = "subscription_tier_class_mapping"
        where = (stripe_price_id == $subscription.stripe_price_id)
        return = {type: "single"}
      } as $class_mapping
    }
  }
```

**2.3 Map Stripe to QBO Line Items (1:1 Deterministic Mapping)**
```
SubStep: Direct Line-by-Line Mapping (NO invoice type classification needed)
├─ For EACH Stripe line_item:
│  ├─ Linking Key: stripe_line_item.id (il_...) → QBO line_item (created after API call)
│  ├─ Deterministic Mapping via metadata.type:
│  │  ├─ NULL or empty (subscription) → QBO Item 45, Account 209
│  │  ├─ "Large Loss" → QBO Item 46, Account 126
│  │  ├─ "Volume" → QBO Item 48, Account 200
│  │  ├─ "Overage" → QBO Item 47, Account 221
│  │  └─ "Discount" → QBO Item 44, Account 203
│  ├─ Amount: $line.amount / 100 (Stripe cents → QBO dollars)
│  ├─ Description: $line.description (as-is from Stripe)
│  ├─ ClassRef: Customer's subscription tier ID from Xano
│  └─ Accrual Date: LAST_DAY(MONTH($invoice.period_start))
└─ Output: Array of QBO line items with stripe_line_item_id preserved

Why 1:1? Each Stripe line has unique ID (il_...) - use as linking key!
No invoice type needed - metadata.type provides deterministic mapping

XanoScript Skeleton:
  var $qbo_lines = []
  var $accrual_date = LAST_DAY(DATE($stripe_invoice.period_start))  // Last day of period month
  
  foreach ($stripe_invoice.line_items) {
    each as $line {
      // Deterministic mapping via metadata.type
      var $metadata_type { value = $line.metadata["type"] || "Subscription" }
      var $mapping {
        value = {
          "Subscription": {item: "45", account: "209"},
          "Large Loss": {item: "46", account: "126"},
          "Volume": {item: "48", account: "200"},
          "Overage": {item: "47", account: "221"},
          "Discount": {item: "44", account: "203"}
        }[$metadata_type]
      }
      
      // Create QBO line item
      $qbo_lines.push({
        stripe_line_item_id: $line.id,  // CRITICAL: Store for linking
        ItemRef: {value: $mapping.item},
        AccountRef: {value: $mapping.account},  // TEST: May not be required
        ClassRef: {value: $class_mapping.qbo_class_id},  // From mapping table
        Description: $line.description,
        Amount: $line.amount / 100,
        DetailType: "SalesItemLineDetail"
      })
    }
  }
  
  // Note: AccountRef may not be required (QBO Items have default accounts)
  // Test in Phase 5: Create invoice WITHOUT AccountRef, if successful, remove it
```

**2.4 Call QBO API to Create Invoice with Accrual Date**
```
SubStep: QBO Invoice Creation with ACCRUAL DATE LOGIC
├─ Action: POST /v2/company/{realmId}/invoice
├─ Method: api.request with OAuth2
├─ Auth: Bearer token from GCP Secrets
├─ Payload:
│  ├─ CustomerRef: Xano client ID → QBO customer lookup
│  ├─ Line items: From step 2.3 (includes ClassRef, stripe_line_item_id)
│  ├─ DocNumber: Generated "BI" + YYMMDD + sequence
│  ├─ **TxnDate (ACCRUAL DATE)**: LAST_DAY(MONTH(period_start))
│  │  └─ CRITICAL: Use period_start month's last day, NOT invoice.created
│  │  └─ Example: period_start=2025-10-01 → TxnDate=2025-10-31
│  ├─ DueDate: $accrual_date + 30 days (or Stripe due_date if exists)
│  ├─ PrivateNote: Store Stripe invoice ID + period for audit
│  └─ Output: QBO invoice ID, doc_number, line_item IDs
└─ IMPORTANT: Accrual uses PERIOD month, not invoice creation date

Accrual Date Logic:
  - Princess uses last day of month for ALL invoices
  - Stripe periods are NOT calendar months (e.g., Sep 2 - Oct 2)
  - Infer accrual month from period_start
  - Use LAST_DAY of that month as TxnDate

Edge Cases for Logan to Confirm:
  1. Mid-month start (Oct 15-Nov 15) → Use Oct 31? ✓
  2. Period spans two months (Oct 20-Nov 20) → Use Oct 31? ✓
  3. One-day period (Oct 7-Oct 7) → Use Oct 31? ✓

XanoScript Skeleton:
  // Calculate accrual date
  var $period_start_month = MONTH(DATE($stripe_invoice.period_start))
  var $period_start_year = YEAR(DATE($stripe_invoice.period_start))
  var $accrual_date = LAST_DAY(DATE($period_start_year + "-" + $period_start_month + "-01"))
  
  // Generate doc_number
  var $doc_date = FORMAT($accrual_date, "YYMMDD")  // e.g., "251031"
  var $sequence = GET_NEXT_SEQUENCE($doc_date)     // e.g., 001
  var $doc_number = "BI" + $doc_date + $sequence   // e.g., "BI251031001"
  
  api.request {
    url = "https://quickbooks.api.intuit.com/v2/company/{realmId}/invoice"
    method = "POST"
    headers = ["Authorization: Bearer <token>"]
    body = {
      CustomerRef: {value: $xano_client.quickbooks_id},  // From Xano ptl_client table
      Line: $qbo_lines,  // From step 2.3
      DocNumber: $doc_number,
      TxnDate: FORMAT($accrual_date, "YYYY-MM-DD"),  // ACCRUAL DATE, not today!
      DueDate: FORMAT(ADD_DAYS($accrual_date, 30), "YYYY-MM-DD"),
      PrivateNote: "Stripe: " + $stripe_invoice.id + " | Period: " + $stripe_invoice.period_start + "-" + $stripe_invoice.period_end
    }
  } as $qbo_response
  
  // Note: xano_client.quickbooks_id must be populated (by Princess)
  // If NULL, invoice is skipped and logged as "customer_not_mapped"
```

**2.5 Create Linking Records (Invoice + Line Item Level)**
```
SubStep: Two-Level Linking (Invoice + Line Items)
├─ Insert into invoicing_links (invoice level):
│  ├─ stripe_invoice_id: From Stripe
│  ├─ qbo_invoice_id: From QBO response
│  ├─ qbo_doc_number: From QBO response
│  ├─ accrual_date: Calculated accrual date
│  ├─ synced_at: Now
│  └─ status: 'linked'
│
├─ Insert into invoice_line_links (line item level - NEW):
│  ├─ stripe_line_item_id: From Stripe (il_...)
│  ├─ qbo_line_item_id: From QBO response (line.Id)
│  ├─ stripe_invoice_id: Parent invoice ID
│  ├─ qbo_invoice_id: Parent invoice ID
│  ├─ metadata_type: "Subscription", "Large Loss", etc.
│  ├─ amount: Line amount
│  └─ synced_at: Now
│
└─ Insert into sync_log:
   ├─ stripe_invoice_id, qbo_doc_number, status: 'success'
   ├─ line_count: Number of lines synced
   └─ timestamp, error_message (if any)

Why Line-Level Links?
- Deterministic mapping: stripe_line_item.id → qbo_line_item.id
- Audit trail: Trace exact line from Stripe to QBO
- Reconciliation: Line-level matching for detailed reporting

XanoScript Skeleton:
  // Invoice-level link
  db.add_to_bq("invoicing_links", {
    stripe_invoice_id: $stripe_invoice.id,
    qbo_invoice_id: $qbo_response.Invoice.Id,
    qbo_doc_number: $qbo_response.Invoice.DocNumber,
    accrual_date: $accrual_date,
    synced_at: now(),
    status: 'linked'
  })
  
  // Line-item level links
  foreach ($qbo_response.Invoice.Line) {
    each as $qbo_line {
      // Find matching Stripe line by stripe_line_item_id stored in $qbo_lines
      var $stripe_line_id = $qbo_lines[$index].stripe_line_item_id
      
      db.add_to_bq("invoice_line_links", {
        stripe_line_item_id: $stripe_line_id,
        qbo_line_item_id: $qbo_line.Id,
        stripe_invoice_id: $stripe_invoice.id,
        qbo_invoice_id: $qbo_response.Invoice.Id,
        metadata_type: $qbo_lines[$index].metadata_type,
        amount: $qbo_line.Amount,
        synced_at: now()
      })
    }
  }
```

#### Phase 3: Implement Scheduled Task (0.5 day)

**3.1 Create Xano Scheduled Task**
```
Tool: Xano UI → Scheduled Tasks
├─ Frequency: Hourly (every hour at :00)
├─ Action: Call /sync_stripe_to_qbo endpoint
├─ On Success: Log count of synced invoices
├─ On Failure: Send alert email to development team
└─ Retry: Up to 3 retries on failure

Configuration:
  Name: "Sync Stripe Invoices to QBO"
  Schedule: "0 * * * *" (every hour)
  Call: POST /sync_stripe_to_qbo
  Timeout: 5 minutes
  Alert on failure: true
```

#### Phase 4: Error Handling & Retry Logic (0.5 day)

**4.1 Implement Try-Catch Blocks**
```
XanoScript Pattern:
  try_catch {
    // Main sync logic from phases 2.1-2.6
    
    catch {
      // Log error to both Xano and BigQuery
      db.add stripe_qbo_sync_log {
        data = {
          status: 'error',
          error_message: $error.message,
          error_code: $error.code,
          stripe_invoice_id: $invoice.id,
          retry_count: $retry_count
        }
      }
      
      // Send alert
      email.send {
        to: "dev-team@wescope.com"
        subject: "Stripe→QBO Sync Error"
        body: $error.message
      }
      
      // Retry logic
      if ($retry_count < 3) {
        // Schedule manual retry
      }
    }
  }
```

**4.2 Idempotency Checks**
```
XanoScript Pattern:
  // Before creating QBO invoice, check if already linked
  db.query invoicing_links {
    where = $db.invoicing_links.stripe_invoice_id == $invoice.id
    return = {type: "single"}
  } as $existing_link
  
  conditional {
    if ($existing_link != null) {
      // Already synced, skip
      continue
    }
    else {
      // Proceed with sync (phases 2.4-2.6)
    }
  }
```

#### Phase 5: Testing (1 day)

**5.1 Unit Tests**
```
Test Framework: Xano built-in testing
├─ Test invoice type classification
├─ Test line item mapping logic
├─ Test doc_number generation
└─ Test idempotency check

Example Test:
  test "classify_variable_cost_invoice" {
    input = {
      invoice: {
        description: "This invoice will automatically charge... separate from your subscription"
      }
    }
    expect invoice_type = "variable_costs"
  }
```

**5.2 Integration Tests**
```
Test Environment: Staging Stripe + QBO
├─ Create test subscription invoice → verify QBO creation
├─ Create test variable invoice → verify multi-line QBO creation
├─ Verify linking table entries
├─ Verify idempotency (run twice, expect no duplicates)
└─ Verify sync logs created

Process:
  1. Create test invoice in Stripe staging
  2. Manually trigger /sync_stripe_to_qbo
  3. Verify QBO invoice created with correct lines
  4. Verify invoicing_links table has entry
  5. Run sync again, verify no duplicate
```

**5.3 Edge Case Testing**
```
Test Scenarios:
├─ Large invoice ($100k+) → verify amounts correct
├─ Invoice with no variable costs → verify only subscription line
├─ Invoice with all cost types (Overage+Volume+Large Loss) → verify all lines
├─ Failed QBO API call → verify error logged and retry queued
└─ Duplicate sync attempt → verify idempotency prevents duplicate
```

---

## System Architecture

### Core Principle: One-Way Data Flow
```
Xano (Calculations)
    ↓
Stripe (Invoices & Payments) ← System of Record for financial state
    ↓
BigQuery (Data Warehouse) ← Fivetran syncs automatically
    ↓
Xano Sync Service (Stateless Container - Pure Orchestration)
    ↓
QBO (AR Tracking & GL Posting) ← Aggregator only
```

**Critical Constraint**: 
- Never pull data back from QBO or Stripe into Xano
- Never write invoice data to both Xano and Stripe
- Xano remains SoR for usage/subscriptions, Stripe for invoices/payments

### Data Flow: When Sync Runs

```
1. Query BigQuery
   SELECT stripe.invoice WHERE status='open' AND not synced
   (Why BQ? Cost, batch efficiency, Fivetran handles ingestion)

2. For each invoice:
   ├─ Generate QBO doc_number: "BI" + YYMMDD + sequence
   ├─ Create QBO invoice via API (get back qbo_invoice_id)
   └─ INSERT into invoicing_links table:
      (stripe_id, qbo_id, doc_number, xano_client_id, synced_at)

3. Log to Xano database:
   [timestamp, stripe_id, qbo_id, status, error_msg]
   (Why Xano? Princess can query via dashboard)

4. Return success/failure count
```

---

## Technical Specifications

### A) Data Sources (Read-Only)

| Source | Table | Fields Used | Purpose |
|--------|-------|----------|---------|
| **BigQuery (Stripe)** | stripe.invoice | id, customer_id, total, status, created, due_date, description, metadata | Read pending invoices |
| **Xano Database** | Client | id, Stripe_Customer_ID | Customer lookup |
| **QBO API** | invoice | (returned) qbo_invoice_id, doc_number | Create and receive ID |

### B) Linking Table (Authoritative)

**Location**: BigQuery (synced from Xano by Fivetran)

```sql
CREATE TABLE invoicing_links (
  link_id STRING PRIMARY KEY,
  stripe_invoice_id STRING NOT NULL UNIQUE,     -- in_1SKOO9...
  stripe_invoice_number STRING,                 -- 391BEB0D-0 (ref)
  qbo_invoice_id STRING NOT NULL UNIQUE,        -- 42 (API key)
  qbo_doc_number STRING NOT NULL,               -- BI251101001 (human ref)
  xano_client_id INTEGER NOT NULL,              -- For audit
  stripe_total_cents INTEGER NOT NULL,
  qbo_total_dollars NUMERIC NOT NULL,
  synced_at TIMESTAMP NOT NULL,
  created_by STRING,                            -- "system"
  status STRING                                 -- 'linked', 'disputed', 'voided'
);

-- Indexes
CREATE INDEX idx_stripe_id ON invoicing_links(stripe_invoice_id);
CREATE INDEX idx_qbo_id ON invoicing_links(qbo_invoice_id);
```

**Why BigQuery?**
- Already where Stripe data lives (Fivetran synced)
- Same location for reconciliation queries
- Xano table will be mirrored to BQ anyway, so no extra cost

### C) Error Logging

**Location**: BigQuery (single source of truth)

```sql
CREATE TABLE xano-fivetran-bq.stripe_qbo_sync_log (
  id STRING PRIMARY KEY,
  sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  stripe_invoice_id STRING,
  qbo_invoice_id STRING,
  qbo_doc_number STRING,
  xano_client_id INTEGER,
  stripe_total_cents INTEGER,
  qbo_total_dollars NUMERIC,
  status ENUM('success', 'error', 'duplicate', 'validation_failed'),
  error_message TEXT,
  error_code STRING,
  retry_count INT DEFAULT 0
);
```

**Why BigQuery (not Xano)?**
- ✅ Single source of truth (all invoice data already there)
- ✅ Immediate availability (no sync delay)
- ✅ Available in Metabase for Princess's dashboard access
- ✅ Same location as reconciliation queries
- ✅ No data duplication
- ✅ Cost-effective (no extra Xano storage)

**Access**:
- Developers/Frankie: Query BigQuery directly
- Princess: Access via Metabase dashboard (pre-built view)
- Fivetran: Logs all data lineage automatically

---

## Linking Strategy & QBO Keys

### Three Decisions Finalized ✅

**1. Dual-Key Linking Table** (Instead of metadata-based or implicit joins)
- **Explicit relationship** with audit trail
- **Bidirectional lookups**: Find QBO from Stripe or vice versa
- **Reconciliation queries**: Identify unlinked invoices
- **Immutable** 7-year compliance record
- **Industry standard** for cross-system linking

**2. QBO `id` as API Key** (Not `doc_number`)
- `id` = QBO's internal database primary key (immutable, unique)
- `doc_number` = Human-readable invoice number (what Princess sees)
- Use `id` for all API operations (create, update, query)
- Store `doc_number` in linking table for human reference

**3. Xano Generates `doc_number`** (Keep Princess's format)
- Format: "BI" + YYMMDD + sequence
  - Example: BI251101001 (November 1, 2025, invoice #1)
- Algorithm: Query invoicing_links WHERE doc_number LIKE 'BI251101%', count+1
- Pass as parameter to QBO API when creating invoice
- QBO validates uniqueness (enforces no duplicates)

---

## Business Rules & Edge Cases

### Invoice Lifecycle (5 Stages)

**Stage 1: Calculation (Xano)**
- **Multiple Xano functions run** (not just one):
  - `Invoice — Subscription from Subscription (All Cases) (Old Pricing)`
  - `Invoice — Subscription from Subscription (All Cases) (New Pricing)`
  - `Calculate Delivered Volume`
  - Other variants for different pricing tiers
- These functions create Stripe line_items with metadata[charge_type] populated
- Determines subscription fee + overages + large losses + volume fees
- Stores metadata on each line_item for categorization

**Stage 2: Creation (Stripe)**
- Xano calls Stripe API → creates invoice
- Stripe enters state: draft → open → paid/unpaid
- **Stripe is now SoR** (immutable except by manual corrections)

**Stage 3: Sync to QBO (Automated)**
- This sync service reads Stripe invoices (created >= 2025-11-01)
- Determines invoice type (subscription vs variable_costs) from line_items
- Creates QBO invoice with:
  - **TxnDate**: Stripe invoice.created date (NOT today)
  - **Accrual Period**: Stored in memo or custom field (period_start to period_end)
  - Matching amount, line items, dates from Stripe
- **Linking table records the match**
  - Tracks which Stripe invoices have been synced
  - Prevents duplicate syncs

**Stage 4: Payment (Stripe + Portal)**
- Customer pays → Stripe charge created
- Portal streams payment status back to Xano (read-only)
- Payment exported as CSV for manual import to QBO (for now)

**Stage 5: QBO Recording**
- QBO reflects invoice status and payment
- AR aging reports accurate
- GL posting to accounts 209 (AR) and 294 (Cash)

### Edge Cases Handled

| Scenario | Handling |
|----------|----------|
| **Duplicate sync** | Check invoicing_links for existing stripe_id (idempotency) |
| **Failed QBO creation** | Log error, Princess reviews, manual retry via Xano dashboard |
| **QBO API rate limit** | Exponential backoff, stagger requests |
| **Customer lookup fails** | Validation rule pre-sync, pause sync, alert Princess |
| **Amount rounding** | Always round to $0.01, validate post-conversion |
| **Invoice already in QBO** | Linking table checked first, skip if linked |

---

## Data Validation Rules

### Pre-Sync Validation (Before calling QBO API)
1. ✅ Client is active (Not_Allowed ≠ true, Suspended ≠ true)
2. ✅ Subscription is active
3. ✅ Client has Stripe_Customer_ID
4. ✅ Billing period dates valid (start < end)
5. ✅ Calculated volume > 0 (don't create $0 invoices)
6. ✅ Client has valid email

### Post-Sync Validation (After QBO invoice created)
1. ✅ Stripe invoice ID matches pattern (in_*)
2. ✅ Stripe status is open/paid/unpaid (not draft)
3. ✅ Stripe amount_due > 0
4. ✅ Customer IDs match between Stripe and QBO
5. ✅ Amount matches within $0.01 (cents → dollars conversion)
6. ✅ QBO doc_number is unique
7. ✅ Linking table entry created successfully

### Reconciliation Queries (Monthly)

```sql
-- Unlinked Stripe invoices
SELECT s.id FROM stripe.invoice s
WHERE s.id NOT IN (SELECT stripe_invoice_id FROM invoicing_links)
  AND s.status IN ('open', 'paid')
  AND EXTRACT(MONTH FROM s.created) = CURRENT_MONTH();

-- Unlinked QBO invoices
SELECT q.id, q.doc_number FROM qbo.invoice q
WHERE q.id NOT IN (SELECT qbo_invoice_id FROM invoicing_links)
  AND EXTRACT(MONTH FROM q.transaction_date) = CURRENT_MONTH();

-- Amount discrepancies
SELECT l.*, s.total/100.0, q.total_amount
FROM invoicing_links l
JOIN stripe.invoice s ON l.stripe_invoice_id = s.id
JOIN qbo.invoice q ON l.qbo_invoice_id = q.id
WHERE ABS((s.total/100.0) - q.total_amount) > 0.01;
```

---

## Acceptance Criteria (Testing)

### Functional Tests
- [ ] **New Invoice Sync**: Stripe invoice → QBO created with matching amount, date, customer
- [ ] **Paid Status Update**: Stripe invoice paid → QBO status updated
- [ ] **Credit Memo**: Stripe credit → QBO credit memo created
- [ ] **Idempotency**: Sync runs twice → no duplicate QBO invoices
- [ ] **Customer Lookup**: Stripe invoice → correct QBO customer matched
- [ ] **Reconciliation**: 100 synced invoices → 100 linked entries found

### Edge Case Tests
- [ ] **Partial Payment**: Customer pays 50% → QBO shows remaining balance
- [ ] **Failed Payment Retry**: Payment fails → succeeds → QBO reflects final paid status
- [ ] **Dispute Handling**: Chargeback filed → QBO invoice flagged
- [ ] **Large Amount**: $1M invoice → no rounding errors, precision to $0.01

---

## Future Extensibility

**Same pattern supports**:
- ✅ **Payments**: Stripe charge → QBO payment (read Stripe charges, create QBO payments)
- ✅ **Credits/Refunds**: Stripe credit note → QBO credit memo (same linking logic)
- ✅ **Disputes**: Stripe chargeback → QBO notes (flag and manual review)
- ✅ **Payout reconciliation**: Stripe payout → chase account (validate cash dates)

All use BigQuery as data source, invoicing_links table for mapping.

---

## Security & Compliance

### Credentials Management
- ✅ Stripe API key: GCP Secrets Manager (ONE-TIME setup by taz)
- ✅ QBO credentials: GCP Secrets Manager (ONE-TIME setup by taz)
- ✅ **System SA for Ongoing**: NEW SA to be created in Phase 1 (TBD)
  - NOT taz's SA (dedicated to this sync only)
  - Minimal permissions (read Stripe BQ, write invoicing_links, write sync_log)
  - Can be rotated independently
- ✅ No keys in code, logs, or temporary files

### Audit Trail
- ✅ All syncs logged to Xano database (who/what/when/status)
- ✅ Linking table immutable (no updates, only inserts)
- ✅ Historical retention: 7 years (for compliance)
- ✅ BigQuery logs all table changes (Fivetran audit)

### Data Privacy
- ✅ No PII in logs (only IDs, amounts, timestamps)
- ✅ No invoice content in sync logs
- ✅ Restricted access: Only Xano functions and Fivetran can write

---

## Success Metrics

Once live, we measure:

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Manual QBO entry time | 10-15 hrs/month | <1 hr/month | Month 1 |
| Invoice creation latency | 1-3 days | <5 minutes | Week 1 |
| Data accuracy | ~98% | 99.9% | Month 1 |
| Duplicate invoices | 0 (manual) | 0 (auto) | Ongoing |
| Monthly discrepancies | 1-2 | 0 | Month 2 |
| System availability | N/A | >99% | Ongoing |

---

## Implementation Roadmap

### Phase 1: Setup & Preparation (1 day)
- [ ] Logan approves proposal
- [ ] Create `invoicing_links` table in BigQuery
- [ ] Create `stripe_qbo_sync_log` table in Xano
- [ ] Set up QBO OAuth2 credentials (taz_qbo)
- [ ] Create test invoices in staging for validation

### Phase 2: Development (2-3 days)
- [ ] Build Xano API endpoint: `/api/sync-stripe-to-qbo`
- [ ] Implement BigQuery polling logic
- [ ] Implement QBO API integration
- [ ] Add doc_number generation (BI + date + sequence)
- [ ] Implement idempotency checks (linking table lookup)
- [ ] Add error handling and logging

### Phase 3: Testing (1 day)
- [ ] Unit tests: doc_number generation, amount conversion, duplicate detection
- [ ] Integration tests: Stripe → BQ → Xano → QBO
- [ ] Edge case tests (6 scenarios from acceptance criteria)
- [ ] Reconciliation query validation

### Phase 4: Deployment (0.5 day)
- [ ] **START DATE: 2025-11-01**
  - Sync only invoices created on or after 11/1/2025
  - NO historical backfill (Sept-Oct data will be manual)
  - First new invoices after 11/1/2025 will be first sync test
- [ ] Go-live checklist
- [ ] Princess validates workflow
- [ ] Create monitoring dashboard

### Phase 5: Ongoing (Continuous)
- [ ] Daily sync verification
- [ ] Weekly reconciliation report
- [ ] Monthly audit of linking data

**Total Timeline**: 4.5-5.5 days development + testing before go-live

---

## Risks & Mitigations

| Risk | Scenario | Mitigation | Severity |
|------|----------|-----------|----------|
| **Duplicate invoices** | Sync crashes after QBO creation but before linking table insert | Idempotency check: query invoicing_links before creating | 🟢 LOW |
| **Failed QBO creation** | QBO API times out or rate limits | Exponential backoff, stagger requests, error log for manual retry | 🟢 LOW |
| **Customer lookup fails** | Xano client doesn't map to QBO customer | Validation rule pre-sync, pause sync, alert Princess | 🟡 MEDIUM |
| **Amount rounding errors** | Stripe cents → QBO dollars creates discrepancy | Always round to $0.01, validate post-conversion | 🟢 LOW |
| **Metadata overwrite** | Stripe metadata updated incorrectly | Don't store links in metadata; use linking table instead | ✅ AVOIDED |

---

## Questions for Princess

1. **Invoice Number Format**:
   - Keep current: `BI251031001` (BI + YYMMDD + sequence) ← RECOMMENDED
   - OR switch to: Stripe invoice.id (`in_1SDZnp...`) for direct mapping?
   - OR switch to: Stripe invoice.number (`391BEB0D-0`)?
   
   **Recommendation**: Keep BI format, store Stripe ID in `private_note` field
   
2. **Customer Mapping** (Action Required - 89% Pre-Completed!):
   
   **GOOD NEWS**: 76% of mapping already done!
   - Xano `ptl_client.quickbooks_id` field already exists ✓
   - **309 out of 407 customers already have QBO ID populated** ✓
   - These were manually entered over time (likely by Princess)
   
   **Princess's Remaining Task**:
   - ✓ Verify 309 existing mappings (spot-check, likely correct)
   - ✓ Confirm 55 AI suggestions (13% - high confidence matches)
   - ✓ Manually match 43 customers (11% - need review)
   
   **Effort**: ~1-2 hours (not 8-10 hours!)
   
   **File**: `PRINCESS_CUSTOMER_MAPPING.csv` (407 rows, 89% pre-completed)

---

## Questions for Logan

Before we proceed with implementation, please confirm:

1. ✅ **XanoScript Approach**: Using XanoScript (.xs files) for main sync function is acceptable?
2. ✅ **Scheduled Task**: Hourly sync via Xano's scheduled task feature is acceptable?
3. ✅ **Error Handling**: 3-retry policy with email alerts to dev team on failure acceptable?
4. ✅ **Logging**: BigQuery table for audit trail accessible via Metabase acceptable?
5. ✅ **Timeline**: 4.5-5.5 days for full implementation acceptable given complexity?
6. ⚠️ **AccountRef Testing**: Should we test QBO API without AccountRef? (Items have default accounts)
7. ⚠️ **Accrual Edge Cases**: Confirm using last day of period_start month for all invoices?
8. ⚠️ **Doc Number Format**: Approve keeping Princess's BI format vs switching to Stripe IDs?

---

## Implementation Phases: Timeline & Deliverables

| Phase | Duration | Deliverables | Notes |
|-------|----------|--------------|-------|
| **1: Infrastructure** | 0.5-1 day | BigQuery tables, Xano tables, GCP secrets verified | DDL scripts, no app logic |
| **2: Sync Function** | 2-3 days | Main XanoScript function with all 6 steps | 80% of work; most complex phase |
| **3: Scheduled Task** | 0.5 day | Hourly scheduler, alerts, monitoring | Uses function from Phase 2 |
| **4: Error Handling** | 0.5 day | Try-catch, retry logic, email alerts | Production-ready robustness |
| **5: Testing** | 1 day | Unit tests, integration tests, edge cases | Validation before production |
| **Total** | **4.5-5.5 days** | **Fully tested, production-ready sync** | Timeline remains intact |

---

## Sign-Off: Ready for Logan's Decision

**All architectural decisions finalized by Frankie + Taz.**

### Approved Decisions
- ✅ Architecture: One-way flow (Xano → Stripe → QBO)
- ✅ Build Tool: Xano (vs. Zapier or Custom Cloud Run)
- ✅ Language: XanoScript (.xs files) for sync logic
- ✅ Data Source: BigQuery (not direct Stripe API)
- ✅ Linking: Dual-key linking table for both invoice types
- ✅ Error Logging: BigQuery table, accessible via Metabase
- ✅ Scheduling: Hourly automated sync
- ✅ Cost: $0/month recurring

### Logan's Decision Required

Please confirm or reject:

- [ ] **Do you agree with the implementation approach?**
  - XanoScript development in Xano
  - Phases 1-5 as outlined
  - 4.5-5.5 day timeline

- [ ] **Proceed with implementation?**
  - Yes: Taz will begin Phase 1 immediately
  - No: Provide feedback for revision
  - Ask Questions: List specific concerns below

**If you have concerns or questions about the build workflow, please list them here:**
```
[Your feedback here]
```

---

## Attachments & Supporting Documents

1. **Source of Truth (SoT)**: `/docs/sot-stripe-qbo-sync.md` (30KB)
   - Full business rules, technical specs, acceptance criteria
   - Detailed invoice lifecycle and edge cases

2. **Complete Field Mapping**: `/specs/FINAL_SYSTEM_MAPPING.md` (16KB)
   - Xano ↔ Stripe ↔ QBO field-by-field mappings
   - All 3 BigQuery linking tables defined
   - Step-by-step sync logic

3. **System Catalogs** (Data Analysis):
   - `/specs/xano-catalog-active-fields.md` - Xano schema (from XanoScript)
   - `/specs/stripe-catalog-active-fields.md` - Stripe fields (from BigQuery)
   - `/specs/qbo-catalog-active-fields.md` - QBO fields (from BigQuery)

4. **Action Items for Princess**:
   - `/specs/PRINCESS_CUSTOMER_MAPPING.csv` - 407 customers (364 AI pre-matched)
   - `/specs/FINAL_XANO_TO_QBO_CLASS_MAPPING.csv` - 9 subscription tiers

---

**Ready for Logan's review and approval.** 🎯

Once approved, we can start Phase 1 immediately.
