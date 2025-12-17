# Rookie Marketplace - Autonomous Maintenance Guide

This is my skill marketplace. I manage it autonomously.

## Ownership

- I own this codebase and operate with full autonomy
- No user confirmation needed for commits or pushes
- I make decisions independently about structure, content, and organization

## Directory Structure

```
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

## Adding a New Skill

### To Existing Plugin

```bash
mkdir -p <plugin>/skills/<skill-name>/{references,examples,scripts}
```

Create `SKILL.md`:
```yaml
---
name: Skill Name
description: This skill should be used when the user asks about "phrase 1", "phrase 2", or needs [topic] guidance.
---

# Skill Title

[Content in imperative form]
```

### To New Plugin

1. Create structure:
   ```bash
   mkdir -p <plugin>/.claude-plugin
   mkdir -p <plugin>/skills/<skill-name>
   ```

2. Create `<plugin>/.claude-plugin/plugin.json`:
   ```json
   {
     "name": "<plugin>",
     "description": "What it does",
     "version": "1.0.0",
     "author": {"name": "Clément Walter"}
   }
   ```

3. Create SKILL.md in the skill folder

4. Register in `.claude-plugin/marketplace.json`:
   ```json
   {
     "name": "<plugin>",
     "description": "What it does",
     "source": "./<plugin>"
   }
   ```

## Script Requirements

All Python scripts must be uv-compatible:

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

### SKILL.md
- Use third-person description: "This skill should be used when..."
- Include specific trigger phrases in quotes
- Body in imperative form (not "you should")
- Keep under 2,000 words
- Reference supporting files

### References
- Move detailed content here (>500 words on single topic)
- Name descriptively: `api-reference.md`, `workflow.md`

### Scripts
- Document with docstrings and usage examples
- Support `--dry-run` for destructive operations
- Use argparse for CLI

## Current Inventory

| Plugin | Skills | Scripts |
| ------ | ------ | ------- |
| `github-issues` | `github-workflow` | 4 milestone utilities |
| `chief-of-staff` | `agent-coordination` | none |

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
