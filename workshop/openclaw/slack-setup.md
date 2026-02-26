# OpenClaw Slack App Setup

> Reference for the Slack app configuration at [api.slack.com/apps](https://api.slack.com/apps)

## App Details

| Field | Value |
|-------|-------|
| **App ID** | `A0AC5M04WHF` |
| **Workspace** | `wescopeworkspace.slack.com` |
| **Bot User ID** | `B0ABQLS7C4W` |
| **Connection** | Socket Mode |
| **Slash Command** | `/tap` |
| **Allowed Channel** | `C0ABQ8TTY21` |
| **Allowed User** | `U03CS6U0QEL` (Frankie) |

## Required Bot Token Scopes

These scopes must be on the **Bot Token** (`xoxb-...`):

| Scope | Purpose |
|-------|---------|
| `chat:write` | Send messages |
| `channels:read` | List/read channels |
| `channels:history` | Read channel message history |
| `groups:read` | Read private channels |
| `groups:history` | Read private channel history |
| `im:read` | Read DM metadata |
| `im:history` | Read DM history |
| `mpim:read` | Read group DM metadata |
| `mpim:history` | Read group DM history |
| `users:read` | Look up user info |
| `reactions:write` | Add reactions to messages |
| `files:read` | Read shared files |

## Required User Token Scopes

These scopes must be on the **User Token** (`xoxp-...`):

| Scope | Purpose |
|-------|---------|
| `users:read` | Resolve user info (added 2026-02-19) |
| `channels:history` | Read channels as user |
| `channels:read` | List channels as user |
| `groups:read` | List private channels |
| `groups:history` | Read private channel history |
| `im:read` | Read DMs |
| `im:history` | Read DM history |
| `mpim:read` | Read group DMs |
| `mpim:history` | Read group DM history |
| `calls:read` | Read call info |

> [!NOTE]
> The user token is marked `userTokenReadOnly: true` — it should only have read scopes.
> If `users:read` is missing, you'll see a non-fatal `missing_scope` warning on startup.

## Required App-Level Token Scopes

The **App Token** (`xapp-...`) needs:

| Scope | Purpose |
|-------|---------|
| `connections:write` | Establish Socket Mode connection |

## Token Rotation

When you add/remove scopes in the Slack app settings:
1. **Reinstall** the app to the workspace
2. Copy the **new tokens** from the OAuth page
3. Update config:
   ```bash
   openclaw config set channels.slack.botToken "xoxb-NEW-TOKEN"
   openclaw config set channels.slack.userToken "xoxp-NEW-TOKEN"
   # App token usually stays the same unless regenerated
   ```
4. Restart gateway:
   ```bash
   launchctl stop com.openclaw.gateway && launchctl start com.openclaw.gateway
   ```
