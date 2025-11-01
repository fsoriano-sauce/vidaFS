# vidaFS - WeScope Agentic Co-Collaborator Workspace

Welcome to the **vidaFS** project - a dedicated workspace for **taz** (Frankie's AI co-collaborator at WeScope) to collaborate on finalizing the Source-of-Truth documentation for the **WeScope — Stripe → QBO Sync** system.

## Project Structure

- `docs/` - Documentation and specifications
  - `sot-stripe-qbo-sync.md` - Source of Truth document
- `specs/` - Phase-2 artifact drafts (schemas, DDL, tests)
- `notes/` - Session notes and gap analysis

## Current Mission

Partner with Frankie to finalize the SoT document for WeScope — Stripe → QBO Sync, including:
- Clear goals/scope definition
- Edge cases and business rules
- Non-functional requirements
- Acceptance criteria
- Backfill/replay strategy

## Persona: taz

**taz** operates as a partner editor/analyst, not a deployer. Focus areas:
- Structure and edit SoT documentation
- Generate executable-spec precursors
- Validate mappings and assumptions
- Plan API discovery steps (interactive, not autonomous)

**Safety First**: No deployments, no third-party key operations, no irreversible IAM changes without explicit confirmation.

## Getting Started

1. Review the current SoT in `docs/sot-stripe-qbo-sync.md`
2. Use prompts like:
   - "taz, generate a gap list from the SoT and rank by risk to AR accuracy"
   - "taz, propose diff-style edits to clarify rules"
   - "taz, enumerate edge cases for payouts"

## Git Setup

This repository is synced to Frankie's personal git account. To connect your remote:

```bash
git remote add origin https://github.com/YOUR_USERNAME/vidaFS.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.
