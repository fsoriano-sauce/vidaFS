# OpenClaw Configuration Reference

> Annotated version of `~/.openclaw/openclaw.json` with explanations.
> Sensitive tokens are redacted.
> **Host:** Mac Mini (macOS 26.3, Apple Silicon) — updated 2026-02-26

```jsonc
{
  // Version tracking — updated automatically by openclaw doctor
  "meta": {
    "lastTouchedVersion": "2026.2.20"
  },

  // Authentication profiles for LLM providers
  "auth": {
    "profiles": {
      "google-antigravity:frankie@wescope.com": {
        "provider": "google-antigravity",  // Google's Antigravity platform
        "mode": "oauth",
        "email": "frankie@wescope.com"
      },
      "openai-codex:default": {
        "provider": "openai-codex",        // OpenAI Codex provider
        "mode": "oauth"
      }
    }
  },

  // Agent defaults — model selection and concurrency
  "agents": {
    "defaults": {
      "model": {
        "primary": "openai-codex/gpt-5.3-codex"  // Current default LLM
      },
      "models": {
        "openai-codex/gpt-5.3-codex": {}         // Model-specific overrides (empty = defaults)
      },
      "workspace": "/Users/frankie/.openclaw/workspace",
      "memorySearch": {
        "enabled": true    // Enables semantic memory search across sessions
      },
      "maxConcurrent": 4   // Max concurrent agent runs
    }
  },

  // Web search tools
  "tools": {
    "web": {
      "search": {
        "enabled": true,
        "provider": "brave",       // Brave Search API
        "apiKey": "BSA1uma..."     // Brave API key (redacted)
      }
    }
  },

  // Messaging channels
  "channels": {
    "slack": {
      "mode": "socket",                    // Socket Mode (no public URL needed)
      "webhookPath": "/slack/events",      // Fallback webhook path
      "enabled": true,

      // Tokens (redacted) — manage at https://api.slack.com/apps
      "botToken": "xoxb-3407599763...",    // Bot User OAuth Token
      "appToken": "xapp-1-A0AC5M04...",   // App-Level Token (Socket Mode)
      "userToken": "xoxp-3407599763...",   // User OAuth Token
      "userTokenReadOnly": true,           // User token has limited scopes

      // Access control
      "groupPolicy": "allowlist",          // Only allowlisted users/channels
      "dmPolicy": "allowlist",
      "allowFrom": ["U03CS6U0QEL"],        // Frankie's Slack user ID

      // Channel-specific settings
      "channels": {
        "C0ABQ8TTY21": {                   // #tap channel
          "enabled": true,
          "requireMention": false,         // Responds without @mention
          "users": ["U03CS6U0QEL"]
        }
      }
    }
  },

  // Gateway server settings
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",      // Valid: "loopback" (localhost only) or "lan" (network-accessible). "all" is INVALID.
    "auth": {
      "mode": "token",
      "token": "cf468190..."  // Gateway auth token (for web UI / API)
    },
    "tailscale": {
      "mode": "off",          // Tailscale mesh networking disabled
      "resetOnExit": false
    }
  },

  // Skill installation settings
  "skills": {
    "install": {
      "nodeManager": "npm"    // Use npm for installing skill dependencies
    }
  },

  // Plugin management
  "plugins": {
    "enabled": true,
    "allow": ["slack"],       // Only Slack plugin enabled on Mac Mini
    "entries": {
      "slack": { "enabled": true }
    }
  },

  // Message handling
  "messages": {
    "ackReactionScope": "group-mentions"  // React to group mentions
  },

  // Command settings
  "commands": {
    "native": "auto",          // Auto-detect native commands
    "nativeSkills": "auto",    // Auto-detect native skills
    "restart": true            // Allow restart command
  },

  // Internal hooks (managed automatically, shown for reference)
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "boot-md": { "enabled": true },
        "bootstrap-extra-files": { "enabled": true },
        "command-logger": { "enabled": true },
        "session-memory": { "enabled": true }
      }
    }
  }
}
```

## Slack Token Types

| Token | Prefix | Purpose | Required Scopes |
|-------|--------|---------|-----------------|
| **Bot Token** | `xoxb-` | Bot actions (messages, reactions, user lookups) | `chat:write`, `users:read`, `channels:read`, etc. |
| **App Token** | `xapp-` | Socket Mode connection | `connections:write` |
| **User Token** | `xoxp-` | Actions as user (optional, read-only here) | `users:read`, `channels:history`, etc. |

## Config Schema Rules

> [!CAUTION]
> The config uses **strict schema validation**. Unknown keys cause a **hard crash**.

### Known Invalid Keys (DO NOT ADD)

- `audio` / `audio.stt` / `audio.tts` — Not a valid root key
- `tts` — TTS config is internal, not user-editable
- `wizard` — Managed automatically by `openclaw doctor`
- `hooks` — Managed automatically

### Modifying Config Safely

Always prefer the CLI:
```bash
openclaw config set <dotted.key> <value>
openclaw config get <dotted.key>
```

If editing JSON directly, validate with:
```bash
openclaw doctor
```

After config changes, restart the gateway:
```bash
launchctl stop com.openclaw.gateway && launchctl start com.openclaw.gateway
```
