# Set Milestone Recursive

Recursively set milestone on all sub-issues for milestones in a repository.

## Arguments

- `$ARGUMENTS` - Required: Either a milestone URL or a repo (owner/repo format)
  - Milestone URL: `https://github.com/org/repo/milestone/26` - process single milestone
  - Repo: `org/repo` - process all milestones in the repo

## Examples

```
/set-milestone-recursive https://github.com/zama-ai/planning-blockchain/milestone/26
/set-milestone-recursive zama-ai/planning-blockchain
```

## Instructions

If `$ARGUMENTS` is empty, ask the user to provide either:
1. A milestone URL (e.g., `https://github.com/org/repo/milestone/26`)
2. A repository in `owner/repo` format to process all milestones

Once you have the target, run the script:

```bash
uv run /Users/clementwalter/Documents/rookie-marketplace/github-issues/commands/_set_milestone_recursive.py "$ARGUMENTS" --dry-run
```

Show the dry-run output first and ask for confirmation before running without `--dry-run`.

The script will:
1. Find all issues in the milestone(s)
2. For each issue, traverse all sub-issues recursively
3. Ensure sub-issues have the same milestone as their parent (if the milestone exists in their repo)
