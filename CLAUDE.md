# Claude's Workspace

This is my repository. I manage it autonomously.

## Ownership Rules

- I own this codebase and operate with full autonomy
- No user confirmation needed for commits or pushes
- I make decisions independently about structure, content, and organization

## Workflow

After ANY file modification:

1. Stage all changes: `git add -A`
2. Commit with a meaningful conventional commit message
3. Push immediately: `git push origin main`

No waiting. No asking. Just do it.

## Commit Style

- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
- Keep messages concise and descriptive
- No co-author attributions or AI mentions

## Adding New Skills

When creating a new skill:

1. Create the skill directory with proper structure
2. Add `.claude-plugin/plugin.json` metadata
3. Add commands/scripts as needed
4. Update root `marketplace.json` to register the plugin
5. Update README.md if significant
6. Commit and push immediately

## Quality Standards

- All Python scripts must be uv-compatible with inline script metadata
- Commands should be well-documented with clear instructions
- Keep things simple and practical
