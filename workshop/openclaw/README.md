# OpenClaw Gateway — Setup & Reference

> **Last updated:** 2026-02-26
> **Version:** OpenClaw 2026.2.26
> **Last updated:** 2026-03-01
> **Version:** OpenClaw 2026.2.27
> **Host:** Mac Mini (macOS 26.3, Apple Silicon)
> **Migrated from:** PrecisionDell (Windows 11 + WSL2 Ubuntu-22.04) on 2026-02-26

## Overview

OpenClaw (codename "moltbot") is an AI agent gateway that connects LLM models to messaging channels (Slack, etc.) with plugin support, voice capabilities, and a web UI. It runs **natively on macOS** as a launchd user agent.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Mac Mini (macOS 26.3, Apple Silicon)                    │
│                                                          │
│  launchd user agent                                      │
│  └─ com.openclaw.gateway                                 │
│     └─ node dist/index.js gateway --port 18789           │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐       │
│  │ Slack    │  │ Web UI   │  │ Google AI         │       │
│  │ (Socket) │  │ :18789   │  │ (Gemini API)     │       │
│  └──────────┘  └──────────┘  └──────────────────┘       │
└──────────────────────────────────────────────────────────┘
```

---

## Key Paths

| What | Path |
|------|------|
| **Source code** | `/Users/frankie/moltbot/` |
| **Config file** | `/Users/frankie/.openclaw/openclaw.json` |
| **Environment** | `/Users/frankie/.openclaw/.env` |
| **Workspace** | `/Users/frankie/.openclaw/workspace/` |
| **Agent sessions** | `/Users/frankie/.openclaw/agents/main/sessions/` |
| **Credentials** | `/Users/frankie/.openclaw/credentials/` |
| **LaunchAgent plist** | `~/Library/LaunchAgents/com.openclaw.gateway.plist` |
| **Extensions** | `/Users/frankie/moltbot/extensions/` |
| **Plugin SDK types** | `/Users/frankie/moltbot/dist/plugin-sdk/` |
| **Node binary** | `/opt/homebrew/bin/node` (v25.6.1) |
| **Service logs** | `/tmp/openclaw-gateway.stdout.log`, `/tmp/openclaw-gateway.stderr.log` |

---

## Remote Access (from PrecisionDell / AI Agents)

> SSH is configured with passwordless key auth from PrecisionDell.

### SSH from PrecisionDell (PowerShell)

```powershell
# Quick access (uses ~/.ssh/config alias)
ssh macmini

# Run a command directly
ssh macmini "export PATH=/opt/homebrew/bin:/usr/bin:/bin:$PATH && openclaw models list"
```

### SSH Config (on PrecisionDell)

```
Host macmini
  HostName 192.168.1.246
  User frankie
  IdentityFile ~/.ssh/id_macmini
```

---

## Configuration Summary

See [config-reference.md](config-reference.md) for the full annotated config.

### Authentication
- **Provider:** Google Antigravity (OAuth) — also Google AI direct
- **User:** `frankie@wescope.com`
- **LLM Model:** `google/gemini-3.1-pro-preview` (primary, via Google AI API)
### Authentication & Model Fallback Chain
- **Provider:** Google AI Studio (Free Tier) + Google Antigravity (OAuth) + OpenAI Codex (OAuth)
- **User:** `frankie@wescope.com`
- **Primary Model:** `google/gemini-2.5-flash` (Free Tier — project: `openclaw-free-tier`)
- **Fallback 1:** `openai-codex/gpt-5.3-codex` (OAuth, no per-token cost)
- **Fallback 2:** `google/gemini-3.1-pro-preview` (Paid — project: `xano-fivetran-bq`, key: `OpenClaw_Paid_Fallback`)
- **Available Antigravity models:** `gemini-3-flash`, `gemini-3-pro-high`, `gemini-3-pro-low`, `claude-opus-4-6-thinking`, `claude-opus-4-6`, `claude-sonnet-4-5`, `gpt-oss-120b-medium`
- **Note:** See [model-registry-lag.md](model-registry-lag.md) for why the model may not be on the Antigravity provider

### Gateway
- **Port:** 18789 (loopback only)
- **Auth:** Token-based
- **Tailscale:** Off

### Slack Integration
- **Mode:** Socket Mode (no public webhook needed)
- **Workspace:** `wescopeworkspace.slack.com`
- **App ID:** `A0AC5M04WHF`
- **Bot user:** Responds in channel `C0ABQ8TTY21`
- **Slash command:** `/tap`
- **Policies:** `groupPolicy: allowlist`, `dmPolicy: allowlist`
- **Allowed user:** `U03CS6U0QEL` (Frankie)

### Plugins
- `slack` — Slack channel integration

---

## Common Operations

### Start / Stop / Restart Gateway

```bash
# Via openclaw CLI (preferred)
openclaw gateway start
openclaw gateway stop

