# API Service — Workspace Rules

## Environment Safety
- **Dev (local):** Free to experiment. Auto-reload enabled.
- **Staging:** Verify all endpoints and integrations manually.
- **Prod:** Deploy via git push + CI/CD only. No Claude Code.

## Deploy Commands
- `/deploy:ship dev` — Start local API server in Docker
- `/deploy:ship staging` — Deploy to staging
- `/deploy:ship prod` — Deploy to production (requires confirmation)

## Conventions
- RESTful endpoints with consistent naming
- Input validation on all endpoints
- Error responses follow a standard format
- API versioning via URL prefix (e.g., `/v1/`)
- All secrets in `.env.*` files (gitignored)
