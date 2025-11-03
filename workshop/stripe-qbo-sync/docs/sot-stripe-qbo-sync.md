# WeScope — Stripe → QBO Sync: Source of Truth (SoT)

## Executive Summary

**System Purpose**: Unidirectional synchronization of Stripe financial data (invoices, payments, refunds, credits, payouts) into QuickBooks Online (QBO) for accurate Accounts Receivable (AR) reporting.

**Key Principles**:
- **Idempotency**: Prevent duplicates through robust linking mechanisms
- **Lean Customer Records**: Maintain minimal QBO customer data
- **Date Accuracy**: Capture critical financial dates (invoice, usage period, payment received, cash/payout dates)
- **Observability**: Strong logging and monitoring without exposing PII/keys

## Current Status

**Phase**: SoT Finalization (taz collaboration phase)
**Next Phase**: Implementation planning and artifact generation

## Goals & Scope

### In Scope
- Mirror Stripe invoices/payments/refunds/credits/payouts into QBO
- Maintain idempotency via link tables
- Capture key dates for financial reporting
- Unidirectional flow: Stripe → QBO only
- Webhook-triggered updates + replay capability
- GCP-based secrets management

### Out of Scope
- Pricing and subscription management (handled in Xano/Stripe)
- Customer UI development
- Bidirectional sync
- QBO pricing/product management

## Business Rules (Overview)

### Invoice Synchronization
- **Trigger**: Stripe invoice finalized
- **Action**: Create QBO Invoice
- **Mapping**: Stripe invoice → QBO invoice with line items
- **Dates**: Invoice date, usage period start/end

### Payment Processing
- **Trigger**: Stripe invoice paid
- **Action**: Create QBO Payment linked to invoice
- **Mapping**: Stripe payment → QBO payment
- **Dates**: Payment received date

### Credits & Refunds
- **Trigger**: Stripe credit/refund created
- **Action**: Create QBO Credit Memo or Refund Receipt
- **Mapping**: Determine Credit Note vs Refund based on context
- **Dates**: Credit/refund date

### Payout Handling
- **Trigger**: Stripe payout completed
- **Action**: Validate cash date vs QBO deposit
- **Mapping**: Payout → QBO deposit reconciliation
- **Dates**: Payout date, cash availability date

## Technical Architecture

### Data Flow
```
Stripe Webhooks → [Processing Layer] → QBO API
                      ↓
                Link Tables (Idempotency)
                      ↓
               Observability Logs
```

### Components
- **Webhook Receiver**: Handle Stripe events
- **Processing Engine**: Transform and validate data
- **QBO Client**: API integration with rate limiting
- **Link Tables**: Stripe↔QBO ID mappings
- **Replay System**: Backfill historical data
- **Observability**: Structured logging and metrics

## Edge Cases & Considerations

### Known Edge Cases
- Partial payments and refunds
- Split deposits and payouts
- Failed webhook deliveries
- QBO API rate limits
- Customer record conflicts

### Idempotency Challenges
- Duplicate webhook events
- System restarts during processing
- Manual QBO modifications

## Non-Functional Requirements

### Performance
- Process webhooks within 30 seconds
- Handle peak load (TBD events/minute)
- Replay historical data efficiently

### Reliability
- 99.9% uptime for webhook processing
- Graceful handling of API failures
- Comprehensive error recovery

### Security
- GCP Secret Manager for all credentials
- No PII in logs (external IDs only)
- IAM least privilege principles

### Observability
- Structured logging with correlation IDs
- Metrics for success/failure rates
- Alerting for sync failures

## Acceptance Criteria

### Functional Tests
- [ ] Invoice creation matches Stripe data
- [ ] Payment linking works correctly
- [ ] Credits/refunds process appropriately
- [ ] Payout reconciliation validates dates

### Edge Case Validation
- [ ] Duplicate events handled idempotently
- [ ] Failed webhooks replay successfully
- [ ] API errors recover gracefully

### Performance Benchmarks
- [ ] Webhook processing < 30s average
- [ ] Replay completes within SLA
- [ ] No data loss during failures

## Backfill & Replay Strategy

### Initial Backfill
- Historical Stripe data ingestion
- QBO state validation
- Incremental processing with checkpoints

### Ongoing Replay
- Failed event reprocessing
- Manual trigger capability
- State consistency verification

## Risks & Mitigations

### High Risk Items
1. **AR Accuracy**: Incorrect mappings could affect financial reporting
   - Mitigation: Comprehensive testing, validation rules

2. **Idempotency Failures**: Duplicate entries in QBO
   - Mitigation: Robust link table design, transaction handling

3. **Date Inaccuracies**: Wrong dates affect reporting periods
   - Mitigation: Clear date mapping rules, validation

## Phase 2: Implementation Planning

### Artifacts to Generate
- OpenAPI specifications
- JSON Schemas for data validation
- BigQuery DDL for link tables
- Acceptance test skeletons
- API discovery plans

---

**Document Status**: DRAFT - Under collaboration with taz
**Last Updated**: November 1, 2025
**Collaborators**: Frankie + taz

