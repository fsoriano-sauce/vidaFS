# Google Workspace Tools

Multi-account OAuth tools for accessing Google Workspace APIs (Gmail, Drive, Docs, Calendar, etc.) across both `frankie@wescope.com` and `frankie.soriano@gmail.com`.

## Setup

```bash
npm install googleapis
```

### Credentials (not committed)

Place these files in this directory (they are gitignored):

| File | Description |
|------|-------------|
| `client_secret.json` | OAuth client credentials for WeScope (GCP project: `xano-fivetran-bq`) |
| `client_secret_personal.json` | OAuth client credentials for Personal (GCP project: `frankie-personal-tools`) |
| `tokens.json` | Stored OAuth tokens for `frankie@wescope.com` |
| `tokens_personal.json` | Stored OAuth tokens for `frankie.soriano@gmail.com` |

## Tools

### `setup_multi_auth.js` — OAuth Token Manager
Handles authentication for both accounts. Supports:
- `node setup_multi_auth.js auth wescope` — Authenticate WeScope account
- `node setup_multi_auth.js auth personal` — Authenticate Personal account  
- `node setup_multi_auth.js status` — Check token health for both accounts

### `search_drive.js` — Google Drive Search
Searches Google Drive across both accounts. Uses AI-style keyword scoring to find files by name relevance. Supports searching trashed files and files shared with specific users.

### `search_gmail.js` — Gmail Search
Searches Gmail across both accounts using Gmail query syntax. Returns message metadata (subject, date, from, to) and snippets.

### `search_links.js` — Gmail Attachment & Link Finder
Searches Gmail for emails with attachments. Parses MIME parts to extract attachment filenames. Useful for finding shared documents sent via email.

## Scopes Granted

Both accounts have the following scopes:
- Gmail (read/modify/send)
- Calendar
- Drive
- Docs / Sheets / Slides
- Chat (readonly)
- Directory & Contacts (readonly)
- Tasks
- User profile info
