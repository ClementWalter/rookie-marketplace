# Rookie Marketplace - Autonomous Maintenance Guide

This is my skill marketplace. I manage it autonomously.

## Ownership

- I own this codebase and operate with full autonomy
- No user confirmation needed for commits or pushes
- I make decisions independently about structure, content, and organization

## Directory Structure

```text
rookie-marketplace/
├── .claude-plugin/
│   └── marketplace.json      # Registry of all plugins
├── <plugin-name>/
│   ├── .claude-plugin/
│   │   └── plugin.json       # Plugin metadata
│   └── skills/
│       └── <skill-name>/
│           ├── SKILL.md      # Required: Core knowledge
│           ├── references/   # Optional: Detailed docs
│           ├── examples/     # Optional: Working samples
│           └── scripts/      # Optional: uv Python scripts
├── diagnostics/
│   └── marketplace_debug.py  # Validation utility
├── CLAUDE.md                 # This file
└── README.md                 # User-facing documentation
```

## Skill Creation

**Primary Guide:** Use the `plugin-dev:skill-development` skill for comprehensive guidance. Invoke it when creating or editing skills:

```text
/skill plugin-dev:skill-development
```

The skill provides detailed methodology for:

- Understanding use cases with concrete examples
- Planning reusable skill contents
- Writing effective SKILL.md with proper frontmatter
- Progressive disclosure design
- Validation and testing

### Quick Reference (Baseline)

**To existing plugin:**

```bash
mkdir -p <plugin>/skills/<skill-name>/{references,examples,scripts}
```

**To new plugin:**

```bash
mkdir -p <plugin>/.claude-plugin
mkdir -p <plugin>/skills/<skill-name>
```

Then create `plugin.json` and register in `.claude-plugin/marketplace.json`.

### Script Requirements

All Python scripts must be uv-compatible (this takes precedence over any other script format):

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

## Commit Workflow

After ANY modification:

```bash
git add -A
git commit -m "<type>: <description>"
git push origin main
```

Types: `feat`, `fix`, `docs`, `refactor`, `chore`

## Quality Guidelines

See `plugin-dev:skill-development` for comprehensive guidelines. Key points:

### SKILL.md

- Use third-person description: "This skill should be used when..."
- Include specific trigger phrases in quotes
- Body in imperative form (not "you should")
- Keep under 2,000 words (ideally 1,500-2,000)
- Reference supporting files in an "Additional Resources" section

### References

- Move detailed content here (>500 words on single topic)
- Name descriptively: `patterns.md`, `api-reference.md`, `workflow.md`

### Scripts

- **Must use uv inline metadata** (no plain Python)
- Document with docstrings and usage examples
- Support `--dry-run` for destructive operations
- Use argparse for CLI

## Current Inventory

| Plugin           | Skills               | Scripts               |
| ---------------- | -------------------- | --------------------- |
| `github-issues`  | `github-workflow`    | 4 milestone utilities |
| `chief-of-staff` | `agent-coordination` | none                  |

## Validation

Run diagnostics:

```bash
uv run diagnostics/marketplace_debug.py
```

## Immediate Availability

This marketplace uses local directory source. Changes are available immediately:

- Skill edits: Next Claude message
- New skills: Next Claude session
- No push required for local testing

Push to GitHub for backup and cross-machine sync.
