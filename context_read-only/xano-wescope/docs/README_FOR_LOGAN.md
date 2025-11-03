# Stripe → QBO Sync: Decision Package for Logan

**Status**: 🟢 **READY FOR APPROVAL**  
**Date**: November 1, 2025  
**Prepared by**: Frankie + Taz

---

## What You Need to Review

This package contains **everything needed to make an approval decision** on automating the Stripe → QBO invoice sync. All architectural decisions are finalized. All unknowns are resolved.

### Read in This Order:

#### 1. **[PROPOSAL_FOR_LOGAN.md](./PROPOSAL_FOR_LOGAN.md)** ← START HERE (20 min read)
   - Executive summary
   - Why Xano (vs. Zapier/Custom)
   - Complete build workflow (XanoScript, phases, timeline)
   - Architecture & data flow
   - All architectural decisions finalized
   - BigQuery tables (4 tables)
   - Customer & tier mapping strategy
   - Questions for you (8 items)
   - Implementation roadmap

#### 2. **[sot-stripe-qbo-sync.md](./sot-stripe-qbo-sync.md)** (Reference - if you have questions)
   - Complete technical specification
   - 10 acceptance criteria tests
   - Full business rules and edge cases
   - Data validation rules
   - Invoice lifecycle (5 stages)

#### 3. **[FINAL_SYSTEM_MAPPING.md](../specs/FINAL_SYSTEM_MAPPING.md)** (Reference - technical deep dive)
   - Complete Xano ↔ Stripe ↔ QBO field mappings
   - All BigQuery table schemas
   - Step-by-step sync logic
   - Customer & tier mapping details

#### 4. **Data Catalogs** (Reference - see analyzed data)
   - [`/specs/xano-catalog-active-fields.md`](../specs/xano-catalog-active-fields.md) - Xano schema
   - [`/specs/stripe-catalog-active-fields.md`](../specs/stripe-catalog-active-fields.md) - Stripe fields
   - [`/specs/qbo-catalog-active-fields.md`](../specs/qbo-catalog-active-fields.md) - QBO fields

---

## Quick Facts

| Item | Value |
|------|-------|
| **Objective** | Automate ~65 monthly QBO invoices Princess creates manually |
| **Current State** | 10-15 hours/month manual work, 1-3 day delay, ~2% errors |
| **Solution** | Xano sync service: BigQuery → QBO via API |
| **Implementation** | Build in Xano (existing infrastructure) |
| **Timeline** | 4.5-5.5 days development + 1-2 days testing = ~1 week go-live |
| **Cost** | $0/month (uses existing Xano infrastructure) |
| **Risk** | 🟢 LOW (tested patterns, no new infrastructure) |
| **Impact** | <1 hr/month manual (verification only), 99.9% accuracy, <5 min latency |

---

## Architectural Decisions Finalized

✅ **Architecture**: One-way flow (Xano → Stripe → QBO)
- Stripe is SoR for invoices/payments
- QBO is aggregator only (AR tracking)
- Never reverse-sync or dual-write

✅ **Implementation**: Build in Xano (XanoScript)
- Cost: $0/month vs. $50-100 for Zapier
- Full control & audit trail
- Team already knows Xano

✅ **Data Source**: BigQuery
- Fivetran syncs Stripe → BigQuery
- Batch efficiency vs. direct API polling
- Cost-effective & audit trail

✅ **Linking**: Two-level (invoice + line item)
- Invoice: BigQuery `invoicing_links` table
- Line Item: BigQuery `invoice_line_links` table
- Deterministic 1:1 mapping via Stripe line_item.id

✅ **Customer Mapping**: Via Xano `ptl_client.quickbooks_id`
- Princess completes mapping (407 customers, 89% AI-matched)
- Field already exists in Xano

✅ **Subscription Tier**: Via BigQuery mapping table
- 9 tiers mapped (Tier 1-4, Essential/Plus/Pro, Large Loss, ARC)
- Uses Stripe price_id as key

✅ **Error Logging**: BigQuery
- Accessible via Metabase
- Single source of truth

---

## Zero Unknowns

Every decision is documented with rationale:
- ✅ What data flows where
- ✅ Why BigQuery vs. direct Stripe API
- ✅ Why dual-key table vs. metadata
- ✅ Why Xano vs. Zapier/Cloud Run
- ✅ What gets logged and where
- ✅ How error recovery works
- ✅ How to reconcile invoices
- ✅ What happens if things fail

---

## Your Only Decision

**Do you want to proceed with this implementation?**

```
☐ YES - Approve and start Phase 1 (table creation, infrastructure setup)
☐ NO - Reject (please explain why)
☐ QUESTIONS - Ask clarifying questions (see references above)
```

---

## What Happens Next (If Approved)

**Week 1 (4-5 business days)**:
- Phase 1: Create tables + infrastructure (1 day)
- Phase 2: Build Xano function (2-3 days)
- Phase 3: Test all scenarios (1 day)

**Week 2 (1-2 business days)**:
- Phase 4: Deploy + backfill historical invoices (0.5 day)
- Phase 5: Princess validates workflow (0.5-1 day)

**Go-Live**: End of Week 2

**Ongoing**: Daily sync + weekly reconciliation + monthly audit

---

## Contact

Questions? 
- **Technical details**: See [sot-stripe-qbo-sync.md](./sot-stripe-qbo-sync.md)
- **Field mappings**: See [FINAL_SYSTEM_MAPPING.md](../specs/FINAL_SYSTEM_MAPPING.md)
- **Why Xano (not Zapier/Cloud Run)**: See [PROPOSAL_FOR_LOGAN.md](./PROPOSAL_FOR_LOGAN.md) Section: "Why Xano"

---

**Status**: 🟢 Ready for your decision.  
**Next**: Review PROPOSAL_FOR_LOGAN.md and confirm approval. 👍
