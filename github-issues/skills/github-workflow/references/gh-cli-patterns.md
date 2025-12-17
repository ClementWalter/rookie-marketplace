# GitHub CLI Patterns

Common `gh` CLI commands for issue and PR management.

## Issue Operations

### List Issues

```bash
# List all open issues
gh issue list --state open

# List unassigned issues
gh issue list --state open --json number,title,assignees \
  --jq '.[] | select(.assignees | length == 0)'

# List issues by label
gh issue list --label "bug" --state open

# List issues in milestone
gh issue list --milestone "v1.0" --state open

# Get issue details as JSON
gh issue view 123 --json title,body,labels,milestone,assignees
```

### Create Issues

```bash
# Create issue interactively
gh issue create

# Create issue with title and body
gh issue create --title "Bug: Login fails" --body "$(cat <<'EOF'
## Why
Users cannot log in after password reset.

## What
Fix authentication flow after password reset.

## How
1. Check token validation
2. Verify session handling
EOF
)"

# Create issue with labels and assignee
gh issue create --title "Feature: Add dark mode" \
  --label "feature,frontend" \
  --assignee "@me"
```

### Update Issues

```bash
# Assign issue
gh issue edit 123 --add-assignee "@me"

# Add labels
gh issue edit 123 --add-label "P1-high,in-progress"

# Set milestone
gh issue edit 123 --milestone "Sprint 5"

# Close with comment
gh issue close 123 --comment "Fixed in #456"
```

## PR Operations

### List PRs

```bash
# List open PRs
gh pr list --state open

# List PRs by author
gh pr list --author "@me"

# List PRs needing review
gh pr list --search "review:required"

# Get PR details
gh pr view 123 --json title,body,reviews,comments,diff
```

### Create PRs

```bash
# Create PR interactively
gh pr create

# Create PR with details
gh pr create --title "Fix login bug" --body "$(cat <<'EOF'
## Summary
- Fixed token validation after password reset
- Added test coverage

## Test Plan
- [ ] Test password reset flow
- [ ] Verify session persistence

Fixes #123
EOF
)"

# Create draft PR
gh pr create --draft --title "WIP: New feature"
```

### Review PRs

```bash
# View PR diff
gh pr diff 123

# Get review comments
gh api repos/{owner}/{repo}/pulls/123/comments

# Approve PR
gh pr review 123 --approve

# Request changes
gh pr review 123 --request-changes --body "Please fix X"

# Add comment
gh pr comment 123 --body "Looks good, minor suggestion..."
```

### Merge PRs

```bash
# Merge with squash
gh pr merge 123 --squash

# Merge with rebase
gh pr merge 123 --rebase

# Merge and delete branch
gh pr merge 123 --squash --delete-branch
```

## Milestone Operations

```bash
# List milestones
gh api repos/{owner}/{repo}/milestones --jq '.[].title'

# Create milestone
gh api repos/{owner}/{repo}/milestones \
  -f title="v2.0" \
  -f due_on="2025-03-31T00:00:00Z" \
  -f description="Version 2.0 release"

# Get milestone by number
gh api repos/{owner}/{repo}/milestones/5

# Close milestone
gh api repos/{owner}/{repo}/milestones/5 -X PATCH -f state="closed"
```

## Sub-Issues (Tasklists)

```bash
# Get sub-issues from parent
gh api graphql -f query='
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $number) {
      trackedIssues(first: 100) {
        nodes {
          number
          title
          state
          repository { nameWithOwner }
        }
      }
    }
  }
}' -f owner="org" -f repo="repo" -F number=123

# Add sub-issue to parent (edit body to include tasklist)
gh issue edit 123 --body "$(gh issue view 123 --json body --jq '.body')

- [ ] #456"
```

## Repository Information

```bash
# Get repo info
gh repo view --json nameWithOwner,defaultBranchRef

# Get repo name
gh repo view --json nameWithOwner --jq '.nameWithOwner'

# Get default branch
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

## Batch Operations

### Process Multiple Issues

```bash
# Assign all unassigned issues to self
gh issue list --state open --json number,assignees \
  --jq '.[] | select(.assignees | length == 0) | .number' | \
  xargs -I {} gh issue edit {} --add-assignee "@me"

# Add label to all issues in milestone
gh issue list --milestone "Sprint 5" --json number --jq '.[].number' | \
  xargs -I {} gh issue edit {} --add-label "sprint-5"
```

### Cross-Repo Operations

```bash
# List issues across repos
for repo in org/repo1 org/repo2; do
  echo "=== $repo ==="
  gh issue list --repo "$repo" --state open
done

# Create issue in specific repo
gh issue create --repo org/other-repo --title "Cross-repo issue"
```

## Advanced Queries

### Search Syntax

```bash
# Complex search
gh issue list --search "is:open label:bug -label:wontfix author:@me"

# Date filtering
gh issue list --search "created:>2025-01-01 updated:<2025-02-01"

# Involves user
gh issue list --search "involves:username is:open"
```

### JSON Processing with jq

```bash
# Extract specific fields
gh issue list --json number,title,labels \
  --jq '.[] | {num: .number, title: .title, labels: [.labels[].name]}'

# Filter by condition
gh issue list --json number,labels \
  --jq '.[] | select(.labels | map(.name) | contains(["P0-critical"]))'

# Count by label
gh issue list --json labels \
  --jq '[.[].labels[].name] | group_by(.) | map({label: .[0], count: length})'
```
