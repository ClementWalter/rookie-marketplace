# Smart Git Commit

Analyze changes and create a meaningful conventional commit.

## Arguments

- `$ARGUMENTS` - Optional: commit message override (if you want to specify your own message)

## Examples

```
/commit                           # Auto-generate commit message
/commit fix: typo in README       # Use provided message
```

## Instructions

I'll analyze your changes and create a meaningful commit message.

First, make sure the linter passes by running `trunk check --ci --fix`. Fix any
errors until the linter passes.

**CRITICAL**: Check branch before committing. Never commit to the main branch.

```bash
git rev-parse --abbrev-ref HEAD
```

If on `main`, create a new branch first:
1. Pick a relevant name based on current changes
2. Create the branch: `git checkout -b <branch-name>`
3. Then proceed with the commit

Check what's changed:

```bash
# Check if we have changes to commit
if ! git diff --cached --quiet || ! git diff --quiet; then
    echo "Changes detected:"
    git status --short
else
    echo "No changes to commit"
    exit 0
fi

# Show detailed changes
git diff --cached --stat
git diff --stat
```

Add all untracked files and review their content to update the commit message.

Analyze the changes to determine:
1. What files were modified
2. The nature of changes (feature, fix, refactor, etc.)
3. The scope/component affected

If analysis or commit encounters errors:
- Explain what went wrong
- Suggest how to resolve it
- Ensure no partial commits occur

```bash
# If nothing is staged, stage modified files (not untracked)
if git diff --cached --quiet; then
    echo "No files staged. Staging modified files..."
    git add -u
fi

# Show what will be committed
git diff --cached --name-status
```

Create a conventional commit message:
- **Type**: feat|fix|docs|style|refactor|test|chore
- **Scope**: component or area affected
- **Subject**: clear description in present tense
- **Body**: why the change was made (if needed)

Do not add co-author or AI assistance mentions. The commit should be entirely
attributed to you.

Before committing, run `trunk check --ci --fix` to ensure code is formatted
correctly. If there are errors, ask to fix them manually.

The commit message will be concise, meaningful, and follow the project's
conventions if detectable from recent commits.
