# Model Registry Lag — Antigravity vs OpenClaw

> **Last updated:** 2026-02-20
> **Affected versions:** OpenClaw ≤ 2026.2.20
> **GitHub Issues:** [#21875](https://github.com/moltbot/moltbot/issues/21875), [#21897](https://github.com/moltbot/moltbot/issues/21897)

## The Problem

When Google Antigravity deprecates a model (e.g., Gemini 3 Pro → Gemini 3.1 Pro), OpenClaw's **bundled model registry** doesn't update automatically. The registry is hardcoded in the source at `src/agents/models-config.providers.ts`.

This causes:
1. The agent returns: _"Gemini 3 Pro is no longer available. Please switch to Gemini 3.1 Pro."_
2. Setting the suggested model fails: _"Unknown model: google-antigravity/gemini-3.1-pro-high"_
3. `openclaw models list` shows the new model as `configured,missing`

### Why It Happens

- The `google-antigravity` model list is **static** — baked into the OpenClaw release.
- OpenClaw has a **forward-compat** system (`model-forward-compat.ts`) that handles upgrades, but it **only covers Anthropic models** (Opus 4.5→4.6, Sonnet 4→4.5).
- **No Gemini forward-compat resolver exists**, so every Gemini version bump breaks the agent until OpenClaw ships a new release.

### History

| Date | Event | Resolution |
|------|-------|------------|
| 2026-02-20 | Gemini 3 Pro deprecated → 3.1 Pro | Switched to `google/gemini-3.1-pro-preview` (direct API) |
| Earlier | Claude Opus 4.5 → 4.6 | Handled by forward-compat resolver + commit `48b0fd8d8` |

---

## How to Fix It

### Option 1: Switch to Google AI direct (recommended)

Bypass the Antigravity provider entirely and use the Google AI API, which always has current model names:

```bash
# Set the model (replace with whatever the current Gemini version is)
openclaw config set agents.defaults.model.primary "google/gemini-3.1-pro-preview"

# Restart
systemctl --user restart openclaw-gateway.service

# Verify
openclaw models list
```

This uses the `GEMINI_API_KEY` in `~/.openclaw/.env`. Confirm it's set:
```bash
grep GEMINI_API_KEY ~/.openclaw/.env
```

### Option 2: Use an Antigravity Claude model (fallback)

Anthropic models on Antigravity are reliably available because they have forward-compat resolvers:

```bash
openclaw config set agents.defaults.model.primary "google-antigravity/claude-opus-4-6-thinking"
systemctl --user restart openclaw-gateway.service
```

### Option 3: Wait for OpenClaw update

Check for upstream fixes:
```bash
cd /home/frank/moltbot
git fetch
git log --oneline origin/main..HEAD   # See if you're behind
openclaw doctor                        # Interactive update + validation
```

After updating, switch back to the new Antigravity model:
```bash
openclaw config set agents.defaults.model.primary "google-antigravity/gemini-3.1-pro-high"
systemctl --user restart openclaw-gateway.service
openclaw models list   # Should NOT show "missing"
```

---

## How to Diagnose

```bash
# 1. Check current model status
openclaw models list
# Look for "missing" tag — means model not in registry

# 2. See all available models for a provider
openclaw models list --all | grep google-antigravity

# 3. Check logs for model errors
journalctl --user -u openclaw-gateway.service --no-pager | grep -i 'unknown model\|missing\|deprecated'

# 4. Check current config
openclaw config get agents.defaults.model.primary
```

---

## Source Code References

| File | Purpose |
|------|---------|
| `src/agents/models-config.providers.ts` | Static model definitions per provider |
| `src/agents/model-forward-compat.ts` | Forward-compat resolvers (Anthropic only) |
| `src/agents/model-catalog.ts` | Reads `models.json` from agent dir |
| `src/agents/pi-model-discovery.ts` | ModelRegistry wrapper from `@mariozechner/pi-coding-agent` |
