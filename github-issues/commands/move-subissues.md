# Move Sub-issues

Move all sub-issues from one parent issue to another, optionally adding labels.

## Arguments

- `$ARGUMENTS` - Required: Two issue URLs separated by space
  - First: source parent issue URL
  - Second: target parent issue URL

## Examples

```
/move-subissues https://github.com/org/repo/issues/123 https://github.com/org/other-repo/issues/456
```

## Instructions

If `$ARGUMENTS` is empty or incomplete, ask the user to provide:
1. Source parent issue URL (the issue whose sub-issues will be moved)
2. Target parent issue URL (the issue that will receive the sub-issues)

Parse `$ARGUMENTS` to extract both URLs.

First, run a dry-run:

```bash
uv run /Users/clementwalter/Documents/rookie-marketplace/github-issues/commands/_move_subissues.py <source_url> <target_url> --dry-run
```

Ask the user if they want to add labels to all moved sub-issues. If yes, add `--label LABEL` flags.

Then run without --dry-run after confirmation.
