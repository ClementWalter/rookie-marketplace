#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "rich"]
# ///
"""
VibeKanban Task Monitor - Polls task status every N minutes.

Usage:
    ./monitor-tasks.py --project "Stark V" --interval 600
"""

import argparse
import subprocess
import time
import json
import sys
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

KNOWN_PROJECTS = {
    "Stark V": "1f96600e-a01a-4afa-a123-7586b080de92",
    "Gateway V2": "4e1f8355-73e7-429a-8fa0-4925bcce8e04",
    "fhevm": "3bdd6e49-46a2-4095-b355-9a9d95776cdd",
}

LOG_FILE = Path.home() / ".claude" / "task-monitor.log"


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    console.print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def run_claude_prompt(prompt: str, cwd: str = None) -> str:
    cmd = ["claude", "--print", "--output-format", "text", prompt]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
            cwd=cwd or str(Path.home() / "Documents" / "starkware" / "stark-v")
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "ERROR: Claude CLI timed out"
    except Exception as e:
        return f"ERROR: {e}"


def check_tasks(project_id: str) -> dict:
    prompt = f'Use mcp__vibe_kanban__list_tasks for project_id {project_id}. Return ONLY JSON: {{"tasks": [{{"id": "...", "title": "...", "status": "...", "has_in_progress_attempt": true/false}}]}}'
    response = run_claude_prompt(prompt)
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except json.JSONDecodeError:
        pass
    return {"error": response, "tasks": []}


def display_status(tasks_data: dict):
    if "error" in tasks_data and tasks_data.get("error"):
        log(f"Error: {tasks_data['error']}")
        return
    tasks = tasks_data.get("tasks", [])
    if not tasks:
        log("No tasks found")
        return

    table = Table(title="Task Status")
    table.add_column("Status", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("ID", style="dim")

    status_emoji = {"todo": "📋", "inprogress": "⏳", "inreview": "🔍", "done": "✅", "cancelled": "❌"}

    for task in tasks:
        status = task.get("status", "unknown")
        table.add_row(f"{status_emoji.get(status, '❓')} {status}", task.get("title", "?")[:50], task.get("id", "?")[:8])

    console.print(table)
    in_progress = sum(1 for t in tasks if t.get("status") == "inprogress")
    in_review = sum(1 for t in tasks if t.get("status") == "inreview")
    done = sum(1 for t in tasks if t.get("status") == "done")
    log(f"Summary: {in_progress} in progress, {in_review} in review, {done} done")


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
            sys.exit(1)
    if not project_id:
        console.print("[red]Please specify --project or --project-id[/red]")
        sys.exit(1)

    log(f"Starting monitor for project {project_id}")
    log(f"Poll interval: {args.interval}s | Log: {LOG_FILE}")

    try:
        while True:
            log("--- Checking tasks ---")
            tasks_data = check_tasks(project_id)
            display_status(tasks_data)
            if args.once:
                break
            log(f"Next check in {args.interval}s...")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        log("Monitor stopped")


if __name__ == "__main__":
    main()
