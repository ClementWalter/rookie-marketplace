---
name: Documentation Writer
description: This skill should be used when an agent is assigned to write a section of technical documentation. Provides guidance on breaking down large tasks, using doc-coauthoring workflow, and coordinating with VibeKanban task management. Use when task description mentions "write section", "document this component", or "expand documentation".
version: 1.0.0
---

# Documentation Writer Guidance

This skill guides agents tasked with writing technical documentation sections. It emphasizes breaking down large work into manageable subtasks and coordinating via VibeKanban.

## ⚠️ CRITICAL: Base Branch Configuration

**ALWAYS use the current local branch as the base branch for VK task attempts, NEVER "main".**

When starting task attempts via `start_task_attempt`, you MUST:

1. Get the current branch name: `git branch --show-current`
2. Use that branch as `base_branch` in the repos parameter

```typescript
// ❌ WRONG - hardcoding "main"
start_task_attempt({
  repos: [{ repo_id: "...", base_branch: "main" }]
})

// ✅ CORRECT - using current branch
const currentBranch = await getCurrentBranch(); // e.g., "cw/comprehensive-doc"
start_task_attempt({
  repos: [{ repo_id: "...", base_branch: currentBranch }]
})
```

**Why this matters:** Tasks targeting the wrong branch will fail to commit changes properly, causing silent execution failures where agents mark work complete but produce no output.

## Core Principle: Break Down Large Tasks

**CRITICAL**: If your assigned documentation task is large (>2000 words or covers 3+ major topics), you MUST break it into subtasks rather than attempting to write everything at once.

### Why Break Down?

- ✅ Better focus and depth per subtask
- ✅ Easier to review incrementally
- ✅ Parallel work possible on subsections
- ✅ Prevents context overload
- ✅ Higher quality output

### When to Break Down

Break into subtasks if ANY of these apply:

| Indicator | Threshold | Action |
|-----------|-----------|--------|
| **Word count estimate** | >2000 words | Split into 2-4 subsections |
| **Major topics** | 3+ distinct topics | One subtask per topic |
| **Code examples** | 5+ examples needed | Group related examples into subtasks |
| **Codebase exploration** | 5+ files to analyze | Create exploration subtask first |
| **Time estimate** | >45 minutes | Break into 20-30 min chunks |

## Phase 1: Scope Assessment (ALWAYS DO THIS FIRST)

Before writing ANY content:

### 1. Read Task Requirements

- Review the full task description
- Note all TODO items to address
- Identify target file and section
- Check word count hints or scope guidance

### 2. Explore the Codebase

Use appropriate tools to understand scope:

```
For finding files:
- Glob tool for pattern matching
- Task tool with Explore agent for broad discovery

For understanding code:
- Read tool for specific files
- Grep for searching patterns
- Task tool with Explore agent for tracing flows
```

### 3. Estimate Scope

Create a rough outline with word estimates:

```markdown
## Proposed Outline

### 3.1 Topic A (~500 words)
- Subtopic 1
- Subtopic 2

### 3.2 Topic B (~800 words)
- Subtopic 1
- Subtopic 2
- Subtopic 3

### 3.3 Topic C (~1000 words)
- Complex subtopic requiring deep dive

**Total estimate: 2300 words → BREAK DOWN RECOMMENDED**
```

### 4. Make Break Down Decision

**If total >2000 words or 3+ major topics:**

→ **STOP writing content**
→ **Proceed to Phase 2: Create Subtasks**

**If manageable (<2000 words, focused scope):**

→ Proceed to Phase 3: Write Content

## Phase 2: Create Subtasks in VibeKanban

### Prerequisites

You need from your original task description:
- `project_id` (UUID) - Which VK project
- `task_id` (UUID) - Your current task ID
- Target file path
- Section numbering

### Breaking Down Strategy

