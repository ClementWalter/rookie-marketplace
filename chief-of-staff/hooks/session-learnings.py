#!/usr/bin/env python3
"""
Session Learnings Hook - Prompts Claude to capture session learnings.

Hook Type: SessionEnd
Matcher: *
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROMPT_FILE = Path(__file__).parent / "session-learnings-prompt.md"


def get_prompt() -> str:
    """Load prompt from file."""
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text()
    return "Capture session learnings before ending."


def main():
    # SessionEnd hook - always return the prompt
    prompt = get_prompt()

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionEnd",
            "message": prompt,
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
