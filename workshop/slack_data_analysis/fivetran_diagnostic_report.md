# Fivetran Slack Connector Diagnostic Report

## Summary
The Slack connector (`checked_correspondence`) experienced a **3-month outage** from September 9, 2025 to December 1, 2025.

## Timeline
- **April 10, 2025:** Connector created
- **July 25, 2025:** Last successful sync before outage (synced June/July data)
- **September 9, 2025:** **Connector failed** at 09:57 UTC
- **September 9 - November 30, 2025:** No successful syncs (83 days offline)
- **December 1, 2025:** Connector resumed at 07:02 UTC

## Impact
- **Missing Data:** August, September, October 2025 (0 messages in BigQuery)
- **Partial Data:** November 2025 (only 23 messages, likely from Dec 1st sync)
- **Investigation Blocked:** Cannot analyze Aug 4th incident for Zach/Ben

## Root Cause
The Fivetran API shows:
```json
"failed_at": "2025-09-09T09:57:17.707000Z"
```

However, the API does not expose:
- Error messages or failure reasons
- Detailed sync logs
- Whether the connector was manually paused

## Why No Backfill?
Fivetran's Slack connector **does not backfill historical data** when it reconnects after a failure. It only syncs forward from the reconnection point. This is a known limitation of the Slack API integration.

## Recommendations
1. **Check Fivetran Dashboard:** Log into https://fivetran.com/dashboard to view detailed error logs for Sept 9th.
2. **Enable Alerts:** Set up Fivetran email/Slack alerts for connector failures to catch issues faster.
3. **Manual Backfill:** If you need Aug-Oct data, you may need to:
   - Contact Fivetran support to request a historical re-sync
   - OR use Slack's export feature to manually import the missing months

## Current Status
✅ Connector is now healthy and syncing daily (1440 min frequency)
