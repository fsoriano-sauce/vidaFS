# WeScope Stripe → QuickBooks Online Sync: Source of Truth

**Status**: FINALIZED FOR IMPLEMENTATION SCOPING
**Last Updated**: November 1, 2025
**Purpose**: Single source of truth for the Stripe invoice-to-QBO sync system, defining business rules, scope, architecture, and acceptance criteria.

---

## 1. Executive Summary

WeScope invoices customers through Stripe based on subscription tiers and usage metrics calculated in Xano. Current state: invoices are created in Stripe and payments tracked through Portal; QBO records are manually created by the AR/AP specialist. **Objective**: Automate the QBO sync while maintaining clear system-of-record boundaries and data integrity.

### Critical Architecture Principle
**Data flows one direction: Xano → Stripe → QBO**
- **Xano** = System of Record for: Usage, Subscriptions, Calculations
- **Stripe** = System of Record for: Invoices, Payments, Financial State
- **QBO** = Aggregator Only: Records Stripe data for AR tracking and GL posting
- **No reverse flows**: Never pull invoice/payment data back from QBO or Stripe into Xano
- **No dual writes**: Never create invoice data in both Xano and Stripe separately

---

## 2. Scope Definition

### In Scope
1. **Automatic QBO Invoice Creation** from Stripe invoices
   - Trigger: Stripe invoice enters "finalized" state
   - Action: Create QBO invoice with matching amount, dates, and line items
   - Linking: Bidirectional reference between Stripe and QBO records

2. **Invoice Status Sync** (read-only)
   - Track when Stripe invoices are paid/unpaid/overdue
   - Reflect payment status in QBO

3. **Credit/Refund Recording** (read-only from Stripe)
   - When Princess manually issues credits/refunds in Stripe → auto-create matching QBO credit memo
   - Maintain audit trail

4. **Payment Data Sync** (read-only from Stripe)
   - Capture when payments are received
   - For now: Export data for manual QBO import (until direct bank feed available)
   - Future: Automate payment posting when bank feed confirms

5. **Dispute Handling**
   - Track disputed charges in Stripe → flag in QBO
   - Resolution flow: Update Stripe first, then sync to QBO

### Out of Scope
- **Xano → QBO direct**: Never write invoice data directly from Xano to QBO
- **Xano invoice storage**: Xano does not store Stripe invoice IDs in its database
- **Stripe customer sync**: Customer management remains in Xano; Stripe IDs are foreign keys only
- **Multi-currency**: USD only for this integration
- **Stripe Connect**: No sub-account processing
- **Tax calculations**: Taxes are $0 in current model; if added, implement at Stripe level only
- **Discounts programmatic**: Discounts issued manually in Stripe; not auto-generated
- **Manual corrections in QBO**: Corrections flow Xano → Stripe → QBO, not the reverse

---

## 3. System Architecture

### 3.1 Data Flow Diagram

```
┌─────────┐  Calculations   ┌──────────┐  Creates Invoice  ┌────────┐  Streams Status  ┌────────┐
│  Xano   │ ────────────→   │ Stripe   │ ─────────────────→ │ Portal │ ─────────────→  │ Xano   │
│ (SoR)   │                 │ (SoR)    │                    │ (UI)   │                  │ Portal │
└─────────┘                 └──────────┘                    └────────┘                  └────────┘
    ↓                            ↓
    │                            │ Fivetran Sync
    │                            ↓
    │                       ┌─────────────────┐
    │                       │ BigQuery Stripe │
    │                       └─────────────────┘
    │                            ↓
    │                     Auto-create invoice
    │                            ↓
    │                       ┌──────────┐
    └──────────────────────→│   QBO    │
                            │(Aggregator)
                            └──────────┘
                                 ↓
                           GL Posting
                           AR Tracking
                           Financial Reports
```

### 3.2 System Roles

