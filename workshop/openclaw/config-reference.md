# OpenClaw Configuration Reference

> Annotated version of `~/.openclaw/openclaw.json` with explanations.
> Sensitive tokens are redacted.

```jsonc
{
  // Version tracking — updated automatically by openclaw doctor
  "meta": {
    "lastTouchedVersion": "2026.2.18"
  },

  // Authentication profiles for LLM providers
  "auth": {
    "profiles": {
      "google-antigravity:frankie@wescope.com": {
        "provider": "google-antigravity",  // Google's Antigravity platform
        "mode": "oauth",                   // OAuth flow (browser-based)
        "email": "frankie@wescope.com"
      }
    }
  },

  // Agent defaults — model selection and concurrency
  "agents": {
    "defaults": {
      "model": {
        "primary": "google-antigravity/gemini-3-pro-high"  // Default LLM
      },
      "workspace": "/home/frank/.openclaw/workspace",
      "memorySearch": {
        "enabled": true    // Enables semantic memory search across sessions
      },
      "maxConcurrent": 4   // Max concurrent agent runs
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
    "bind": "loopback",      // Only accessible from localhost
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
    "allow": [                 // Whitelist of allowed plugins
      "slack",
      "google-antigravity-auth"
    ],
    "entries": {               // Plugin-specific configs
      "google-antigravity-auth": { "enabled": true },
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
    "nativeSkills": "auto"     // Auto-detect native skills
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
