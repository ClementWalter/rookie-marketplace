#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Stop hook for Rust development: runs cargo test and trunk check.
Only triggers if Rust files were modified in the current session.
"""

import json
import os
import subprocess
import sys


def find_cargo_root(start_path: str) -> str | None:
    """Find the nearest Cargo.toml directory."""
    current = start_path
    while current != "/":
        if os.path.exists(os.path.join(current, "Cargo.toml")):
            return current
        current = os.path.dirname(current)
    return None


def run_command(cmd: list[str], cwd: str) -> tuple[bool, str]:
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Command timed out after 5 minutes"
    except FileNotFoundError:
        return True, f"Command not found: {cmd[0]} (skipping)"


def main():
    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        # No valid input, allow continuation
        sys.exit(0)

    # Get the working directory
    cwd = hook_input.get("cwd", os.getcwd())

    # Find Cargo.toml root
    cargo_root = find_cargo_root(cwd)
    if not cargo_root:
        # Not a Rust project, allow continuation
        sys.exit(0)

    # Check if any .rs files were mentioned in the session
    # For Stop hooks, we check the transcript for Rust file interactions
    transcript = hook_input.get("transcript", [])
    rust_file_touched = False

    for entry in transcript:
        content = str(entry)
        if ".rs" in content and ("Edit" in content or "Write" in content):
            rust_file_touched = True
            break

    if not rust_file_touched:
        # No Rust files were modified, allow continuation
        sys.exit(0)

    errors = []

    # Run cargo test
    print("Running cargo test --release --workspace...", file=sys.stderr)
    success, output = run_command(
        ["cargo", "test", "--release", "--workspace"],
        cargo_root
    )
    if not success:
        errors.append(f"cargo test failed:\n{output[-2000:]}")  # Last 2000 chars

    # Run trunk check if available
    print("Running trunk check...", file=sys.stderr)
    success, output = run_command(
        ["trunk", "check", "--ci"],
        cargo_root
    )
    if not success and "Command not found" not in output:
        errors.append(f"trunk check failed:\n{output[-2000:]}")

    if errors:
        # Output error message for Claude to see
        error_response = {
            "decision": "block",
            "reason": "Rust quality checks failed:\n\n" + "\n\n".join(errors)
        }
        print(json.dumps(error_response))
        sys.exit(1)

    # All checks passed
    sys.exit(0)


if __name__ == "__main__":
    main()
