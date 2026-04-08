# AI Agent — Workspace Rules

## Agent Architecture
- Entry point: `src/agent.py`
- Tools: `src/tools/` — each tool is a separate module
- Prompts: `src/prompts/` — version controlled, never hardcoded

## Deploy
- Default: local execution only
- Optional: Docker container for background service
- Registration: `/deploy:ship` registers with agent framework

## Conventions
- All tool calls must be idempotent where possible
- Prompts are data (in files), not code (in strings)
- Agent config separate from secrets
- Test with real tool calls in E2E tests, mock in unit tests
