# 1Password MCP Server

Minimal, secure MCP server for accessing 1Password credentials in Claude Code sessions.

## Security Model

- **Zero third-party dependencies** for credential handling
- All credential access goes through the **official 1Password CLI** (`op`)
- Credentials are never logged or stored
- Requires explicit user authentication via `op signin`

## Prerequisites

1. Install the 1Password CLI from https://1password.com/downloads/command-line/
2. Authenticate with your 1Password account:
   ```bash
   op signin
   ```

## Usage

Once installed, the `get_credential` tool is available in Claude Code sessions:

```
Get credentials for "GitHub" from 1Password
```

### Tool: get_credential

**Arguments:**
- `item_name` (required): Name or ID of the 1Password item
- `vault` (optional): Vault name or ID to search in

**Returns:**
```json
{
  "username": "user@example.com",
  "password": "..."
}
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| `op not installed` | Install from https://1password.com/downloads/command-line/ |
| `Command timed out` | Run `op signin` to authenticate |
| `Item not found` | Check item name spelling or specify vault |

## Implementation Notes

- ~90 lines of auditable Python code
- Uses `op item get <item> --format json` under the hood
- Extracts fields with `purpose: USERNAME/PASSWORD` or `id: username/password`
