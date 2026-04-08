# Workspace Type Templates

Each workspace type defines a scaffold structure, a `workspace.json` template,
and type-specific CLAUDE.md instructions. The `/spec` skill reads these during
Phase 2 (Workspace Creation) to generate the appropriate project skeleton.

## Available Types

| Type | Use Case | Docker | Deploy |
|------|----------|--------|--------|
| `webapp` | Full-stack web application | Yes (full stack) | dev + staging + prod |
| `api` | Backend API service | Yes (backend) | dev + staging + prod |
| `agent` | AI agent or automation tool | Optional | Register with framework |
| `skill` | Clawd-Lobster skill | No | skill:register |
| `mcp-server` | MCP tool server | Optional | .mcp.json registration |
| `project` | General coding project | No | git push only |

## File Naming Convention

Each type has:
- `<type>.workspace.json` — workspace.json template with type-specific defaults
- `<type>.scaffold.md` — directory structure + file descriptions
- `<type>.claude.md` — CLAUDE.md additions specific to this type