| System | Role | Owns | Doesn't Own |
|--------|------|------|------------|
| **Xano** | SoR for Usage & Subscriptions | Client data, usage calculations, subscription tiers | Invoice creation, payment processing |
| **Stripe** | SoR for Invoices & Payments | Invoice state, line items, charges, refunds | Usage metrics, subscription rules |
| **QBO** | Aggregator for AR | Invoice records from Stripe, GL posting | Invoice business logic, payment decisions |
| **Portal** | Streaming UI | Customer-facing invoice links, payment status display | Data persistence (UI layer) |
| **BigQuery** | Data Warehouse | Historical data, data lineage, analytics | Real-time transaction processing |

---

## 4. Business Rules

### 4.1 Invoice Lifecycle

#### Stage 1: Calculation (Xano)
1. **Multiple Xano functions run** (not just one):
   - `Invoice — Subscription from Subscription (All Cases) (Old Pricing)` - Legacy pricing model
   - `Invoice — Subscription from Subscription (All Cases) (New Pricing)` - Current model (calls legacy `Calculate Delivered Volume`)
   - `Calculate Delivered Volume` - Calculates billable usage volumes
   - Other variants for different pricing tiers/scenarios
   
   **Key Finding**: Despite the "(New Pricing)" function name, it still calls the legacy `Calculate Delivered Volume` function, indicating potential incomplete migration.

2. Reads client subscription, usage submits, and pricing tier

3. Calculates billable volume using `Calculate Delivered Volume` function
   - **QA/Change Order QA** submissions: Base subscription volume
   - **Supplemental submissions**: Additional volume with multipliers (0.0125 for normal, 0.005 for large loss)
   - **Revisions**: Adjustments at base rates

4. Creates invoice items in Stripe - **CRITICAL: TWO SEPARATE INVOICES PER MONTH**

   **INVOICE #1: Subscription (Auto-billed subscription)**
   - Single line item: Base monthly subscription fee (e.g., $3,000)
   - Part of Stripe's recurring subscription system
   - Description: e.g., "1 × Subscription Estimating (at $3,000.00 / month)"
   
   **INVOICE #2: Variable Costs** (Only if any variable costs exist)
   - Description: "This invoice will automatically charge to your payment method on file on [DATE] and is separate from your subscription. This covers ancillary items..."
   - Contains MULTIPLE line items created via separate API calls:
     - **Overage line item**: IF usage exceeds tier threshold
     - **Volume fee line item**: For Tier 4 customers (subscription ID = 5)
     - **Large loss line items**: Multiple items IF invoiceable_value ≥ $50,000 per job (can have 0 to many)

#### Stage 2: Creation (Stripe)
1. **INVOICE #1 (Subscription)**:
   - Auto-created by Stripe recurring subscription system
   - Single line item: Subscription amount
   - Enters state: **draft** → **open** → **paid/uncollectible**

2. **INVOICE #2 (Variable Costs)** (if applicable):
   - Manually created by Xano function via API calls
   - Multiple line items added (Overage, Volume, Large Loss)
   - Final invoice created via `POST /invoices` API call
   - Enters state: **draft** → **open** → **paid/uncollectible**

3. **Stripe is now SoR** (immutable except by Princess for manual corrections)

#### Stage 3: Sync to QBO
**CRITICAL ARCHITECTURE CHANGE**: This is where Stripe's multi-invoice model maps to QBO's multi-line model.

1. Fivetran continuously syncs both Stripe invoices to BigQuery

2. QBO sync service (Xano, Zapier, or custom) reads Stripe invoices:
   - If status == "open" and NOT previously synced → **Create in QBO**
   - If status changed (paid/unpaid) → **Update QBO**

