# Gmail MCP Server

Minimal, secure Gmail access via IMAP/SMTP with 1Password credential storage.

## Features

- **Multi-account support**: Use any Gmail account stored in 1Password
- **Secure credentials**: App passwords fetched from 1Password via `op` CLI
- **Full email operations**: List, read, send, and search emails
- **Minimal dependencies**: Only `mcp` package (uses stdlib for email)

## Setup

### 1. Install 1Password CLI

```bash
# macOS
brew install 1password-cli

# Authenticate
op signin
```

### 2. Create Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification if not already enabled
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Create a new app password for "Mail"

### 3. Store in 1Password

Create a 1Password item with:
- **Item name**: Your Gmail address (e.g., `user@gmail.com`)
- **Password field**: The app password from step 2

The item name MUST match your Gmail address exactly.

### 4. Enable in Claude Code

The plugin auto-loads from the marketplace. Verify with:
```bash
claude /mcp
```

## Tools

### list_emails

List recent emails from a folder.

```
account: user@gmail.com
folder: INBOX (optional)
limit: 10 (optional)
```

Returns: `[{id, from, subject, date, snippet}, ...]`

### read_email

Read full email content.

```
account: user@gmail.com
email_id: 123 (from list_emails)
```

Returns: `{from, to, subject, date, body}`

### send_email

Send an email.

```
account: user@gmail.com
to: recipient@example.com
subject: Hello
body: Email content here
cc: optional@example.com (optional)
bcc: hidden@example.com (optional)
```

Returns: Success/error message

### search_emails

Search using IMAP syntax.

```
account: user@gmail.com
query: FROM sender@example.com
folder: INBOX (optional)
limit: 10 (optional)
```

Common IMAP search queries:
- `FROM sender@example.com`
- `SUBJECT meeting`
- `UNSEEN` (unread)
- `SINCE 01-Jan-2024`
- `FROM john SUBJECT report` (AND)
- `OR FROM john FROM jane`

Returns: `[{id, from, subject, date}, ...]`

## Security Notes

- **Never stores credentials**: Passwords fetched on-demand from 1Password
- **Never logs credentials**: No password logging or caching
- **Uses App Passwords**: Not your main Google password
- **Requires op CLI auth**: Must run `op signin` before use
- **SSL/TLS only**: IMAP over SSL (993), SMTP with STARTTLS (587)

## Troubleshooting

### "Failed to get password for account"

- Verify 1Password item name matches your Gmail address exactly
- Run `op signin` to authenticate
- Check: `op item get "your@gmail.com" --fields password`

### "Authentication failed"

- Ensure you're using an App Password, not your main password
- Verify 2-Step Verification is enabled on Google account
- Check if "Less secure app access" needs to be enabled (legacy accounts)

### "Connection refused"

- Check firewall settings for ports 993 (IMAP) and 587 (SMTP)
- Verify Gmail IMAP/SMTP is enabled in Gmail settings
