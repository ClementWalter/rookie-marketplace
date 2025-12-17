# Rookie Marketplace

Agent Context Protocol (ACP) skills for Claude Code, managed and extended as Claude works.

## Overview

This marketplace contains reusable skills (plugins) for Claude Code that automate common development workflows. Skills are self-organizing - Claude adds new ones as she works on various tasks.

## Available Skills

### chief-of-staff

VibeKanban-powered project coordination and task orchestration for agent teams.

**Skills (auto-loaded by Claude):**

| Skill | Triggers On |
| ----- | ----------- |
| `agent-coordination` | "coordinate agents", "orchestrate tasks", "manage agent team", "vibekanban workflow" |

**Slash Commands:**

| Command | Description |
| ------- | ----------- |
| `/cos [project]` | Start Chief of Staff mode for coordinating agent teams via VibeKanban |

**What it does:**
- Acts as coordinator/orchestrator for a team of coding agents
- Creates and manages tasks on VibeKanban
- Assigns agents to tasks and tracks progress
- Does NOT execute tasks directly—only plans, clarifies, and coordinates

**Requires:** VibeKanban MCP server configured

---

### github-issues

GitHub issue and milestone management utilities for streamlined project management.

**Skills (auto-loaded by Claude):**

| Skill | Triggers On |
| ----- | ----------- |
| `github-workflow` | "github issue workflow", "organize issues", "milestone planning", "PR workflow", "issue hierarchy", "sub-issues" |

**Slash Commands:**

| Command | Description |
| ------- | ----------- |
| `/work [pr-url]` | Autonomous issue management and PR workflow |
| `/commit` | Smart git commit with automatic change analysis |
| `/new-issue` | Create well-structured GitHub issues |
| `/pr [issue-url]` | Complete PR workflow: commit, rebase, create/update PRs |
| `/set-milestone-recursive` | Recursively set milestone on sub-issues |
| `/milestone-from-issues` | Convert milestone issues into new milestones |
| `/division-to-milestones` | Convert Division-labeled issues to milestones |
| `/move-subissues` | Move sub-issues between parent issues |

**Python Utilities:**

All scripts are uv-compatible and can be run directly. They are prefixed with `_` to indicate they are helper utilities called by the slash commands.

| Script | Purpose |
| ------ | ------- |
| `_move_subissues.py` | Move sub-issues between parent issues |
| `_milestone_from_issues.py` | Convert issues into new milestones |
| `_set_milestone_recursive.py` | Set milestone on sub-issues recursively |
| `_division_to_milestones.py` | Convert Division-labeled issues to milestones |

These are typically invoked via slash commands (e.g., `/move-subissues`, `/milestone-from-issues`) which provide guided usage with dry-run confirmation.

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
│   └── marketplace.json      # Marketplace metadata
├── chief-of-staff/
│   ├── .claude-plugin/
│   │   └── plugin.json       # Plugin metadata
│   ├── commands/
│   │   └── cos.md            # Chief of Staff coordination mode
│   └── skills/
│       └── agent-coordination/
│           ├── SKILL.md      # Agent coordination patterns
│           ├── references/   # VibeKanban API reference
│           └── examples/     # Task templates
├── github-issues/
│   ├── .claude-plugin/
│   │   └── plugin.json       # Plugin metadata
│   ├── commands/
│   │   ├── work.md           # Autonomous workflow command
│   │   ├── commit.md         # Smart commit command
│   │   ├── new-issue.md      # Issue creation command
│   │   ├── pr.md             # PR workflow command
│   │   ├── set-milestone-recursive.md
│   │   ├── milestone-from-issues.md
│   │   ├── division-to-milestones.md
│   │   ├── move-subissues.md
│   │   └── _*.py             # Helper scripts
│   └── skills/
│       └── github-workflow/
│           ├── SKILL.md      # GitHub workflow patterns
│           ├── references/   # gh CLI patterns
│           └── examples/     # Issue templates
├── diagnostics/
│   └── marketplace_debug.py  # Marketplace validation tool
└── README.md
```

## Contributing

New plugins are added organically as Claude works on tasks. To add a plugin manually:

1. Create a new directory for the plugin
2. Add a `.claude-plugin/plugin.json` with metadata
3. Add commands as `.md` files in a `commands/` directory
4. Add skills as `SKILL.md` files in `skills/<skill-name>/` directories
5. Add scripts as uv-compatible Python files
6. Update the marketplace.json to register the new plugin

### Adding Skills

Skills provide contextual knowledge that Claude loads automatically based on trigger phrases. To add a skill:

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter
2. Include `name` and `description` (with trigger phrases) in frontmatter
3. Write the skill body in imperative form
4. Add `references/` for detailed documentation
5. Add `examples/` for working code samples

## License

MIT
