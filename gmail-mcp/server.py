#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp"]
# ///
"""Gmail MCP server using IMAP/SMTP with 1Password for credentials.

Supports flexible 1Password item naming - extracts username from the item
rather than using the item name as the login credential.
"""

import asyncio
import email
import imaplib
import json
import os
import smtplib
import subprocess
from email import encoders
from email.header import decode_header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

server = Server("gmail")

# Gmail server settings
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL port


def get_credentials(item_name: str) -> dict:
    """Get username and password from 1Password item.

    This extracts the actual username field from the 1Password entry,
    allowing flexible item naming (e.g., "Gmail Work Claude" instead of
    requiring the item name to match the email address).
    """
    result = subprocess.run(
        ["op", "item", "get", item_name, "--format", "json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise ValueError(f"Failed to get 1Password item '{item_name}': {result.stderr.strip()}")

    item = json.loads(result.stdout)
    creds = {"username": None, "password": None}

    for field in item.get("fields", []):
        field_id = field.get("id", "")
        field_label = field.get("label", "").lower()
        if field_id == "username" or field_label == "username":
            creds["username"] = field.get("value")
        elif field_id == "password" or field_label == "password":
            creds["password"] = field.get("value")

    if not creds["username"] or not creds["password"]:
        raise ValueError(f"1Password item '{item_name}' missing username or password field")

    return creds


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


def connect_imap(item_name: str) -> tuple[imaplib.IMAP4_SSL, str]:
    """Connect to Gmail IMAP server. Returns (imap, username)."""
    creds = get_credentials(item_name)
    imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    imap.login(creds["username"], creds["password"])
    return imap, creds["username"]


def list_emails_impl(account: str, folder: str = "INBOX", limit: int = 10) -> list[dict]:
    """List recent emails from folder."""
    imap, _ = connect_imap(account)
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


def read_email_impl(account: str, email_id: str, folder: str = "INBOX") -> dict:
    """Read full email content."""
    imap, _ = connect_imap(account)
    try:
        imap.select(folder, readonly=True)
        _, msg_data = imap.fetch(email_id.encode(), "(RFC822)")
        if not msg_data or not msg_data[0]:
            raise ValueError(f"Email {email_id} not found")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract reply-to address
        from_header = decode_mime_header(msg.get("From"))
        if "<" in from_header and ">" in from_header:
            reply_to = from_header[from_header.index("<") + 1 : from_header.index(">")]
        else:
            reply_to = from_header

        return {
            "id": email_id,
            "from": from_header,
            "reply_to": reply_to,
            "to": decode_mime_header(msg.get("To")),
            "subject": decode_mime_header(msg.get("Subject")),
            "date": msg.get("Date", ""),
            "message_id": msg.get("Message-ID", ""),
            "references": msg.get("References", ""),
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
    attachments: list[str] | None = None,
) -> str:
    """Send email via SMTP."""
    creds = get_credentials(account)

    if attachments:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body, "plain", "utf-8"))
        for filepath in attachments:
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(filepath)
                part.add_header("Content-Disposition", f"attachment; filename={filename}")
                msg.attach(part)
    else:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body, "plain", "utf-8"))

    msg["From"] = creds["username"]
    msg["To"] = to
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    if cc:
        msg["Cc"] = cc

    recipients = [addr.strip() for addr in to.split(",")]
    if cc:
        recipients.extend(addr.strip() for addr in cc.split(","))
    if bcc:
        recipients.extend(addr.strip() for addr in bcc.split(","))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(creds["username"], creds["password"])
        smtp.send_message(msg, to_addrs=recipients)

    attachment_info = f" with {len(attachments)} attachment(s)" if attachments else ""
    return f"Email sent successfully to {to}{attachment_info}"


