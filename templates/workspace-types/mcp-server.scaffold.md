# MCP Server Scaffold

## Directory Structure

```
<workspace>/
├── CLAUDE.md
├── workspace.json
├── .gitignore
├── knowledge/
├── openspec/
│   ├── project.md
│   ├── changes/
│   └── specs/
├── src/
│   ├── server.py            # MCP server entry point
│   ├── tools/               # Tool implementations (one per file)
│   ├── resources/           # Resource providers
│   └── config.py            # Server configuration
├── tests/
│   ├── unit/
│   └── integration/         # Test tool calls end-to-end
├── pyproject.toml           # or package.json for Node.js
└── deploy/                  # Optional: Docker
    ├── Dockerfile
    └── docker-compose.yml
```

## Notes

- Default transport: stdio (for Claude Code integration).
- Ship via `.mcp.json` registration — `/deploy:ship` handles this.
- Each tool in `src/tools/` should be self-contained with clear input/output schemas.
- Test integration: call tools via MCP protocol in tests.
- Optional Docker for running as SSE/HTTP server instead of stdio.
