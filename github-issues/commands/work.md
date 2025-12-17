# Work Command

Autonomous issue management and PR workflow.

## Arguments

- `$ARGUMENTS` - Optional: PR URL to review and create issues from

## Examples

```
/work                                           # Fetch and work on unassigned issues
/work https://github.com/org/repo/pull/123      # Review PR, create issues, then work
```

## Instructions

You are an autonomous agent that manages GitHub issues and pull requests.

### Pre-flight: Discover CI Requirements

**CRITICAL**: Before any work, check CI configuration:

```bash
ls .github/workflows/
cat .github/workflows/*.yml
```

Common CI checks to run locally before pushing:
- `trunk check --ci` - Linting and formatting
- `cargo build` - Rust compilation
- `cargo test` - Rust tests
- `cargo clippy` - Rust lints

**NEVER push code that would fail CI. Always run CI checks locally first.**

### Mode 1: PR Review (when $ARGUMENTS is a PR URL)

1. **Fetch the PR**: `gh pr view <url> --json body,comments,reviews,diff`
2. **Analyze** for code quality issues, improvements, suggestions
3. **Create consolidated issues** - Group related comments into meaningful issues:
   - Address multiple related concerns in a single issue
   - Minimize potential merge conflicts (group by file/module)
   - Are actionable and well-scoped
   - Include clear Why/What/How sections
4. **Proceed to Mode 2**

### Mode 2: Issue Resolution (default, or after Mode 1)

1. **Fetch open unassigned issues**:
   ```bash
   gh issue list --repo <repo> --state open --json number,title,assignees,body --jq '.[] | select(.assignees | length == 0)'
   ```

2. **Get current user**: `gh api user --jq '.login'`

3. **Assign all issues** to yourself in parallel

4. **For each issue, in parallel**:
   - Create git worktree at `/tmp/<repo>-issue-<number>` with branch `fix/issue-<number>`
   - Implement the fix
   - Run ALL CI checks locally
   - Fix any CI failures before committing
   - Commit with message `Fixes #<number>`
   - Push and create PR

5. **Report PR URLs** when complete

### Mode 3: Rebase Loop

After initial PRs are created, or when user says "rebase":

1. Fetch open PRs: `gh pr list --state open --json number,title,headRefName`
2. Check for review comments: `gh api repos/<owner>/<repo>/pulls/<number>/comments`
3. For each PR in parallel:
   - Go to its worktree
   - `git fetch origin main && git rebase origin/main`
   - Resolve conflicts
   - Address review comments
   - Run ALL CI checks locally
   - Fix issues and amend commit
   - Force push
4. Report status for all PRs

### Cleanup

When all PRs are merged:
- Remove worktrees: `git worktree remove /tmp/<repo>-issue-<number> --force`
- Verify: `git worktree list`
- Update main: `git checkout main && git pull origin main`

### Repository Detection

```bash
gh repo view --json nameWithOwner --jq '.nameWithOwner'
```
