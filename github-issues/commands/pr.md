# PR Workflow

Commit pending changes and create/update a pull request.

## Arguments

- `$ARGUMENTS` - Optional: issue URL/number to close (e.g., `#123` or full URL)

## Examples

```
/pr                                              # Create PR and auto-create issue
/pr #123                                         # Create PR that closes issue #123
/pr https://github.com/org/repo/issues/123       # Same, with full URL
```

## Instructions

### Step 1: Commit pending changes

Use the [commit](./commit.md) command if there are any pending changes.
Untracked files should be committed, not ignored.

If you find unrelated changes, make several commits.

### Step 2: Sync with main

Once the git tree is clean:
```bash
git pull --rebase origin main
```

Use only the diff between origin/main and the rebased current branch (not the
whole branch history, as the branch may have been used for other PRs).

### Step 3: Generate PR summary

```bash
git diff origin/main...HEAD
```

Generate a concise summary of the content and purpose of these changes.

**IMPORTANT**: Do not add co-author or AI assistance mentions in commits or PR
descriptions. All work should be attributed solely to the user.

### Step 4: Handle issue reference

- If `$ARGUMENTS` is provided: add "Closes $ARGUMENTS" to the PR summary
- If no arguments: use [new-issue](./new-issue.md) to create an issue first

### Step 5: Create or update PR

If there's already an open PR for the current branch, update it instead of
creating a new one.

```bash
gh pr list --head $(git branch --show-current) --state open
```