**Option A: By Topic (Most Common)**
```
Original: "Document Coprocessor Architecture"
↓
Subtask 1: "Doc Coprocessor: Worker Architecture"
Subtask 2: "Doc Coprocessor: Scheduler & Job Orchestration"
Subtask 3: "Doc Coprocessor: GPU Optimization"
Subtask 4: "Doc Coprocessor: Database Schema"
```

**Option B: By Depth**
```
Original: "Document Authentication System"
↓
Subtask 1: "Doc Auth: High-Level Overview & Flow"
Subtask 2: "Doc Auth: Deep Dive - Implementation Details"
Subtask 3: "Doc Auth: Security Considerations & Best Practices"
```

**Option C: By Component**
```
Original: "Document Gateway Contracts"
↓
Subtask 1: "Doc Gateway: GatewayConfig & Decryption"
Subtask 2: "Doc Gateway: MultichainACL & CiphertextCommits"
Subtask 3: "Doc Gateway: Payment Protocol"
```

### Creating Subtasks

Use the vibe_kanban MCP tools:

```
1. Create subtask for each section:

mcp__vibe_kanban__create_task
  project_id: [same as parent]
  title: "Doc: Section X.Y - Subtopic Name"
  description: |
    **IMPORTANT: Use document-skills:doc-coauthoring skill**

    **Parent Task:** [parent-task-id]
    **Target File:** docs/codebase/src/components/example.md
    **Section:** 3.2 Subtopic Name

    Write focused documentation covering:
    - Topic detail 1
    - Topic detail 2
    - Topic detail 3

    **Word target:** ~500-800 words

    **Source files to reference:**
    - path/to/relevant/file.ts
    - path/to/another/file.sol

    **Success criteria:**
    - Remove [TODO] marker
    - Include code examples
    - Cross-link to related sections

    After completion, mark as inreview.
```

### Update Parent Task

After creating subtasks:

```
mcp__vibe_kanban__update_task
  task_id: [your-current-task-id]
  description: |
    [original description]

    ---
    **BROKEN DOWN INTO SUBTASKS:**
    - [subtask-1-id] Section X.1
    - [subtask-2-id] Section X.2
    - [subtask-3-id] Section X.3

    This parent task tracks subtask completion.
  status: inprogress
```

### Scaffold Target File

If not already done, create section placeholders:

```markdown
## 3.1 Topic A

[TODO: Pending subtask subtask-1-id]

## 3.2 Topic B

[TODO: Pending subtask subtask-2-id]

## 3.3 Topic C

[TODO: Pending subtask subtask-3-id]
```

### Report to Coordinator

**DO NOT** attempt to write content yourself. Instead:

1. Mark your task as `inreview`
2. Add a comment explaining the breakdown
3. Let the coordinator (Chief of Staff) spawn agents for subtasks

```
Task broken down into [N] focused subtasks (see description).
Each subtask is ~500-800 words and covers one coherent topic.
Ready for coordinator to spawn agents for parallel execution.
```

## Phase 3: Write Content (For Manageable Tasks)

Only reach this phase if scope assessment shows <2000 words and focused topic.

### Use Doc-Coauthoring Skill

**ALWAYS invoke the doc-coauthoring skill:**

```
Use document-skills:doc-coauthoring skill to:
1. Gather context efficiently
2. Structure content clearly
3. Iterate on drafts
4. Verify for readers
```

The doc-coauthoring skill provides a structured workflow. Follow its guidance.

### Content Structure

Every documentation section should have:

#### 1. Overview (10-15% of content)
```markdown
## Section Title

**Purpose:** One sentence describing what this section covers

Brief 2-3 sentence introduction establishing context.
```

#### 2. Core Content (70-80% of content)

Use appropriate subsections:

```markdown
### Key Concepts

[Explain foundational ideas]

### Architecture / Implementation

[Detail how it works]

### Code Examples

[Provide working examples from codebase]

### Best Practices / Common Pitfalls

[Practical guidance]
```

#### 3. Cross-Links & Next Steps (5-10% of content)

