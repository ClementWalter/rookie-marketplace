#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp"]
# ///
"""1Password MCP server with URL-based credential lookup."""

import asyncio
import json
import subprocess
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("1password")

# Common domain aliases (sites that share credentials)
DOMAIN_ALIASES = {
    "x.com": ["x.com", "twitter.com"],
    "twitter.com": ["x.com", "twitter.com"],
}


def run_op(args: list[str]) -> tuple[bool, str]:
    """Execute op CLI command, return (success, output)."""
    try:
        result = subprocess.run(["op", *args], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return False, result.stderr.strip() or "Unknown error"
        return True, result.stdout
    except FileNotFoundError:
        return False, "op CLI not installed. Get it from https://1password.com/downloads/command-line/"
    except subprocess.TimeoutExpired:
        return False, "Timed out. Run `op signin` to authenticate."


def normalize_domain(url: str) -> str:
    """Extract domain from URL."""
    return url.lower().replace("https://", "").replace("http://", "").split("/")[0]


def extract_creds_from_item(item: dict) -> dict[str, str | None]:
    """Extract username/password from item dict."""
    username, password = None, None
    for f in item.get("fields", []):
        fid, purpose, val = f.get("id", ""), f.get("purpose", ""), f.get("value")
        if purpose == "USERNAME" or fid == "username":
            username = val
        elif purpose == "PASSWORD" or fid == "password":
            password = val
    return {"username": username, "password": password}


def extract_creds(item_json: str) -> dict[str, str | None]:
    """Extract username/password from op item JSON string."""
    try:
        item = json.loads(item_json)
    except json.JSONDecodeError:
        return {"error": "Failed to parse 1Password response"}
    return extract_creds_from_item(item)


def find_items_by_url(url: str, vault: str | None = None) -> list[dict]:
    """Find 1Password items matching a URL/domain."""
    cmd = ["item", "list", "--format", "json"]
    if vault:
        cmd.extend(["--vault", vault])

    success, output = run_op(cmd)
    if not success:
        return []

    try:
        items = json.loads(output)
    except json.JSONDecodeError:
        return []

    domain = normalize_domain(url)
    search_domains = DOMAIN_ALIASES.get(domain, [domain])

    matching = []
    for item in items:
        item_urls = item.get("urls", [])
        for url_entry in item_urls:
            href = url_entry.get("href", "").lower()
            for sd in search_domains:
                if sd in href:
                    matching.append(item)
                    break
            else:
                continue
            break

    return matching


def get_item_details(item_id: str) -> dict | None:
    """Get full item details by ID."""
    success, output = run_op(["item", "get", item_id, "--format", "json"])
    if not success:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return None


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_credential",
            description="Retrieve username and password for a 1Password item by name or ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_name": {"type": "string", "description": "Name or ID of the 1Password item"},
                    "vault": {"type": "string", "description": "Optional vault name or ID"},
                },
                "required": ["item_name"],
            },
        ),
        Tool(
            name="find_credential",
            description="Find credential by URL/domain and optionally filter by username. Use this when you know the website URL and/or username but not the 1Password item name. Handles domain aliases (e.g., x.com/twitter.com).",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Website URL or domain (e.g., 'twitter.com', 'https://github.com')"},
                    "username": {"type": "string", "description": "Optional username to filter results when multiple entries exist"},
                    "vault": {"type": "string", "description": "Optional vault name or ID"},
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="list_items_for_url",
            description="List all 1Password items matching a URL/domain. Shows item names and usernames. Useful to see available accounts before selecting one.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Website URL or domain"},
                    "vault": {"type": "string", "description": "Optional vault name or ID"},
                },
                "required": ["url"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_credential":
        item_name = arguments.get("item_name")
        if not item_name:
            return [TextContent(type="text", text="Error: item_name is required")]
        cmd = ["item", "get", item_name, "--format", "json"]
        if vault := arguments.get("vault"):
            cmd.extend(["--vault", vault])
        success, output = run_op(cmd)
        if not success:
            return [TextContent(type="text", text=f"Error: {output}")]
        creds = extract_creds(output)
        if "error" in creds:
            return [TextContent(type="text", text=f"Error: {creds['error']}")]
        return [TextContent(type="text", text=json.dumps(creds))]

    elif name == "find_credential":
        url = arguments.get("url")
        if not url:
            return [TextContent(type="text", text="Error: url is required")]
        username_filter = arguments.get("username", "").lower()
        vault = arguments.get("vault")

        items = find_items_by_url(url, vault)
        if not items:
            return [TextContent(type="text", text=f"No items found for URL: {url}")]

        # Get full details for each item and filter by username if specified
        candidates = []
        for item in items:
            details = get_item_details(item["id"])
            if not details:
                continue
            creds = extract_creds_from_item(details)
            item_username = (creds.get("username") or "").lower()

            if username_filter:
                if username_filter == item_username:
                    # Exact match - return immediately
                    return [TextContent(type="text", text=json.dumps({
                        "item_name": item.get("title"),
                        "item_id": item["id"],
                        **creds
                    }))]
            candidates.append({
                "item_name": item.get("title"),
                "item_id": item["id"],
                **creds
            })

        if not candidates:
            return [TextContent(type="text", text=f"No matching credentials found for URL: {url}" + (f" with username: {username_filter}" if username_filter else ""))]

        if len(candidates) == 1:
            return [TextContent(type="text", text=json.dumps(candidates[0]))]

        # Multiple matches - return list for user to choose
        return [TextContent(type="text", text=json.dumps({
            "message": f"Multiple items found for {url}. Specify username to filter.",
            "items": [{"item_name": c["item_name"], "username": c["username"]} for c in candidates]
        }))]

    elif name == "list_items_for_url":
        url = arguments.get("url")
        if not url:
            return [TextContent(type="text", text="Error: url is required")]
        vault = arguments.get("vault")

        items = find_items_by_url(url, vault)
        if not items:
            return [TextContent(type="text", text=f"No items found for URL: {url}")]

        # Get usernames for each item
        result = []
        for item in items:
            details = get_item_details(item["id"])
            username = None
            if details:
                creds = extract_creds_from_item(details)
                username = creds.get("username")
            result.append({
                "item_name": item.get("title"),
                "item_id": item["id"],
                "username": username
            })

        return [TextContent(type="text", text=json.dumps(result))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
