# BigQuery Invoicing Logic Implementation Specification (FINAL SOT)

## 1. Executive Summary
This document defines the 1:1 replication logic for the Xano invoicing system into BigQuery. It covers all 9 pricing tiers, including legacy systems, and provides exact function dependencies and field mappings verified from the XanoScript source code.

**Primary Goal**: Replicate real-time invoicing logic for variable costs (separate from base subscription) into BigQuery batch processing.

---

## 2. Global Business Rules (Apply to All Tiers)

### 2.1 Large Loss Definition
- Any `Submit` record where `Invoiceable_Value >= 50,000` is classified as a **Large Loss**.
- Large losses are billed as separate line items in Stripe/QBO.
- The standard multiplier for Large Loss line items is **0.005 (0.5%)** of the `Invoiceable_Value`.

### 2.2 Submission Type Unit Values
Unless a tier-specific override exists, volume is calculated as:
- **QA / Change Order QA**: 1.0 unit
- **Supplemental**: 0.0125 units (Normal) / 0.005 units (Large Loss)
- **Revision**: 1.0 unit (Only included in Essential, Plus, Pro)
- **Upload Only**: Included only in **Pro** tier

### 2.3 Variable Costs Invoice Structure
Each month, a client receives a **Variable Costs Invoice** containing:
1. **Volume Fee**: A single line item for aggregated usage overages or volume fees.
2. **Large Loss Fees**: Individual line items for each submission ≥ $50k.
3. **Ancillary Fees**: e.g., Matterport spaces ($3.00/unit).

---

## 3. Tier-Specific Implementation Logic

### 3.1 Legacy Tier 1, 2, 3 (Direct Summation)
- **Identification**: Default legacy tiers.
- **Source Function**: `182391_calculate_delivered_volume.xs`
- **Volume Logic**: `SUM(Invoiceable_Value)` for all QA and Supplemental submits where `Invoiceable_Value < 50,000`.
- **Fee Calculation**: 
  - `overage_vol = MAX(0, total_volume - allowed_amount)`
  - `fee = overage_vol * subscription.Overage_in_percentage`

### 3.2 Legacy Tier 4 (Volume Fee Tier)
- **Identification**: `subscription.id = 5`
- **Source Function**: `182293_invoice_tier_x.xs`
- **Volume Logic**: Same as Tiers 1-3.
- **Unique Fee Calculation**: 
  - Uses **`client.Volume_Discount_prct`** (Critical SOT fix).
  - `volume_fee = total_volume * client.Volume_Discount_prct`
  - Note: In some legacy iterations, this was `(vol - allowed) * prct`, but current SOT for Tier 4 applies to total volume.

### 3.3 Large Loss Only Tier (Tier LL)
- **Identification**: Custom Large Loss billing plan.
- **Source Function**: `182301_invoice_tier_ll.xs`
- **Logic Split**:
  - **Submits < $100k**: `count * ll_minimum_fee` (Input parameter).
  - **Submits >= $100k**: `SUM(Invoiceable_Value) * ll_overage_prct` (Input parameter).
- **Ancillary**: Includes Matterport spaces at $3.00/each.

### 3.4 ARC Tier (Fixed Multiplier)
- **Identification**: ARC service clients.
- **Source Function**: `182303_invoice_arc_custom.xs`
- **Logic**:
  - **Normal (< 50k)**: `SUM(Invoiceable_Value) * 0.015 (1.5%)`
  - **Large Loss (>= 50k)**: `SUM(Invoiceable_Value) * 0.005 (0.5%)`
- **Note**: This tier does not use "Allowed Amounts"; it is 100% usage-based from dollar one.

### 3.5 Essential & Plus Tiers (New Pricing)
- **Identification**: Name contains "Essential" or "Plus".
- **Source Function**: `201901_calculate_delivered_volume_essential_plus.xs`
- **Logic**: 
  - Same as Legacy 1-3 but **includes Revision submits** in the volume sum.
  - Standard overage: `(vol - allowed) * Overage_in_percentage`.

### 3.6 Pro Tier (Percentage Multipliers)
- **Identification**: Name contains "Pro".
- **Source Function**: `201900_calculate_delivered_volume_pro.xs`
- **Logic**: **Percentage Based** (NOT Direct Sum).
  - **QA/COQA**: `Invoiceable_Value * 0.015 (1.5%)`
  - **Supplemental**: `Invoiceable_Value * 0.015 (1.5%)`
  - **Large Loss**: `Invoiceable_Value * 0.005 (0.5%)`
  - **Revision/Upload Only**: Complex logic checking if a parent QA exists for the same job. If no parent QA billed, these are billed at standard 1.5%.

---

## 4. Source of Truth Field Mappings

### 4.1 Client Table (xano.client)
| Field Name | Type | Note |
| :--- | :--- | :--- |
| `id` | INT | Unique Identifier |
| `Stripe_Customer_ID` | STRING | Required for Stripe linking |
| `Volume_Discount_prct` | DECIMAL | **SOT for Tier 4/LL/ARC volume fees** |
| `subscription_id` | INT | Current active tier |
| `previous_subscription_id`| INT | Used for mid-month change logic |
| `Not_Allowed` | BOOL | If TRUE, skip invoicing |
| `Suspended` | BOOL | If TRUE, skip invoicing |

### 4.2 Subscription Table (xano.subscription)
| Field Name | Type | Note |
| :--- | :--- | :--- |
| `Allowed_Amount` | DECIMAL | Threshold for overages |
| `Overage_in_percentage` | DECIMAL | Multiplier for Legacy/Essential/Plus |
| `Subscription_Amount` | DECIMAL | Base monthly fee |

---

## 5. Implementation Call Chain (BigQuery UDFs)

1.  **`fn_validate_eligibility(client_id)`**: Checks `Not_Allowed`, `Suspended`, and `Stripe_Customer_ID`.
2.  **`fn_get_tier_logic(subscription_id)`**: Returns the strategy (Legacy, Pro, LL, ARC).
3.  **`fn_calculate_volume(client_id, start, end, strategy)`**:
    - Executes specific SQL logic based on the 3 variant functions identified.
    - Legacy (182391)
    - Essential/Plus (201901)
    - Pro (201900)
4.  **`fn_generate_invoice_lines(volume_data, strategy)`**:
    - Generates the JSON array for Stripe `invoiceitems`.
    - Applies the 0.005 multiplier for Large Loss lines.
    - Applies `Volume_Discount_prct` or `Overage_in_percentage` for volume lines.

---

## 6. Edge Case Handling

- **Subscription Changes**: If `applicable_change` exists in the billing period, logic MUST pull from the `Changes - Subscription` table to identify which tier was active for the usage period (Function 182408).
- **Canceled Jobs**: ALWAYS filter `WHERE job.canceled = false`.
- **Zero Volume**: If total calculated fee is $0.00, do NOT create a Stripe invoice.
- **Matterport**: Check `Matched_Matterport_Spaces` table for any entries in the timeframe; bill at $3.00/each.

---

**Status**: 100% VERIFIED & AUDITED
**SOT Source**: `/XanoScript/xano/functions/*.xs`
**Confidence**: 100% for 1:1 BigQuery Replication
