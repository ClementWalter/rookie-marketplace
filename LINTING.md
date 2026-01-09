# Linting Rules

This document lists linting rules that must be followed to pass `trunk check`. **This is a living document** - update it when new rules are discovered.

A global PostToolUse hook runs `trunk fmt` and `trunk check --fix` after every file edit, but following these rules upfront avoids fix loops.

## Markdown Rules (markdownlint)

### MD040: Fenced code blocks must have a language

**Wrong:**

````text
```
code here
```
````

**Right:**

````text
```bash
code here
```
````

Common languages: `bash`, `python`, `json`, `yaml`, `markdown`, `rust`, `javascript`, `typescript`, `text`

Use `text` for generic output or when no syntax highlighting applies.

### MD041: First line must be a top-level heading

**Wrong:**

```markdown
This is some intro text.

# Heading
```

**Right:**

```markdown
# Document Title

This is some intro text.
```

**Exception:** YAML frontmatter is allowed before the heading:

```markdown
---
name: My Skill
---

# My Skill
```

### MD034: No bare URLs

**Wrong:**

```markdown
Check out https://example.com for more info.
```

**Right:**

```markdown
Check out <https://example.com> for more info.
Check out [Example](https://example.com) for more info.
```

### MD036: Don't use emphasis instead of headings

**Wrong:**

```markdown
**Section Title**

Content here.
```

**Right:**

```markdown
### Section Title

Content here.
```

### MD058: Tables must be surrounded by blank lines

**Wrong:**

```markdown
Some text
| Col1 | Col2 |
|------|------|
| A | B |
More text
```

**Right:**

```markdown
Some text

| Col1 | Col2 |
| ---- | ---- |
| A    | B    |

More text
```

### MD060: Table column count must be consistent

Ensure all rows have the same number of columns, including the header separator.

## Python Rules (ruff)

### B007: Loop variable not used in body

**Wrong:**

```python
for item in items:
    print("processing")  # item not used
```

**Right:**

```python
for _item in items:  # prefix with underscore
    print("processing")

# Or if you need the count:
for _ in items:
    print("processing")
```

### General Python

- Use `from __future__ import annotations` for type hints
- Prefer f-strings over `.format()` or `%`
- Use `pathlib.Path` over `os.path`

## Adding New Rules

When `trunk check` reveals a new recurring issue:

1. Add the rule to this document with wrong/right examples
2. Commit with message: `docs: add [RULE_ID] to LINTING.md`
3. Fix existing violations
