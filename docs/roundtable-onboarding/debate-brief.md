# Roundtable Debate: Onboarding & Persistent Dashboard Redesign

**Date:** 2026-04-08
**Participants:** Claude Opus 4.6 (Lead/CIO), Codex GPT-5.4 (Critic), Gemini 3.1 Pro (Consultant)
**Rounds:** 5
**Owner:** Ted (project owner)

---

## Context: What is clawd-lobster?

An AI-native spec-to-code framework built as a Claude Code skills wrapper. It provides:
- **14 skills** across 3 kinds (MCP-server, prompt-pattern, cron)
- **Multi-agent orchestration** (Claude lead + Codex worker/critic + Gemini consultant)
- **4-layer memory** (CC auto-memory → SQLite+MCP → Git Wiki → Oracle Vault)
- **Spec Squad** (Architect → Reviewer → Coder → Tester pipeline)
- **Cross-machine Hub** via private GitHub repo

## Current Onboarding (what exists today)

### CLI Installer (install.ps1 / install.sh)
9-step pipeline: prerequisites → auth → hub create/join → config → MCP memory server → Claude Code setup → workspace deploy → scheduler → migration. Resumable via install-state.json.

### Web UI (clawd-lobster serve → localhost:3333)
5-step wizard in pages.py: language → welcome → prerequisites → persona → workspace. Plus workspaces dashboard and squad page.

### Redesign Spec (docs/onboarding-redesign-spec.md)
3-page approach: Welcome+Language → Prerequisites Babysit → Handoff to Claude Code CLI. Backend APIs exist but frontend not updated.

## All 14 Skills (with setup requirements)

### Always-On / Required
| # | Skill | Kind | Setup Required | Dependencies |
|---|-------|------|---------------|-------------|
| 1 | **memory-server** | MCP-server | pip install fastmcp, init SQLite DB | Python, pip |
| 2 | **spec** | Prompt-pattern | None (uses memory-server) | memory-server, absorb, evolve |
| 3 | **absorb** | Prompt-pattern | None (but Oracle optional for L3) | memory-server |
| 4 | **evolve** | Cron (2h) | Register cron job | memory-server, git, claude CLI |
| 5 | **heartbeat** | Cron (30m) | Register cron job | claude CLI |
| 6 | **deploy** | Prompt-pattern | Docker (optional) | spec |

### Optional / Integration
| # | Skill | Kind | Setup Required | Dependencies |
|---|-------|------|---------------|-------------|
| 7 | **codex-bridge** | Prompt-pattern | npm install @openai/codex, codex login | Node.js, OpenAI account |
| 8 | **gemini-bridge** | Prompt-pattern | npm install @google/gemini-cli, gemini auth | Node.js, Google account |
| 9 | **notebooklm-bridge** | Prompt-pattern | pip install notebooklm-py, Google auth | Python, Google account |
| 10 | **connect-odoo** | Poller (5m) | Odoo server URL + credentials | Python, Odoo instance |
| 11 | **migrate** | Prompt-pattern | None (scans existing systems) | memory-server |

### Infrastructure
| # | Skill | Kind | Setup Required | Dependencies |
|---|-------|------|---------------|-------------|
| 12 | **learned** | Directory | None (auto-populated by evolve) | evolve |
| 13 | Oracle Vault (L3) | Via absorb/memory | Oracle wallet + credentials | oracledb pip package |
| 14 | GitHub Hub | Via install | gh auth login, create/join Hub repo | git, gh CLI |

## Ted's Requirements (verbatim, organized)

### R1: TUI Onboarding
Want a terminal UI (TUI) version of onboarding, not just CLI prompts or web.

### R2: Oracle NOT in onboarding
Oracle setup belongs in skills setup, not the main onboarding flow. It should come up when the user reaches the absorb/memory skill configuration.

### R3: Skills-first post-handoff
After Claude Code takes over from onboarding, the flow should go to a **skills page** where each skill is presented one by one for setup.

### R4: Ordered skill setup
- Memory-server is the FIRST skill to set up
- GitHub/Hub registration should happen early (or even before skills)
- Oracle comes later, during absorb/memory skill setup
- Each skill explains what it does before asking for setup

### R5: Skill explanation UX
Each skill should have a cute logo/icon next to an explanation bubble describing what the skill does. Visual, friendly, not just text.

### R6: Required skills first, then optional
- Go through ALL required skills first (memory, spec, absorb, evolve, heartbeat, deploy)
- Then go through ALL optional skills (codex-bridge, gemini-bridge, notebooklm, connect-odoo, migrate)
- Each one gets a setup flow if needed

### R7: Cron jobs configured during setup
All cron/scheduler jobs (evolve every 2h, heartbeat every 30m, sync every 30m, connect-odoo polling) must be registered during the skill setup process.

### R8: Persistent web dashboard
A web page that can stay open showing:
- **All workspaces** — list, create, launch squad
- **All skills** — 3 tabs (MCP-server, prompt-pattern, cron)
- **All skill setup** — can modify configuration from the dashboard
- **All API keys** — can change keys, manage SSO, rotate credentials
- **Consistent session** — maintains state while open

