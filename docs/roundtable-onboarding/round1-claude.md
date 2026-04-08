# Round 1: Claude Opus 4.6 (Lead/CIO) — Onboarding & Dashboard Redesign

## Executive Summary

I propose a **3-phase onboarding** (Bootstrap → Skill Parade → Go Live) with a **persistent dashboard daemon** that runs independently of any terminal or browser session. The key insight: onboarding IS skill setup — there's no separate "onboarding" and "skills configuration" step. They're the same flow.

---

## 1. Onboarding Architecture: 3 Phases

### Phase 1: Bootstrap (TUI or Web — user chooses)

**Goal:** Get the minimum viable environment running.

```
┌─────────────────────────────────────────────┐
│  clawd-lobster setup                        │
│                                             │
│  How do you want to set up?                 │
│  [1] Terminal (TUI)     ← textual/rich      │
│  [2] Web browser        ← localhost:3333    │
│  [3] Headless (CI/Docker)                   │
└─────────────────────────────────────────────┘
```

Bootstrap checks (same regardless of UI):
1. Python 3.10+ ✓
2. Node.js 18+ ✓
3. Git 2.x+ ✓
4. Claude Code CLI ✓
5. Claude Code auth ✓

Bootstrap actions:
1. Create `~/.clawd-lobster/config.json`
2. Choose language (en, zh-TW, zh-CN, ja, ko)
3. Hub: create new or join existing
4. Set workspace root directory

**Duration:** ~2 minutes. No skills yet. No Oracle. No API keys.

### Phase 2: Skill Parade (the core innovation)

**Goal:** Walk through every skill, explain it, set it up if needed.

After bootstrap, the user enters the **Skill Parade** — a guided tour of all skills in dependency order:

```
┌──────────────────────────────────────────────────────────┐
│  🦞 Skill Parade                              [2/14]    │
│                                                          │
│  ┌────────┐                                              │
│  │  🧠    │  Memory Server                               │
│  │        │  Your AI's long-term memory. Stores           │
│  └────────┘  decisions, learnings, and skills in a        │
│              local SQLite database. Every other skill      │
│              depends on this.                              │
│                                                          │
│  Status: Not installed                                    │
│                                                          │
│  Setup steps:                                            │
│  [✓] pip install fastmcp                                 │
│  [✓] Initialize memory.db                                │
│  [✓] Register MCP server in .mcp.json                    │
│  [ ] Verify: memory_status tool responds                  │
│                                                          │
│  [Install]  [Skip]  [What is this?]                      │
└──────────────────────────────────────────────────────────┘
```

**Skill order (dependency-respecting):**

**Required (must complete):**
1. **memory-server** — Foundation. Everything else depends on it.
2. **GitHub Hub** — Register Hub repo. Need git + gh auth.
3. **spec** — No setup needed (just explanation + enable).
4. **absorb** — Explain. If user wants Oracle Vault → setup Oracle HERE.
5. **evolve** — Register cron job (every 2h).
6. **heartbeat** — Register cron job (every 30m).
7. **deploy** — Explain. Docker optional.

**Optional (can skip, but explain each):**
8. **codex-bridge** — Install Codex CLI + auth. Explain worker/critic role.
9. **gemini-bridge** — Install Gemini CLI + auth. Explain consultant role.
10. **notebooklm-bridge** — Install notebooklm-py + Google auth.
11. **connect-odoo** — Odoo server URL + credentials. Register poller cron.
12. **migrate** — Scan for legacy systems. One-time import.

**Post-parade:**
13. **sync-all** — Register 30-min sync scheduler.
14. **Verification** — Run health check on all enabled skills.

### Phase 3: Go Live

After Skill Parade completes:
1. All cron jobs registered ✓
2. All MCP servers configured ✓
3. All credentials saved ✓
4. First workspace created (if not during bootstrap) ✓
5. Dashboard daemon started ✓
6. Print: "You're ready. Run `claude` in any workspace to start coding."

---

## 2. Persistent Dashboard Architecture

### The Daemon Model

```
┌─────────────────────────────────────────────────────┐
│  clawd-lobster daemon                               │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ HTTP Server   │  │ Scheduler    │                │
│  │ :3333         │  │ (internal)   │                │
│  │               │  │              │                │
│  │ Web Dashboard │  │ evolve 2h    │                │
│  │ API endpoints │  │ heartbeat 30m│                │
│  │ SSE stream    │  │ sync 30m     │                │
│  └──────────────┘  └──────────────┘                │
│                                                     │
│  PID: ~/.clawd-lobster/daemon.pid                   │
│  Log: ~/.clawd-lobster/daemon.log                   │
└─────────────────────────────────────────────────────┘
```

**Key design decisions:**

1. **Single daemon process** — HTTP server + scheduler in one Python process. No separate cron/Task Scheduler dependency.
2. **Web is optional** — Dashboard is just a view into the daemon's state. Close browser = nothing dies.
3. **Scheduler runs inside daemon** — Use `sched` or `APScheduler` (or simple threading.Timer loop). No OS-level cron needed.
4. **Daemon auto-starts** — On login (Task Scheduler on Windows, launchd on macOS, systemd on Linux). Or `clawd-lobster daemon start`.
5. **Graceful shutdown** — `clawd-lobster daemon stop` or system shutdown signal.

### Dashboard Pages (Web)

