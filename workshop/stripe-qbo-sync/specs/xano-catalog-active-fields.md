# Xano Active Fields & Objects Catalog

**Purpose**: Document which Xano fields and objects are actively used in the invoicing process for Stripe → QBO sync.

**Data Source**: XanoScript functions (`.xs` files)
**Method**: Analyzed invoicing functions to extract schema and field usage
**Status**: CATALOGING ONLY (no transformations or work beyond analysis)

---

## Xano Client Object (`Client` table)

### Fields Being Used (From Invoicing Functions)

| Field Name | Type | Description | Sample Value | Notes |
|---|---|---|---|---|
| `id` | INTEGER | Client ID (Primary Key) | `42` | **PK in Xano** |
| `Stripe_Customer_ID` | STRING | Stripe customer reference | `cus_Ph9xvNCv` | **FK to Stripe customer** |
| `subscription_id` | INTEGER | Reference to Subscription table | `3` | **FK to Xano Subscription** |
| `Full_Name` | STRING | Client full name | `Acme Corp` | Used for QBO lookup |
| `Not_Allowed` | BOOLEAN | Client restriction flag | `false` | Validation check |
| `Suspended` | BOOLEAN | Account suspension status | `false` | Validation check |
| `Senior_Estimator_id` | INTEGER | FK to User (Senior Estimator) | `123` | For notifications |
| `Team_Lead_id` | INTEGER | FK to User (Team Lead) | `456` | For notifications |
| `Billing_POC_id` | INTEGER | FK to Contact (Billing POC) | `789` | For invoice delivery |

### Fields NOT Observed in Invoicing Functions

- `qbo_customer_id` - **QUESTION**: Does this field exist for QBO linking?
- Various other operational fields (Team, National_Affiliation, etc.)

---

## Xano Subscription Object (`Subscription` table)

### Fields Being Used (From Invoicing Functions)

| Field Name | Type | Description | Sample Value | Notes |
|---|---|---|---|---|
| `id` | INTEGER | Subscription ID (Primary Key) | `3` | **PK in Xano** |
| `Name` | STRING | Subscription name | `Subscription Estimating` | Display name |
| `Subscription_Amount` | DECIMAL | Monthly subscription fee | `3000` | In dollars |
| `Allowed_Amount` | DECIMAL | Usage threshold (volume units) | `100000` | Overage trigger |
| `Overage_in_percentage` | DECIMAL | Overage rate | `0.02` | 2% overage fee |

### Fields NOT Observed

- `qbo_class_id` - **QUESTION**: Does this field exist for QBO Class mapping?
- Tier/pricing details

---

## Xano Submit Object (`Submit` table)

### Fields Being Used (From Calculate Delivered Volume)

| Field Name | Type | Description | Sample Value | Notes |
|---|---|---|---|---|
| `id` | INTEGER | Submit ID (Primary Key) | `12345` | **PK** |
| `Type` | STRING | Submit type | `QA`, `Change Order QA`, `Supplemental`, `Revision` | Classification |
| `Invoiceable_Value` | DECIMAL | Dollar value of submit | `75000` | Large loss threshold check |
| `Client_id` | INTEGER | FK to Client | `42` | Links to client |
| `Job_id` | INTEGER | FK to Job | `987` | Links to job |
| `Submission_Date` | TIMESTAMP | When submitted | `2025-10-15` | Date filtering |

### Usage in Invoicing
- Filtered by `Type` to calculate volume
- `Invoiceable_Value` determines large loss treatment (threshold: $50,000)
- Aggregated by client and date range

---

## Xano Job Object (`Job` table)

### Fields Being Used (From Calculate Delivered Volume)

| Field Name | Type | Description | Sample Value | Notes |
|---|---|---|---|---|
| `id` | INTEGER | Job ID (Primary Key) | `987` | **PK** |
| `Canceled` | BOOLEAN | Job cancellation status | `false` | Filter canceled jobs |
| `Client_id` | INTEGER | FK to Client | `42` | Links to client |

### Usage in Invoicing
- Filter out canceled jobs (`Canceled = true`)
- Link submits to client via job relationship

---

## Xano Invoices Object (`Invoices` table) - **Invoice Finalization Log**

### Purpose
This table DOES NOT store Stripe invoice data. It logs when Xano finalized invoice creation in Stripe.

