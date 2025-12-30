---
description: Merge all git worktree changes back to main with AI-generated commit
---

# Merge Worktrees Command

Merge all active worktree changes back to the main branch with a single, comprehensive AI-generated commit message.

## Procedure

### Step 1: List Active Worktrees

Run `git worktree list` to show all worktrees and their branches.

### Step 2: Analyze Changes

For each worktree (excluding the main one):

1. Check if there are uncommitted changes: `git -C <worktree-path> status --porcelain`
2. Check if there are commits ahead of main: `git -C <worktree-path> log main..<branch> --oneline`
3. Show a summary of changes: `git -C <worktree-path> diff main --stat`

### Step 3: Present Summary to User

Display a table showing:

| Worktree | Branch | Uncommitted | Commits Ahead | Files Changed |
|----------|--------|-------------|---------------|---------------|

Ask user to confirm which worktrees to merge.

### Step 4: Commit Any Uncommitted Changes

For worktrees with uncommitted changes, commit them first with descriptive messages.

### Step 5: Merge to Main

For each confirmed worktree:

1. Return to main worktree
2. Merge the branch: `git merge --squash <branch>`
3. Record the changes for the final commit message

### Step 6: Generate AI Commit Message

Create a comprehensive commit message in this format:

```
<type>: <concise summary covering all merged work>

Merged branches:
- <branch-1>: <what was accomplished>
- <branch-2>: <what was accomplished>

<detailed description of the combined changes>
```

Where `<type>` is one of: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`

### Step 7: Commit and Cleanup

1. Create the final commit with the generated message
2. Ask user if they want to clean up merged worktrees
3. If yes, remove worktrees: `git worktree remove <path>`
4. Delete merged branches: `git branch -d <branch>`

### Step 8: Final Status

Show `git log -1` and `git worktree list` to confirm the result.

## Important Notes

- Always ask for user confirmation before merging
- Never force-delete branches with unmerged changes
- If merge conflicts occur, pause and ask user how to resolve
- Keep worktrees intact if user wants to continue working on them
