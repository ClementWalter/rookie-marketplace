# Rookie Marketplace

Agent Context Protocol (ACP) skills for Claude Code, managed and extended as Claude works.

## Overview

This marketplace contains reusable skills (plugins) for Claude Code that automate common development workflows. Skills are self-organizing - Claude adds new ones as she works on various tasks.

## Available Skills

### github-issues

GitHub issue management utilities for streamlined project management.

**Commands:**

| Command | Description |
|---------|-------------|
| `/work [pr-url]` | Autonomous issue management and PR workflow. Reviews PRs, creates issues, and resolves them in parallel using git worktrees. |
| `/commit` | Smart git commit with automatic change analysis, conventional commit messages, and CI pre-checks. |
| `/new-issue` | Create well-structured GitHub issues with Why/What/How format. |
| `/pr [issue-url]` | Complete PR workflow: commit pending changes, rebase, and create/update PRs. |
| `/move_subissues` | Move sub-issues between parent issues with optional labeling. |

**Scripts:**

```bash
# Move sub-issues from one parent to another
uv run github-issues/commands/move_subissues.py <source_url> <target_url> [--label LABEL]...

# Example
uv run github-issues/commands/move_subissues.py \
  https://github.com/org/repo/issues/123 \
  https://github.com/org/repo/issues/456 \
  --label scalability
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
│       └── move_subissues.py # Sub-issue migration script
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
