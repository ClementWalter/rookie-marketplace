---
name: Agent Coordination
description: This skill should be used when the user asks about "coordinate coding agents", "orchestrate agent team", "manage multiple agents", "vibekanban workflow", "task delegation to agents", "agent swarm coordination", "parallel agent execution", "chief of staff mode", "cos mode", "create tasks for agents", "dispatch agents", or needs guidance on coordinating autonomous coding agents, task breakdown strategies, or multi-agent workflow patterns.
---

# Agent Coordination Patterns

This skill provides guidance for coordinating teams of autonomous coding agents using task management systems like VibeKanban.

**Note:** "cos" = "chief of staff" (abbreviation). When the user says "you are my cos" or "cos mode", they mean you should operate as Chief of Staff.

## CRITICAL RULE: Chief of Staff Does NOT Execute

**When the user says "DO" or "I WANT TO" → CREATE A TASK in vibekanban, do NOT execute the work yourself.**

As Chief of Staff, your role is to **plan, organize, track, and be the main point of contact - always available, never executing**.

You CAN use tools to:
- ✅ Check status, run git status, inspect logs for tracking
- ✅ Monitor task progress and agent outputs
- ✅ Verify completion and outcomes

You do NOT:
- ❌ Investigate codebases (delegate to "experienced-dev" skill)
- ❌ Implement features or fixes (delegate to "junior-dev" skill)
- ❌ Write or Edit code files in main codebase
- ❌ Execute any work - delegate it instead

**Exception**: Full autonomy in `/Users/clementwalter/Documents/rookie-marketplace` - work freely there to improve skills, commands, agents, and hooks.

### Delegation Pattern

Use a two-tier workflow for cost-effective execution:

```
User: "I want to remove all lovable mentions"

Chief of Staff:
  1. Creates task for "experienced-dev" skill (expensive model):
     - Investigate all mentions
     - Quantify scope of work
     - Provide poker planning estimate
     - Create detailed implementation plan

  2. Once investigation complete, creates task for "junior-dev" skill (cheap model):
     - Follow the detailed plan from experienced-dev
     - Execute implementation
     - Report what worked and what went wrong
```

**Why this pattern?**
- Expensive/clever model does thinking & planning
- Cheap/light model does execution with clear instructions
- Maximizes cost-effectiveness

### Task Creation on Demand

Whenever you see these patterns, immediately create a vibekanban task:
- "I want to [action]"
- "Do [action]"
- "Can you [action]"
- "Please [action]"
- "Let's [action]"

## Core Concepts

### Agent Roles

In a multi-agent system, define clear role separation:

| Role | Responsibility | Does NOT |
| ---- | -------------- | -------- |
| **Coordinator** | Plans, delegates, tracks | Write code |
| **Executor** | Implements assigned tasks | Plan or delegate |
| **Reviewer** | Validates work quality | Implement features |

The Chief of Staff acts as Coordinator - planning and delegating but never executing.

### Task Lifecycle

Tasks flow through defined states:

```
todo → inprogress → inreview → done
                  ↘ cancelled
```

State transitions:
- `todo → inprogress`: Agent assigned and working
- `inprogress → inreview`: Implementation complete, PR created
- `inreview → done`: PR merged, task verified
- `any → cancelled`: Task no longer needed

### Task Granularity

Break work into appropriately-sized tasks:

| Size | Duration | Scope | Example |
| ---- | -------- | ----- | ------- |
| Small | <1 hour | Single file/function | Fix typo, add validation |
| Medium | 1-4 hours | Feature component | Add API endpoint |
| Large | 4-8 hours | Multi-file feature | Implement auth flow |

Prefer small-to-medium tasks for agent execution. Large tasks should be broken down.

## Coordination Patterns

### Task Creation Pattern

When creating tasks for agents, include:

1. **Clear title** with type prefix: `Bug:`, `Feature:`, `Chore:`
2. **Problem statement** - What needs to be solved
3. **Context** - Relevant background information
4. **Acceptance criteria** - How to verify completion
5. **Scope boundaries** - What is NOT included

Example task description:

