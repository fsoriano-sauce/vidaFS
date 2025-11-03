# Stripe Active Fields & Objects Catalog

**Purpose**: Document which Stripe fields and objects are actively used in the WeScope system, based on actual data synced to BigQuery.

**Data Period Analyzed**: September - October 2025
**Method**: Analyzed live Stripe data synced via Fivetran to `xano-fivetran-bq.stripe.*`
**Status**: CATALOGING ONLY (no transformations or work beyond analysis)

---

## Stripe Invoice Object (`stripe.invoice`)

### Summary Statistics
- **Total Invoices**: 104 (Sept-Oct 2025)
- **Unique Customers**: 65
- **Stripe Connect Usage**: 0 (NOT IN USE)

### Fields Being Used (Actively Populated)

| Field Name | Type | Description | Sample Value |
|---|---|---|---|
| `id` | STRING | Stripe invoice ID | `in_1SKOO9L6RKmCZ5rpi` |
| `number` | STRING | Invoice number (UUID-like) | `391BEB0D-0` |
| `customer_id` | STRING | Stripe customer ID | `cus_Ph9xvNCv` |
| `amount_due` | INTEGER | Amount due in cents | 665612 (=$6,656.12) |
| `amount_paid` | INTEGER | Amount paid in cents | 665612 |
| `amount_remaining` | INTEGER | Remaining balance in cents | 0 |
| `total` | INTEGER | Total invoice amount in cents | 665612 |
| `subtotal` | INTEGER | Subtotal before tax in cents | 665612 |
| `tax` | INTEGER | Tax amount in cents | 0 |
| `currency` | STRING | Currency code | "usd" |
| `status` | STRING | Invoice status | "paid", "open", "draft" |
| `paid` | BOOLEAN | Whether invoice is paid | true/false |
| `created` | TIMESTAMP | Invoice creation time | 2025-10-20T... |
| `due_date` | TIMESTAMP | Invoice due date | 2025-10-20T... |
| `period_start` | TIMESTAMP | Period start date | 2025-10-01T... |
| `period_end` | TIMESTAMP | Period end date | 2025-10-31T... |
| `description` | STRING | Invoice description | "Monthly subscription" |
| `collection_method` | STRING | How invoice is collected | "send_invoice" |
| `billing_reason` | STRING | Reason for invoice | "subscription_cycle" |
| `payment_intent_id` | STRING | Associated payment intent | `pi_...` |
| `subscription_id` | STRING | Associated subscription | `sub_...` |
| `hosted_invoice_url` | STRING | Hosted invoice link | URL to Stripe-hosted invoice |
| `metadata` | STRING | Custom key-value data | JSON string (may contain Xano client_id) |

### Fields NOT Being Used (Null/Empty)

- All `payment_settings_*` fields - Not configured
- All `shipping_*` fields - No shipping on subscription invoices
- `on_behalf_of` - Stripe Connect NOT in use
- `from_invoice_*` - No invoice drafts from templates
- `from_invoice_action` - Related to drafts
- `application` - Third-party app field
- `footer`, `rendering_*` - Display customization
- `last_finalization_error_*` - Only populated if error
- `threshold_reason_*` - Only for threshold invoices
- `post_payment_credit_notes_amount` - No credits issued
- `pre_payment_credit_notes_amount` - No pre-credits

---

## Stripe Invoice Line Items (`stripe.invoice_line_item`)

### Usage Pattern
- Every invoice has **1 subscription line item**
- Followed by optional **tax rate line items** (not present in this dataset)
- Then optional **discount line items** (not present)

### Fields Being Used

| Field Name | Type | Description | Sample Value |
|---|---|---|---|
| `invoice_id` | STRING | Reference to invoice | `in_1SOjNfL6RKmCZ5rpc` |
| `id` | STRING | Line item ID | `il_...` (USE THIS for audit trail) |
| `type` | STRING | Type of line item | "subscription", "invoiceitem" |
| `description` | STRING | Line item description | "1 × Subscription Estimating (at $3,000.00 / month)" or "Volume Fee ($104,521 in Total Volume)" |
| `amount` | INTEGER | **Amount in cents** (divide by 100 for dollars) | 300000 (=$3,000.00) |
| `currency` | STRING | Currency | "usd" |
| `metadata` | JSON | **Type classification** (CRITICAL for mapping) | `{}` (subscription) or `{"type":"Large Loss"}` or `{"type":"Volume"}` |
| `livemode` | BOOLEAN | Live or test mode | true |

### Observed Pattern
Line items have two types:
1. **Subscription** (`type = "subscription"`):
   - Format: `{quantity} × {product_name} (at ${price} / {billing_period})`
   - metadata = `{}` (empty)
   - Amount = monthly subscription price (in cents)

2. **Variable Costs** (`type = "invoiceitem"`):
   - metadata.type = "Large Loss", "Volume", "Overage", or "Discount"
   - Description varies by type
   - Amount = calculated fee (in cents)

**Key for QBO Sync**: Use `metadata.type` to determine QBO Item/Account mapping

---

## Stripe Charge Object (`stripe.charge`) - Represents Payments

### Key Statistics
- **Total Charges**: Mix of succeeded, failed, and pending
- **Succeeded Charges**: Payment completed
- **Failed Charges**: Payment declined/failed

### Fields Being Used

