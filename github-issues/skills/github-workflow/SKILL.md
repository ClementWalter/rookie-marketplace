---
name: GitHub Workflow
description: This skill should be used when the user asks about "github issue workflow", "organize issues with milestones", "manage github project", "issue hierarchy", "sub-issues", "milestone planning", "PR workflow", "issue triage", or needs guidance on GitHub issue management patterns, milestone organization strategies, or automated issue workflows.
---

# GitHub Workflow Patterns

This skill provides guidance for managing GitHub issues, milestones, and pull requests effectively using structured workflows and automation.

## Core Concepts

### Issue Hierarchy

GitHub supports hierarchical issue organization through sub-issues (tasklists). Structure work as:

```
Epic Issue (Milestone-level)
├── Feature Issue (Parent)
│   ├── Sub-issue 1 (Implementation task)
│   ├── Sub-issue 2 (Implementation task)
│   └── Sub-issue 3 (Implementation task)
└── Feature Issue (Parent)
    └── Sub-issues...
```

To create sub-issues, use GitHub's tasklist syntax in the parent issue body:

```markdown
## Tasks

- [ ] #123
- [ ] #124
- [ ] #125
```

### Milestone Strategy

Milestones represent time-boxed delivery targets. Organize milestones by:

1. **Sprint milestones** - Short-term (1-2 weeks), specific deliverables
2. **Release milestones** - Medium-term (1-3 months), version targets
3. **Division milestones** - Team or domain-specific groupings

When converting issues to milestones:
- Use the issue title as milestone name
- Copy issue description to milestone description
- Set due dates based on project timeline
- Move sub-issues to use the new milestone

### Issue Labels

Apply consistent labeling for triage and filtering:

| Label Type | Purpose | Examples |
| ---------- | ------- | -------- |
| Priority | Urgency level | `P0-critical`, `P1-high`, `P2-medium` |
| Type | Work category | `bug`, `feature`, `chore`, `docs` |
| Status | Workflow state | `needs-triage`, `blocked`, `ready` |
| Area | Code domain | `frontend`, `api`, `infra` |

## Workflow Patterns

### Issue Creation Pattern

When creating issues, follow the Why/What/How structure:

```markdown
## Why

[Problem statement - what pain point or need does this address?]

## What

[Solution description - what will be built or changed?]

## How

[Implementation approach - technical details or steps]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
```

### PR Workflow Pattern

For pull requests, follow this sequence:

1. **Create feature branch** from main: `fix/issue-<number>` or `feat/<description>`
2. **Implement changes** with atomic commits
3. **Run CI locally** before pushing (linting, tests, build)
4. **Create PR** with reference to issue: `Fixes #<number>`
5. **Address reviews** by pushing new commits (not amending)
6. **Rebase on main** before merge if needed

### Autonomous Issue Resolution

When working through a backlog autonomously:

1. **Fetch unassigned issues**: Filter by `assignees:0` or empty assignees
2. **Self-assign** to prevent conflicts with other agents
3. **Create worktree** for parallel work: `/tmp/<repo>-issue-<number>`
4. **Implement fix** with proper testing
5. **Create PR** linking the issue
6. **Report completion** with PR URL

For parallel execution, use git worktrees:

```bash
# Create worktree for issue
git worktree add -b fix/issue-123 /tmp/repo-issue-123 main

# Work in worktree
cd /tmp/repo-issue-123
# ... implement fix ...

# Clean up after merge
git worktree remove /tmp/repo-issue-123 --force
```

### Milestone Propagation

When managing issue hierarchies with milestones:

1. **Set milestone on parent** issue first
2. **Propagate to sub-issues** - sub-issues should inherit parent's milestone
3. **Handle cross-repo** - if sub-issue is in different repo, check if milestone exists there
4. **Recursive traversal** - some sub-issues may have their own sub-issues

Use the marketplace utilities for bulk operations:
- `/set-milestone-recursive` - Propagate milestone to all sub-issues
- `/milestone-from-issues` - Convert issues into milestones
- `/move-subissues` - Transfer sub-issues between parents

## CI Integration

### Pre-Push Validation

Before pushing any changes, run CI checks locally:

```bash
# Check for CI workflow files
ls .github/workflows/

# Common checks to run
trunk check --ci          # Linting/formatting
cargo build && cargo test # Rust projects
npm test && npm run build # Node projects
pytest                    # Python projects
```

### Handling CI Failures

When CI fails on a PR:

1. **Read the failure log** to identify the issue
2. **Fix locally** and verify the fix passes
3. **Push fix** as new commit (preserve review context)
4. **Re-request review** if needed

## Best Practices

### Issue Hygiene

- Close stale issues with explanation
- Link related issues with references
- Update issue description as understanding evolves
- Add reproduction steps for bugs
- Include environment details when relevant

### Milestone Management

- Set realistic due dates
- Close milestones when all issues resolved
- Archive old milestones, don't delete
- Use milestone descriptions for release notes

### PR Quality

- Keep PRs focused and small when possible
- Include test coverage for changes
- Update documentation alongside code
- Use draft PRs for work-in-progress

## Utility Scripts

The github-issues plugin provides Python utilities for bulk operations:

| Script | Purpose |
| ------ | ------- |
| `_set_milestone_recursive.py` | Propagate milestone to sub-issues |
| `_milestone_from_issues.py` | Convert issues to milestones |
| `_division_to_milestones.py` | Convert labeled issues to milestones |
| `_move_subissues.py` | Move sub-issues between parents |

All scripts support `--dry-run` for preview before execution.

## Additional Resources

### Reference Files

For detailed API patterns and advanced workflows:
- **`references/gh-cli-patterns.md`** - Common gh CLI commands and patterns

### Examples

Working examples in `examples/`:
- **`examples/issue-template.md`** - Issue template with Why/What/How structure
