---
name: GitHub Workflow
description: This skill should be used when the user asks about "github issue workflow", "organize issues with milestones", "manage github project", "issue hierarchy", "sub-issues", "milestone planning", "PR workflow", "issue triage", "git commit", "create PR", "work on issues", "autonomous issue resolution", or needs guidance on GitHub issue management, milestone organization, commit workflows, PR creation, or automated issue workflows.
---

# GitHub Workflow Patterns

This skill provides guidance for managing GitHub issues, milestones, pull requests, and automated workflows.

## Core Concepts

### Issue Hierarchy

GitHub supports hierarchical organization through sub-issues (tasklists):

```
Epic Issue (Milestone-level)
├── Feature Issue (Parent)
│   ├── Sub-issue 1 (Implementation task)
│   └── Sub-issue 2 (Implementation task)
└── Feature Issue (Parent)
    └── Sub-issues...
```

Create sub-issues using tasklist syntax in parent issue body:

```markdown
## Tasks
- [ ] #123
- [ ] #124
```

### Milestone Strategy

Milestones represent time-boxed delivery targets:

| Type | Duration | Purpose |
| ---- | -------- | ------- |
| Sprint | 1-2 weeks | Specific deliverables |
| Release | 1-3 months | Version targets |
| Division | Varies | Team/domain groupings |

### Issue Labels

| Label Type | Examples |
| ---------- | -------- |
| Priority | `P0-critical`, `P1-high`, `P2-medium` |
| Type | `bug`, `feature`, `chore`, `docs` |
| Status | `needs-triage`, `blocked`, `ready` |
| Area | `frontend`, `api`, `infra` |

## Workflow Procedures

### Creating Issues

Use Why/What/How structure:

```markdown
## Why
[Problem statement - what need does this address?]

## What
[Solution description - what will be built?]

## How
[Implementation approach]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

### Committing Changes

Follow conventional commit format:

```
<type>(<scope>): <subject>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Key rules:
- Never commit to main directly
- Run linter before committing: `trunk check --ci --fix`
- Use present tense imperative: "add" not "added"

### Creating Pull Requests

1. Commit all changes
2. Sync with main: `git rebase origin/main`
3. Generate summary from diff
4. Link to issue: `Closes #<number>`
5. Create or update PR

### Autonomous Issue Resolution

For parallel issue work:

1. Fetch unassigned issues
2. Self-assign to claim
3. Create worktree: `git worktree add -b fix/issue-<n> /tmp/repo-issue-<n> main`
4. Implement, test, commit
5. Create PR and report

## Utility Scripts

Execute milestone and issue operations with these uv scripts:

| Script | Usage |
| ------ | ----- |
| `set_milestone_recursive.py` | Set milestone on all sub-issues recursively |
| `milestone_from_issues.py` | Convert issues into new milestones |
| `division_to_milestones.py` | Convert Division-labeled issues to milestones |
| `move_subissues.py` | Move sub-issues between parent issues |

Run scripts with `--dry-run` first:

```bash
uv run scripts/set_milestone_recursive.py <milestone_url> --dry-run
uv run scripts/milestone_from_issues.py <milestone_url> --dry-run
uv run scripts/move_subissues.py <source_url> <target_url> --dry-run
```

## Additional Resources

### Reference Files

For detailed procedures, consult:
- **`references/commit-workflow.md`** - Detailed commit procedure
- **`references/pr-workflow.md`** - PR creation and management
- **`references/work-workflow.md`** - Autonomous issue resolution
- **`references/gh-cli-patterns.md`** - Common gh CLI commands

### Examples

Working examples in `examples/`:
- **`examples/issue-template.md`** - Issue templates (bug, feature, chore)

### Scripts

Utility scripts in `scripts/`:
- **`scripts/set_milestone_recursive.py`** - Milestone propagation
- **`scripts/milestone_from_issues.py`** - Issue-to-milestone conversion
- **`scripts/division_to_milestones.py`** - Division label processing
- **`scripts/move_subissues.py`** - Sub-issue migration
