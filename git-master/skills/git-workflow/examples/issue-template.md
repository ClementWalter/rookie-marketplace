# Issue Template: Why/What/How Structure

Use this template when creating GitHub issues for clear communication.

---

## Bug Report Template

```markdown
## Why

[Describe the problem and its impact]

- What is broken or not working as expected?
- How does this affect users/developers?
- What is the expected behavior?

## What

[Describe what needs to be fixed]

- Specific component or feature affected
- Scope of the fix

## How

[Technical approach to fix]

1. Step 1: Investigate root cause
2. Step 2: Implement fix
3. Step 3: Add regression test

## Reproduction Steps

1. Go to '...'
2. Click on '...'
3. See error

## Environment

- OS: [e.g., macOS 14.0]
- Browser: [e.g., Chrome 120]
- Version: [e.g., v1.2.3]

## Acceptance Criteria

- [ ] Bug no longer reproducible
- [ ] Regression test added
- [ ] No new warnings in logs
```

---

## Feature Request Template

```markdown
## Why

[Problem statement or opportunity]

- What user need does this address?
- What is the current pain point?
- What value does this provide?

## What

[Solution description]

- High-level description of the feature
- User-facing changes
- Non-goals (what this is NOT)

## How

[Implementation approach]

### Technical Design

1. Component A changes
2. Component B additions
3. API modifications

### Dependencies

- Requires: #123 to be completed first
- Blocks: #456 depends on this

## Acceptance Criteria

- [ ] Feature works as described
- [ ] Documentation updated
- [ ] Tests cover main use cases
- [ ] Performance impact assessed
```

---

## Chore/Task Template

```markdown
## Why

[Reason for this maintenance task]

- Technical debt being addressed
- Improvement opportunity
- Compliance or security requirement

## What

[Scope of work]

- Files/components affected
- Expected outcome

## How

[Approach]

1. Step 1
2. Step 2
3. Step 3

## Acceptance Criteria

- [ ] Task completed
- [ ] No regressions introduced
- [ ] Relevant tests pass
```

---

## Epic Template (Parent Issue)

```markdown
## Overview

[High-level description of this epic/initiative]

## Goals

- Goal 1
- Goal 2
- Goal 3

## Non-Goals

- What this epic does NOT include

## Tasks

Sub-issues to complete this epic:

- [ ] #101 - Task 1
- [ ] #102 - Task 2
- [ ] #103 - Task 3

## Success Metrics

- Metric 1: Target value
- Metric 2: Target value

## Timeline

- Start: YYYY-MM-DD
- Target completion: YYYY-MM-DD
- Milestone: v1.0

## Dependencies

- Depends on: #50 (external API ready)
- Blocked by: None currently
```
