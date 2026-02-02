---
description: Sync portal and xano reference repos before context-dependent work
---

# When to Use
Before starting any task that may reference:
- Portal codebase (frontend, components, API routes)
- Xano configurations (database schemas, workflows, API endpoints)

# Steps

// turbo
1. Pull latest portal repo:
```bash
cd c:\Users\frank\OneDrive\Desktop\vidaFS\context_read-only\portal && git pull
```

// turbo
2. Pull latest xano-wescope repo:
```bash
cd c:\Users\frank\OneDrive\Desktop\vidaFS\context_read-only\xano-wescope && git pull
```

3. Continue with the requested task using up-to-date references.

# Notes
- These are read-only reference copies, not for direct editing
- If pull fails, check for uncommitted changes or network issues
