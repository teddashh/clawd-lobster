# Round 5: Final Unanimous Consensus — Onboarding & Dashboard Redesign

**Date:** 2026-04-08
**Participants:** Claude Opus 4.6, Codex GPT-5.4, Gemini 3.1 Pro
**Rounds:** 5
**Status:** UNANIMOUS CONSENSUS

---

## 1. Core Architecture Decisions (All 3 Agree)

| # | Decision | Proposed By | Agreed In |
|---|----------|-------------|-----------|
| D1 | OS scheduler (cron/Task Scheduler/launchd) for recurring jobs — no internal daemon scheduler | Codex R1 | Round 1 |
| D2 | Backend API is the **sole authority** for state transitions — no direct file writes by web, TUI, or Claude | Codex R2 | Round 2 |
| D3 | Multi-page server-rendered dashboard with JS islands — no SPA, no React/Vue | Codex R2, Gemini R2 | Round 2 |
| D4 | Token-based auth (Jupyter-style `?token=...`) for localhost dashboard — CSRF protection | Gemini R1 | Round 1 |
| D5 | Atomic file writes (temp + rename) for all state persistence | All | Round 2 |
| D6 | Separate rendering for Web and TUI — share API/state layer only | Gemini R1, Codex R1 | Round 1 |
| D7 | Agent-Guided "Escape Room" — Web = visual layer, Claude = conversation layer, state.json = shared brain | Ted + Gemini R1 | Round 2 |
| D8 | One controller lease at a time — web OR Claude can mutate, never both | Codex R2, Gemini R2 | Round 2 |
| D9 | Oracle NOT in onboarding — appears during absorb skill setup | Ted R2 | Round 1 |
| D10 | Separate Foundations (not skills) from Skills (manifest-driven) from Jobs (OS scheduler) | Codex R1 | Round 1 |
| D11 | Skill onboarding metadata in skill.json — constrained schema with fixed step kinds | Codex R4 | Round 4 |
| D12 | Append-only events.jsonl audit trail with seq/revision/actor attribution | Codex R4 | Round 4 |
| D13 | Reconciliation probes must be side-effect free (detect + verify, never mutate) | Codex R4 | Round 4 |
| D14 | MVP = Bootstrap + Foundations + Required Skills only — defer power skills, TUI parity, credential backends | All R2-3 | Round 3 |

---

## 2. The Onboarding Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AGENT-GUIDED ONBOARDING                          │
│                                                                         │
│  ┌──────────────────┐                                                   │
│  │ install.ps1/.sh  │ ← Traditional installer (only runs once)          │
│  │                  │                                                   │
│  │ 1. Prerequisites │ Python, Node, Git                                 │
│  │ 2. Claude Code   │ npm install -g @anthropic-ai/claude-code          │
│  │ 3. clawd-lobster │ pip install clawd-lobster                         │
│  │ 4. Init config   │ ~/.clawd-lobster/config.json + token              │
│  │ 5. First workspace│ Create + git init                                │
│  │ 6. Start web     │ clawd-lobster serve --daemon                      │
│  │ 7. Open browser  │ localhost:3333/?token=abc123                      │
│  │ 8. Launch Claude │ claude (in first workspace)                       │
│  └──────────────────┘                                                   │
│           ↓                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ ESCAPE ROOM (Web + Claude co-pilot)                              │   │
│  │                                                                  │   │
│  │ Tier 1: FOUNDATIONS (not skills)                                 │   │
│  │   [✓] Language selection                                        │   │
│  │   [✓] Claude Code auth verification                             │   │
│  │   [✓] GitHub Hub registration                                   │   │
│  │   [✓] Workspace root + first workspace                         │   │
│  │                                                                  │   │
│  │ Tier 2: REQUIRED SKILLS (manifest-driven)                       │   │
│  │   [ ] 🧠 Memory Server — Your AI's long-term memory             │   │
│  │   [ ] 📋 Spec — Structured specification framework               │   │
│  │   [ ] 📥 Absorb — Knowledge ingestion (+ optional Oracle)        │   │
│  │   [ ] 🔄 Evolve — Pattern learning (+ register cron 2h)         │   │
│  │   [ ] 💓 Heartbeat — Session monitoring (+ register cron 30m)    │   │
│  │   [ ] 🚀 Deploy — Docker deployment pipeline                    │   │
│  │                                                                  │   │
│  │ Tier 3: POWER SKILLS (optional, explain + skip)                 │   │
│  │   [ ] 🤖 Codex Bridge — GPT-5.4 worker/critic                   │   │
│  │   [ ] 💎 Gemini Bridge — Consultant/validator                    │   │
│  │   [ ] 📓 NotebookLM — Free RAG + content gen                    │   │
│  │   [ ] 🏢 Connect Odoo — ERP integration                         │   │
│  │                                                                  │   │
│  │ Tier 4: ONE-TIME (conditional)                                  │   │
│  │   [ ] 📦 Migrate — Only if legacy system detected               │   │
│  │   [ ] ⏰ Scheduler registration                                 │   │
│  │                                                                  │   │
│  │ VERIFICATION: Health check all enabled skills                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           ↓                                                             │
│  ┌──────────────────┐                                                   │
│  │ GO LIVE           │                                                   │
│  │ Dashboard ready   │ Workspaces | Skills (3 tabs) | Settings/Keys     │
│  │ Schedulers active │ evolve 2h, heartbeat 30m, sync 30m               │
│  │ "Start coding"   │ Run claude in any workspace                       │
│  └──────────────────┘                                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. State Model (v1)

