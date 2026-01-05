#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp"]
# ///
"""Minimal Gmail MCP server using IMAP/SMTP with 1Password for credentials."""

import asyncio
import email
import imaplib
import smtplib
import subprocess
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, parseaddr

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

server = Server("gmail")

# Gmail server settings
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def get_password(account: str) -> str:
    """Get app password from 1Password using account email as item name."""
    result = subprocess.run(
        ["op", "item", "get", account, "--fields", "password"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise ValueError(f"Failed to get password for {account}: {result.stderr.strip()}")
    return result.stdout.strip()


def decode_mime_header(header: str | None) -> str:
    """Decode MIME encoded header to string."""
    if not header:
        return ""
    decoded_parts = decode_header(header)
    result = []
    for data, charset in decoded_parts:
        if isinstance(data, bytes):
            result.append(data.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(data)
    return "".join(result)


def get_email_body(msg: email.message.Message) -> str:
    """Extract text body from email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
        # Fallback to HTML if no plain text
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
    return ""


def connect_imap(account: str) -> imaplib.IMAP4_SSL:
    """Connect to Gmail IMAP server."""
    password = get_password(account)
    imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    imap.login(account, password)
    return imap


def list_emails_impl(account: str, folder: str = "INBOX", limit: int = 10) -> list[dict]:
    """List recent emails from folder."""
    imap = connect_imap(account)
    try:
        imap.select(folder, readonly=True)
        _, data = imap.search(None, "ALL")
        email_ids = data[0].split()
        email_ids = email_ids[-limit:] if email_ids else []
        email_ids.reverse()  # Most recent first

        results = []
        for eid in email_ids:
            _, msg_data = imap.fetch(eid, "(RFC822.HEADER BODY.PEEK[TEXT]<0.200>)")
            if not msg_data or not msg_data[0]:
                continue
            header_data = msg_data[0][1] if isinstance(msg_data[0], tuple) else b""
            msg = email.message_from_bytes(header_data)
            snippet = ""
            if len(msg_data) > 1 and msg_data[1] and isinstance(msg_data[1], tuple):
                snippet_bytes = msg_data[1][1] if len(msg_data[1]) > 1 else b""
                snippet = snippet_bytes.decode("utf-8", errors="replace")[:100]

            results.append({
                "id": eid.decode(),
                "from": decode_mime_header(msg.get("From")),
                "subject": decode_mime_header(msg.get("Subject")),
                "date": msg.get("Date", ""),
                "snippet": snippet.replace("\n", " ").strip(),
            })
        return results
    finally:
        imap.logout()


def read_email_impl(account: str, email_id: str) -> dict:
    """Read full email content."""
    imap = connect_imap(account)
    try:
        imap.select("INBOX", readonly=True)
        _, msg_data = imap.fetch(email_id.encode(), "(RFC822)")
        if not msg_data or not msg_data[0]:
            raise ValueError(f"Email {email_id} not found")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        return {
            "from": decode_mime_header(msg.get("From")),
            "to": decode_mime_header(msg.get("To")),
            "subject": decode_mime_header(msg.get("Subject")),
            "date": msg.get("Date", ""),
            "body": get_email_body(msg),
        }
    finally:
        imap.logout()


def send_email_impl(
    account: str,
    to: str,
    subject: str,
    body: str,
    cc: str | None = None,
    bcc: str | None = None,
) -> str:
    """Send email via SMTP."""
    password = get_password(account)

    msg = MIMEMultipart()
    msg["From"] = account
    msg["To"] = to
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    if cc:
        msg["Cc"] = cc
    msg.attach(MIMEText(body, "plain"))

    recipients = [addr.strip() for addr in to.split(",")]
    if cc:
        recipients.extend(addr.strip() for addr in cc.split(","))
    if bcc:
        recipients.extend(addr.strip() for addr in bcc.split(","))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(account, password)
        smtp.send_message(msg, to_addrs=recipients)

    return f"Email sent successfully to {to}"


def search_emails_impl(
    account: str, query: str, folder: str = "INBOX", limit: int = 10
) -> list[dict]:
    """Search emails using IMAP search syntax."""
    imap = connect_imap(account)
    try:
        imap.select(folder, readonly=True)
        _, data = imap.search(None, query)
        email_ids = data[0].split()
        email_ids = email_ids[-limit:] if email_ids else []
        email_ids.reverse()

        results = []
        for eid in email_ids:
            _, msg_data = imap.fetch(eid, "(RFC822.HEADER)")
            if not msg_data or not msg_data[0]:
                continue
            header_data = msg_data[0][1] if isinstance(msg_data[0], tuple) else b""
            msg = email.message_from_bytes(header_data)
            results.append({
                "id": eid.decode(),
                "from": decode_mime_header(msg.get("From")),
                "subject": decode_mime_header(msg.get("Subject")),
                "date": msg.get("Date", ""),
            })
        return results
    finally:
        imap.logout()


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_emails",
            description="List recent emails from a Gmail account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string", "description": "Gmail address (must match 1Password item name)"},
                    "folder": {"type": "string", "description": "Folder to list (default: INBOX)", "default": "INBOX"},
                    "limit": {"type": "integer", "description": "Max emails to return (default: 10)", "default": 10},
                },
                "required": ["account"],
            },
        ),
        Tool(
            name="read_email",
            description="Read full content of an email",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string", "description": "Gmail address"},
                    "email_id": {"type": "string", "description": "Email ID from list_emails"},
                },
                "required": ["account", "email_id"],
            },
        ),
        Tool(
            name="send_email",
            description="Send an email via Gmail SMTP",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string", "description": "Gmail address to send from"},
                    "to": {"type": "string", "description": "Recipient email(s), comma-separated"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body (plain text)"},
                    "cc": {"type": "string", "description": "CC recipients, comma-separated"},
                    "bcc": {"type": "string", "description": "BCC recipients, comma-separated"},
                },
                "required": ["account", "to", "subject", "body"],
            },
        ),
        Tool(
            name="search_emails",
            description="Search emails using IMAP syntax (e.g., FROM john, SUBJECT meeting, UNSEEN)",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string", "description": "Gmail address"},
                    "query": {"type": "string", "description": "IMAP search query (e.g., 'FROM sender@example.com', 'SUBJECT hello')"},
                    "folder": {"type": "string", "description": "Folder to search (default: INBOX)", "default": "INBOX"},
                    "limit": {"type": "integer", "description": "Max results (default: 10)", "default": 10},
                },
                "required": ["account", "query"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "list_emails":
            result = list_emails_impl(
                arguments["account"],
                arguments.get("folder", "INBOX"),
                arguments.get("limit", 10),
            )
        elif name == "read_email":
            result = read_email_impl(arguments["account"], arguments["email_id"])
        elif name == "send_email":
            result = send_email_impl(
                arguments["account"],
                arguments["to"],
                arguments["subject"],
                arguments["body"],
                arguments.get("cc"),
                arguments.get("bcc"),
            )
        elif name == "search_emails":
            result = search_emails_impl(
                arguments["account"],
                arguments["query"],
                arguments.get("folder", "INBOX"),
                arguments.get("limit", 10),
            )
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
