#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "rich"]
# ///
"""
VibeKanban Task Monitor - Direct API polling.

Usage:
    ./monitor-tasks.py --project "Stark V" --interval 600
"""

import argparse
import time
import sys
from datetime import datetime
from pathlib import Path

import httpx
from rich.console import Console
from rich.table import Table

console = Console()

# VibeKanban local API (MCP server must be running)
VK_API_BASE = "http://localhost:62350"

KNOWN_PROJECTS = {
    "Stark V": "1f96600e-a01a-4afa-a123-7586b080de92",
    "Gateway V2": "4e1f8355-73e7-429a-8fa0-4925bcce8e04",
    "fhevm": "3bdd6e49-46a2-4095-b355-9a9d95776cdd",
    "rookie-marketplace": "4960ca4a-5481-46fb-9702-cc84928c79aa",
}

LOG_FILE = Path.home() / ".claude" / "task-monitor.log"


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    console.print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def fetch_tasks(project_id: str) -> list:
    """Fetch tasks from VibeKanban API."""
    try:
        resp = httpx.get(f"{VK_API_BASE}/api/tasks", params={"project_id": project_id}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("success"):
            return data.get("data", [])
        else:
            log(f"API error: {data.get('message', 'Unknown')}")
            return []
    except httpx.ConnectError:
        log("ERROR: Cannot connect to VibeKanban. Is 'npx vibe-kanban --mcp' running?")
        return []
    except Exception as e:
        log(f"ERROR: {e}")
        return []


def display_status(tasks: list):
    if not tasks:
        log("No tasks found")
        return

    table = Table(title="Task Status")
    table.add_column("Status", style="cyan", width=12)
    table.add_column("Title", style="white", max_width=50)
    table.add_column("ID", style="dim", width=8)
    table.add_column("Agent", style="yellow", width=6)

    status_emoji = {
        "todo": "📋",
        "inprogress": "⏳",
        "inreview": "🔍",
        "done": "✅",
        "cancelled": "❌",
    }

    for task in tasks:
        status = task.get("status", "unknown")
        emoji = status_emoji.get(status, "❓")
        agent = "Yes" if task.get("has_in_progress_attempt") else "-"
        table.add_row(
            f"{emoji} {status}",
            task.get("title", "?")[:50],
            task.get("id", "?")[:8],
            agent,
        )

    console.print(table)

    # Summary
    counts = {}
    for t in tasks:
        s = t.get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1

    summary = ", ".join(f"{v} {k}" for k, v in counts.items())
    log(f"Summary: {summary}")


def main():
    parser = argparse.ArgumentParser(description="Monitor VibeKanban tasks")
    parser.add_argument("--project", help="Project name (e.g., 'Stark V')")
    parser.add_argument("--project-id", help="Project UUID")
    parser.add_argument("--interval", type=int, default=600, help="Poll interval in seconds (default: 600)")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    project_id = args.project_id
    if not project_id and args.project:
        project_id = KNOWN_PROJECTS.get(args.project)
        if not project_id:
            console.print(f"[red]Unknown project: {args.project}[/red]")
            console.print(f"Known: {list(KNOWN_PROJECTS.keys())}")
            sys.exit(1)

    if not project_id:
        console.print("[red]Specify --project or --project-id[/red]")
        sys.exit(1)

    log(f"Monitoring project {project_id}")
    log(f"Interval: {args.interval}s | Log: {LOG_FILE}")

    try:
        while True:
            log("--- Polling ---")
            tasks = fetch_tasks(project_id)
            display_status(tasks)

            if args.once:
                break

            log(f"Next check in {args.interval}s...")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        log("Stopped")


if __name__ == "__main__":
    main()
