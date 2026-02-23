# OpenClaw Gateway — Setup & Reference

> **Last updated:** 2026-02-22
> **Version:** OpenClaw 2026.2.20 (commit `72e937a`)
> **Host:** PrecisionDell (Windows 11 + WSL2 Ubuntu-22.04)

## Overview

OpenClaw (codename "moltbot") is an AI agent gateway that connects LLM models to messaging channels (Slack, etc.) with plugin support, voice capabilities, and a web UI. It runs **natively in WSL2** as a systemd user service.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Windows 11 (PrecisionDell)                              │
│  ┌────────────────────────────────────────────────────┐  │
│  │  WSL2 (Ubuntu-22.04)                               │  │
│  │                                                    │  │
│  │  systemd user service                              │  │
│  │  └─ openclaw-gateway.service                       │  │
│  │     └─ node dist/index.js gateway --port 18789     │  │
│  │                                                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │  │
│  │  │ Slack    │  │ Web UI   │  │ Google           │ │  │
│  │  │ (Socket) │  │ :18789   │  │ Antigravity Auth │ │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘ │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## Key Paths

| What | Path |
|------|------|
| **Source code** | `/home/frank/moltbot/` |
| **Config file** | `/home/frank/.openclaw/openclaw.json` |
| **Environment** | `/home/frank/.openclaw/.env` |
| **Workspace** | `/home/frank/.openclaw/workspace/` |
| **Agent sessions** | `/home/frank/.openclaw/agents/main/sessions/` |
| **Credentials** | `/home/frank/.openclaw/credentials/` |
| **Systemd unit** | `~/.config/systemd/user/openclaw-gateway.service` |
| **Extensions** | `/home/frank/moltbot/extensions/` |
| **Plugin SDK types** | `/home/frank/moltbot/dist/plugin-sdk/` |
| **Node binary** | `/home/linuxbrew/.linuxbrew/Cellar/node/25.5.0/bin/node` |

---

## Remote Access (from Windows / AI Agents)

> **Critical:** OpenClaw runs in WSL2, not native Windows. SSH to `PrecisionDell` will fail
> (port 22 is not open). Use `wsl -e` to run commands from PowerShell.

### Running commands in WSL from Windows

```powershell
# Simple commands — use wsl -e directly
wsl -e grep -n "bind" /home/frank/.openclaw/openclaw.json
wsl -e systemctl --user status openclaw-gateway.service --no-pager

# Commands needing a login shell (for PATH, env vars)
wsl -e bash -lc "openclaw doctor"

# Reading files
wsl -e cat /home/frank/.openclaw/openclaw.json
```

### ⚠️ PowerShell Escaping Gotcha

PowerShell mangles quotes when passed through `wsl -e bash -c "..."`. Inline `sed` commands with double quotes will break silently or produce syntax errors.

**Don't do this** (fails due to PowerShell quote stripping):
```powershell
wsl -e bash -c "sed -i 's/\"old\"/\"new\"/' /path/to/file"  # BROKEN
```

**Do this instead** — use `wsl -e` without bash wrapper, or use Python:
```powershell
# Option 1: wsl -e sed directly (no bash -c wrapper)
wsl -e sed -i 's/"old"/"new"/' /path/to/file

# Option 2: Python for reliable JSON edits (recommended for config)
wsl -e python3 -c "
import json
with open('/home/frank/.openclaw/openclaw.json') as f:
    config = json.load(f)
config['gateway']['bind'] = 'loopback'
with open('/home/frank/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)
"
```

### Filesystem Cross-Reference

| From | Path |
|------|------|
| WSL → Windows | `/mnt/c/Users/frank/...` |
| Windows → WSL | `\\wsl$\Ubuntu-22.04\home\frank\...` |
| PowerShell → WSL command | `wsl -e <command>` |

---

## Configuration Summary

See [config-reference.md](config-reference.md) for the full annotated config.

### Authentication
- **Provider:** Google Antigravity (OAuth) — also Google AI direct
- **User:** `frankie@wescope.com`
- **LLM Model:** `google/gemini-3.1-pro-preview` (primary, via Google AI API)
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
- `google-antigravity-auth` — OAuth authentication
- `slack` — Slack channel integration

---

## Common Operations

### Start / Stop / Restart Gateway

```bash
# Via openclaw CLI (preferred)
openclaw gateway start
openclaw gateway stop

# Via systemd directly
systemctl --user start openclaw-gateway.service
systemctl --user stop openclaw-gateway.service
systemctl --user restart openclaw-gateway.service
```

### View Logs

