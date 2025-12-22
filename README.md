# Rookie Marketplace

Claude Code skills marketplace - contextual knowledge auto-loaded based on user queries.

## Overview

This marketplace contains skills for Claude Code that provide specialized knowledge and workflows. Skills automatically load when Claude detects relevant queries based on trigger phrases.

## Available Plugins

### chief-of-staff

Agent coordination and task orchestration via VibeKanban.

**Skills:**

| Skill | Triggers On |
| ----- | ----------- |
| `agent-coordination` | "coordinate agents", "orchestrate tasks", "chief of staff mode", "vibekanban workflow", "dispatch agents" |

**What it provides:**
- Multi-agent coordination patterns
- Task lifecycle management
- VibeKanban API reference
- Chief of Staff workflow procedures
- Task templates for agent work

**Requires:** VibeKanban MCP server configured

---

### github-issues

GitHub issue, PR, and milestone management workflows.

**Skills:**

| Skill | Triggers On |
| ----- | ----------- |
| `github-workflow` | "github issue", "milestone planning", "PR workflow", "git commit", "work on issues", "sub-issues" |

**What it provides:**
- Issue hierarchy and milestone strategies
- Commit and PR workflows
- Autonomous issue resolution patterns
- gh CLI command reference
- Milestone management scripts (uv)

**Scripts (in skills/github-workflow/scripts/):**

| Script | Purpose |
| ------ | ------- |
| `set_milestone_recursive.py` | Set milestone on sub-issues recursively |
| `milestone_from_issues.py` | Convert issues into new milestones |
| `division_to_milestones.py` | Convert Division-labeled issues to milestones |
| `move_subissues.py` | Move sub-issues between parent issues |

Run scripts with uv:
```bash
uv run skills/github-workflow/scripts/set_milestone_recursive.py <milestone_url> --dry-run
```

---

### rust-dev

Senior-level Rust development practices and workspace architecture.

**Skills:**

| Skill | Triggers On |
| ----- | ----------- |
| `senior-rust-practices` | "rust workspace", "rust best practices", "cargo workspace", "rust architecture", "rust dependencies", "rust testing strategy", "scalable rust" |

**What it provides:**
- Workspace architecture patterns ("one product = one workspace")
- Crate organization and boundary design
- Dependency hygiene (workspace deps, features, MSRV)
- Testing pyramid (unit, integration, e2e, property tests)
- CI quality gates and compile-time optimization
- Project-specific patterns (CLI, services, ZK, WASM)

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
│   └── marketplace.json        # Marketplace metadata
├── chief-of-staff/
│   ├── .claude-plugin/
│   │   └── plugin.json         # Plugin metadata
│   └── skills/
│       └── agent-coordination/
│           ├── SKILL.md        # Core knowledge (auto-loaded)
│           ├── references/     # Detailed docs (loaded on demand)
│           │   ├── vibekanban-api.md
│           │   └── cos-workflow.md
│           └── examples/       # Templates and examples
│               └── task-templates.md
├── github-issues/
│   ├── .claude-plugin/
│   │   └── plugin.json         # Plugin metadata
│   └── skills/
│       └── github-workflow/
│           ├── SKILL.md        # Core knowledge (auto-loaded)
│           ├── references/     # Detailed docs (loaded on demand)
│           │   ├── gh-cli-patterns.md
│           │   ├── commit-workflow.md
│           │   ├── pr-workflow.md
│           │   └── work-workflow.md
│           ├── examples/       # Templates and examples
│           │   └── issue-template.md
│           └── scripts/        # uv Python scripts
│               ├── set_milestone_recursive.py
│               ├── milestone_from_issues.py
│               ├── division_to_milestones.py
│               └── move_subissues.py
├── diagnostics/
│   └── marketplace_debug.py    # Marketplace validation tool
└── README.md
```

## How Skills Work

Skills use **progressive disclosure**:

1. **Metadata** (always in context): Skill name + description with trigger phrases
2. **SKILL.md body** (loaded when triggered): Core concepts and procedures
3. **References** (loaded on demand): Detailed documentation
4. **Scripts** (executed as needed): Automation utilities

When you ask Claude about "milestone planning" or "coordinate agents", the relevant skill loads automatically.

## Contributing

**Primary Guide:** Use the `plugin-dev:skill-development` skill for comprehensive skill creation guidance:
```
/skill plugin-dev:skill-development
```

### Quick Start

1. Create plugin directory with `.claude-plugin/plugin.json`
2. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter
3. Add `references/`, `examples/`, `scripts/` as needed
4. Register in `.claude-plugin/marketplace.json`

### Skill Structure

```
skill-name/
├── SKILL.md           # Required: Core knowledge
│   ├── YAML frontmatter (name, description with triggers)
│   └── Markdown body (1,500-2,000 words, imperative form)
├── references/        # Optional: Detailed docs (loaded on demand)
├── examples/          # Optional: Working samples
└── scripts/           # Optional: uv Python scripts
```

### Script Requirements

All Python scripts **must** use uv inline metadata (no plain Python):

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

### Writing Guidelines

The `plugin-dev:skill-development` skill covers these in detail:

- **Description:** Third-person format with specific trigger phrases
- **Body:** Imperative/infinitive form (verb-first), not second person
- **Progressive disclosure:** Keep SKILL.md lean, move details to references/
- **Validation:** Use `skill-reviewer` agent to check quality

## License

MIT
