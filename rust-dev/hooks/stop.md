---
name: Verify Tests and Trunk
description: Ensures tests pass and trunk check is clean before completing Rust work
event: Stop
---

# Pre-Completion Verification

Before completing this task, you MUST verify that the code passes quality checks.

## Required Steps

Run these commands in the worktree where you made changes:

1. **Run tests:**
   ```bash
   cargo test --workspace
   ```

2. **Run trunk (lint + format):**
   ```bash
   trunk check
   ```

## Decision Logic

- If tests PASS and trunk is CLEAN: Proceed with completion
- If tests FAIL: Fix the failing tests before completing
- If trunk has issues: Run `trunk fmt` to auto-fix, then re-check

## Important

Do NOT complete the task if:
- Tests are failing
- Trunk check has errors
- You haven't run both commands

If you haven't run these checks yet, run them now before responding to the user.
