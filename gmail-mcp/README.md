# Gmail MCP Server

Secure Gmail access via IMAP/SMTP with 1Password credential storage. Supports flexible 1Password item naming, email threading, and attachments.

## Features

- **Flexible 1Password naming**: Use any item name (e.g., "Gmail Work Claude") - username extracted from item fields
- **Secure credentials**: App passwords fetched from 1Password via `op` CLI
- **Full email operations**: List, read, send, search, and reply to emails
- **Proper threading**: Reply emails maintain thread continuity via In-Reply-To/References headers
- **Attachment support**: Send and reply with file attachments
- **Standalone scripts**: CLI tools for use outside MCP

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
- **Item name**: Any descriptive name (e.g., "Gmail Work Claude")
- **username** field: Your Gmail address (e.g., `user@gmail.com`)
- **password** field: The app password from step 2

**Note:** Unlike the previous version, the item name no longer needs to match your email address. The plugin extracts the username from the item's fields.

### 4. Enable in Claude Code

The plugin auto-loads from the marketplace. Verify with:
```bash
claude /mcp
```

## MCP Tools

### list_emails

List recent emails from a folder.

```
account: "Gmail Work Claude"  # 1Password item name
folder: INBOX (optional)
limit: 10 (optional)
```

Returns: `[{id, from, subject, date, snippet}, ...]`

### read_email

Read full email content including threading headers.

```
account: "Gmail Work Claude"
email_id: "46" (from list_emails)
folder: INBOX (optional)
```

Returns: `{id, from, reply_to, to, subject, date, message_id, references, body}`

### send_email

Send an email with optional attachments.

```
account: "Gmail Work Claude"
to: recipient@example.com
subject: Hello
body: Email content here
cc: optional@example.com (optional)
bcc: hidden@example.com (optional)
attachments: ["/path/to/file.pdf"] (optional)
```

Returns: Success/error message

### reply_email

Reply to an email, maintaining the thread.

```
account: "Gmail Work Claude"
email_id: "46" (from list_emails or read_email)
body: "Thanks for your message!"
attachments: ["/path/to/doc.pdf"] (optional)
folder: INBOX (optional)
```

Returns: Success/error message

Threading is automatic:
- Sets `In-Reply-To` to original `Message-ID`
- Builds proper `References` header chain
- Adds `RE:` prefix to subject if needed
- Replies to sender's email address

### search_emails

Search using IMAP syntax.

```
account: "Gmail Work Claude"
query: FROM sender@example.com
folder: INBOX (optional)
limit: 10 (optional)
```

Common IMAP search queries:
- `FROM sender@example.com`
- `SUBJECT meeting`
- `UNSEEN` (unread)
- `SINCE 01-Jan-2024`
- `BODY "keyword"`
- `FROM john SUBJECT report` (AND)
- `OR FROM john FROM jane`

Returns: `[{id, from, subject, date}, ...]`

## Standalone CLI Scripts

Located in `skills/gmail-tools/scripts/`:

```bash
# List emails
./skills/gmail-tools/scripts/gmail_list.py "Gmail Work Claude" --limit 20

# Read email
./skills/gmail-tools/scripts/gmail_read.py "Gmail Work Claude" "46"

# Reply with attachment (dry run)
./skills/gmail-tools/scripts/gmail_reply.py "Gmail Work Claude" "46" \
  --body "Thanks!" --attachment ~/doc.pdf --dry-run

# Reply with attachment (send)
./skills/gmail-tools/scripts/gmail_reply.py "Gmail Work Claude" "46" \
  --body "Thanks!" --attachment ~/doc.pdf
```

## Security Notes

- **Never stores credentials**: Passwords fetched on-demand from 1Password
- **Never logs credentials**: No password logging or caching
- **Uses App Passwords**: Not your main Google password
- **Requires op CLI auth**: Must run `op signin` before use
- **SSL only**: IMAP over SSL (993), SMTP over SSL (465)

## Troubleshooting

### "1Password item not found"

- Verify the exact item name you're using
- Run `op item list | grep -i gmail` to find items
- Check: `op item get "Gmail Work Claude" --format json`

### "Authentication failed"

- Ensure you're using an App Password, not your main password
- Verify 2-Step Verification is enabled on Google account
- Check that the username field in 1Password is your full Gmail address

### "IMAP not enabled"

- Enable IMAP in Gmail Settings → Forwarding and POP/IMAP → Enable IMAP

### "Connection refused"

- Check firewall settings for ports 993 (IMAP) and 465 (SMTP)
- Verify Gmail IMAP/SMTP is enabled in Gmail settings
