# 1Password MCP Server

Minimal, secure MCP server for accessing 1Password credentials in Claude Code sessions.

## Security Model

- **Zero third-party dependencies** for credential handling
- All credential access goes through the **official 1Password CLI** (`op`)
- **Passwords are never returned** - they are copied directly to your clipboard
- Credentials are never logged or stored
- Requires explicit user authentication via `op signin`

## Prerequisites

1. Install the 1Password CLI from https://1password.com/downloads/command-line/
2. Authenticate with your 1Password account:
   ```bash
   op signin
   ```

## Usage

Once installed, the credential tools are available in Claude Code sessions:

```
Get credentials for github.com
```

The password is automatically copied to your clipboard - just paste it!

### Tool: find_credential (Primary)

**Arguments:**
- `url` (required): Website domain (e.g., 'github.com', 'linkedin.com')
- `username` (optional): Username/email to filter by
- `vault` (optional): Vault name or ID

**Returns:**
```json
{
  "item_name": "GitHub",
  "item_id": "abc123...",
  "username": "user@example.com",
  "password": "[COPIED TO CLIPBOARD - User can paste with Cmd+V / Ctrl+V]"
}
```

> **🔒 Security Note:** The password is **automatically copied to your clipboard** and never displayed or returned. Just paste it where needed!

### Tool: get_credential

**Arguments:**
- `item_name` (required): Exact 1Password item ID (not URL or guessed name)
- `vault` (optional): Vault name or ID to search in

**Returns:** Same format as `find_credential` - password copied to clipboard.

### Tool: list_items_for_url

**Arguments:**
- `url` (required): Website domain
- `vault` (optional): Vault name or ID

**Returns:** List of items with usernames (no passwords - use `find_credential` to get credentials).

## For AI Agents

When credentials are retrieved, **passwords are never returned in the response**. Instead:

1. The password is automatically copied to the user's system clipboard
2. The response includes `"password": "[COPIED TO CLIPBOARD - User can paste with Cmd+V / Ctrl+V]"`

**Your job as an agent:** Tell the user their password is ready to paste. Example responses:
- "I found your credentials. Your password is now in your clipboard - just paste it with Cmd+V (or Ctrl+V on Windows/Linux)."
- "Got it! The password for user@example.com has been copied. Paste it into the password field."

## Troubleshooting

| Error | Solution |
|-------|----------|
| `op not installed` | Install from https://1password.com/downloads/command-line/ |
| `Command timed out` | Run `op signin` to authenticate |
| `Item not found` | Check item name spelling or specify vault |
| `Clipboard error` | Ensure `pbcopy` (macOS), `xclip`/`xsel` (Linux), or `clip` (Windows) is available |

## Implementation Notes

- ~300 lines of auditable Python code
- Uses `op item get <item> --format json` under the hood
- Extracts fields with `purpose: USERNAME/PASSWORD` or `id: username/password`
- Cross-platform clipboard support: `pbcopy` (macOS), `xclip`/`xsel` (Linux), `clip.exe` (Windows)
