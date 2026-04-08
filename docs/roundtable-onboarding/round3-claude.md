# Round 3: Claude Opus 4.6 — Convergence

## Round 2 Concessions

### 1. State ownership: Backend is sole writer (Codex was right)
I concede. Direct shared writes to state.json is a race condition waiting to happen. The architecture becomes:
- **Backend API** is the sole authority for state transitions
- Web, TUI, and Claude all submit **intents** via API calls (HTTP endpoints or CLI commands)
- The backend validates, applies transitions, and persists atomically
- File is a storage artifact, not a coordination primitive

### 2. State model needs more detail (Codex was right)
The state model must include per-item status, timestamps, last actor, retry count, dependency satisfaction, and error details. Not just progress labels.

### 3. MVP scope cut (both were right)
v1 cuts to: Bootstrap + Foundations + Required Skills only. Defer power skills, migrate (unless detected), sync-all prominence, TUI dashboard parity.

### 4. Multi-page with JS islands, not SPA (both agreed)
Server-rendered pages, fetch for small actions, SSE only where live progress matters.

### 5. TUI is read-only viewer in v1 (Gemini was right)
If web is the active controller, TUI is read-only. One controller lease at a time.

---

## EMERGING CONSENSUS (Round 3)

After 2 rounds, here is what all three agree on:

### Architecture
1. **OS scheduler** for cron jobs (not internal daemon)
2. **Backend API** as sole state transition authority
3. **Multi-page** server-rendered dashboard with JS islands
4. **Token-based auth** (Jupyter-style) for localhost
5. **Atomic file writes** (temp + rename) for state persistence
6. **Separate rendering** for Web and TUI (shared API/state only)

### Onboarding Flow
1. **Bootstrap:** install.ps1/sh → prerequisites → Claude Code → pip install clawd-lobster → init config → start web → open browser → launch Claude in workspace
2. **Foundations (not skills):** language, auth, hub, workspace root
3. **Required Skills (manifest-driven):** memory-server → spec → absorb (Oracle here if wanted) → evolve → heartbeat → deploy
4. **Optional Skills (explain + skip):** codex-bridge, gemini-bridge, notebooklm, connect-odoo
5. **One-time (conditional):** migrate (only if legacy detected), scheduler registration
6. **Go Live:** health check → dashboard ready → "start coding"

### UX Model
1. **Agent-Guided Escape Room:** Web = visual layer, Claude = conversation layer, state.json = shared brain
2. **Reactive State Loop:** Claude reads state → explains → user responds → Claude calls API → web updates live
3. **One controller lease:** web OR Claude can mutate, not both simultaneously without coordination
4. **Cute skill cards:** icon + name + explanation bubble + status + setup steps

### MVP Scope (v1)
- Bootstrap + Foundations + Required Skills
- Web dashboard: Onboarding, Workspaces, Skills (3 tabs), Settings/Credentials
- Terminal: Claude as conversational guide + `rich` progress output
- NO TUI dashboard parity
- NO power skill onboarding flows (just enable/disable from dashboard)
- NO advanced credential backends

### State Model (v1)
```json
{
  "version": 1,
  "created_at": "2026-04-08T...",
  "updated_at": "2026-04-08T...",
  "token": "abc123...",
  "phase": "foundations | skills_required | skills_optional | jobs | complete",
  "items": [
    {
      "id": "memory-server",
      "tier": "required",
      "kind": "mcp-server",
      "status": "pending | running | succeeded | failed | skipped | blocked",
      "depends_on": [],
      "started_at": null,
      "completed_at": null,
      "last_actor": "claude | web | cli",
      "retry_count": 0,
      "error": null,
      "facts": {
        "pip_installed": false,
        "db_initialized": false,
        "mcp_registered": false,
        "health_check_passed": false
      }
    }
  ],
  "active_controller": {
    "type": "web | tui | claude",
    "session_id": "...",
    "acquired_at": "..."
  }
}
```

---

## Remaining Open Items for Rounds 4-5

### For Round 4 (Architecture Deep-Dive):
1. **API endpoint design** — what specific endpoints does the backend need?
2. **Skill manifest `onboarding` section** — what metadata format for setup steps?
3. **Controller lease protocol** — how does handoff work between web and Claude?
4. **Event/audit trail** — events.jsonl format?
5. **Health check protocol** — how does reconciliation probe each skill?

### For Round 5 (Final Consensus):
1. **Implementation phases** — what ships in which week?
2. **File structure** — what new files/modules are created?
3. **Ted's approval checklist** — what does Ted need to sign off on?
4. **Risk register** — what could still go wrong?
