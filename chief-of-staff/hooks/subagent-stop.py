#!/usr/bin/env python3
"""
Subagent Stop Hook - Enforces code quality checklist before agent completion.

Hook Type: SubagentStop
Matcher: *
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROMPT_FILE = Path(__file__).parent / "subagent-stop-prompt.md"


def get_prompt() -> str:
    """Load prompt from file."""
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text()
    return "Run quality checks before completing."


def main():
    prompt = get_prompt()

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SubagentStop",
            "message": prompt,
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
