# Web Application — Workspace Rules

## Environment Safety
- **Dev (local):** Free to experiment. Hot reload enabled. Debug mode on.
- **Staging:** Manual verification only. Test all API integrations here.
- **Prod:** NEVER run Claude Code on production. Deploy via git push + CI/CD only.

## Deploy Commands
- `/deploy:ship dev` — Start local Docker environment
- `/deploy:ship staging` — Deploy to staging server
- `/deploy:ship prod` — Deploy to production (requires confirmation)
- `/deploy:status` — Check all environments
- `/deploy:teardown dev` — Stop local containers

## Conventions
- All secrets in `.env.*` files (gitignored), never hardcoded
- Database migrations tracked in version control
- API endpoints documented in `openspec/specs/`
- Tests required before staging deploy
