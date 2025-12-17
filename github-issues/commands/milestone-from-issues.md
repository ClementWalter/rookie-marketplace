# Milestone from Issues

Convert issues from a milestone into new milestones, migrating their sub-issues.

## Arguments

- `$ARGUMENTS` - Required: A milestone URL (e.g., `https://github.com/org/repo/milestone/26`)

## Examples

```
/milestone-from-issues https://github.com/zama-ai/planning-blockchain/milestone/26
```

## Instructions

If `$ARGUMENTS` is empty, ask the user to provide a milestone URL.

For each issue in the source milestone, this will:
1. Create a new milestone with the issue title as name
2. Set the milestone due date and description from the issue
3. Move all sub-issues to use the new milestone

First, run a dry-run to show what would happen:

```bash
uv run /Users/clementwalter/Documents/rookie-marketplace/github-issues/commands/_milestone_from_issues.py "$ARGUMENTS" --dry-run
```

Ask the user if they want to:
- Proceed with defaults (due date: 2025-12-31)
- Specify a different due date
- Specify target repos for issues without sub-issues (--target-repo owner/repo)
- Specify routing rules (--route "[prefix]=owner/repo")

Then run without --dry-run after confirmation.