```markdown
**Related:**
- [Related Section A](../path/to/section.md)
- [Related Section B](./another-section.md)

**Next:** [What to read next](next-section.md) →
```

### Quality Checklist

Before marking task complete:

- [ ] Removed [TODO] marker from target section
- [ ] Included 2-4 code examples from actual codebase
- [ ] Added architecture diagram (ASCII art acceptable)
- [ ] Cross-linked to 2-3 related sections
- [ ] Used consistent terminology (check glossary)
- [ ] Verified technical accuracy against source code
- [ ] Provided practical value (not just theory)
- [ ] Length appropriate for scope (~500-1500 words for focused sections)

## Phase 4: Completion

### Mark Task Complete

```
mcp__vibe_kanban__update_task
  task_id: [your-task-id]
  status: inreview
```

### Self-Review Note

Add a brief note about what you accomplished:

```markdown
**Completed:**
- Documented [topic] with [N] code examples
- Added architecture diagram showing [X]
- Cross-linked to [related sections]
- ~[N] words

**Note:** [Any concerns or follow-up suggestions]
```

The coordinator will review and either approve (→ done) or provide feedback.

## Common Patterns

### Pattern: Component Documentation

```
1. Assess scope (usually 4-6 major topics)
2. Break down by topic:
   - Overview & Purpose
   - Key Contracts/Files
   - Architecture & Relationships
   - Recent Development Focus
   - Deep Dives (separate subtasks)
3. Create subtasks for deep dives only
4. Write overview sections yourself (lighter weight)
```

### Pattern: Workflow Documentation

```
1. Assess scope (usually 1-2 major flows)
2. If 2+ flows, break down:
   - One subtask per complete flow
3. Each flow subtask includes:
   - Step-by-step breakdown
   - Sequence diagram
   - Example scenarios
   - Error handling
```

### Pattern: Reference Documentation

```
1. Assess scope (# of items to document)
2. If 10+ items:
   - Create overview subtask
   - Create deep-dive subtasks (5-7 items each)
3. Use tables for reference lists
4. Provide 1-2 detailed examples
```

## Quick Decision Tree

```
Receive doc writing task
       ↓
Read full requirements
       ↓
Explore codebase (10-15 min)
       ↓
Estimate scope
       ↓
   ┌───────────────┐
   │ >2000 words?  │
   │ OR 3+ topics? │
   └───────────────┘
      ↙         ↘
    YES         NO
     ↓           ↓
Create       Write
subtasks     content
in VK        with
     ↓       doc-coauthoring
Mark as          ↓
inreview     Mark as
             inreview
```

## Examples

See `examples/` directory:
- `examples/breakdown-decision.md` - Example scope assessment
- `examples/subtask-creation.md` - Creating VK subtasks
- `examples/section-content.md` - Well-structured documentation section

## Tips for Success

1. **Start with exploration** - Never write before understanding scope
2. **Be ruthless about breaking down** - When in doubt, break it down
3. **Use the doc-coauthoring skill** - It's specifically designed for this
4. **Write for readers, not yourself** - Explain concepts clearly
5. **Include real code** - Reference actual codebase, not hypotheticals
6. **Cross-link liberally** - Connect related concepts
7. **Iterate** - First draft doesn't need to be perfect

## Troubleshooting

**Q: I don't have project_id or task_id**

A: Check your task description. Coordinators should include these. If missing, ask in your task output.

**Q: Should I create subtasks via Task tool or VK?**

A: ALWAYS use VK MCP tools (`mcp__vibe_kanban__create_task`). This maintains central tracking.

**Q: What if I'm unsure about breaking down?**

A: Err on the side of breaking down. Create outline, estimate words, and if borderline (1500-2000), break it down.

**Q: Can I write a quick draft first?**

A: No. If scope is large, creating subtasks IS the task. Don't write content for large scopes.

---

**Remember:** Your job is to produce HIGH-QUALITY, FOCUSED documentation. Breaking down large tasks is not "extra work" - it's essential to quality.