3. **QBO invoices created with line items (1:1 from Stripe)**:
   
   **For EACH Stripe line_item, create ONE QBO line_item**:
   - Stripe metadata.type → QBO Item/Account mapping:
     - NULL or empty (subscription) → Item 45, Account 209
     - "Large Loss" → Item 46, Account 126
     - "Volume" → Item 48, Account 200
     - "Overage" → Item 47, Account 221
     - "Discount" → Item 44, Account 203
   - Description: Copy from Stripe line.description
   - Amount: Stripe line.amount / 100 (cents → dollars)
   - ClassRef: Customer's subscription tier ID (from Xano)
   - Subtotal: Auto-generated by QBO
   
   **Example**:
   Stripe Invoice with 2 line items:
   - Line 1: Subscription, $1,500, metadata.type = NULL
   - Line 2: Volume Fee, $1,732.53, metadata.type = "Volume"
   
   QBO Invoice with 2 line items:
   - Line 1: Item 45, Account 209, ClassRef 568238, $1,500, "Subscription for September 2025"
   - Line 2: Item 48, Account 200, ClassRef 568238, $1,732.53, "Volume Fee ($139,535 in Total Volume)"

4. **Store linking metadata**: 
   - Link INVOICE #1 (Stripe subscription) → QBO subscription invoice
   - Link INVOICE #2 (Stripe variable) → QBO variable costs invoice
   - Each link: `{stripe_invoice_id: "in_...", qbo_doc_number: "BI...", invoice_type: "subscription|variable"}`

#### Stage 4: Payment (Stripe + Portal)
1. **INVOICE #1**: Auto-billed via Stripe subscription (typically succeeds immediately)
2. **INVOICE #2**: Customer receives "send_invoice" request, pays manually
3. Portal streams payment status back to Xano (read-only)
4. Payment data exported from Stripe → CSV → Manual import to QBO (until automated)

#### Stage 5: QBO Recording
1. QBO reflects both invoices and their respective line items
2. AR aging reports accurate (subscription + variable costs tracked separately)
3. GL: Line items post to their respective accounts (209 for subscription, 126/200/221 for variable)
4. Clean financial separation between recurring and ancillary charges

### 4.2 Correction & Refund Flow

**Policy**: Immutable invoices in Stripe; corrections via credits/refunds.

**If invoice error discovered BEFORE payment**:
1. Princess voids/cancels Stripe invoice (if policy allows)
2. OR: Issues credit memo in Stripe for the difference
3. QBO sync reflects credit memo
4. Clean audit trail

**If invoice error discovered AFTER payment**:
1. Princess issues credit/refund in Stripe
2. Stripe refund processed (charge reversed)
3. QBO sync creates credit memo matching Stripe credit
4. Customer receives refund or credit toward future invoices

**Xano does NOT receive updated invoice data**: Xano stores only the calculation; Stripe is SoR for actual invoice state.

### 4.3 Usage & Volume Calculation Rules

**Data Sources** (all from Xano database):
- `Submit` table: Filtered by type ("QA", "Change Order QA", "Supplemental", "Revision")
- `Job` table: Canceled status filtering
- `Project` table: Address/metadata

**Calculation Logic**:
1. **QA/Change Order QA Submits**:
   - If Invoiceable_Value < $50,000 → Subscription volume
   - If Invoiceable_Value ≥ $50,000 → Large loss volume (separate treatment)

2. **Supplemental Submits** (Revised in New Pricing model):
   - Determine if related job has QA with Invoiceable_Value ≥ $50,000
   - If YES (Large Loss job) → Supplement @ 0.5% (0.005)
   - If NO (Normal job) → Supplement @ 1.25% (0.0125)

3. **Revision Submits** (New Pricing model):
   - Same logic as supplementals

4. **Overage Threshold**:
   - If total volume > subscription tier threshold → Overage fee
   - Overage amount = (volume - threshold) × Overage_in_percentage
   - Trigger email notification offering tier upgrade

### 4.4 Customer Data Sync

**Policy**: Xano is SoR for customers.

1. New customer created in Xano (full record: name, email, location, etc.)
2. When subscription activated → Create Stripe customer
   - Stripe customer ID stored in `Client.Stripe_Customer_ID`
   - Include Xano client ID in Stripe customer `metadata`
3. QBO customer lookup:
   - Use Xano client ID from Stripe metadata to find QBO customer by name/reference
   - OR: Store QBO customer ID in Xano client record for direct lookup
