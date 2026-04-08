# Rounds 4+5: Gemini 3.1 Pro (Consultant) — Architecture & Implementation

## Round 4: Architecture & Schemas

### 1. API Endpoints (The Sole State Transition Authority)

The backend API must be the absolute arbiter of state.json.
- `GET /api/state` → Returns current state.json
- `POST /api/state/transition` → Payload: `{"skill_id": "...", "status": "pending|in_progress|done|failed", "actor": "web|claude"}`. Enforces valid state machine edges.
- `POST /api/lease/request` → Payload: `{"actor": "web|claude"}`. Grants single controller lease if available.
- `POST /api/lease/release` → Payload: `{"actor": "web|claude"}`. Yields control.
- `POST /api/skills/{skill_id}/reconcile` → Triggers health check/verification for a specific skill and syncs outcome to state.json.

### 2. `skill.json` Onboarding Section Schema

Minimal to support MVP "Agent-Guided Escape Room" without bloat:
```json
"onboarding": {
  "required": true,
  "dependencies": ["core-auth"],
  "prompts": {
    "intro": "Let's connect your database.",
    "success": "Database initialized and verified.",
    "error": "Failed to connect. Have you checked your credentials?"
  },
  "verification_command": "python -m clawd_lobster.skills.check_db",
  "expected_facts": ["db_url", "db_user"]
}
```

### 3. Controller Lease Handoff Protocol

state.json contains a `controller` object: `{"active": "web|claude", "acquired_at": "ISO-8601", "expires_at": "ISO-8601"}`.

- **Web → Claude:** User clicks "Ask Claude for Help". Web calls `/api/lease/release`. Web disables input. Claude polls/SSE, calls `/api/lease/request`, takes over.
- **Claude → Web:** Claude finishes task, writes state via API, auto-releases lease. Web regains control.
- **Safety:** State transition without active lease returns `409 Conflict`. Leases auto-expire after 5 minutes to prevent deadlocks.

### 4. `events.jsonl` Audit Trail

Append-only, machine/human-readable:
```json
{"timestamp": "2026-04-08T10:00:00Z", "actor": "web", "action": "lease_acquired", "details": {}}
{"timestamp": "2026-04-08T10:01:00Z", "actor": "claude", "action": "state_transition", "target": "skill:connect-odoo", "from": "pending", "to": "in_progress"}
{"timestamp": "2026-04-08T10:02:00Z", "actor": "system", "action": "fact_extracted", "key": "odoo_url", "value": "***"}
{"timestamp": "2026-04-08T10:05:00Z", "actor": "system", "action": "reconciliation_failed", "target": "skill:connect-odoo", "details": {"error": "timeout"}}
```

### 5. Health Check / Reconciliation

Each skill defines a `verification_command`. OS scheduler triggers periodic sync that loops through active skills, runs verification, and POSTs to `/api/skills/{skill_id}/reconcile`. If system state drifts from state.json, backend downgrades status to "failed" and writes to events.jsonl.

---

## Round 5: Implementation & Execution

### 1. Implementation Phases

| Phase | Days | Deliverable |
|-------|------|------------|
| 1: Foundations | 1-3 | state.py (atomic writes/locks), lease.py, core server endpoints |
| 2: Visuals | 4-7 | Server-rendered dashboard, JS islands, token auth |
| 3: The Brain | 8-10 | Claude agent integration, lease handoff protocol |
| 4: Escape Room MVP | 11-14 | skill.json onboarding schema, reconciliation cron, E2E testing |

### 2. New Files/Modules

- `clawd_lobster/state.py` — Atomic state.json reads/writes
- `clawd_lobster/lease.py` — Web/Claude controller handoff
- `clawd_lobster/audit.py` — Append-only events.jsonl writer
- `clawd_lobster/api/routes.py` — Endpoint definitions
- `webapp/js/islands/` — Vanilla JS for fetching state + rendering UI components

### 3. Ted's Approval Checklist

- [ ] OS scheduler (cron) for polling; NO background daemons
- [ ] API is sole authority for state transitions; no direct file writes by Web/Claude
- [ ] Multi-page with server-side rendering + JS islands (no SPA build step)
- [ ] Controller lease cleanly locks out concurrent actor modifications
- [ ] Atomic file replacements guaranteed for state.json

### 4. Top 5 Risks

| Risk | Mitigation |
|------|-----------|
| Race conditions on state.json | Strict file-level locking (fcntl/msvcrt) + atomic renames (os.replace) |
| Deadlocks if Claude/Web crashes while holding lease | 5-minute hard expiration; auto-revoke stale leases |
| System state drifts from state.json | Reconciliation cron job; source of truth for downgrading skill status |
| UI shows stale data | JS islands short-poll (3s) or SSE to continuously fetch state |
| Scope creep in skill.json schema | Reject non-MVP additions; stick to required/dependencies/verification_command |

```json
{"agent":"gemini","role":"consultant","task":"round4-5-onboarding-debate","findings":[{"type":"decision","description":"API must serve as single source of truth for state transitions."},{"type":"decision","description":"Strict lease handoff using timestamps and actor IDs to prevent race conditions."},{"type":"risk","description":"Deadlocks possible if controller lease is not auto-expired."}],"summary":"Completed Rounds 4+5 defining concrete API endpoints, schemas, controller lease mechanisms, audit logs, and 4-phase 14-day implementation plan.","disagreements":[]}
```
