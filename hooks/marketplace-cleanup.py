#!/usr/bin/env python3
"""
Marketplace Cleanup Hook - Triggers cleanup review after commits to rookie-marketplace.

This PostToolUse hook monitors for successful git commits in the marketplace directory
and instructs Claude to spawn a cleanup agent for quality review.

Hook Type: PostToolUse
Matcher: Bash
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

MARKETPLACE_PATH = Path("/Users/clementwalter/Documents/rookie-marketplace")

# Path to the cleanup prompt file (can be updated by cleanup agents)
CLEANUP_PROMPT_FILE = MARKETPLACE_PATH / "hooks" / "cleanup-prompt.md"


def get_cleanup_prompt() -> str:
    """Load cleanup prompt from file, allowing it to be updated."""
    if CLEANUP_PROMPT_FILE.exists():
        return CLEANUP_PROMPT_FILE.read_text()

    # Fallback default prompt
    return """Review the rookie-marketplace for quality issues and fix them."""


def is_marketplace_commit(tool_input: dict, tool_output: str, cwd: str) -> bool:
    """Check if this was a git commit in the marketplace directory."""
    command = tool_input.get("command", "")

    # Must be a git commit command
    if "git commit" not in command:
        return False

    # Check for error indicators
    if "error" in tool_output.lower() or "fatal" in tool_output.lower():
        return False

    # Must be in marketplace directory
    cwd_path = Path(cwd).resolve()

    try:
        cwd_path.relative_to(MARKETPLACE_PATH)
        return True
    except ValueError:
        pass

    # Check if we're committing to marketplace from another location
    if str(MARKETPLACE_PATH) in command:
        return True

    return False


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    tool_output = input_data.get("tool_output", "")
    cwd = input_data.get("cwd", os.getcwd())

    # Only process Bash tool calls
    if tool_name != "Bash":
        sys.exit(0)

    # Check if this was a successful marketplace commit
    if not is_marketplace_commit(tool_input, tool_output, cwd):
        sys.exit(0)

    # Load the cleanup prompt (can be self-updated by cleanup agents)
    cleanup_prompt = get_cleanup_prompt()

    # Return instruction to spawn cleanup agent
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "message": f"""## Marketplace Commit Detected

A commit was made to rookie-marketplace. Spawn a background cleanup agent.

**Required Action**: Use the Task tool to spawn a cleanup agent:

```
Task tool:
  subagent_type: general-purpose
  model: haiku
  description: "Marketplace cleanup review"
  run_in_background: true
  prompt: |
{cleanup_prompt}
```

This is an automated quality check. The cleanup agent has full autonomy in the marketplace directory and can update its own prompt for future improvements.
"""
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
