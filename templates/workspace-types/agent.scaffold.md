# Agent Scaffold

## Directory Structure

```
<workspace>/
├── CLAUDE.md
├── workspace.json
├── .gitignore
├── knowledge/
├── skills/learned/
├── openspec/
│   ├── project.md
│   ├── changes/
│   └── specs/
├── src/
│   ├── agent.py             # Main agent entry point
│   ├── tools/               # MCP tool implementations
│   ├── prompts/             # System prompts and templates
│   └── config.py            # Agent configuration
├── tests/
│   ├── unit/
│   └── e2e/                 # Agent end-to-end tests
└── deploy/                  # Optional: Docker for containerized agent
    ├── Dockerfile
    └── docker-compose.yml
```

## Notes

- Agents default to local-only deployment.
- Optional Docker support for running as a background service.
- `tools/` contains MCP tool implementations the agent exposes.
- `prompts/` contains system prompts — version controlled, not hardcoded.
- Registration with the agent framework is via `/deploy:ship` (type-aware).
