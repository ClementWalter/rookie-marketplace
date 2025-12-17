# Division to Milestones

Convert issues with a specific label (default: "Division") from a milestone into new milestones.

## Arguments

- `$ARGUMENTS` - Required: A milestone URL (e.g., `https://github.com/org/repo/milestone/26`)

## Examples

```
/division-to-milestones https://github.com/zama-ai/planning-blockchain/milestone/26
```

## Instructions

If `$ARGUMENTS` is empty, ask the user to provide a milestone URL.

This will find all issues with the "Division" label in the specified milestone and create a new milestone for each one.

First, run a dry-run:

```bash
uv run /Users/clementwalter/Documents/rookie-marketplace/github-issues/commands/_division_to_milestones.py "$ARGUMENTS" --dry-run
```

Ask the user if they want to:
- Proceed with defaults (label: Division, due date: 2025-12-31)
- Use a different label (--label LABEL)
- Use a different due date (--due-date YYYY-MM-DD)

Then run without --dry-run after confirmation.