| Field Name | Type | Description | Sample Value |
|---|---|---|---|
| `id` | STRING | Charge ID | `ch_3SKP8LL6RKmCZ5rp0` |
| `customer_id` | STRING | Stripe customer | `cus_Ph9xvNCvcIQ` |
| `invoice_id` | STRING | Associated invoice | `in_1SKOO9L6RKmCZ5rpi` |
| `amount` | INTEGER | Charge amount in cents | 665612 |
| `currency` | STRING | Currency | "usd" |
| `status` | STRING | Charge status | "succeeded", "failed" |
| `created` | TIMESTAMP | Charge creation time | 2025-10-20T... |
| `paid` | BOOLEAN | Whether charge succeeded | true/false |
| `refunded` | BOOLEAN | Whether charge was refunded | true/false |

### Pattern Observed
- Charges are created when invoices are sent to customers
- Multiple charge attempts can exist for same invoice (retries)
- Only **succeeded** charges represent actual payments
- **Failed** charges indicate payment method declined

---

## Stripe Customer Object

**Status**: NO DEDICATED CUSTOMER TABLE IN STRIPE FIVETRAN SYNC

Customer data comes embedded in:
- `invoice.customer_id` - Reference to Stripe customer
- Actual customer records NOT synced to BigQuery (would need separate Fivetran table)

### Implication
- Customer linking happens at Xano level (Xano is SoR for customer data)
- Stripe customer ID used as foreign key reference
- No need to sync Stripe customer details if Xano maintains customer SoR

---

## Stripe Credit Notes & Refunds (`stripe.credit_note`, `stripe.refund`)

**Status**: TABLES EXIST but UNUSED in current dataset (Princess manages manually)

- `credit_note` table: Contains credit memos issued
- `credit_note_line_item` table: Line items in credits
- `refund` table: Refunds processed
- Current process: Princess manually creates credits/refunds in Stripe
- Future process: May need to capture these for QBO sync

---

## Key Observations for Stripe → QBO Mapping

### Invoice ID Linking
- **Stripe Invoice ID**: `in_1SKOO9L6RKmCZ5rpi`
- **Stripe Invoice Number**: `391BEB0D-0` (UUID-like, auto-generated)
- **QBO doc_number**: `BI10251041` (manually assigned format: `BI` + `YYMMDD` + seq)

**Recommendation for Linking**:
Three possible strategies:

1. **Metadata-based (RECOMMENDED)**
   - Store QBO doc_number in Stripe `metadata` field
   - Pros: Bidirectional lookup, no manual entry
   - Cons: Requires Xano to write back to Stripe after QBO creation

2. **Number-based**
   - Store Stripe invoice number in QBO as reference
   - Pros: Simple, one-way
   - Cons: UUID format not human-friendly

3. **Dual-key system**
   - Maintain link table: Stripe ID ↔ QBO doc_number
   - Pros: Flexible, audit trail
   - Cons: Requires separate database table

### Data Quality Observations
- **Single currency**: USD only (confirmed - no multi-currency)
- **No Stripe Connect**: `on_behalf_of` always NULL (confirmed)
- **No complex tax logic**: `tax` always 0 in sample data
- **Clean subscription pattern**: All invoices follow 1-line subscription format
- **Disputes in data**: Mix of succeeded/failed charges indicates payment retries

### Payment Flow
1. Invoice created in Stripe by Xano function
2. Customer receives invoice
3. Payment processed → Charge created
4. Portal streams payment status back to Xano
5. Princess exports payment CSV
6. Princess manually imports to QBO
7. Chase account auto-synced separately

---

## Summary: Active Stripe Fields for Sync

**Invoice Fields (23 active, 50+ inactive)**:
- Core: `id`, `number`, `customer_id`, `total`, `status`, `paid`
- Amounts: `amount_due`, `amount_paid`, `amount_remaining`, `subtotal`, `tax`
- Dates: `created`, `due_date`, `period_start`, `period_end`
- Content: `description`, `collection_method`, `billing_reason`
- Links: `payment_intent_id`, `subscription_id`, `metadata`

**Line Item Fields (6 active, 20+ inactive)**:
- Always: `invoice_id`, `id`, `type`, `description`, `amount`, `currency`, `livemode`

**Charge/Payment Fields (9 active)**:
- Core: `id`, `customer_id`, `invoice_id`, `amount`, `currency`
- Status: `status`, `paid`, `refunded`, `created`

**NOT IN USE**:
- Stripe Connect fields (NOT used)
- Shipping fields (subscription invoices only)
- Tax customization (flat rate or none)
- Discount fields (manual credits instead)
- Payment settings (simple send invoice model)

---

## Comparison: Stripe vs QBO Active Fields

| Aspect | Stripe | QBO |
|---|---|---|
| **Invoice ID** | Stripe ID (`in_...`) | doc_number (`BI...`) |
| **Customer ID** | Stripe customer ID | QBO customer ID |
| **Amount** | Single total (cents) | Single total (dollars) |
| **Line Items** | 1 subscription per invoice | 1 subscription per invoice |
| **Tax** | Always 0 in current data | Not used |
| **Dates** | Multiple (created, due, period) | transaction_date, due_date |
| **Linking Field** | **UNCLEAR** - needs decision | `doc_number` (manual entry) |

---

**Status**: Stripe Catalog Complete ✓
**Awaiting**: Decision on Stripe Invoice ID linking strategy for QBO