### state.json
```json
{
  "version": 1,
  "session_id": "ob_abc123",
  "created_at": "2026-04-08T...",
  "updated_at": "2026-04-08T...",
  "revision": 42,
  "token_hash": "sha256:...",
  "phase": "skills_required",
  "items": [
    {
      "id": "memory-server",
      "tier": "required",
      "kind": "mcp-server",
      "status": "succeeded",
      "depends_on": ["foundation.workspace_root"],
      "started_at": "2026-04-08T...",
      "completed_at": "2026-04-08T...",
      "last_actor": "claude",
      "retry_count": 0,
      "error": null,
      "facts": {
        "package_installed": true,
        "config_written": true,
        "mcp_registered": true,
        "health_check_passed": true
      }
    }
  ]
}
```

### controller.json
```json
{
  "lease_id": "lease_xyz",
  "holder": "claude",
  "session_id": "ob_abc123",
  "acquired_at": "2026-04-08T...",
  "expires_at": "2026-04-08T...",
  "revision": 5
}
```

### events.jsonl (append-only)
```json
{"ts":"...","seq":1,"session_id":"ob_abc123","revision":1,"type":"session_created","actor":"backend","ok":true}
{"ts":"...","seq":2,"session_id":"ob_abc123","revision":2,"type":"intent_applied","actor":"claude","item_id":"memory-server","ok":true}
```

---

## 4. API Surface (22 endpoints)

### Onboarding
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/onboarding/state` | Read current state |
| GET | `/api/onboarding/manifest` | Resolved plan + phases |
| POST | `/api/onboarding/session` | Create session + mint token |
| POST | `/api/onboarding/intent` | Generic state transition (sole mutation path) |
| POST | `/api/onboarding/reconcile` | Full reconciliation pass |
| POST | `/api/onboarding/complete` | Mark complete |
| GET | `/api/onboarding/events` | Incremental audit feed |
| GET | `/api/onboarding/stream` | SSE for live updates |
| GET | `/api/onboarding/health` | Aggregate health |
| GET | `/api/onboarding/health/<id>` | Per-item probe |

### Controller Lease
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/controller/acquire` | Request lease (TTL 90s) |
| POST | `/api/controller/renew` | Renew (every 30s) |
| POST | `/api/controller/release` | Release voluntarily |
| POST | `/api/controller/handoff` | Transfer web↔claude |
| GET | `/api/controller` | Current holder + expiry |

### Skills
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/skills/catalog` | All skills + onboarding metadata |
| GET | `/api/skills/<id>` | One skill detail |
| POST | `/api/skills/<id>/install` | Execute install step |
| POST | `/api/skills/<id>/configure` | Write config/credentials |
| POST | `/api/skills/<id>/verify` | Run probe |
| POST | `/api/skills/<id>/skip` | Skip optional skill |

### Jobs
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/jobs/register` | Register OS scheduler entry |
| GET | `/api/jobs/status` | Scheduler status + next run |

---

## 5. Implementation Plan

