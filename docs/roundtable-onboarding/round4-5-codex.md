# Rounds 4+5: Codex GPT-5.4 (Critic) — Architecture Deep-Dive & Final Consensus

## Round 4: Architecture Deep-Dive

### 1. Backend API Endpoints

**Onboarding:**
- `GET /api/onboarding/state?session_id=<id>` — read current state
- `GET /api/onboarding/manifest` — resolved plan, skills, phases
- `POST /api/onboarding/session` — create session, mint token, init state/events/controller
- `POST /api/onboarding/intent` — generic state transition. Body: `{session_id, token, controller_lease_id, intent, payload, expected_revision}`
- `POST /api/onboarding/reconcile` — full reconciliation pass
- `POST /api/onboarding/complete` — mark complete after validation
- `GET /api/onboarding/events?after=<offset>` — incremental audit feed
- `GET /api/onboarding/stream?session_id=<id>` — SSE for live updates
- `GET /api/onboarding/health` — aggregate health summary
- `GET /api/onboarding/health/<item_id>` — per-item probe result

**Controller Lease:**
- `POST /api/controller/acquire` — request lease
- `POST /api/controller/renew` — renew active lease
- `POST /api/controller/release` — release voluntarily
- `POST /api/controller/handoff` — transfer between web/claude
- `GET /api/controller` — inspect current holder + expiry

**Skills:**
- `GET /api/skills/catalog` — all skills with onboarding metadata
- `GET /api/skills/<skill_id>` — full metadata for one skill
- `POST /api/skills/<skill_id>/install` — execute install step
- `POST /api/skills/<skill_id>/configure` — write config/credentials
- `POST /api/skills/<skill_id>/verify` — run verification probe
- `POST /api/skills/<skill_id>/skip` — mark optional skill skipped

**Jobs:**
- `POST /api/jobs/register-scheduler` — register OS scheduled task
- `GET /api/jobs/status` — inspect scheduler registration + next run

### 2. `skill.json` Onboarding Schema

```json
{
  "id": "memory-server",
  "name": "Memory Server",
  "kind": "mcp-server",
  "version": "1.0.0",
  "onboarding": {
    "tier": "required",
    "phase": "skills_required",
    "order": 10,
    "title": "Install Memory Server",
    "summary": "Installs, configures, registers, and verifies the memory MCP server.",
    "why_it_matters": "Required for persistent memory and downstream skills.",
    "estimated_minutes": 3,
    "controller_mode": "web|claude|either",
    "depends_on": ["foundation.workspace_root"],
    "facts_schema": {
      "package_installed": "boolean",
      "config_written": "boolean",
      "mcp_registered": "boolean",
      "health_check_passed": "boolean"
    },
    "steps": [
      {
        "id": "install_package",
        "label": "Install package",
        "kind": "command",
        "required": true,
        "command": {
          "windows": "pip install clawd-lobster[memory]",
          "macos": "pip install 'clawd-lobster[memory]'",
          "linux": "pip install 'clawd-lobster[memory]'"
        },
        "success_sets": ["package_installed"]
      },
      {
        "id": "write_config",
        "label": "Write config",
        "kind": "config",
        "required": true,
        "fields": [{"name": "db_path", "type": "path", "required": true}],
        "success_sets": ["config_written"]
      },
      {
        "id": "register_mcp",
        "label": "Register MCP server",
        "kind": "command",
        "required": true,
        "command": {"all": "clawd-lobster skill install memory-server"},
        "success_sets": ["mcp_registered"]
      },
      {
        "id": "verify",
        "label": "Run health check",
        "kind": "probe",
        "required": true,
        "probe": "memory-server",
        "success_sets": ["health_check_passed"]
      }
    ]
  }
}
```

**Constraint:** `facts_schema` must be flat (boolean/string/integer only) in v1. Step kinds limited to: `command|config|probe|link`.

### 3. Controller Lease Handoff

- Lease in `controller.json`: `{lease_id, holder, session_id, token_fingerprint, acquired_at, expires_at, handoff_nonce, revision}`
- Only backend writes lease state
- `acquire`: grants if none exists or expired. **TTL: 90 seconds. Renew every 30 seconds.**
- `handoff`: requires active holder + target + fresh `handoff_nonce`. Target must accept within 30 seconds.
- Expired lease → both clients read-only until one reacquires
- **Claude never mutates state without a valid lease_id. No exceptions.**

### 4. `events.jsonl` Format

