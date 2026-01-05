#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp"]
# ///
"""Minimal 1Password MCP server using the official `op` CLI."""

import asyncio
import json
import subprocess
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("1password")


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


def extract_creds(item_json: str) -> dict[str, str | None]:
    """Extract username/password from op item JSON."""
    try:
        item = json.loads(item_json)
    except json.JSONDecodeError:
        return {"error": "Failed to parse 1Password response"}
    username, password = None, None
    for f in item.get("fields", []):
        fid, purpose, val = f.get("id", ""), f.get("purpose", ""), f.get("value")
        if purpose == "USERNAME" or fid == "username":
            username = val
        elif purpose == "PASSWORD" or fid == "password":
            password = val
    return {"username": username, "password": password}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [Tool(
        name="get_credential",
        description="Retrieve username and password for a 1Password item",
        inputSchema={
            "type": "object",
            "properties": {
                "item_name": {"type": "string", "description": "Name or ID of the 1Password item"},
                "vault": {"type": "string", "description": "Optional vault name or ID"},
            },
            "required": ["item_name"],
        },
    )]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "get_credential":
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
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


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
