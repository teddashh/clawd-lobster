# Clawd-Lobster v1.0 — Unified User Experience

## Why

Clawd-Lobster has 10 skills, 32 tools, 15+ scripts, and 3 versions of Spec Squad — but no coherent user journey. A new user clones the repo and has no idea what to do first. An experienced user can't tell which of the 3 spec-squad scripts to run. The product vision (5-minute setup, noob-friendly, always-on AI) exists in NotebookLM slides but not in the actual codebase.

The gap: **we have components but not a product.**

## What

A complete user experience redesign that turns scattered scripts into a unified product:
1. **Web-based onboarding wizard** — install, configure, first workspace in 5 minutes
2. **Unified Spec Squad** — one entry point (web or terminal), not 3 competing scripts
3. **Dashboard** — persistent web UI showing all workspaces, agents, heartbeat status
4. **CLI integration** — every web feature also works from terminal

## Who

Three user personas (from product docs):
1. **Noob** — never used Claude Code, needs hand-holding, zero terminal experience
2. **Struggling Expert** — used OpenClaw/Hermes/raw Claude, wants to migrate, knows terminal
3. **Tech Expert** — wants the architecture, wants to extend, reads SKILL.md

## How

- **Web layer**: Single Python web server (`clawd-lobster serve`) serving all UI
- **Agent layer**: Claude Agent SDK for all Claude interactions (discovery chat, squad agents)
- **CLI layer**: Every web action has a CLI equivalent (`clawd-lobster workspace create`, `clawd-lobster squad start`)
- **State layer**: Existing SQLite memory + `.spec-squad.json` + `workspaces.json`

## Scope

**v1.0 MVP** — focus on getting a new user from zero to first working project:
- Web onboarding (install wizard, OAuth, first workspace)
- Unified Spec Squad (one script, two interfaces: web chat + terminal)
- Workspace dashboard (list workspaces, show status, launch squad)
- Consolidate the 3 spec-squad scripts into one

**NOT in v1.0:**
- Multi-machine dashboard (keep as CLI sync for now)
- Plugin marketplace
- Team features / multi-user
- Mobile app

## Integrations

- Claude Code CLI (`claude -p`, `claude --resume`)
- Claude Agent SDK (`claude-agent-sdk` pip package)
- OpenAI Codex CLI (optional, for delegation)
- NotebookLM (optional, for doc generation)
- GitHub (for Hub sync)

## Constraints

- Zero external service dependencies (no cloud DB required)
- Must work on Windows 11, macOS, Linux
- Must work offline (except OAuth and Claude API)
- Python only (no Node.js requirement for core)
- Total codebase under 5,000 LOC (currently ~2,000)
- Web server must be lightweight (stdlib http.server, no Flask/Django)

## References

- NotebookLM product slides (9 PDFs, 8 infographics)
- The Dev Squad (johnkf5-ops/the-dev-squad) — multi-agent visual UI
- shanraisshan/claude-code-best-practice — community best practices
- Boris Cherny tips (skills, hooks, commands, plan mode)
