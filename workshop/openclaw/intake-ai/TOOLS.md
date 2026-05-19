# TOOLS.md - Intake AI

## WeScope Portal

- **URL**: https://portal.wescope.com/control-center
- **API Base**: `https://api.wescope.com/api:DCl68q1L:live`
- **Auth**: Bearer token from browser `localStorage.AuthToken` after login

### Login

**Always use the login script — do not attempt manual login:**
```bash
/Users/frankie/.openclaw/workspace/skills/wescope-login.sh
```
After login succeeds, extract the auth token:
```bash
AUTH=$(agent-browser storage local AuthToken)
```

### 1Password CLI

`op` runs as a service account — **requires `--vault` flag**:
```bash
op item get d3vcoqfnfzoddly4e44ktyuidi --fields password --vault "Frankie - WeScope Admin" --reveal
op item get d3vcoqfnfzoddly4e44ktyuidi --otp --vault "Frankie - WeScope Admin"
```

### API Endpoints

```bash
# List all intake items (paginated, 300/page)
curl -s -H "Authorization: Bearer $AUTH" \
  "https://api.wescope.com/api:DCl68q1L:live/intake/new-home?inbox_id=-1&type=&status=&page=1&orderBy=asc"

# Archive an item (PATCH)
curl -s -X PATCH -H "Authorization: Bearer $AUTH" -H "Content-Type: application/json" \
  -d '{"Status":"Archived","Last_Updated_By":2}' \
  "https://api.wescope.com/api:36yU9h93:live/intake/{id}"
```

- Frankie's `user_id` = **2** (always use for `Last_Updated_By`)
- Total ~480 items across 2 pages

### Key References (in main workspace)

These files contain classification logic and learned patterns:
- **Framework**: `/Users/frankie/.openclaw/workspace/wescope/INTAKE-TRIAGE-FRAMEWORK.md`
- **Classification Guide**: `/Users/frankie/.openclaw/workspace/wescope/intake-classification-guide.md`
- **Audit Log**: `/Users/frankie/.openclaw/workspace/wescope/portal-actions.log`
- **Prior Candidates**: `/Users/frankie/.openclaw/workspace/wescope/high-confidence-archive-candidates.json`
