# Safety & Isolation Rules

<important if="writing files, running commands, or accessing other workspaces">

## Workspace Isolation
- Each workspace has its own `.claude-memory/memory.db`
- NEVER cross-read another workspace's memory
- Knowledge base is shared (read-only)
- MCP tools auto-detect current workspace

## Security
- Never commit secrets, API keys, tokens, or credentials
- Never include personal names, hardcoded user paths, or machine-specific info in shared files
- Validate all external input before processing
- Check `.blitz-active` marker before running evolve — never evolve during blitz

## Git Safety
- Always review diffs before committing
- Never force-push without explicit user approval
- Commit after each completed phase, not in bulk

</important>
