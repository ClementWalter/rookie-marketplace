#!/usr/bin/env python3
"""
Marketplace Cleanup Hook - Triggers cleanup review at session end.

This Stop hook checks if the session involved the marketplace directory
and instructs Claude to spawn a cleanup agent for quality review.

Hook Type: Stop
Matcher: *
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

MARKETPLACE_PATH = Path("/Users/clementwalter/Documents/rookie-marketplace")

# Path to the cleanup prompt file (colocated with this hook)
CLEANUP_PROMPT_FILE = Path(__file__).parent / "cleanup-prompt.md"


def get_cleanup_prompt() -> str:
    """Load cleanup prompt from file, allowing it to be updated."""
    if CLEANUP_PROMPT_FILE.exists():
        return CLEANUP_PROMPT_FILE.read_text()

    # Fallback default prompt
    return """Review the rookie-marketplace for quality issues and fix them."""


def should_run_cleanup(cwd: str) -> bool:
    """Check if we should run cleanup (session was in marketplace)."""
    cwd_path = Path(cwd).resolve()

    try:
        cwd_path.relative_to(MARKETPLACE_PATH)
        return True
    except ValueError:
        return False


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # Stop hook input has different structure
    cwd = input_data.get("cwd", "")

    # Check if session was in marketplace directory
    if not should_run_cleanup(cwd):
        sys.exit(0)

    # Load the cleanup prompt
    cleanup_prompt = get_cleanup_prompt()

    # Return instruction to spawn cleanup agent
    output = {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "message": f"""## Marketplace Session Ending

This session was in rookie-marketplace. Spawn a cleanup agent before ending.

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

This is an automated quality check. The cleanup agent has full autonomy in the marketplace directory.
""",
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
