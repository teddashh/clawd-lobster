# Memory Server

> Unified MCP memory server with 4-layer architecture, salience engine, and 32 tools.

## What It Does

Memory Server is the core persistence layer for clawd-lobster. It provides structured memory storage across four layers: L1.5 (Claude Code native MEMORY.md), L2 (local SQLite), L3 (markdown files synced via git), and L4 (optional Oracle cloud). All other skills that need to remember anything depend on this server.

## How It Works

Runs as an always-on MCP server (`python -m mcp_memory.server`) that exposes 32 tools over the MCP protocol. Claude Code connects to it automatically on startup.

**Salience engine** keeps memories relevant over time:
- Access a memory: salience +5%
- Reinforce a memory: salience +20%
- Passive decay: -1% per day (30-day half-life)

**Key tool groups:**
- **Store/Record**: `memory_store`, `memory_record_decision`, `memory_record_resolved`, `memory_record_question`, `memory_record_knowledge`
- **Retrieve**: `memory_list`, `memory_get`, `memory_get_summary`, `memory_search`
- **Manage**: `memory_delete`, `memory_reinforce`, `memory_compact`, `memory_status`
- **Skills**: `memory_learn_skill`, `memory_list_skills`, `memory_improve_skill`
- **Audit/Logs**: `memory_log_action`, `memory_audit_search`, `memory_audit_stats`, `memory_daily_report`, `memory_activity_log`
- **TODOs**: `memory_todo_add`, `memory_todo_list`, `memory_todo_update`, `memory_todo_search`
- **Cloud**: `memory_oracle_summary`

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `oracle_enabled` | boolean | `false` | Enable Oracle L4 cross-workspace sync |
| `embeddings_enabled` | boolean | `false` | Enable OpenAI embeddings for vector search |

## Dependencies

| Type | Requirement |
|------|-------------|
| System | Python 3 |
| Python | `fastmcp >=3.0, <4.0` |
| Skills | None (this is the foundation) |

## Credentials

- **Oracle L4** (optional): Oracle DB connection string, only needed if `oracle_enabled: true`
- **OpenAI** (optional): API key for embeddings, only needed if `embeddings_enabled: true`

No credentials are required for the default SQLite-only configuration.

## Maintenance

- **Core skill** -- cannot be disabled (`alwaysOn: true`).
- Health check: MCP ping every 300 seconds.
- Source code lives in the `mcp_memory/` Python package within this directory.
- This is the only skill without a `SKILL.md` file; this README serves as its primary documentation.
- SQLite database is stored locally; back it up if you care about L2 data.
- When upgrading `fastmcp`, test that the MCP server still starts before committing.

**Version:** 0.4.0 | **Kind:** mcp-server | **Category:** core
