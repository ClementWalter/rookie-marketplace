## MANDATORY: Completion Checklist

**You CANNOT complete this task until you have done ALL of the following:**

### 1. Run CI/Build/Tests
Run the project's test suite or build command. Common patterns:
```bash
# Check for package.json scripts
npm test OR npm run build OR npm run check

# Check for Makefile
make test OR make check

# Check for Cargo.toml
cargo test && cargo clippy

# Check for pyproject.toml
pytest OR uv run pytest
```

### 2. Verify git status is clean
```bash
git status
```
All changes should be committed. No untracked files that should be included.

---

**RESPOND WITH:**
- `approve` — ONLY if CI/tests passed and git is clean
- `block: [reason]` — if you haven't completed the checklist, explaining what's missing

**Note:** Trunk formatting/linting is handled automatically by a global hook after each file edit.

**If you claim completion without running these checks, you are violating process. The Chief of Staff will reject your work.**
