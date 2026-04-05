# Migrate — Import from existing AI agent setups

!ls -d ~/.claude 2>/dev/null && echo "Found: ~/.claude" || true
!ls -d ~/.openclaw 2>/dev/null && echo "Found: ~/.openclaw" || true
!ls -d ~/.hermes 2>/dev/null && echo "Found: ~/.hermes" || true
!ls -d ~/Documents/claude-setup 2>/dev/null && echo "Found: ~/Documents/claude-setup" || true

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

## Gotchas

1. **Overwriting instead of merging.** Claude's instinct is to write a fresh config file. Migration MUST merge into existing configs, preserving any clawd-lobster settings already configured. Read the destination file first, merge the new entries, then write.

2. **Importing secrets accidentally.** Source directories often contain `.env` files, API keys in config files, or credentials in memory databases. Claude must skip these and note them for manual setup — never store credentials in L2 memory or copy them to new config files.

3. **Path assumptions across operating systems.** `~/Documents/claude-setup/` may not exist on Linux. `~/.openclaw/` may be at a different path on Windows. Always use the `!command` detection above to verify which sources actually exist before scanning.

4. **Stale or corrupted SQLite databases.** Old memory databases from previous agent setups may have schema mismatches or corrupted data. When reading from a foreign `.claude-memory/memory.db`, catch SQLite errors gracefully and report which items could not be read instead of failing the entire migration.

5. **Double migration creates duplicates.** Running `/migrate` twice imports the same items again. Before storing each item via `memory_record_*`, search for existing items with matching titles or content to avoid duplicates. Report skipped duplicates in the summary.