```
/                    → Dashboard home (system health overview)
/workspaces          → All workspaces + squad state
/skills              → 3 tabs: MCP | Prompt-pattern | Cron
/skills/:id/setup    → Individual skill config editor
/keys                → API key management + SSO
/settings            → Global settings (language, workspace root, etc.)
/squad               → Spec Squad execution view
```

### Dashboard Views (TUI)

Same views, rendered with `textual` (Python TUI framework):

```
clawd-lobster tui              # Launch TUI dashboard
clawd-lobster tui workspaces   # Jump to workspaces view
clawd-lobster tui skills       # Jump to skills view
clawd-lobster tui keys         # Jump to keys view
```

### Session Consistency

- **Web:** SSE (Server-Sent Events) for real-time updates. No polling.
- **TUI:** Direct reads from daemon state (shared memory or HTTP localhost).
- **State file:** `~/.clawd-lobster/state.json` — daemon writes, UI reads.

---

## 3. Credential Management

### Storage
```
~/.clawd-lobster/
  config.json          ← non-sensitive config
  credentials.json     ← encrypted at rest (AES-256, key from OS keyring)
  daemon.pid           ← daemon process ID
  daemon.log           ← daemon output log
```

### Dashboard Key Management

```
┌──────────────────────────────────────────────────────┐
│  🔑 API Keys & Authentication                        │
│                                                      │
│  Claude Code    ✅ Authenticated (Pro plan)           │
│                 [Re-authenticate]                     │
│                                                      │
│  GitHub         ✅ teddashh (PAT)                     │
│                 [Rotate token]  [Switch to SSO]       │
│                                                      │
│  OpenAI/Codex   ✅ Authenticated (Plus)               │
│                 [Re-authenticate]                     │
│                                                      │
│  Google/Gemini  ✅ Authenticated (OAuth)              │
│                 [Re-authenticate]                     │
│                                                      │
│  Oracle Vault   ⚠️ Wallet expires 2026-05-15          │
│                 [Test connection]  [Update wallet]    │
│                                                      │
│  Odoo ERP       ❌ Not configured                     │
│                 [Configure]                           │
└──────────────────────────────────────────────────────┘
```

---

## 4. Skills Tab Design

Three tabs, each showing cards:

### Tab 1: MCP Servers (always-on services)
- memory-server — Running ✅ | 847 items | 2.3 MB
- connect-odoo — Disabled ❌ | [Enable + Configure]

### Tab 2: Prompt Patterns (on-demand skills)
- spec — Enabled ✅ | Last used: 2h ago
- absorb — Enabled ✅ | Oracle Vault: Connected
- deploy — Enabled ✅ | Docker: Available
- codex-bridge — Enabled ✅ | Model: GPT-5.4
- gemini-bridge — Enabled ✅ | Model: Gemini 3.1 Pro
- notebooklm-bridge — Disabled ❌ | [Enable]
- migrate — Enabled ✅ | Legacy: OpenClaw detected

### Tab 3: Cron Jobs (scheduled tasks)
- evolve — Every 2h ✅ | Last run: 45m ago | 3 patterns learned
- heartbeat — Every 30m ✅ | Last run: 12m ago | 4 sessions alive
- sync-all — Every 30m ✅ | Last run: 12m ago | Hub up to date
- connect-odoo — Every 5m ❌ | Disabled

---

## 5. Implementation Plan

### Phase 1: Daemon + API (Week 1)
- Implement `clawd-lobster daemon start/stop/status`
- Move scheduler from OS cron to in-process scheduler
- Add SSE endpoint for real-time updates
- Add `/api/skills/*`, `/api/keys/*` endpoints

### Phase 2: Skill Parade (Week 1-2)
- Define skill setup protocol (each skill.json gets `onboarding` section)
- Implement ordered skill walker
- Build TUI Skill Parade with textual
- Build Web Skill Parade (new page in pages.py)

### Phase 3: Dashboard (Week 2)
- Redesign pages.py with new routes
- Skills page with 3 tabs
- Keys management page
- Workspace dashboard upgrade

### Phase 4: TUI Dashboard (Week 3)
- textual-based TUI app mirroring web views
- Workspaces, Skills, Keys, Settings views
- Live updates via daemon HTTP API

### Phase 5: Polish (Week 3)
- Cute skill icons/logos
- Mascot explanations
- Cross-platform testing
- Security audit on credential handling

---

## Key Positions

1. **Daemon > OS cron** — A single daemon process is more portable and debuggable than OS-level schedulers.
2. **Skill Parade = onboarding** — Don't separate "onboarding" from "skill setup." They're the same flow.
3. **textual for TUI** — It's the best Python TUI framework, actively maintained, rich widgets.
4. **SSE > WebSocket** — Simpler, HTTP-native, good enough for dashboard updates.
5. **Oracle in absorb skill setup** — Not in main onboarding. It's an optional L3 feature.
6. **Credentials in OS keyring** — Not plaintext JSON. Use `keyring` Python package.

---

## Open Questions for Codex & Gemini

1. Is a single daemon process the right architecture? Or should web server and scheduler be separate?
2. Should TUI and Web share the same pages.py code? Or separate rendering?
3. How to handle the Skill Parade when running headless (CI/Docker)?
4. Is `textual` the right TUI framework? Or something lighter?
5. How to handle skill dependencies during Skill Parade if a required skill fails to install?
6. Should the dashboard have authentication (even on localhost)?
