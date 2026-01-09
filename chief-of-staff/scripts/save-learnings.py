#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Save session learnings from Stop hook feedback.

Reads JSON input from stdin containing session retrospective data
and appends it to the learnings file.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def extract_json_from_text(text: str) -> dict | None:
    """Extract JSON object from text that may contain markdown code blocks."""
    # Try to find JSON in code blocks first
    json_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to parse the whole text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find any JSON object in the text
    brace_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
    matches = re.findall(brace_pattern, text)
    for potential_json in matches:
        try:
            return json.loads(potential_json)
        except json.JSONDecodeError:
            continue

    return None


def format_learning_entry(feedback: dict, timestamp: str) -> str:
    """Format feedback as a markdown entry."""
    lines = [f"## Session: {timestamp}", ""]

    # Summary
    if summary := feedback.get("session_summary"):
        lines.extend([f"**Summary**: {summary}", ""])

    # What worked well
    if worked := feedback.get("worked_well"):
        lines.append("### What Worked Well")
        for item in worked:
            lines.append(f"- {item}")
        lines.append("")

    # What didn't work
    if didnt := feedback.get("didnt_work"):
        lines.append("### What Didn't Work")
        for item in didnt:
            lines.append(f"- {item}")
        lines.append("")

    # Key learnings
    if learnings := feedback.get("key_learnings"):
        lines.append("### Key Learnings")
        for item in learnings:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point for the save-learnings script."""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # No valid JSON input, silently continue
        print(json.dumps({"continue": True}))
        return
    except Exception:
        print(json.dumps({"continue": True}))
        return

    # Get plugin root from environment or derive from script location
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not plugin_root:
        plugin_root = Path(__file__).parent.parent

    learnings_file = Path(plugin_root) / "learnings" / "session-learnings.md"

    # Ensure learnings directory exists
    learnings_file.parent.mkdir(parents=True, exist_ok=True)

    # Extract feedback from tool result if available
    tool_result = input_data.get("tool_result", "")
    if not tool_result:
        # Try other possible fields
        tool_result = input_data.get("result", "") or input_data.get("output", "")

    # Try to parse JSON from the result
    feedback = None
    if isinstance(tool_result, str):
        feedback = extract_json_from_text(tool_result)
    elif isinstance(tool_result, dict):
        feedback = tool_result

    if not feedback:
        # No feedback to save, continue silently
        print(json.dumps({"continue": True}))
        return

    # Create timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Format the entry
    entry = format_learning_entry(feedback, timestamp)

    # Append to learnings file
    try:
        with open(learnings_file, "a") as f:
            f.write(entry)
    except Exception as e:
        # Log error but don't block session end
        sys.stderr.write(f"Error saving learnings: {e}\n")

    # Signal to continue (don't block session end)
    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
