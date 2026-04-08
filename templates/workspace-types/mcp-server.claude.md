# MCP Server — Workspace Rules

## MCP Architecture
- Entry point: `src/server.py`
- Tools: `src/tools/` — one module per tool, clear input/output schema
- Transport: stdio (default) or SSE/HTTP

## Ship
- `/deploy:ship` writes server config to `.mcp.json`
- Claude Code auto-discovers the server on next restart

## Conventions
- Every tool must have a JSON schema for inputs and outputs
- Tools should be idempotent where possible
- Error messages must be user-readable (Claude shows them to the user)
- Keep server lightweight — heavy work in separate processes
