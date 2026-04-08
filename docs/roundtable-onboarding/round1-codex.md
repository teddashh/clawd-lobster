# Round 1: Codex GPT-5.4 (Critic) — Onboarding & Dashboard Redesign

## Agreements

Claude is right on three core points.

1. Oracle should stay out of first-run onboarding and appear only when the user reaches memory/absorb configuration. That matches the brief and current skill metadata, where Oracle is a memory capability toggle rather than a bootstrap prerequisite.
2. Skills need ordered setup and user-facing explanations. The repo already has the right source of truth for this in manifests and the skill-manager registry flow.
3. Web closeable while background automation survives is non-negotiable.

## Challenges

### 1. The "single daemon replaces cron" idea is wrong for this repo

Claude proposes one daemon process with internal scheduling and "no separate cron/Task Scheduler dependency". That conflicts with both the brief and the current architecture.

- The brief explicitly requires cron/scheduler jobs to be registered during setup, not simulated in-process.
- The architecture doc describes cron jobs as run-and-exit tasks, with low resident footprint, not a permanent orchestration daemon.
- Skill manifests already encode OS-style schedules for `evolve`, `heartbeat`, and `connect-odoo`.

My position: keep OS scheduler as source of truth. The dashboard should inspect, register, repair, and display jobs. It should not become the scheduler.

### 2. "Skill Parade" is directionally right but modeled against the wrong abstraction

Claude mixes actual skills with non-skill setup checkpoints: GitHub Hub and `sync-all` are not skills, but they are inserted into the parade as if they were first-class skill cards. That will create a mismatch between the setup flow and the actual registry model and the dashboard's "all skills" view.

My position: separate setup units into:
- Foundations: language, workspace root, Claude auth, Hub registration
- Required skills: registry/manifests drive this
- Optional skills: registry/manifests drive this
- Background jobs: scheduler registration attached to the relevant skill or foundation

That preserves a clean skills page without lying about what is and is not a skill.

### 3. Textual parity is too expensive for v1

Claude wants full web/TUI parity via `textual`. That adds a new dependency, a second rendering surface, and a new widget model while the current dashboard service layer is barely present: `dashboard.py` is still a stub, and the current web server is a simple `HTTPServer` app.

My position: parity should be at the command/data model level, not pixel parity. Build one backend with:
- registry/config/workspace/credential APIs
- web UI first
- a simpler terminal dashboard second: list/detail/actions, not a full mirrored UI framework

### 4. Credential design is under-specified and mismatched to current implementation

Claude proposes encrypted JSON with OS keyring. The repo today stores credentials as separate restricted JSON files under `~/.clawd-lobster/credentials`. Moving immediately to AES + keyring adds non-stdlib complexity and migration burden without a service abstraction in place.

My position: phase it.
- v1: masked display, per-credential files, restrictive permissions, never echo secrets back
- v2: optional OS keyring backend behind the same credential provider interface

## Alternative Architecture

I would replace Claude's 3 phases with 4 narrower ones.

### Phase A: Bootstrap
- Keep current prerequisite checking and handoff pattern.
- Do not ask the user to choose between web and TUI first. Default to the web flow if available, with a terminal fallback.
- Complete only foundations here: language, auth, workspace root, Hub registration.

### Phase B: Setup Queue
- Enter a manifest-driven queue after handoff.
- Queue order comes from dependency graph plus `required/optional` grouping.
- Each card has icon, explanation, dependencies, status, "Set up", "Skip", "Why first?", "Fix issue".

### Phase C: Dashboard
- Dashboard is a control plane over files and OS schedulers, not the runtime owner.
- Tabs: Workspaces, Skills, Jobs, Credentials, Settings.
- The current workspaces-only dashboard expands from `pages.py` rather than inventing a new daemon protocol first.

### Phase D: TUI
- Same backend actions, simpler terminal presentation.
- Exact feature coverage for create/update flows; looser visual parity.

## Answers To Claude's 6 Open Questions

1. **Single daemon process?**
No. Use separate concerns: file-backed config/registry plus OS schedulers for jobs. The web server can be long-running, but it must not be the scheduler of record.

2. **Shared `pages.py` for TUI and web?**
No. Share backend services and view-model shaping. Do not share renderers.

3. **Headless Skill Parade?**
Use a noninteractive profile: `clawd-lobster setup --profile path.json` or flags. Headless mode should execute the same setup graph with explicit defaults and fail on missing required dependencies.

4. **Is `textual` right?**
Not for v1. It is viable later, but it is the wrong first move under stdlib-preferred constraints and current backend immaturity.

5. **What if a required skill fails?**
Hard-stop on foundational required skills. Offer `Retry`, `Troubleshoot`, `Skip and stay degraded` only where the dependency graph allows limited mode. For optional skills, skip is fine.

6. **Should localhost dashboard have auth?**
Yes, for mutating endpoints. Loopback-only is not enough. At minimum require a per-session nonce or local admin token for POST actions.

## Concerns Claude Missed

1. The current server is single-threaded `HTTPServer`. Long-lived SSE streams will compete with normal requests unless the server model changes.
2. The current `serve --daemon` flag only detaches the web server and writes `server.pid`. It is not a service manager and should not be treated as one.
3. The dashboard service layer is not built yet. `dashboard.py` is a placeholder, so the first implementation step should be backend extraction, not UI expansion.
4. Skill docs are inconsistent: `skills/memory-server/SKILL.md` does not exist. There is a manifest and README instead. Onboarding cannot assume every skill has uniform rich setup docs.
5. The global boot protocol depends on memory being operational very early. Any UX that lets users "skip memory for now" needs to describe the degraded system honestly.
6. Claude's sample key-management UI exposes too much account identity detail. This repo explicitly warns against leaking personal info.

## Bottom Line

Claude's proposal gets the user-facing direction mostly right, but the control-plane architecture is upside down. The redesign should be manifest-driven, scheduler-aware, and file-backed first. Do not replace OS jobs with a monolithic daemon. Do not build full TUI/web parity before there is a real backend service layer. Do not blur skills, foundations, and jobs into one parade model.

```json
{"agent":"codex","role":"critic","task":"round1-onboarding-debate","findings":[{"type":"blocker","description":"Claude's single-daemon scheduler proposal conflicts with the brief's explicit cron/Task Scheduler setup requirement and the repo's existing scheduled-skill manifests."},{"type":"risk","description":"Skill Parade currently mixes real skills with non-skill setup checkpoints like GitHub Hub and sync-all, which will create a mismatch between onboarding, registry state, and dashboard UX."},{"type":"risk","description":"Full textual-based TUI/web parity is premature because the backend service layer is not implemented and the current web server is a minimal single-threaded HTTPServer."},{"type":"suggestion","description":"Use a manifest-driven setup queue with separate categories for foundations, required skills, optional skills, and background jobs; keep OS schedulers as source of truth and let the dashboard inspect/manage them."},{"type":"suggestion","description":"Phase credential management: start with masked file-backed secrets and a provider abstraction, then add optional OS keyring support later."}],"summary":"My main objection is architectural: Claude pushes too much responsibility into a single long-running daemon, but this repo already models automation as OS-scheduled jobs plus file-backed state. I support a skills-first post-handoff setup flow, but it should be manifest-driven, dependency-aware, and separated into foundations, skills, and jobs rather than presented as one undifferentiated parade.","disagreements":["Single daemon should not replace OS schedulers","TUI parity should be backend-level, not renderer-level","GitHub Hub and sync-all should not be modeled as skills"]}
```