| Week | Phase | Deliverable |
|------|-------|------------|
| 1 | Backend Core | State store, lease manager, event log, manifest loader, onboarding API endpoints |
| 2 | Web MVP | Server-rendered pages, JS islands, foundations flow, required skills tab, token auth |
| 3 | Skill Execution | Install/configure/verify endpoints, per-skill probes, scheduler registration, retry/skip |
| 4 | Claude Integration | Tokenized handoff, intent API from Claude, lease transfer, audit trail visibility |
| 5 | Hardening | Crash recovery, stale lease cleanup, acceptance tests, Ted signoff |

**Post-MVP (deferred):**
- Power skill onboarding flows
- TUI dashboard (Textual)
- Advanced credential backends (OS keyring)
- Simultaneous multi-controller sessions
- Migrate as auto-detected flow

---

## 6. File Structure

```
clawd_lobster/
  server.py                           ← thin HTTP routing
  onboarding/
    __init__.py
    api.py                            ← request handlers
    state_store.py                    ← atomic read/write state/controller/events
    lease.py                          ← acquire/renew/release/handoff
    manifest.py                       ← load/validate skill onboarding metadata
    reconcile.py                      ← reconciliation runner
    probes.py                         ← per-skill probe registry
    intents.py                        ← allowed transitions + validation
  pages_onboarding.py                 ← server-rendered onboarding pages
  assets/
    onboarding.js                     ← client helpers (SSE/polling/actions)

skills/*/skill.json                   ← add onboarding sections
templates/onboarding/state.v1.json    ← initial state template

~/.clawd-lobster/onboarding/<session_id>/
  state.json                          ← workflow state (backend-owned)
  controller.json                     ← lease state
  events.jsonl                        ← audit trail
  CLAUDE.md                           ← handoff instructions
```

---

## 7. Ted's Approval Checklist

- [ ] **Single-writer guarantee:** all state mutations go through backend `/api/onboarding/intent`
- [ ] **Lease safety:** simultaneous web + Claude mutation attempts correctly rejected
- [ ] **Crash recovery:** kill server mid-write → restart → state remains valid
- [ ] **Reconciliation:** uninstall/break a skill → dashboard reflects drift correctly
- [ ] **Security:** localhost bind only, token required, token never logged in cleartext
- [ ] **UX baseline:** bootstrap → foundations → required skills complete E2E without terminal spelunking
- [ ] **Agent-guided:** Claude + Web co-pilot experience feels natural, not scripted
- [ ] **Scope discipline:** optional skills and TUI parity explicitly deferred, not half-implemented
- [ ] **Skill cards:** each skill has icon + explanation + status + setup steps
- [ ] **Cron jobs:** all required schedulers registered during skill setup

---

## 8. Risk Register

| # | Risk | Severity | Mitigation |
|---|------|----------|-----------|
| 1 | Lease split-brain between web and Claude | HIGH | Short TTL (90s), backend-issued lease_id, compare-and-swap revision, hard reject stale leases |
| 2 | Manifest complexity explodes | MEDIUM | Constrain v1 to fixed step kinds: command/config/probe/link. Flat facts_schema only. |
| 3 | Health probes become destructive or flaky | MEDIUM | Separate detect from verify; no probe may mutate system state |
| 4 | Windows scheduler + path handling failures | MEDIUM | Explicit OS adapters; test paths with spaces; atomic rename already present |
| 5 | State/event corruption from abrupt termination | HIGH | Temp-write + rename for JSON; append-only event log with monotonic seq; recovery from latest valid state |

---

## 9. Key Innovation: Agent-Guided Escape Room

This is not a traditional installer. It's a **new paradigm** for developer tool onboarding:

1. **The Web is not a wizard** — it's a **visual companion** that shows state, progress, and forms
2. **Claude is not a script reader** — it's a **conversational guide** that reads state and helps the user
3. **Together they create a collaborative experience** — the user talks to Claude while the web shows what's happening
4. **The environment is pre-staged** — the first workspace and dashboard are set up by the installer, so Claude enters a world that already knows it's in onboarding mode
5. **Either can advance the flow** — but through the same backend API, never by direct file manipulation

> "既然我們已經進入 Agent 時代，讓 Agent 帶著安裝完是一個新的角度。" — Ted

---

**Confidence Scores:**
- Claude: 0.95
- Codex: 0.92
- Gemini: 0.93

**Zero open disputes.**