4. **No reverse sync**: Never update Xano customer data from Stripe or QBO

---

## 5. Technical Specifications

### 5.1 Stripe Invoice Data Model

**Active Fields** (from BigQuery sync):
```
stripe.invoice {
  id: "in_...",                    // Stripe invoice ID (immutable)
  number: "UUID-like",             // Auto-generated invoice number
  customer_id: "cus_...",          // Stripe customer ID
  status: "draft|open|paid|uncollectible",
  amount_due: <cents>,
  amount_paid: <cents>,
  total: <cents>,
  subtotal: <cents>,
  tax: 0,                          // Always 0 in current model
  currency: "usd",
  created: <timestamp>,
  due_date: <timestamp>,
  period_start: <timestamp>,
  period_end: <timestamp>,
  description: "<string>",
  collection_method: "send_invoice",
  billing_reason: "subscription_cycle|etc",
  payment_intent_id: "pi_...",
  subscription_id: "sub_...",
  metadata: {                      // JSON - can store references
    client_id: <xano_id>,
    qbo_doc_number: "BI...",      // ** RECOMMENDED: Store QBO link here **
    xano_calculation_date: <timestamp>
  }
}

stripe.invoice_line_item {
  invoice_id: "in_...",
  id: "il_...",
  type: "subscription|invoiceitem|tax|discount",
  description: "1 × Subscription Estimating (at $3,000.00 / month)",
  amount: <cents>,
  currency: "usd"
}

stripe.charge {
  id: "ch_...",
  customer_id: "cus_...",
  invoice_id: "in_...",
  amount: <cents>,
  status: "succeeded|failed",
  paid: <boolean>,
  refunded: <boolean>,
  created: <timestamp>
}
```

### 5.2 QBO Invoice Data Model

**Active Fields** (from reverse-engineered manual entry):
```
qbo.invoice {
  id: "<string>",                  // QBO internal ID
  customer_id: "<string>",         // QBO customer ID
  doc_number: "BI...",            // Format: BI + YYMMDD + seq (manual)
  transaction_date: <date>,        // Invoice date
  due_date: <date>,                // Payment due date
  total_amount: <decimal>,         // Dollars (not cents)
  balance: <decimal>,              // Outstanding balance
  status: "SYNCED|UNSYNC|CLOSED",
  customer_memo: "<string>",       // Optional invoice memo
  private_note: "<string>"         // Optional internal notes
}

qbo.invoice_line {
  invoice_id: "<string>",
  line_num: <integer>,
  description: "<string>",
  amount: <decimal>,               // Dollars
  sales_item_item_id: "<string>", // Item ID (45=Subscription, 46=Large Loss, 48=Volume, 47=Overage)
  sales_item_account_id: "<string>" // Account ID (209=AR, 126=Large Loss AR, 200=Volume AR, 221=Overage)
}

qbo.payment {
  id: "<string>",
  customer_id: "<string>",
  transaction_date: <date>,
  total_amount: <decimal>,
  deposit_to_account_id: "294",  // Cash account
  receivable_account_id: "<string>"
}
```

**QBO Line Item Mapping** (from actual data):
| Item ID | Account ID | Description | Use Case |
|---------|-----------|-------------|----------|
| 45 | 209 | Subscription | Monthly subscription fee |
| 46 | 126 | Large Loss | Large loss project fees |
| 48 | 200 | Volume | Volume/Tier 4 fees |
| 47 | 221 | Overage | Overage fees |
| 44 | 203 | Discount | Discounts/credits |

### 5.3 Linking Strategy: Stripe ↔ QBO

**Critical Change**: Stripe creates TWO invoices per customer/month (subscription + variable), which map to QBO invoices with MULTIPLE line items.

**Dual-Invoice Linking Model**:

