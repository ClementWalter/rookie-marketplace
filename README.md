# Rookie Marketplace

Claude Code skills marketplace - contextual knowledge auto-loaded based on user queries.

## Overview

This marketplace contains skills for Claude Code that provide specialized knowledge and workflows. Skills automatically load when Claude detects relevant queries based on trigger phrases.

## Available Plugins

### chief-of-staff

Agent coordination and task orchestration.

**Skills:**

| Skill | Triggers On |
| ----- | ----------- |
| `agent-coordination` | "coordinate agents", "orchestrate tasks", "chief of staff mode", "vibekanban workflow", "dispatch agents" |
| `doc-writing-coordination` | "coordinate document writing", "manage doc writers", "orchestrate documentation" |
| `efficient-scraping` | "scrape website", "extract data", "web scraping", "fetch API", "programmatic extraction" |

**What it provides:**
- Multi-agent coordination patterns
- Task lifecycle management
- VibeKanban API reference
- Document writing coordination
- **Efficient web scraping guidance** (uv scripts over reading thousands of lines)

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

---

### rust-dev

Senior-level Rust development practices and workspace architecture.

**Skills:**

| Skill | Triggers On |
| ----- | ----------- |
| `senior-rust-practices` | "rust workspace", "rust best practices", "cargo workspace", "rust architecture", "rust dependencies", "rust testing strategy" |

**What it provides:**
- Workspace architecture patterns ("one product = one workspace")
- Crate organization and boundary design
- Dependency hygiene (workspace deps, features, MSRV)
- Testing pyramid (unit, integration, e2e, property tests)
- CI quality gates and compile-time optimization

**Hooks:**
- `Stop`: Enforces running `cargo test` and `trunk check` before task completion

---

### air-cryptographer

Expert-level AIR (Algebraic Intermediate Representation) cryptographer for ZK constraint systems.

**Skills:**

| Skill | Triggers On |
| ----- | ----------- |
| `air-expertise` | "AIR", "algebraic intermediate representation", "ZK constraints", "trace design", "constraint soundness", "lookup arguments", "STARK" |

**What it provides:**
- Finite field foundations and polynomial mechanics
- Trace design principles (column classification, row semantics)
- Constraint categories (transition, boundary, booleanity, selectors)
- Global consistency arguments (permutation, lookup, memory)
- Adversarial witness exercises

**References:**
- `review-checklist.md`: Complete systematic AIR soundness review procedure

---

### security-researcher

Senior security researcher guidelines based on NIST, CIS, OWASP, MITRE ATT&CK, and SLSA frameworks.

**Skills:**

| Skill | Triggers On |
| ----- | ----------- |
| `security-audit` | "security audit", "vulnerability assessment", "pentest", "security review", "threat model" |

**What it provides:**
- Web application security checklist (OWASP Top 10)
- Smart contract security patterns
- Supply chain security (SLSA)
- ZK/cryptography security review
- General crypto implementation review

---

### growth-hacker

Modern growth strategy: loops + product-led growth + disciplined experimentation.

**Skills:**

| Skill | Triggers On |
| ----- | ----------- |
| `growth-strategy` | "growth strategy", "GTM plan", "growth loops", "A/B testing", "viral loops", "PLG" |

**What it provides:**
- Growth model design (NSM, input metrics)
- Growth loops > funnels framework
- Experimentation engine (RICE/ICE scoring)
- Lever-specific playbooks (activation, viral, SEO, lifecycle)
- Privacy and measurement constraints

**Note:** For LinkedIn-specific growth automation, see `linkedin-growth-agent`.

---

### linkedin-growth-agent

Daily LinkedIn growth automation for Clément Walter.

**Skills:**

| Skill | Triggers On |
| ----- | ----------- |
| `daily-growth` | "linkedin growth", "cross-post twitter", "linkedin engagement", "daily growth checklist" |

**What it provides:**
- Daily execution checklist
- Twitter → LinkedIn content adaptation
- French tone/voice guidelines (50 patterns)
- LinkedIn algorithm best practices
- Supervised workflow (draft only, user posts)

**Target accounts:**
- Twitter: @ClementWalter
- LinkedIn: Clément Walter

---

### git-workflow

Git worktree workflow commands.

**Commands:**

| Command | Purpose |
| ------- | ------- |
| `/merge` | Merge worktree changes back to main branch |

---

### 1password-mcp

Secure 1Password credential access via official `op` CLI.

**Skills:**

| Skill | Triggers On |
| ----- | ----------- |
| `credential-lookup` | "get credential", "1password", "fetch password", "vault lookup" |

**MCP Tools:**
- `get_credential`: Retrieve username/password from 1Password item

**Requires:** 1Password CLI (`op`) installed and configured

---

### gmail-mcp

Secure Gmail access via IMAP/SMTP with 1Password credential storage.

**Skills:**

| Skill | Triggers On |
| ----- | ----------- |
| `gmail-tools` | "send email", "read email", "gmail", "email inbox" |
| `email-assistant` | "draft email", "compose email", "email workflow" |

**MCP Tools:**
- `list_emails`: List recent emails from inbox
- `read_email`: Read full email content
- `send_email`: Send email via SMTP
- `search_emails`: Search emails using IMAP syntax

**Requires:** Gmail app password stored in 1Password

---

## Key Guidelines

### Efficient Data Extraction

**Use uv scripts for web scraping instead of reading raw HTML/JSON into context:**

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "beautifulsoup4"]
# ///
# Extract ONLY needed fields → output structured JSON
```

This reduces token usage by 10-100x and improves output quality.

See `chief-of-staff/skills/efficient-scraping/SKILL.md` for full guidance.

---

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
│   └── skills/
│       ├── agent-coordination/
│       ├── doc-writing-coordination/
│       └── efficient-scraping/
├── github-issues/
│   └── skills/
│       └── github-workflow/
├── rust-dev/
│   └── skills/
│       └── senior-rust-practices/
├── air-cryptographer/
│   └── skills/
│       └── air-expertise/
├── security-researcher/
│   └── skills/
│       └── security-audit/
├── growth-hacker/
│   └── skills/
│       └── growth-strategy/
├── linkedin-growth-agent/
│   └── skills/
│       └── daily-growth/
├── git-workflow/
│   └── commands/
│       └── merge.md
├── 1password-mcp/
│   └── skills/
│       └── credential-lookup/
├── gmail-mcp/
│   └── skills/
│       ├── gmail-tools/
│       └── email-assistant/
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

All Python scripts **must** use uv inline metadata:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

## License

MIT