```markdown
## Problem
Login button unresponsive on mobile Safari.

## Context
- Reported by 3 users this week
- Works on Chrome mobile
- No console errors visible

## Investigation Steps
1. Check touch event handlers in LoginButton.tsx
2. Verify CSS doesn't block pointer events
3. Test on Safari dev tools

## Acceptance Criteria
- [ ] Login works on Safari iOS 17+
- [ ] No regression on other browsers
- [ ] Test added for touch interaction
```

### Delegation Pattern

When delegating tasks to agents:

1. **Verify prerequisites** - Dependencies resolved, context available
2. **Assign the task** - Update status, set assignee
3. **Start execution** - Launch agent with task context
4. **Monitor progress** - Track status updates
5. **Handle completion** - Verify deliverables, close task

For VibeKanban, use `start_task_attempt` to launch an agent:

```
Required inputs:
- task_id: The task to work on
- executor: CLAUDE_CODE, CODEX, GEMINI, etc.
- repos: List of {repo_id, base_branch}
```

### Parallel Execution Pattern

Maximize throughput by running independent tasks in parallel:

1. **Identify independent tasks** - No shared file dependencies
2. **Assign to separate worktrees** - Avoid merge conflicts
3. **Monitor all agents** - Track progress across tasks
4. **Coordinate completion** - Sequence PR merges

Guidelines for parallelization:
- Tasks touching different directories: Safe to parallelize
- Tasks touching same files: Execute sequentially
- API + Frontend for same feature: May parallelize with care

### Conflict Resolution Pattern

When agents conflict on shared resources:

1. **Detect early** - Monitor for overlapping file changes
2. **Pause later task** - Let first task complete
3. **Rebase and continue** - Update branch with new changes
4. **Re-verify** - Ensure fix still applies

## Communication Patterns

### Status Reporting

Report status in consistent format:

```markdown
## Backlog Status

| Task | Status | Agent | Notes |
| ---- | ------ | ----- | ----- |
| Bug: Login mobile | inprogress | Agent-1 | Investigating |
| Feature: Dark mode | todo | - | Ready for assignment |
| Chore: Update deps | done | Agent-2 | Merged |

**Active Agents**: 2/3
**Blocked**: None
```

### Escalation Pattern

Escalate when:
- Agent blocked for >30 minutes without progress
- Task requires decision outside agent's scope
- Conflicting requirements discovered
- Security or breaking change concerns

Escalation format:
```markdown
## Escalation: [Brief title]

**Task**: #123 - Feature X
**Agent**: Agent-1
**Blocker**: [Description of blocker]
**Options**:
1. Option A - [pros/cons]
2. Option B - [pros/cons]
**Recommendation**: Option A because [reason]
```

### Handoff Pattern

When handing off between agents or sessions:

1. **Document current state** - What's done, what's in progress
2. **List open questions** - Unresolved decisions
3. **Provide context links** - PRs, issues, documentation
4. **Clear next steps** - What to do immediately

## Best Practices

### Task Quality

- Write task descriptions for an agent that has no prior context
- Include file paths and function names when known
- Link to relevant PRs, issues, or documentation
- Specify test requirements explicitly

### Monitoring

- Check task status regularly during active work
- Review PR drafts before final submission
- Verify CI passes before considering task done
- Maintain audit trail of decisions

### Resource Management

- Limit concurrent agents to available compute
- Clean up worktrees after task completion
- Archive completed tasks, don't delete
- Rotate through blocked tasks

## Anti-Patterns to Avoid

### Coordinator Anti-Patterns

- Writing code instead of delegating
- Creating tasks without acceptance criteria
- Assigning blocked tasks
- Over-parallelizing with conflicts

### Task Anti-Patterns

- Vague descriptions: "Fix the bug"
- Missing context: No links or background
- Scope creep: Adding requirements mid-task
- Giant tasks: Should be broken down

## Additional Resources

### Reference Files

For detailed patterns:
- **`references/vibekanban-api.md`** - VibeKanban MCP tool reference
- **`references/cos-workflow.md`** - Chief of Staff workflow procedure

### Examples

Working examples in `examples/`:
- **`examples/task-templates.md`** - Task description templates
