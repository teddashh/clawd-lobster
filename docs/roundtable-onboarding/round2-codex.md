# Round 2: Codex GPT-5.4 (Critic) - Claude's Revised Onboarding Proposal

Claude fixed three major problems from round 1. That meaningfully improves the direction. The remaining issues are narrower now, but they are still architectural, not cosmetic.

## What Is Now Correct

1. OS scheduler remains the scheduler of record.
2. Foundations, skills, and jobs are now separated.
3. Web and TUI no longer try to share rendering.
4. Token auth for localhost is the right baseline.
5. Oracle is kept out of first-run bootstrap and delayed until the relevant skill flow.

## What Is Still Wrong

### 1. `~/.clawd-lobster/state.json` should not be a shared direct-write surface

"Both web and Claude read/write it" is the new weak point.

That creates predictable failure modes:
- torn writes or partial writes if two actors save near-simultaneously
- no concurrency control across web, TUI, and Claude
- no audit trail for who changed what
- no event mechanism beyond polling file timestamps
- no validation boundary, so malformed state can brick onboarding
- no clean way to distinguish desired state from observed state

My position: keep file-backed persistence, but do **not** let every actor mutate the file directly.

Use this instead:
- API/service layer owns all writes
- web, TUI, and Claude call the same mutation endpoints or CLI commands
- the persisted file is a storage artifact, not a public coordination primitive
- write atomically via temp file + rename
- include a `version` or `etag` field for optimistic concurrency
- log state transitions separately from durable config

If you want a concrete model:
- `config.json`: durable user configuration
- `onboarding-state.json`: resumable workflow state
- `events.jsonl`: append-only audit trail for transitions/errors

### 2. "Neither is master" is good UX language but bad systems language

For the user, yes: web and Claude feel like co-pilots.

For the implementation, no: there must still be one authority for state transitions. Otherwise "either can advance the flow" becomes race-condition-as-a-feature.

My position:
- Presentation has two peers: web and Claude
- Control plane has one authority: backend state machine/service
- Agents and UI submit intents; the service validates and applies transitions

### 3. The current state model is underspecified for recovery

Claude's example state is too lossy for real recovery. It captures progress labels, not execution truth.

It is missing:
- per-item status: `pending|running|blocked|succeeded|failed|skipped`
- timestamps
- last actor
- retry count
- dependency satisfaction
- observed environment facts vs requested setup
- last error details with remediation hint
- active session/lease info

Without that, "resume after reboot" will devolve into guessing.

### 4. Tiering is improved, but the required set is still too large for MVP

For v1, the proposal still tries to deliver too much. Cut aggressively.

### 5. `migrate` and `sync-all` should not sit in the main parade path

- `migrate` should appear only when legacy artifacts are detected
- `sync-all` should be configured as infrastructure setup, not presented as a user-facing chapter

### 6. "Rich now, Textual later" is acceptable only if v1 TUI stays narrow

v1 TUI: guided terminal onboarding, status screens, simple action prompts. Do not commit to Textual dashboard work without proven need.

## Answers To Claude's 4 New Questions

### 1. SPA or multi-page?
Multi-page, with small JS islands. Fits stdlib server, simpler history/reload, easier to secure and debug, keeps backend state machine as source of truth. Do not build a JavaScript router.

### 2. How should "resume after reboot" work?
Reconcile from real environment on restart:
1. Load persisted onboarding state
2. Probe machine for actual facts (auth valid? workspace exists? scheduler entries installed?)
3. Recompute each item's status
4. Resume from first incomplete or failed required item

If persisted state and observed facts diverge, observed facts win.

### 3. Simultaneous web + TUI sessions?
For visibility: yes. For mutating onboarding control: only with coordination.
- Allow multiple read-only viewers
- Allow exactly one active onboarding controller lease at a time
- Permit another client to "take control" explicitly if needed

### 4. What is the MVP scope?
Cut to:
1. Bootstrap (prerequisites, Claude Code, config/token, first workspace, dashboard)
2. Foundations (language, auth, hub, workspace root)
3. Required skills only (memory-server, spec, absorb, evolve, heartbeat, deploy)
4. Scheduler registration for required jobs only
5. Persistent web dashboard (Onboarding, Workspaces, Skills, Settings/Credentials)
6. Minimal terminal companion (launch Claude, CLI status, optional rich progress)

Defer: power skills, migrate (unless detected), sync-all prominence, TUI dashboard parity, advanced credential backends, simultaneous multi-controller sessions.

## Remaining Risks

1. Server/runtime may be too thin for live coordination
2. Skill setup docs are not uniform — need manifest-level onboarding metadata
3. Credential UX can still leak sensitive account identity
4. "Co-pilot" can drift into duplicated guidance — need one generated explanation source
5. Recovery logic can be deceptive if it checks files not executable reality
6. Dashboard scope creep remains the main delivery risk

## Bottom Line

Claude's revised proposal is directionally sound. The remaining correction is straightforward:
- keep the co-pilot UX
- reject direct shared writes to a single state file
- make the backend the sole transition authority
- design reboot recovery around reconciliation with real machine state
- cut the MVP to foundations plus required skills only

```json
{"agent":"codex","role":"critic","task":"round2-onboarding-debate","findings":[{"type":"risk","description":"Direct shared reads/writes to state.json by web, TUI, and Claude will create race conditions and weak recovery semantics."},{"type":"decision","description":"Keep co-pilot UX, but make the backend service/state machine the sole authority for workflow transitions."},{"type":"suggestion","description":"Multi-page server-rendered dashboard with small JS islands rather than a SPA."},{"type":"suggestion","description":"Reboot resume by reconciling persisted state against real machine facts."},{"type":"suggestion","description":"Allow multiple viewers but only one active onboarding controller lease at a time."},{"type":"risk","description":"MVP is still too large; defer power-skill flows, migrate-by-default, TUI dashboard parity."}],"summary":"Claude corrected the major Round 1 architecture mistakes, but the revised proposal still makes state ownership too loose and keeps MVP scope too broad. Move all workflow mutations behind a single backend authority, using file-backed persistence only as an implementation detail.","disagreements":["Web, TUI, and Claude should not all directly mutate a shared state.json","Neither-is-master is acceptable as UX but not as control-plane design","Migrate and sync-all should not be prominent onboarding chapters","TUI dashboard parity should stay out of MVP"]}
```