```sql
CREATE TABLE xano-fivetran-bq.invoicing_links (
  link_id STRING PRIMARY KEY,
  stripe_invoice_id STRING NOT NULL UNIQUE,     -- in_1SKOO9... (subscription OR variable)
  stripe_invoice_type STRING NOT NULL,          -- 'subscription' or 'variable_costs'
  qbo_invoice_id STRING NOT NULL,               -- QBO internal ID (may map to multiple line items)
  qbo_doc_number STRING NOT NULL,               -- BI251101 (human reference)
  xano_client_id INTEGER NOT NULL,              -- For audit
  stripe_total_cents INTEGER NOT NULL,
  qbo_total_dollars NUMERIC NOT NULL,
  synced_at TIMESTAMP NOT NULL,
  created_by STRING,                            -- "system"
  status STRING                                 -- 'linked', 'disputed', 'voided'
);
```

**Linking Logic**:

1. **INVOICE #1 (Subscription)**:
   - Read Stripe subscription invoice (single line item)
   - Find/create QBO invoice with subscription line (Item 45, Account 209)
   - Link: `stripe_subscription_inv_id → qbo_doc_number (subscription)`

2. **INVOICE #2 (Variable Costs)** - if exists:
   - Read Stripe variable invoice (multiple line items: Overage, Volume, Large Loss)
   - Find/create QBO invoice with variable cost lines (Items 46/48/47, Accounts 126/200/221)
   - Link: `stripe_variable_inv_id → qbo_doc_number (variable)`

**Why Two Links?**
- Stripe separates subscription (auto-recurring) from ancillary charges (manual)
- QBO reflects this with different line items and accounts
- Linking captures this structural difference for proper reconciliation

**Example**:
```
Customer: Acme Corp
Month: October 2025

Stripe:
├─ Invoice in_1SDz... (Subscription) - $3,000
└─ Invoice in_1SFh... (Variable)     - $500 (Overage $300 + Volume $200)

QBO: 
├─ Invoice BI251101 (Subscription line) - Item 45, Account 209, $3,000
└─ Invoice BI251102 (Variable lines)    - Item 47, Account 221, $300 (Overage)
                                         Item 48, Account 200, $200 (Volume)

Links:
├─ in_1SDz... → BI251101 (type: subscription)
└─ in_1SFh... → BI251102 (type: variable_costs)
```

---

## 6. Edge Cases & Exception Handling

### 6.1 Duplicate Prevention (Idempotency)

**Problem**: If sync service crashes after creating QBO invoice but before recording link, next run might create duplicate.

**Solution**: 
1. **Check linking metadata first**: Before creating new QBO invoice, query BigQuery for existing Stripe invoice with same attributes
2. **Idempotency key**: Include invoice creation timestamp in query to avoid re-processing
3. **QBO deduplication**: Search QBO for invoice with doc_number prefix matching pattern before creating

### 6.2 Failed Payments

**Scenario**: Payment fails (charge declined), Stripe invoice remains unpaid.

**Handling**:
1. Stripe charge status = "failed"
2. QBO invoice status = "open" (still owed)
3. Customer retries payment
4. If successful: Stripe charge succeeds, invoice marked paid, QBO updated
5. If max retries exceeded: Princess issues credit or suspends service

### 6.3 Partial Payments

**Scenario**: Customer pays less than invoice total (e.g., deposit-based model).

**Current State**: Unlikely with Stripe send_invoice model (all-or-nothing)
**Future Consideration**: If payment plans introduced, implement installment logic in Stripe, sync payment schedule to QBO

### 6.4 Over-Payments

**Scenario**: Customer accidentally pays more than invoice total.

**Handling**:
1. Stripe charge exceeds invoice amount
2. Excess recorded in Stripe account credit or as customer balance
3. QBO payment synced as received; balance tracked separately
4. Princess reconciles in next billing cycle (apply credit to future invoices)

### 6.5 Invoice Disputes

**Scenario**: Customer disputes invoice amount.

**Handling**:
1. If dispute filed with card processor:
   - Stripe chargeback initiated
   - Stripe records dispute status
   - QBO invoice remains "open" until resolved
   - Princess follows chargeback process
2. If customer claims calculation error:
   - Review Xano calculation
   - If correct: Explain to customer
   - If error: Princess issues credit memo in Stripe, QBO reflects credit