### Fields Being Used

| Field Name | Type | Description | Sample Value | Notes |
|---|---|---|---|---|
| `id` | INTEGER | Record ID (Primary Key) | Auto-increment | **PK** |
| `Associated_Client` | STRING | Xano client unique_id | `client_uuid_123` | **NOT client.id** (uses unique_id) |
| `Creation_Date` | TIMESTAMP | When invoice was finalized | `2025-10-31 12:00:00` | Log timestamp |
| `Previous_Month_Subscription` | STRING | Subscription name | `Subscription Estimating` | For tracking |
| (Other fields TBD) | | | | Need to check actual schema |

### Important Notes
- This is a **LOG TABLE**, not invoice data storage
- Stores when Xano created Stripe invoices
- Does NOT store Stripe invoice IDs (Stripe is SoR)
- Used for checking if invoice was already processed

---

## Inferred Xano Schema (From XanoScript Analysis)

### Primary Tables Used in Invoicing

1. **`Client`** - Customer master data
   - PK: `id` (INTEGER)
   - FK: `subscription_id` → Subscription
   - FK: `Stripe_Customer_ID` → Stripe Customer (STRING)
   - Validation: `Not_Allowed`, `Suspended`

2. **`Subscription`** - Pricing tiers
   - PK: `id` (INTEGER)
   - Fields: `Name`, `Subscription_Amount`, `Allowed_Amount`, `Overage_in_percentage`

3. **`Submit`** - Usage records
   - PK: `id` (INTEGER)
   - FK: `Client_id`, `Job_id`
   - Fields: `Type`, `Invoiceable_Value`, `Submission_Date`

4. **`Job`** - Projects
   - PK: `id` (INTEGER)
   - FK: `Client_id`
   - Fields: `Canceled`

5. **`Invoices`** - Invoice finalization log
   - PK: `id` (INTEGER)
   - Fields: `Associated_Client` (unique_id), `Creation_Date`, `Previous_Month_Subscription`

---

## ❓ OPEN QUESTIONS FOR FRANKIE

To complete the Xano catalog, please confirm:

1. **QBO Customer Mapping**:
   - Does `Client` table have a `qbo_customer_id` field?
   - If not, how do we map Xano client → QBO customer? (By `Full_Name`?)

2. **Subscription Tier → QBO Class**:
   - Does `Subscription` table have a `qbo_class_id` field?
   - Or is the mapping stored elsewhere?
   - Current observation from QBO data:
     - Subscription ID 3 ($1,500) → QBO Class `7100000000001469972`
     - Subscription ID 4 ($2,750) → QBO Class `7100000000001469973`
     - Subscription ID 5 (Tier 4) → QBO Class `568238` or `568239`
     - Subscription ID 6 ($5,500) → QBO Class `7100000000001474306`

3. **Invoices Table Schema**:
   - What are ALL fields in the `Invoices` table?
   - Is `Stripe_Invoice_ID` stored anywhere in Xano?
   - Or is Xano purely a log of "invoice created" without Stripe ID?

4. **Client Unique ID vs ID**:
   - Why does `Invoices.Associated_Client` use `unique_id` instead of `id`?
   - Should we use `client.id` or `client.unique_id` for linking?

---

## Summary: Active Xano Fields for Stripe → QBO Sync

**Client Fields (9 active)**:
- Required: `id`, `Stripe_Customer_ID`, `subscription_id`, `Full_Name`
- Validation: `Not_Allowed`, `Suspended`
- Optional: `Senior_Estimator_id`, `Team_Lead_id`, `Billing_POC_id`
- **MISSING**: `qbo_customer_id` (needs confirmation)

**Subscription Fields (5 active)**:
- Required: `id`, `Name`, `Subscription_Amount`, `Allowed_Amount`, `Overage_in_percentage`
- **MISSING**: `qbo_class_id` (needs confirmation)

**Submit Fields (6 active)**:
- Used for volume calculation
- Not directly involved in Stripe → QBO sync

**Invoices Fields (3 known)**:
- Log table only (not invoice data storage)
- Needs complete schema confirmation

---

**Status**: Xano Catalog Incomplete - Awaiting Frankie's confirmation on missing fields
**Next Step**: Frankie provides Xano schema details for QBO mapping fields

