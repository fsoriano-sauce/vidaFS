# QBO Active Fields & Objects Catalog

**Purpose**: Document which QBO fields and objects are actively populated when the AR/AP specialist manually syncs Stripe invoice data into QuickBooks Online.

**Data Period Analyzed**: September - October 2025
**Method**: Reverse-engineered from actual QBO data (BigQuery `quickbooks.*` tables)
**Status**: CATALOGING ONLY (no transformations or work beyond analysis)

---

## QBO Invoice Object (`quickbooks.invoice`)

### Fields Being Used (Actively Populated)

| Field Name | Type | Description | Usage |
|---|---|---|---|
| `id` | STRING | QBO internal invoice ID | Primary key |
| `customer_id` | STRING | Reference to customer | Required for linking |
| `doc_number` | STRING | Invoice document number (e.g., `BI10251041`) | **CRITICAL: Linking field** |
| `transaction_date` | DATE | Invoice date | Billing date |
| `due_date` | DATE | Invoice due date | Payment terms |
| `total_amount` | BIGNUMERIC | Total invoice amount in dollars | Core billing amount |
| `balance` | BIGNUMERIC | Outstanding balance (0 if paid) | AR tracking |
| `private_note` | STRING | Internal notes | Manual annotations |
| `customer_memo` | STRING | Customer-facing memo | Invoice description |
| `billing_email` | STRING | Email address for invoice | Delivery |
| `allow_online_payment` | BOOLEAN | Enable online payments | Payment options |
| `allow_online_credit_card_payment` | BOOLEAN | Enable credit card payments | Payment method |
| `billing_address_id` | STRING | Reference to billing address | Shipping details |

### Fields NOT Being Used (Null/Empty)

- `billing_cc_email`, `billing_bcc_email` - CC recipients not used
- `total_tax` - No tax lines present
- `tax_code_id` - No tax coding
- `shipping_address_id` - Shipping address not used
- `deposit_to_account_id` - Deposit account not specified
- `class_id` - Classes not used for segmentation
- `department_id` - Departments not used
- `sales_term_id` - Sales terms not specified
- `custom_p_o_number` - Custom PO fields not used

---

## QBO Invoice Line Items (`quickbooks.invoice_line`)

### Line Item Detail Types Used

1. **SalesItemLineDetail** (194 instances)
   - Represents actual line items
   - Contains item/service charges

2. **SubTotalLineDetail** (166 instances)
   - Represents subtotal line (auto-calculated)
   - Always appears at end of invoice

### SalesItemLineDetail Fields Being Used

| Field Name | Type | Description | Sample Value |
|---|---|---|---|
| `line_num` | INTEGER | Line number (starts at 1) | 1 |
| `description` | STRING | Line item description | "Subscription for October 2025" |
| `amount` | BIGNUMERIC | Line item total | 1500, 3000, 5500 |
| `sales_item_item_id` | STRING | QBO Item reference | "45" (standard subscription item) |
| `sales_item_account_id` | STRING | GL account for line item | "209" (AR account) |
| `sales_item_quantity` | BIGNUMERIC | Quantity (not used) | NULL |
| `sales_item_unit_price` | BIGNUMERIC | Unit price (not used) | NULL |
| `sales_item_tax_code_id` | STRING | Tax code (not used) | NULL |
| `sales_item_class_id` | STRING | **Subscription tier ID** (ACTIVELY USED) | `7100000000001469973`, `568238`, `7100000000001474306`, etc. |

### Pattern Observed

- **Multiple line items**: Invoices can have one or more sales item lines (1:1 mapping from Stripe)
- **Multiple item IDs used**:
  - Item `45` (Account `209`): Subscription fees
  - Item `46` (Account `126`): Large Loss fees
  - Item `48` (Account `200`): Volume fees
  - Item `47` (Account `221`): Overage fees
  - Item `44` (Account `203`): Discounts
- **Class ID = Subscription Tier**: Each line has `sales_item_class_id` populated with the customer's subscription tier ID
- **Standardized account**: All lines post to GL Account `209` (AR account)
- **No quantity pricing**: Quantity and unit price are not used; amount is the total
- **Simple structure**: Description contains period (e.g., "Subscription for October 2025") + amount

---

## QBO Customer Object (`quickbooks.customer`)

### Key Fields Referenced