### 6.6 Customer Deleted/Suspended

**Scenario**: Customer removed from Xano but invoice still in Stripe.

**Handling**:
1. Customer record soft-deleted in Xano
2. Existing Stripe invoices remain for historical records
3. No new invoices created for deleted customer
4. QBO invoices remain for reconciliation (GL posting still valid)

---

## 7. Data Quality & Validation Rules

### 7.1 Pre-Invoice Creation Validation (Xano)

**Must be true before calling Stripe API**:
1. Client record exists and is active (`Client.Not_Allowed ≠ true`, `Client.Suspended ≠ true`)
2. Subscription exists and is active
3. `Client.Stripe_Customer_ID` is populated
4. Billing period dates are valid (`month_start < month_end`)
5. Calculated volume > 0 OR invoice has other line items (don't create $0 invoices)
6. Client has valid email for invoice delivery

### 7.2 Post-Creation Validation (Stripe ↔ QBO)

**Must be true after invoice synced**:
1. Stripe invoice ID is non-null and matches pattern `in_*`
2. Stripe invoice status is not "draft" (should be open/paid/etc)
3. Stripe amount_due > 0
4. Stripe customer_id is mapped to QBO customer_id (via Xano)
5. QBO invoice created with matching amount (within $0.01 due to rounding)
6. QBO invoice doc_number is unique
7. Linking metadata is populated on both sides

### 7.3 Reconciliation Checks

**Monthly reconciliation queries** (run in BigQuery):
```sql
-- Find Stripe invoices without corresponding QBO invoices
SELECT 
  s.id as stripe_id,
  s.number,
  s.total,
  s.status,
  s.metadata
FROM stripe.invoice s
LEFT JOIN qbo.invoice q ON s.metadata LIKE CONCAT('%', q.id, '%')
WHERE q.id IS NULL AND EXTRACT(MONTH FROM s.created) = CURRENT_MONTH()
  AND s.status NOT IN ('draft', 'void')

-- Find QBO invoices without corresponding Stripe reference
SELECT
  q.doc_number,
  q.total_amount,
  q.private_note
FROM qbo.invoice q
WHERE q.private_note NOT LIKE 'Stripe: in_%'
  AND EXTRACT(MONTH FROM q.transaction_date) = CURRENT_MONTH()

-- Find payment discrepancies
SELECT
  s.id,
  s.amount_paid,
  q.balance,
  (s.amount_paid / 100.0) - q.total_amount as discrepancy
FROM stripe.invoice s
JOIN qbo.invoice q ON ...
WHERE ABS((s.amount_paid / 100.0) - (q.total_amount - q.balance)) > 0.05
```

---

## 8. Non-Functional Requirements

### 8.1 Performance
- Invoice sync latency: < 5 minutes from Stripe creation to QBO
- Batch sync (if implemented): Process up to 1000 invoices/run
- Query latency: < 30 seconds for reconciliation checks

### 8.2 Reliability
- Sync service must be idempotent (safe to retry)
- Failed syncs must log error details for manual investigation
- Automatic retry on transient failures (network, rate limits)
- Manual sync capability (Princess can trigger QBO upload from UI)

### 8.3 Security
- Stripe API key stored in GCP Secrets Manager (restricted access)
- QBO API credentials in GCP Secrets (taz_qbo service account)
- BigQuery queries use principle of least privilege
- No invoice data stored in logs or temporary files

### 8.4 Audit & Compliance
- All invoice changes logged with timestamp and actor (system or manual)
- Linking metadata immutable once created
- Monthly reconciliation report generated
- Historical data retained for 7 years (compliance)

---

## 9. Acceptance Criteria

### 9.1 Functional Acceptance Tests

**Test 1: New Invoice Sync**
- Given: New invoice created in Stripe for customer
- When: Sync service runs
- Then: QBO invoice created with matching amount, date, customer
- Expected: Linking metadata populated, status "open"

**Test 2: Paid Invoice Update**
- Given: Invoice marked paid in Stripe (charge succeeded)
- When: Sync service runs
- Then: QBO invoice status updated to reflect payment
- Expected: Balance = $0, status = "SYNCED"

**Test 3: Credit Memo Sync**
- Given: Credit note issued in Stripe
- When: Sync service runs
- Then: QBO credit memo created with matching amount
- Expected: Credit linked to original invoice

**Test 4: Idempotency**
- Given: Sync service runs and creates QBO invoice
- When: Sync service runs again (duplicate run)
- Then: No duplicate QBO invoice created
- Expected: Same QBO record updated, linking preserved

**Test 5: Customer Lookup**
- Given: Stripe invoice for customer
- When: Sync service runs
- Then: Correct QBO customer matched
- Expected: QBO invoice linked to correct customer (via Xano metadata)

**Test 6: Reconciliation Report**
- Given: 100 Stripe invoices synced
- When: Reconciliation query runs
- Then: 100 corresponding QBO invoices found
- Expected: Zero discrepancies, all links valid

### 9.2 Edge Case Acceptance Tests

**Test 7: Partial Payment**
- Given: Customer pays partial amount
- When: Sync service runs
- Then: QBO invoice shows balance remaining
- Expected: Multiple payments tracked correctly

**Test 8: Failed Payment Retry**
- Given: Payment fails, then succeeds on retry
- When: Sync service runs
- Then: QBO reflects final paid status
- Expected: No duplicate payment records

**Test 9: Dispute Handling**
- Given: Chargeback filed for invoice
- When: Sync service runs
- Then: Dispute status visible in QBO notes
- Expected: Invoice flagged for review

**Test 10: Large Invoice**
- Given: Invoice amount = $1,000,000
- When: Sync service runs
- Then: QBO invoice created correctly
- Expected: No rounding errors, precision maintained to $0.01

---

## 10. Implementation Roadmap

### Phase 1: Infrastructure & Preparation (2-3 days)
- [ ] Stripe metadata schema defined (fields to include)
- [ ] QBO linking field decided (metadata vs. private_note vs. doc_number format)
- [ ] BigQuery view created for "ready-to-sync" invoices (status=open, not synced)
- [ ] Error logging infrastructure (Cloud Logging or similar)
- [ ] Manual reconciliation query templates created

### Phase 2: Build Decision & Design (1-2 days)
- [ ] Decision: Build in Xano vs. Zapier vs. custom
- [ ] Pro/Con analysis:
  - **Zapier**: Easy setup, limited error handling, vendor lock-in
  - **Xano**: Full control, integrates with Xano backend, requires development
  - **Custom service**: Maximum flexibility, requires infrastructure (Cloud Run, etc.)
- [ ] Architecture finalized based on decision
- [ ] API rate limits documented (Stripe: 100 RPS, QBO: varies by endpoint)

### Phase 3: Development & Testing (3-5 days)
- [ ] Sync service implemented
- [ ] Authentication & secret management set up
- [ ] Idempotency logic implemented
- [ ] Error handling & logging implemented
- [ ] Unit tests written
- [ ] Integration tests with staging Stripe/QBO

### Phase 4: Pilot & Validation (2-3 days)
- [ ] Test with sample invoices (5-10)
- [ ] Manual reconciliation against actual QBO records
- [ ] Edge cases tested (failed payments, credits, disputes)
- [ ] Acceptance tests passed
- [ ] Princess approves workflow

### Phase 5: Production Rollout (1 day)
- [ ] Deploy to production
- [ ] Initial run on historical invoices (Sept-Oct backfill)
- [ ] Monitor for errors
- [ ] Gradual rollout (10% → 50% → 100% of invoices)

### Phase 6: Ongoing Operations (ongoing)
- [ ] Daily sync runs
- [ ] Weekly reconciliation report
- [ ] Monthly audit of linking data
- [ ] Quarterly review of performance & error logs

---

## 11. Appendix: Reference Data & Examples

### 11.1 Example: Subscription Invoice Creation Flow

**Input (Xano)**:
```
{
  client_id: 42,
  month_start: 2025-10-01T00:00:00Z,
  month_end: 2025-10-31T23:59:59Z,
  change_id: null
}
```

**Xano Calculation**:
```
client = fetch(Client, id=42)
  → Stripe_Customer_ID: "cus_Ph9xvNCv"
  → subscription_id: 3
  → Full_Name: "Acme Corp"

subscription = fetch(Subscription, id=3)
  → Name: "Subscription Estimating"
  → Subscription_Amount: 3000 (dollars)
  → Allowed_Amount: 100000 (volume units)
  → Overage_in_percentage: 0.02

volume = Calculate_Delivered_Volume(client_id=42, month_start=..., month_end=...)
  → total_subscription_delivered: 87500
  → total_large_loss_delivered: 0
  → large_loss_data: []

// No overage (87500 < 100000 threshold)
```

**Stripe Invoice Created**:
```json
{
  "customer": "cus_Ph9xvNCv",
  "line_items": [
    {
      "type": "invoiceitem",
      "description": "1 × Subscription Estimating (at $3,000.00 / month)",
      "amount": 300000,
      "currency": "usd"
    }
  ],
  "metadata": {
    "client_id": "42",
    "xano_calculation_date": "2025-10-31T12:00:00Z"
  },
  "collection_method": "send_invoice",
  "due_date": 1730419200
}
```

**Stripe Response**:
```json
{
  "id": "in_1SKOO9L6RKmCZ5rpi",
  "number": "391BEB0D-0",
  "customer_id": "cus_Ph9xvNCv",
  "status": "open",
  "total": 300000,
  "currency": "usd",
  "created": 1730419200,
  "due_date": 1730505600,
  "metadata": {
    "client_id": "42",
    "xano_calculation_date": "2025-10-31T12:00:00Z"
  }
}
```

**Fivetran Sync to BigQuery** (5-10 min later):
```sql
INSERT INTO stripe.invoice (
  id, number, customer_id, total, status, created, due_date, metadata, ...
) VALUES (
  'in_1SKOO9L6RKmCZ5rpi',
  '391BEB0D-0',
  'cus_Ph9xvNCv',
  300000,
  'open',
  TIMESTAMP('2025-10-31T12:00:00Z'),
  TIMESTAMP('2025-11-01T00:00:00Z'),
  '{"client_id": "42", ...}',
  ...
);
```

**QBO Sync Service Processes**:
```
1. Query BigQuery: SELECT * FROM stripe.invoice WHERE status='open' AND metadata LIKE '%qbo%' IS NULL
2. Find matching: in_1SKOO9L6RKmCZ5rpi → client_id=42 → lookup Xano client
3. Lookup QBO customer: SELECT * FROM qbo.customer WHERE name='Acme Corp'
4. Create QBO Invoice:
   {
     "customer_id": "3",
     "doc_number": "BI251101",
     "transaction_date": "2025-10-31",
     "due_date": "2025-11-01",
     "total_amount": 3000,
     "line_items": [
       {
         "description": "1 × Subscription Estimating (at $3,000.00 / month)",
         "amount": 3000,
         "sales_item_item_id": "45",
         "sales_item_account_id": "209"
       }
     ],
     "private_note": "Stripe: in_1SKOO9L6RKmCZ5rpi"
   }
5. Store linking: stripe.invoice.metadata.qbo_doc_number = "BI251101"
6. Mark as synced
```

---

## 12. Sign-Off & Approval

**Document Status**: READY FOR IMPLEMENTATION SCOPING

**To Proceed**: 
- [ ] Confirm Stripe metadata linking strategy (Section 5.3)
- [ ] Decide build method: Xano vs. Zapier vs. Custom (Section 10)
- [ ] Allocate resources and timeline
- [ ] Finalize Phase 1 tasks

---

**Version History**:
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-01 | Assistant (Taz) | Initial finalized SoT with full spec, catalogs, and acceptance criteria |
