# Intake AI - Memory

## Status
- **Created:** 2026-03-10
- **Items archived (total):** 112 (94 prior + 18 on 2026-02-23)
- **Audit log entries:** 170
- **Patterns swept:** XA, Claims Workspace, Alacrity

## Active Patterns

| Pattern | Source | Subject Match | Default |
|---------|--------|--------------|---------|
| XA (XactAnalysis) | Verisk | "Assignment Note/Status Has Been Updated on XactAnalysis" | ARCHIVE if no revision keywords |
| Claims Workspace | Sedgwick | "New: Claims Workspace" | ARCHIVE (notifications) |
| Alacrity | Nexxus | Various (see classification guide) | ON HOLD |

## Lessons Learned
- Asbestos abatement review items from WMU are NOT archivable
- Alacrity items on hold until workflow addressed
- "Upload repair assignment ASAP" and "ETA on MIT?" are follow-up/upload requests, NOT revisions
- Claims Workspace rejection notices are ACTIONABLE — do not auto-archive
- `Currently_Viewing_User_id` check: if another user is on it, SKIP

## Pending
- 10 XA revision-matched archives pending Frankie's approval
- 5 jobs needing revision tasks
- Alacrity workflow needs addressing before resuming that pattern
