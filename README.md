# Rookie Marketplace

Agent Context Protocol (ACP) skills for Claude Code, managed and extended as Claude works.

## Overview

This marketplace contains reusable skills (plugins) for Claude Code that automate common development workflows. Skills are self-organizing - Claude adds new ones as she works on various tasks.

## Available Skills

### github-issues

GitHub issue and milestone management utilities for streamlined project management.

**Slash Commands:**

| Command | Description |
|---------|-------------|
| `/work [pr-url]` | Autonomous issue management and PR workflow |
| `/commit` | Smart git commit with automatic change analysis |
| `/new-issue` | Create well-structured GitHub issues |
| `/pr [issue-url]` | Complete PR workflow: commit, rebase, create/update PRs |

**Python Scripts:**

All scripts are uv-compatible and can be run directly.

#### move_subissues.py
Move sub-issues between parent issues with optional labeling.

```bash
uv run github-issues/commands/move_subissues.py <source_url> <target_url> [--label LABEL]...

# Example
uv run github-issues/commands/move_subissues.py \
  https://github.com/org/repo/issues/123 \
  https://github.com/org/repo/issues/456 \
  --label scalability
```

#### milestone_from_issues.py
Convert issues from a milestone into milestones, with prefix-based routing for different repos.

```bash
uv run github-issues/commands/milestone_from_issues.py <milestone_url> [options]

# Options:
#   --due-date YYYY-MM-DD   Due date for milestones (default: 2025-12-31)
#   --route PREFIX=REPO     Route issues by prefix to specific repos
#   --target-repo REPO      Fallback repo for issues without matching routes
#   --dry-run               Show what would be done
#   --limit N               Limit issues to process

# Example with routing
uv run github-issues/commands/milestone_from_issues.py \
  https://github.com/org/planning/milestone/26 \
  --route "[MPC]=org/mpc-repo" \
  --route "[Gateway]=org/gateway-repo" \
  --dry-run
```

#### set_milestone_recursive.py
Recursively set milestone on all sub-issues of issues in a given milestone.

```bash
uv run github-issues/commands/set_milestone_recursive.py <milestone_url> [--dry-run]

# Example
uv run github-issues/commands/set_milestone_recursive.py \
  https://github.com/org/repo/milestone/26 \
  --dry-run
```

#### set_milestone_recursive_all.py
Process all milestones in a repository, setting milestones on sub-issues recursively. Uses parallel processing for speed.

```bash
uv run github-issues/commands/set_milestone_recursive_all.py <owner/repo> [options]

# Options:
#   --dry-run           Show what would be done
#   --state STATE       Filter milestones: open, closed, all (default: all)
#   --milestone TITLE   Process only a specific milestone
#   --workers N         Number of parallel workers (default: 10)

# Example
uv run github-issues/commands/set_milestone_recursive_all.py \
  org/repo \
  --dry-run \
  --workers 20
```

#### division_issues_to_milestones.py
Convert issues with a specific label (default: "Division") from a milestone into milestones.

```bash
uv run github-issues/commands/division_issues_to_milestones.py <milestone_url> [options]

# Options:
#   --dry-run           Show what would be done
#   --due-date DATE     Due date (default: 2025-12-31)
#   --label LABEL       Label to filter by (default: Division)
#   --workers N         Parallel workers (default: 10)

# Example
uv run github-issues/commands/division_issues_to_milestones.py \
  https://github.com/org/repo/milestone/26 \
  --dry-run
```

## Installation

Add this marketplace to your Claude Code configuration:

```bash
# Clone the repository
git clone https://github.com/clementwalter/rookie-marketplace.git

# Add to your Claude Code settings
# In ~/.claude/settings.json, add the path to the marketplace
```

## Structure

```
rookie-marketplace/
├── .claude-plugin/
│   └── marketplace.json     # Marketplace metadata
├── github-issues/
│   ├── .claude-plugin/
│   │   └── plugin.json      # Plugin metadata
│   └── commands/
│       ├── work.md          # Autonomous workflow command
│       ├── commit.md        # Smart commit command
│       ├── new-issue.md     # Issue creation command
│       ├── pr.md            # PR workflow command
│       ├── move_subissues.py
│       ├── milestone_from_issues.py
│       ├── set_milestone_recursive.py
│       ├── set_milestone_recursive_all.py
│       └── division_issues_to_milestones.py
└── README.md
```

## Contributing

New skills are added organically as Claude works on tasks. To add a skill manually:

1. Create a new directory for the skill
2. Add a `.claude-plugin/plugin.json` with metadata
3. Add commands as `.md` files in a `commands/` directory
4. Add scripts as uv-compatible Python files
5. Update the marketplace.json to register the new plugin

## License

MIT