| Field Name | Type | Used In | Purpose |
|---|---|---|---|
| `id` | STRING | invoice.customer_id | Customer linking |
| `display_name` | STRING | Display/reporting | Customer identification |
| `email` | STRING | Potential contact | Email communication |
| `active` | BOOLEAN | Filtering | Active customer check |
| `balance` | BIGNUMERIC | AR reporting | Customer balance |
| `billing_address_id` | STRING | Address reference | Billing address |

---

## QBO Payment Object (`quickbooks.payment`)

### Fields Being Used

| Field Name | Type | Description | Usage |
|---|---|---|---|
| `id` | STRING | QBO internal payment ID | Primary key |
| `customer_id` | STRING | Reference to customer | Required for linking |
| `reference_number` | STRING | Payment reference (usually NULL) | External reference |
| `transaction_date` | DATE | Payment date | Cash date |
| `total_amount` | BIGNUMERIC | Payment amount in dollars | Core payment amount |
| `unapplied_amount` | BIGNUMERIC | Unapplied portion (usually 0) | Overpayment tracking |
| `payment_method_id` | STRING | Payment method reference | Payment type |
| `deposit_to_account_id` | STRING | GL account for deposit | Usually Account 294 |
| `receivable_account_id` | STRING | AR account reference | AR clearing |

### Pattern Observed

- **Deposit Account**: All payments deposit to Account `294` (Cash)
- **Unapplied Amount**: Almost always `0` (payments are fully applied)
- **Reference Number**: Typically NULL (no external reference)
- **Date Alignment**: Payment dates align with invoice dates or shortly after

---

## Key Observations for Stripe→QBO Mapping

### Line Item Mapping Pattern: 1:1 from Stripe to QBO

**Stripe line items map directly to QBO line items** (NOT aggregated):

| Stripe Line Item | Stripe metadata.type | QBO Item ID | QBO Account | Description Example |
|------------------|---------------------|-------------|-------------|---------------------|
| Subscription | (empty) | 45 | 209 | "Subscription for September 2025" |
| Large Loss | `"Large Loss"` | 46 | 126 | "Matthew Hall - CON" or "June 2025 Large Loss" |
| Volume Fee | `"Volume"` | 48 | 200 | "Volume Fee ($104,521 in Total Volume)" or "July 2025 Volume Discount" |
| Overage | `"Overage"` | 47 | 221 | (TBD - not seen in Sept-Oct data) |
| Discount | `"Discount"` | 44 | 203 | (TBD - not seen in Sept-Oct data) |

**For Sync**: When syncing Stripe → QBO:
- Read each Stripe `invoice_line_item` 
- Check `metadata.type` field to determine QBO Item/Account mapping
- Create one QBO line item per Stripe line item (1:1 mapping)
- Set `sales_item_class_id` = customer's subscription tier ID
- Amount conversion: Stripe cents → QBO dollars (divide by 100)

### No Tax, No Discounts
- No tax lines present in any invoice
- No discount lines present
- All amounts are net totals

### Doc Number as Linking Key
- Format: `BI10251041` (pattern: `BI` + `YYMMDD` + sequence)
- This is the **critical field** for matching Stripe invoices to QBO invoices
- Appears to be manually assigned or auto-generated

### Payment Reconciliation
- Payments always fully applied (unapplied_amount = 0)
- Single deposit account (294) used for all payments
- Payment dates track closely with invoice due dates

---

## Summary: Active QBO Fields for Stripe Sync

**Invoice Fields (13 active, 30+ inactive)**:
- Required: `customer_id`, `doc_number`, `total_amount`, `transaction_date`, `due_date`
- Optional: `private_note`, `customer_memo`, `billing_email`, `billing_address_id`
- Payment Settings: `allow_online_payment`, `allow_online_credit_card_payment`
- Balance Tracking: `balance`

**Line Item Fields (6 active, 8+ inactive)**:
- Always Active: `description`, `amount`, `sales_item_item_id` (45/46/47/48/44), `sales_item_account_id` (209/126/200/221/203), `sales_item_class_id` (subscription tier), `detail_type` ("SalesItemLineDetail")
- Not Used: `quantity`, `unit_price`, `tax_code`, `discount`, `markup`

**Payment Fields (9 active)**:
- Required: `customer_id`, `transaction_date`, `total_amount`
- Deposit: `deposit_to_account_id` (294)
- AR: `receivable_account_id`
- Optional: `reference_number` (usually NULL)

---

**Status**: QBO Catalog Complete ✓
**Next Step**: Analyze Stripe data catalog when sync completes