def reply_email_impl(
    account: str,
    email_id: str,
    body: str,
    attachments: list[str] | None = None,
    folder: str = "INBOX",
) -> str:
    """Reply to an email, maintaining the thread."""
    creds = get_credentials(account)

    # Get original email details for threading
    original = read_email_impl(account, email_id, folder)

    # Build references header (original references + original message-id)
    references = original["references"]
    if references and original["message_id"]:
        references = f"{references} {original['message_id']}"
    elif original["message_id"]:
        references = original["message_id"]

    # Prepare subject (add RE: if not present)
    subject = original["subject"]
    if not subject.upper().startswith("RE:"):
        subject = f"RE: {subject}"

    # Create message
    if attachments:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body, "plain", "utf-8"))
        for filepath in attachments:
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(filepath)
                part.add_header("Content-Disposition", f"attachment; filename={filename}")
                msg.attach(part)
    else:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body, "plain", "utf-8"))

    msg["From"] = creds["username"]
    msg["To"] = original["reply_to"]
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    if original["message_id"]:
        msg["In-Reply-To"] = original["message_id"]
    if references:
        msg["References"] = references

    # Send via SMTP
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(creds["username"], creds["password"])
        smtp.send_message(msg)

    attachment_info = f" with {len(attachments)} attachment(s)" if attachments else ""
    return f"Reply sent successfully to {original['reply_to']}{attachment_info}"


def search_emails_impl(
    account: str, query: str, folder: str = "INBOX", limit: int = 10
) -> list[dict]:
    """Search emails using IMAP search syntax."""
    imap, _ = connect_imap(account)
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
                    "account": {
                        "type": "string",
                        "description": "1Password item name containing Gmail credentials (username/password fields)",
                    },
                    "folder": {
                        "type": "string",
                        "description": "Folder to list (default: INBOX)",
                        "default": "INBOX",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max emails to return (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["account"],
            },
        ),
        Tool(
            name="read_email",
            description="Read full content of an email, including threading headers for reply",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "description": "1Password item name containing Gmail credentials",
                    },
                    "email_id": {"type": "string", "description": "Email ID from list_emails"},
                    "folder": {
                        "type": "string",
                        "description": "Folder containing the email (default: INBOX)",
                        "default": "INBOX",
                    },
                },
                "required": ["account", "email_id"],
            },
        ),
        Tool(
            name="send_email",
            description="Send a new email via Gmail SMTP (with optional attachments)",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "description": "1Password item name containing Gmail credentials",
                    },
                    "to": {"type": "string", "description": "Recipient email(s), comma-separated"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body (plain text)"},
                    "cc": {"type": "string", "description": "CC recipients, comma-separated"},
                    "bcc": {"type": "string", "description": "BCC recipients, comma-separated"},
                    "attachments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of absolute file paths to attach",
                    },
                },
                "required": ["account", "to", "subject", "body"],
            },
        ),
        Tool(
            name="reply_email",
            description="Reply to an email, maintaining the thread (with optional attachments)",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "description": "1Password item name containing Gmail credentials",
                    },
                    "email_id": {
                        "type": "string",
                        "description": "Email ID to reply to (from list_emails or read_email)",
                    },
                    "body": {"type": "string", "description": "Reply body (plain text)"},
                    "attachments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of absolute file paths to attach",
                    },
                    "folder": {
                        "type": "string",
                        "description": "Folder containing the email (default: INBOX)",
                        "default": "INBOX",
                    },
                },
                "required": ["account", "email_id", "body"],
            },
        ),
        Tool(
            name="search_emails",
            description="Search emails using IMAP syntax (e.g., FROM john, SUBJECT meeting, UNSEEN)",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "description": "1Password item name containing Gmail credentials",
                    },
                    "query": {
                        "type": "string",
                        "description": "IMAP search query (e.g., 'FROM sender@example.com', 'SUBJECT hello')",
                    },
                    "folder": {
                        "type": "string",
                        "description": "Folder to search (default: INBOX)",
                        "default": "INBOX",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default: 10)",
                        "default": 10,
                    },
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
            result = read_email_impl(
                arguments["account"],
                arguments["email_id"],
                arguments.get("folder", "INBOX"),
            )
        elif name == "send_email":
            result = send_email_impl(
                arguments["account"],
                arguments["to"],
                arguments["subject"],
                arguments["body"],
                arguments.get("cc"),
                arguments.get("bcc"),
                arguments.get("attachments"),
            )
        elif name == "reply_email":
            result = reply_email_impl(
                arguments["account"],
                arguments["email_id"],
                arguments["body"],
                arguments.get("attachments"),
                arguments.get("folder", "INBOX"),
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

        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
