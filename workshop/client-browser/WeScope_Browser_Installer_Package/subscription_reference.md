# Subscription ID Reference

| ID | Name | Default Category | Notes |
|---|---|---|---|
| 2 | Tier 1 | LEGACY | Legacy Tiers |
| 3 | Tier 2 | LEGACY | Legacy Tiers |
| 4 | Tier 3 | LEGACY | Legacy Tiers |
| 5 | Tier 4 | LEGACY | Legacy Tiers |
| 8 | Large Loss | LEGACY | Legacy Tiers |
| 9 | Arc - Custom | LEGACY | Legacy Tiers |
| 12 | Essential | NEW | New Structure (Essential/Plus) |
| 13 | Plus | NEW | New Structure (Essential/Plus) |
| 14 | Pro | PRO | Pro Tier (Always PRO) |

## Logic Mapping
1. **PRO (Green)**: Subscription ID = 14
2. **KEY (Blue)**: If Client is 'Key Account' (Verified) AND not PRO.
3. **NEW (Dark Grey)**: Subscription ID = 12 or 13
4. **LEG (Light Grey)**: All other legacy IDs (2-9)