```json
{"ts":"2026-04-08T12:00:00Z","seq":1,"session_id":"ob_123","revision":1,"type":"session_created","actor":"backend","controller":"web","item_id":null,"ok":true,"message":"onboarding session initialized"}
{"ts":"2026-04-08T12:01:10Z","seq":2,"session_id":"ob_123","revision":2,"type":"intent_applied","actor":"web","controller":"web","item_id":"foundation.language","intent":"set_foundation","before":{"status":"pending"},"after":{"status":"succeeded","facts":{"value":"en"}},"ok":true,"message":"language selected"}
{"ts":"2026-04-08T12:02:00Z","seq":3,"session_id":"ob_123","revision":3,"type":"probe_failed","actor":"backend","controller":"web","item_id":"memory-server","intent":"verify_skill","before":{"status":"running"},"after":{"status":"failed","error":{"code":"PROCESS_EXIT","detail":"port unavailable"}},"ok":false,"message":"health probe failed"}
```

Required keys: `ts`, `seq`, `session_id`, `revision`, `type`, `actor`, `controller`, `item_id`, `ok`. Append-only.

### 5. Health Check / Reconciliation

Probe contract per skill:
- `detect`: is it installed/configured at all?
- `verify`: can it perform its primary function?
- `repair_hint`: human-readable next action

**Probes must be side-effect free.** No reinstalling, no deploying, no credential mutation.

---

## Round 5: Final Consensus

### 1. Implementation Phases

| Week | Deliverable |
|------|------------|
| 1 | Backend core: state store, lease manager, event log, manifest loader, onboarding API |
| 2 | Web onboarding MVP: server-rendered pages, JS islands, foundations flow, required skills tab |
| 3 | Skill execution + reconciliation: install/configure/verify endpoints, probes, scheduler registration |
| 4 | Claude handoff: tokenized handoff, intent API, lease transfer, audit trail visibility |
| 5 | Hardening: crash recovery, stale lease cleanup, acceptance tests, Ted signoff |

**Do not ship optional skills, TUI parity, or credential backends before Week 5 hardening passes.**

### 2. File Structure

```
clawd_lobster/
  server.py                          ← thin HTTP routing only
  onboarding/
    api.py                           ← request handlers
    state_store.py                   ← atomic read/write state/controller/events
    lease.py                         ← acquire/renew/release/handoff
    manifest.py                      ← load/validate skill onboarding metadata
    reconcile.py                     ← reconciliation runner
    probes.py                        ← per-skill probe registry
    intents.py                       ← allowed transitions + validation
  pages_onboarding.py                ← server-rendered pages + JS islands
  assets/
    onboarding.js                    ← small client helpers (SSE/polling/actions)

skills/*/skill.json                  ← add onboarding sections
templates/onboarding/state.v1.json   ← initial session state template
docs/onboarding-api.md               ← endpoint contract
docs/onboarding-state.md             ← state/event schema

~/.clawd-lobster/onboarding/<session_id>/
  state.json
  controller.json
  events.jsonl
  CLAUDE.md
```

### 3. Ted's Approval Checklist

- [ ] Single-writer guarantee: all state mutations go through backend intents
- [ ] Lease safety: simultaneous web+Claude mutation attempts rejected correctly
- [ ] Crash recovery: kill server mid-write → restart → state remains valid
- [ ] Reconciliation: uninstall a skill → dashboard reflects drift correctly
- [ ] Security: localhost only, token required, token never logged in cleartext
- [ ] UX baseline: bootstrap → foundations → required skills complete E2E without terminal spelunking
- [ ] Scope discipline: optional skills and TUI parity explicitly deferred, not half-implemented

### 4. Top 5 Risks

| Risk | Mitigation |
|------|-----------|
| Lease split-brain between web and Claude | Short TTL, backend-issued lease_id, compare-and-swap expected_revision |
| Manifest complexity explodes | Constrain v1 to fixed step kinds: command/config/probe/link |
| Health probes become destructive or flaky | Separate detect from verify; no probe may mutate system state |
| Windows scheduler + path handling failures | Explicit OS adapters; test paths with spaces; atomic rename |
| State/event corruption from abrupt termination | Temp-write + rename; append-only event log with monotonic seq |

```json
{"agent":"codex","role":"critic","task":"round4-5-onboarding-debate","findings":[{"type":"decision","description":"Backend must expose a single generic intent mutation endpoint plus explicit lease, health, events, and skill execution endpoints."},{"type":"decision","description":"skill.json onboarding metadata constrained to fixed step kinds and flat facts schema in v1."},{"type":"risk","description":"Controller lease handoff is highest architectural risk; requires TTLs, revision checks, backend-only mutation."},{"type":"decision","description":"events.jsonl append-only with seq/revision/before/after/actor attribution."},{"type":"risk","description":"Health probes must be side-effect free."}],"summary":"Converted consensus into concrete architecture: 22 API endpoints, skill manifest schema, lease handoff protocol, event format, probe contracts, 5-week implementation plan, file structure, approval checklist, and risk register.","disagreements":["No direct state.json writes from Claude or web UI","No free-form skill onboarding schema in v1","No side-effect health probes"]}
```
