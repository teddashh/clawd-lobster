# Migrate — Import from existing AI agent setups

When the user asks to migrate or import from an existing setup, scan these paths and import what you find:

## Sources to scan

### claude-setup (predecessor)
- Path: `~/Documents/claude-setup/`
- Import: `workspace-map.json` → convert to `workspaces.json` format
- Import: `global/soul/` → copy to `soul/`
- Import: `secrets/wallet/` → copy to `secrets/`
- Import: `.claude-memory/memory.db` from each workspace → keep in place
- Import: `scripts/oracle_*.py` → note Oracle config for L4 setup
- Note: `mcp-memory-server/` has been absorbed into clawd-lobster skills/

### Raw Claude Code
- Path: `~/.claude/`
- Import: `CLAUDE.md` → merge useful rules into template
- Import: `.mcp.json` → note existing MCP servers
- Import: `settings.json` → merge hooks and permissions
- Import: `projects/*/memory/` → auto-memory files, read and store key items to L2

### OpenClaw
- Path: `~/.openclaw/`
- Import: `SOUL.md` → copy to `soul/personality.md`
- Import: `MEMORY.md`, `USER.md` → read and store items to L2 via memory_record_*
- Import: `skills/` → list available skills, suggest clawd-lobster equivalents
- Import: `workspace/` → note workspace configs
- Import: `exec-approvals.json` → convert to settings.json permissions

### Hermes Agent
- Path: `~/.hermes/`
- Import: memory database → read and store items to L2
- Import: skills/ → list skills, suggest equivalents
- Import: profiles/ → note multi-profile configs
- Import: `.env` → extract non-secret config values

## Migration process

1. Scan all paths, report what was found
2. Ask user which sources to import (default: all found)
3. For each source:
   a. Read all relevant files using Read tool
   b. Extract important content (decisions, knowledge, preferences, configs)
   c. Store to L2 via MCP memory tools (memory_record_decision, memory_record_knowledge, etc.)
   d. Copy config files to appropriate locations
   e. Report what was imported
4. Show summary: X decisions, Y knowledge items, Z configs imported
5. Suggest next steps (verify configs, test MCP connection, etc.)

## Important
- Never overwrite existing clawd-lobster configs without asking
- Merge, don't replace
- Skip binary files and credentials (note them for manual setup)
- Use `--dry-run` flag to preview without changes