# Via launchd directly
launchctl start com.openclaw.gateway
launchctl stop com.openclaw.gateway
# Restart = stop + start
launchctl stop com.openclaw.gateway && launchctl start com.openclaw.gateway
```

### View Logs

```bash
# Recent logs
tail -50 /tmp/openclaw-gateway.stderr.log

# Follow live
tail -f /tmp/openclaw-gateway.stderr.log

# Filter for errors
grep -i 'error\|warn' /tmp/openclaw-gateway.stderr.log
```

### Check Status

```bash
# Service status
launchctl list com.openclaw.gateway

# Process check
pgrep -f 'moltbot/dist/index.js gateway'

# Web UI health
curl -s http://127.0.0.1:18789/
```

### Update OpenClaw

```bash
openclaw doctor    # Interactive — offers to update from git, then validates config
```

### Edit Config

```bash
# Via CLI (recommended — validates schema)
openclaw config set <key> <value>
openclaw config get <key>

# Direct edit (caution — strict schema validation)
nano ~/.openclaw/openclaw.json
```

> **If the config is already broken**, the CLI will refuse to run (it validates on startup).
> You must edit the JSON file directly — see [Remote Access](#remote-access-from-windows--ai-agents).

---

## Troubleshooting

### Gateway won't start — "Unrecognized keys"

The config schema is **strict**. Any unknown root-level key will cause a hard crash.

**Common offenders:**
- `audio.stt` / `audio.tts` — these are NOT valid root-level keys
- `tts` — TTS config is internal, not user-editable at root level

**Fix:**
```bash
# Remove invalid keys
openclaw doctor --fix

# Or manually with Python
python3 -c "
import json
f = '/Users/frankie/.openclaw/openclaw.json'
c = json.load(open(f))
for k in ['audio', 'tts']:
    c.pop(k, None)
json.dump(c, open(f, 'w'), indent=2)
"
launchctl stop com.openclaw.gateway && launchctl start com.openclaw.gateway
```

> **Warning:** `openclaw doctor` updates can sometimes re-inject invalid keys.
> Always check logs after an update.

### Gateway config invalid — `gateway.bind: Invalid input`

The `gateway.bind` field has **strict schema validation**. Only specific values are accepted.

| Value | Meaning |
|-------|----------|
| `"loopback"` | Bind to `127.0.0.1` only (recommended for security) |
| `"lan"` | Bind to LAN IP (required for device pairing / VS Code extension) |
| `"all"` | ❌ **Invalid** — will crash the gateway |
| `"0.0.0.0"` | ❌ **Invalid** — will crash the gateway |

When this happens, the CLI is **completely unusable** — every command (including `openclaw config set` and `openclaw doctor --fix`) will fail with the same validation error.

**Fix** (must edit JSON directly since CLI is broken):
```bash
# Use Python for reliable JSON editing
python3 -c "
import json
f = '/Users/frankie/.openclaw/openclaw.json'
c = json.load(open(f))
c['gateway']['bind'] = 'loopback'
json.dump(c, open(f, 'w'), indent=2)
print('Fixed: gateway.bind set to loopback')
"

# Then restart
launchctl stop com.openclaw.gateway && launchctl start com.openclaw.gateway
```

### Gateway crash loop

```bash
# Check service status
launchctl list com.openclaw.gateway

# Read crash reason
tail -20 /tmp/openclaw-gateway.stderr.log