```bash
# Recent logs
journalctl --user -u openclaw-gateway.service --no-pager -n 50

# Follow live
journalctl --user -u openclaw-gateway.service -f

# Filter for errors
journalctl --user -u openclaw-gateway.service --no-pager | grep -i 'error\|warn'
```

### Check Status

```bash
# Service status
systemctl --user status openclaw-gateway.service

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
f = '/home/frank/.openclaw/openclaw.json'
c = json.load(open(f))
for k in ['audio', 'tts']:
    c.pop(k, None)
json.dump(c, open(f, 'w'), indent=2)
"
systemctl --user restart openclaw-gateway.service
```

> **Warning:** `openclaw doctor` updates can sometimes re-inject invalid keys.
> Always check logs after an update.

### Gateway config invalid — `gateway.bind: Invalid input`

The `gateway.bind` field has **strict schema validation**. Only specific values are accepted.

| Value | Meaning |
|-------|----------|
| `"loopback"` | Bind to `127.0.0.1` only (recommended) |
| `"all"` | ❌ **Invalid** — will crash the gateway |
| `"0.0.0.0"` | ❌ **Invalid** — will crash the gateway |

When this happens, the CLI is **completely unusable** — every command (including `openclaw config set` and `openclaw doctor --fix`) will fail with the same validation error.

**Fix** (must edit JSON directly since CLI is broken):
```powershell
# From Windows PowerShell — use Python for reliable JSON editing
wsl -e python3 -c "
import json
f = '/home/frank/.openclaw/openclaw.json'
c = json.load(open(f))
c['gateway']['bind'] = 'loopback'
json.dump(c, open(f, 'w'), indent=2)
print('Fixed: gateway.bind set to loopback')
"

# Then restart
wsl -e bash -lc "systemctl --user restart openclaw-gateway.service"
```

### Gateway crash loop

```bash
# Check restart counter
systemctl --user status openclaw-gateway.service

# Read crash reason
journalctl --user -u openclaw-gateway.service --no-pager -n 20

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
systemctl --user restart openclaw-gateway.service
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

Located at `/home/frank/moltbot/extensions/talk-voice/`. This is an ElevenLabs voice management plugin (list/set voices). Requires `talk.apiKey` to be configured.

> **Important:** Do NOT add `audio.stt`, `audio.tts`, or `tts` keys to `openclaw.json`.
> These will crash the gateway.

---

## Extensions

40+ extensions are available at `/home/frank/moltbot/extensions/`. Currently enabled:

| Extension | Status | Purpose |
|-----------|--------|---------|
| `google-antigravity-auth` | ✅ Enabled | OAuth for Google Antigravity |
| `slack` | ✅ Enabled | Slack channel integration |

Others available include: `discord`, `telegram`, `signal`, `whatsapp`, `memory-core`, `memory-lancedb`, `talk-voice`, `voice-call`, `copilot-proxy`, `diagnostics-otel`, etc.

To enable an extension:
```bash
openclaw plugins enable <name>
# Then add to plugins.allow in config
openclaw config set plugins.allow '["slack","google-antigravity-auth","<name>"]'
```

---

## Environment Variables

**File:** `/home/frank/.openclaw/.env`

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | API key for Google Gemini (used by Gemini CLI auth) |

The systemd service also sets:
- `OPENCLAW_GATEWAY_PORT=18789`
- `OPENCLAW_GATEWAY_TOKEN=<gateway auth token>`
- `OPENCLAW_SERVICE_VERSION=2026.2.18`

---

## Workspace ("Brain on Disk")

The agent workspace (`/home/frank/.openclaw/workspace/`) is TapBot's persistent "brain on disk." It lives locally inside WSL and **persists across restarts**, meaning the agent retains context, memory, and skills between sessions.

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

The workspace also holds scripts, temporary data, and downloads (e.g., audio files, Xactimate scripts). These live here unless explicitly moved to Windows.

### 🔗 Cross-Filesystem Access

Even though TapBot runs in Linux (WSL), it can access Windows files via `/mnt/c/Users/frank/...`. The pattern is:
- **Workspace** → internal logic, memory, and tools
- **Windows folders** (e.g., Desktop) → user-facing deliverables

---

## History

### Migration from Docker to Native WSL

The `archive/` directory contains the original Docker-based deployment approach:
- `docker-compose.yml` — Docker service definition (moltbot image)
- `docker-compose.override.yml` — Port overrides
- `enable_wsl_features.ps1` — Script to enable WSL features in Windows

The setup was migrated to **native WSL2 execution** with systemd for better performance and simpler management. The gateway now runs directly via `node` instead of inside a Docker container.
