# vidaFS - WeScope Agentic Co-Collaborator Workspace

Welcome to **vidaFS** - Frankie's workspace for AI-assisted project development at WeScope.

## Project Structure

```
vidaFS/
├── workshop/                      # Active development projects
│   ├── stripe-qbo-sync/          # Stripe → QuickBooks integration
│   │   ├── docs/                 # Project documentation
│   │   └── specs/                # Specifications and mappings
│   ├── docs/                     # General workshop documentation
│   ├── notes/                    # Session notes
│   └── specs/                    # General specifications
│
├── context_read-only/            # Read-only reference code
│   └── xano-wescope/             # XanoScript codebase (local reference)
│       ├── docs/                 # XanoScript documentation (committed)
│       ├── specs/                # System catalogs (committed)
│       └── [apis/, functions/, etc.] # XanoScript code (local only)
│
└── README.md
```

## Current Projects

### Stripe → QuickBooks Integration
**Location:** `workshop/stripe-qbo-sync/`

Automating the invoice sync from Stripe to QuickBooks Online. Key deliverables:
- **PROPOSAL_FOR_LOGAN.md** - Integration proposal for head developer review
- **FINAL_SYSTEM_MAPPING.md** - Field mappings across Xano/Stripe/QBO
- **PRINCESS_CUSTOMER_MAPPING.csv** - Customer reconciliation data for AR/AP specialist
- System catalogs for all three platforms

**Status:** Analysis complete, awaiting Logan's review

## Working with taz

**taz** is your AI co-collaborator. Key capabilities:
- Reference XanoScript code examples from `context_read-only/`
- Analyze system integrations and data flows
- Create documentation and specifications
- Assist with BigQuery, Stripe, and QuickBooks analysis

**Example prompts:**
- "Show me the Invoice function logic from xano-wescope"
- "Analyze the customer mapping for missing QBO IDs"
- "What's the data flow for Stripe invoice line items?"

## Git Configuration

- **Remote:** https://github.com/fsoriano-sauce/vidaFS.git
- **Branch:** main
- **Push Access:** Enabled (documentation only for context_read-only/)

### XanoScript Reference Code
The `context_read-only/xano-wescope/` directory contains 949 XanoScript files for reference. These files:
- Are available locally for AI context
- Contain production secrets (not pushed to GitHub)
- Have read-only git configuration (pushurl=DISABLED)
- Can be updated via `git pull` for latest reference code

## Getting Started

1. **Review active project:** `workshop/stripe-qbo-sync/docs/PROPOSAL_FOR_LOGAN.md`
2. **Check chat history:** `workshop/CHAT_HISTORY_RECOVERY.md` for context
3. **Ask taz questions** about XanoScript syntax, integration patterns, or business logic