# Common causes:
# 1. Invalid config keys (see above)
# 2. Port already in use (lock timeout after 5000ms)
# 3. Missing module files after update (restart fixes this)
```

### Slack "missing_scope" warning

The gateway calls `users.info` using the **user token** (`xoxp-...`). If this token lacks `users:read`, you'll see:
```
[slack] user resolve failed; using config entries. Error: missing_scope
```

**Fix:** Add `users:read` to **User Token Scopes** (not Bot Token Scopes) in [api.slack.com/apps](https://api.slack.com/apps), reinstall the app, and update the token if it changed.

> The **bot token** (`xoxb-...`) has `users:read` and works fine.
> This warning is non-fatal — the gateway falls back to config entries.

### Model "Unknown" or "missing" after Antigravity upgrade

See **[model-registry-lag.md](model-registry-lag.md)** for the full write-up.

**Quick fix:** Switch to the Google AI direct provider:
```bash
openclaw config set agents.defaults.model.primary "google/gemini-3.1-pro-preview"
launchctl stop com.openclaw.gateway && launchctl start com.openclaw.gateway
```

---

## TTS / Voice Capabilities

### Supported TTS Providers

| Provider | API Key Required | Notes |
|----------|-----------------|-------|
| **Edge** | No (free) | Microsoft Edge TTS, works out of the box |
| **OpenAI** | Yes (`OPENAI_API_KEY`) | `gpt-4o-mini-tts`, `tts-1`, `tts-1-hd` |
| **ElevenLabs** | Yes (`talk.apiKey`) | Managed via `talk-voice` extension |

### TTS Configuration

TTS is configured at **runtime**, not in `openclaw.json`. Use slash commands in chat:
```
/tts on
/tts provider edge
```

### talk-voice Extension

Located at `/Users/frankie/moltbot/extensions/talk-voice/`. This is an ElevenLabs voice management plugin (list/set voices). Requires `talk.apiKey` to be configured.

> **Important:** Do NOT add `audio.stt`, `audio.tts`, or `tts` keys to `openclaw.json`.
> These will crash the gateway.

---

## Extensions

40+ extensions are available at `/Users/frankie/moltbot/extensions/`. Currently enabled:

| Extension | Status | Purpose |
|-----------|--------|---------|
| `slack` | ✅ Enabled | Slack channel integration |

Others available include: `discord`, `telegram`, `signal`, `whatsapp`, `memory-core`, `memory-lancedb`, `talk-voice`, `voice-call`, `copilot-proxy`, `diagnostics-otel`, etc.

To enable an extension:
```bash
openclaw plugins enable <name>
# Then add to plugins.allow in config
openclaw config set plugins.allow '["slack","<name>"]'
```

---

## Environment Variables

**File:** `/Users/frankie/.openclaw/.env`

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | API key for Google Gemini (used by Gemini CLI auth) |
**File:** `/Users/frankie/.openclaw/.env` and `~/.zshenv`

| Variable | Purpose | Set In |
|----------|---------|--------|
| `GEMINI_API_KEY` | API key for Google Gemini (used by Gemini CLI auth) | `.env` |
| `GEMINI_API_KEY_FREE` | Free-tier Gemini API key (project: `openclaw-free-tier`) | `~/.zshenv` |
| `OPENCLAW_MODEL_PRIMARY` | Primary model override | `~/.zshenv` |
| `OPENCLAW_MODEL_FALLBACKS` | Comma-separated fallback models | `~/.zshenv` |

The launchd service also sets:
- `OPENCLAW_GATEWAY_PORT=18789`
- `OPENCLAW_GATEWAY_TOKEN=<gateway auth token>`
- `GEMINI_API_KEY_FREE=<free tier key>`
- `OPENCLAW_MODEL_PRIMARY=google/gemini-2.5-flash`
- `OPENCLAW_MODEL_FALLBACKS=openai-codex/gpt-5.3-codex,google-antigravity/gemini-3.1-pro-preview`

---

## Workspace ("Brain on Disk")

The agent workspace (`/Users/frankie/.openclaw/workspace/`) is TapBot's persistent "brain on disk." It **persists across restarts**, meaning the agent retains context, memory, and skills between sessions.

### 🧠 Memory

| File / Path | Purpose |
|---|---|
| `MEMORY.md` | Long-term notes and accumulated knowledge |
| `memory/YYYY-MM-DD.md` | Daily logs of activity — what was done each session |

### 🪪 Identity & Persona

| File | Purpose |
|---|---|
| `IDENTITY.md` | Agent identity definition |
| `SOUL.md` | Agent personality / persona |
| `FRANKIE_PERSONA.soul` | Custom Frankie persona overlay |
| `USER.md` | User profile (about you) |
| `AGENTS.md` | Agent definitions |

### 🛠️ Skills & Tools

| Path | Purpose |
|---|---|
| `TOOLS.md` | Available tools documentation and local config |
| `skills/` | Custom tool integrations (e.g., Linear, GitHub, etc.) |

### 📂 Working Files

The workspace also holds scripts, temporary data, and downloads.

---

## History

### Local LLM Attempt (2026-02-28) — Failed, 16 GB Insufficient

> **Result:** Local models **do not work** on a 16 GB Mac Mini for OpenClaw's agent pipeline.
> A **32+ GB** machine is required for local model operation.

#### Why It Fails

OpenClaw's embedded agent prompt is very large (system instructions + all tools/skills + session history).
When Ollama loads a model, it auto-sizes the context window to fit the prompt. For `llama3.1:8b`,
this resulted in a **131K context window using 22 GB** — far exceeding 16 GB unified memory.

#### Models Tested

| Model | Size | Issue |
|---|---|---|
| `qwen2.5-coder:14b` | 9 GB (Q4_K_M) | Loaded as 14 GB in memory; Ollama hung, runner process wouldn't die |
| `qwen2.5-coder:7b` | 4.7 GB | Coding-only model returned `NO_REPLY` for casual chat; OpenClaw dropped the response |
| `qwen3:8b` | 5.2 GB | Thinking model put output in `reasoning` field, left `content` empty; OpenAI-compat API incompatible |
| `qwen3:30b-a3b` (MoE) | 18 GB | MoE requires all weights loaded; far too large for 16 GB |
| `llama3.1:8b` | 4.9 GB | Model itself fits, but 131K context allocation → 22 GB total; `fetch failed` after 5 min |
| `llama3.1-small` (custom 4K ctx) | 4.9 GB | Ollama ignored custom `num_ctx`; still loaded 131K context |

#### Key Learnings

1. **Model file size ≠ memory usage.** A 4.9 GB model can use 22 GB with a large context window.
2. **Ollama's OpenAI-compat API** has issues with Qwen3 thinking models (`content` vs `reasoning`).
3. **Coding-only models** (e.g., `qwen2.5-coder`) return `NO_REPLY` for conversational prompts.
4. **Ollama `num_ctx` in Modelfile** may be overridden by the client (OpenClaw) at request time.
5. **Stuck Ollama runner processes** survive `brew services restart`; require `pkill -9 -f "ollama runner"`.
6. **Minimum hardware for local OpenClaw:** Mac with **32 GB+ unified memory**, or use a cloud model API.

#### Current Model (cloud)

```
google/gemini-2.5-flash          (Free Tier, primary)
openai-codex/gpt-5.3-codex       (OAuth, fallback 1)
google/gemini-3.1-pro-preview    (Paid, fallback 2)
```

---

### Google Cloud Project Cleanup (2026-03-01)

> **Result:** Consolidated from 5 API keys across 3 projects down to 2 keys across 2 projects.

#### What Was Done

1. **Deleted projects:** `Frankie Moltbot` (`gen-lang-client-0492263578`) and `xanoslackapi` (`gen-lang-client-0967890067`) — zero usage, unnecessary billing.
2. **Deleted keys:** Two unused `Gemini-Live-Agent-Key-V3` keys from `xano-fivetran-bq`, plus the exposed `xanogemini` key.
3. **Created:** New free-tier project `OpenClaw Free Tier` with a dedicated API key for TapBot.
4. **Renamed:** `Openclaw_free` key → `OpenClaw_Paid_Fallback` for clarity.
5. **Security:** Exposed API key in `run_analysis.py` was replaced with `os.environ["GEMINI_API_KEY"]`, git history scrubbed via `filter-branch`, and force-pushed. The exposed key was deleted from Google AI Studio.
6. **Installed:** `gcloud` CLI via Homebrew, authenticated as `frankie@wescope.com`.

#### Current API Key Inventory

| Key Name | Project | Tier | Purpose |
|---|---|---|---|
| `Free Gemini API Key` | `openclaw-free-tier` | Free | TapBot primary model |
| `OpenClaw_Paid_Fallback` | `xano-fivetran-bq` | Paid (Tier 3) | TapBot last-resort fallback |

### Slack Streaming Duplicate Fix (2026-03-01)

> **Problem:** TapBot was sending every message twice in Slack.
> **Root cause:** `streaming: partial` + `nativeStreaming: true` caused OpenClaw to post an initial message and then edit it. With Gemini 2.5 Flash responding in ~1.6s, Slack rendered both as separate messages.
> **Fix:** Set `streaming: off` and `nativeStreaming: false`. Also cleared stale `delivery-queue` entries from old failed local model attempts.

---

### Migration from WSL2 to Mac Mini (2026-02-26)

The gateway was migrated from WSL2 Ubuntu-22.04 on PrecisionDell to a Mac Mini (Apple Silicon, macOS 26.3). Service management moved from systemd to launchd. See `implementation_plan.md` in the vidaFS repo for the full migration steps.

### Migration from Docker to Native WSL (earlier)

The `archive/` directory contains the original Docker-based deployment approach:
- `docker-compose.yml` — Docker service definition (moltbot image)
- `docker-compose.override.yml` — Port overrides
- `enable_wsl_features.ps1` — Script to enable WSL features in Windows