### R9: Web closeable but scheduler survives
The web dashboard can be closed without killing background jobs. Schedulers (cron/Task Scheduler) run independently.

### R10: TUI session as alternative
Users should also be able to run a TUI session that provides the same views as the web dashboard (workspaces, skills, keys, setup).

## Ted's Critical Insight: Agent-Guided Onboarding (added after Round 1)

> "既然我們已經進入 Agent 時代，讓 Agent 帶著安裝完是一個新的角度。當 Claude Code 被裝起來，Claude Code 就可以從終端機出現，一路帶著我們走完網頁。這是一種全新的體驗。"
>
> "不用硬去寫 CLAUDE.md。網頁要寫得讓 Claude Code 一進場就知道他要幹什麼。畢竟第一個 workspace 是我們開的，網頁也是。這是一個預先設好的環境。因為網頁 + Claude 決定了我們的 presentation。"

**Key implications:**
1. The ONLY thing the installer needs to do is: install Claude Code + open the web dashboard + create the first workspace.
2. The web dashboard already knows it's in onboarding mode — the pages show the right UI.
3. Claude Code enters an environment that's already staged for it — it doesn't need CLAUDE.md scripts.
4. The **web is the presentation layer**, Claude Code is the **conversational guide**. Together they ARE the onboarding.
5. This is NOT a traditional installer. It's an agent-assisted experience where the user talks to Claude while the web shows progress.

## Key Questions for Debate

1. **Onboarding flow**: What's the optimal sequence? TUI first or web first? How does the handoff work?
2. **Skill setup UX**: How to present 14 skills one by one without overwhelming the user? Grouping? Progressive disclosure?
3. **Persistent dashboard architecture**: How to implement a web dashboard that survives page reloads, shows live state, and allows config changes?
4. **TUI vs Web parity**: Should TUI mirror the web exactly? Or is it a subset? What framework for TUI?
5. **Session management**: How to maintain a consistent session? WebSocket? Polling? Server-sent events?
6. **Scheduler independence**: How to ensure cron jobs run even when web/TUI is closed? What's the daemon architecture?
7. **Credential management**: How to securely show/edit API keys in the dashboard? Encryption at rest?
8. **Skill dependency ordering**: How to handle skills that depend on other skills being set up first?

## Technical Constraints

- **Zero external web framework** — stdlib http.server only (no Flask, no Express)
- **Cross-platform** — Windows (PowerShell + Task Scheduler), macOS (launchd), Linux (cron)
- **Offline-capable** — core features work without internet
- **Python stdlib preferred** — minimize pip dependencies for core
- **TUI framework options** — textual (Python), blessed (Node), raw ANSI, curses
- **Current web tech** — inline HTML/CSS/JS in pages.py, no bundler, no CDN

## Existing API Endpoints

```
GET  /                           → redirect
GET  /onboarding                 → onboarding page
GET  /workspaces                 → workspace dashboard
GET  /squad                      → spec squad page
GET  /api/status                 → system health
GET  /api/workspaces             → workspace list
GET  /api/squad/state            → squad execution state
GET  /api/onboarding/state       → onboarding session state
GET  /api/onboarding/instructions → CLAUDE.md for handoff
POST /api/onboarding/check       → prerequisite validation
POST /api/onboarding/complete    → finalize setup
POST /api/onboarding/handoff     → create session for CLI
POST /api/onboarding/update      → CLI reports progress
POST /api/workspaces/create      → create workspace
POST /api/squad/chat             → discovery chat
POST /api/squad/start            → launch squad agents
POST /api/vault/test             → test Oracle connection
POST /api/vault/save             → save Oracle config
```

## File Structure

```
clawd_lobster/
  __init__.py, __main__.py, cli.py, server.py,
  onboarding.py, pages.py, dashboard.py, squad.py
skills/
  absorb/, codex-bridge/, connect-odoo/, deploy/,
  evolve/, gemini-bridge/, heartbeat/, learned/,
  memory-server/, migrate/, notebooklm-bridge/, spec/
scripts/
  agent_dispatch.py, vault_mcp_server.py, evolve-tick.py,
  skill-manager.py, workspace-create.py, init_db.py,
  sync-all.ps1/.sh, heartbeat.ps1/.sh, security-scan.py,
  sync-claude-to-codex.py, sync-knowledge.py, notebooklm-sync.py,
  install-lib.ps1/.sh, setup-hooks.ps1/.sh, new-workspace.ps1,
  patch-codex-plugin.py, validate-spec.py
templates/
  global-CLAUDE.md, workspace-CLAUDE.md,
  mcp.json.template, settings.json.template,
  .claude/hooks/*, .claude/rules/*
```

## Deliverable

A complete architecture proposal covering:
1. Onboarding flow (TUI + Web + CLI handoff)
2. Skills setup sequence with UX mockups
3. Persistent dashboard architecture
4. Session/daemon model
5. Credential management
6. Implementation plan with phases
