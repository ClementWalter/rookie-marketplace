# New Issue

Create a GitHub issue with Why/What/How structure.

## Arguments

- `$ARGUMENTS` - Optional: issue title or description to base the issue on

## Examples

```
/new-issue                                    # Create based on conversation context
/new-issue Add dark mode support              # Create issue with this title
/new-issue Fix login timeout after 5 minutes  # Create issue for this bug
```

## Instructions

Use the gh CLI to create an issue in the current repository.

Structure the issue body as **Why/What/How**:
1. **Why** - Why we need to do this
2. **What** - What needs to be done or fixed
3. **How** - Concise to-do list to implement the what

Do not change the codebase or create any code. Focus only on project management
and creating the issue properly.

Get the issue content from:
1. Previous conversation context (if any)
2. Current pending diff (if any)
3. `$ARGUMENTS` (if provided)

**Before creating**:
1. Display the proposed issue content
2. Ask for confirmation
3. Create the issue with proper markdown syntax (don't escape backticks)

Assign the issue to the current GitHub user:
```bash
gh api user --jq '.login'
```
