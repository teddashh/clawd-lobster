# V1 Tasks: Unified User Experience

## Phase 1: Package Structure (Foundation)

- [ ] Create `clawd_lobster/` Python package directory (`clawd_lobster/__init__.py`)
- [ ] Create `clawd_lobster/cli.py` — argparse entry point with subcommands: serve, setup, workspace, squad, status
- [ ] Create `clawd_lobster/server.py` — unified HTTP server (merge spec-squad-ui.py + spec-squad-viewer.py logic)
- [ ] Create `clawd_lobster/squad.py` — merge spec-squad-sdk.py orchestration into a clean module
- [ ] Create `clawd_lobster/onboarding.py` — setup wizard logic (prerequisite check, config init)
- [ ] Create `clawd_lobster/dashboard.py` — workspace list + health data provider
- [ ] Create `clawd_lobster/pages.py` — all HTML page strings (onboarding, workspaces, squad)
- [ ] Add `pyproject.toml` with `[project.scripts] clawd-lobster = "clawd_lobster.cli:main"` entry point
- [ ] Verify: `pip install -e .` works and `clawd-lobster --help` shows all subcommands

## Phase 2: CLI Entry Point

- [ ] Implement `clawd-lobster serve` — start web server on port 3333, open browser (`clawd_lobster/cli.py`)
- [ ] Implement `clawd-lobster setup` — terminal onboarding wizard (`clawd_lobster/cli.py`)
- [ ] Implement `clawd-lobster workspace create <name>` — proxy to workspace-create.py logic (`clawd_lobster/cli.py`)
- [ ] Implement `clawd-lobster squad start` — terminal squad mode (`clawd_lobster/cli.py`)
- [ ] Implement `clawd-lobster status` — show system health in terminal (`clawd_lobster/cli.py`)
- [ ] Implement `clawd-lobster serve --daemon` — background mode with PID file (`clawd_lobster/cli.py`)
- [ ] Verify: each subcommand runs without error and shows help text

## Phase 3: Web Server + Routing

- [ ] Implement route `/` — home page, redirect to /onboarding if first-time (`clawd_lobster/server.py`)
- [ ] Implement route `/onboarding` — setup wizard page (`clawd_lobster/server.py`)
- [ ] Implement route `/workspaces` — workspace list page (`clawd_lobster/server.py`)
- [ ] Implement route `/squad` — spec squad chat + dashboard page (`clawd_lobster/server.py`)
- [ ] Implement API `/api/status` — system health JSON (`clawd_lobster/server.py`)
- [ ] Implement API `/api/workspaces` — workspace list JSON (`clawd_lobster/server.py`)
- [ ] Implement API `/api/workspaces/create` — create workspace POST (`clawd_lobster/server.py`)
- [ ] Implement API `/api/squad/chat` — discovery chat POST (`clawd_lobster/server.py`)
- [ ] Implement API `/api/squad/start` — launch squad POST (`clawd_lobster/server.py`)
- [ ] Implement API `/api/squad/state` — squad state GET (`clawd_lobster/server.py`)
- [ ] Verify: `clawd-lobster serve` starts and all routes return 200

## Phase 4: Onboarding Wizard

- [ ] Implement prerequisite checker — Python, Claude CLI, git, Node (optional) (`clawd_lobster/onboarding.py`)
- [ ] Build onboarding HTML page — 4-step wizard, dark theme, progress bar (`clawd_lobster/pages.py`)
- [ ] Step 1: Prerequisites check with live status indicators (`clawd_lobster/pages.py`)
- [ ] Step 2: Claude auth check + "Login" button (`clawd_lobster/pages.py`)
- [ ] Step 3: Persona selector (Noob/Expert/Tech) — saves to config.json (`clawd_lobster/onboarding.py`)
- [ ] Step 4: Create first workspace — name input + "Create" button (`clawd_lobster/pages.py`)
- [ ] Terminal equivalent: `clawd-lobster setup` asks same questions in terminal (`clawd_lobster/onboarding.py`)
- [ ] Verify: fresh user can complete onboarding in < 5 minutes

## Phase 5: Workspace Dashboard

- [ ] Build workspace list HTML — cards with name, status, last activity, spec progress (`clawd_lobster/pages.py`)
- [ ] Implement workspace data provider — read workspaces.json + each workspace's state (`clawd_lobster/dashboard.py`)
- [ ] Add "New Workspace" button → inline create form (`clawd_lobster/pages.py`)
- [ ] Add "Launch Squad" button per workspace → redirect to /squad?workspace=<path> (`clawd_lobster/pages.py`)
- [ ] Add health indicators — heartbeat status, memory size, sync status (`clawd_lobster/dashboard.py`)
- [ ] Verify: dashboard shows accurate data for existing workspaces

## Phase 6: Unified Squad

- [ ] Merge squad orchestration from spec-squad-sdk.py into `clawd_lobster/squad.py`
- [ ] Build squad HTML — chat panel (left) + agent dashboard (right), single page (`clawd_lobster/pages.py`)
- [ ] Chat discovery: Agent SDK `query()` with discovery system prompt (`clawd_lobster/squad.py`)
- [ ] DISCOVERY_COMPLETE detection → auto-transition to dashboard view (`clawd_lobster/pages.py`)
- [ ] Dashboard: 4 agent cards + timeline + stats (reuse spec-squad-viewer.py design) (`clawd_lobster/pages.py`)
- [ ] Terminal mode: `clawd-lobster squad start` runs same orchestration with terminal output (`clawd_lobster/squad.py`)
- [ ] Verify: web and terminal modes produce same .spec-squad.json state file

## Phase 7: Script Consolidation + Cleanup

- [ ] Move spec-squad.py to `scripts/legacy/spec-squad-v1.py` (keep for reference)
- [ ] Move spec-squad-ui.py to `scripts/legacy/spec-squad-ui-v1.py`
- [ ] Move spec-squad-viewer.py to `scripts/legacy/spec-squad-viewer-v1.py`
- [ ] Move spec-squad-sdk.py to `scripts/legacy/spec-squad-sdk-v1.py`
- [ ] Update skills/spec/SKILL.md — replace script references with `clawd-lobster` CLI commands
- [ ] Update README.md — add "Getting Started" section with `clawd-lobster serve`
- [ ] Add `scripts/legacy/README.md` explaining these are v0 prototypes
- [ ] Verify: `clawd-lobster squad start` works end-to-end without referencing legacy scripts

## Phase 8: Testing + Polish

- [ ] Test Flow 1: Fresh install → onboarding → first workspace → first squad run
- [ ] Test Flow 2: Returning user → dashboard → launch squad on existing workspace
- [ ] Test Flow 3: Terminal expert → CLI-only workflow
- [ ] Test: Windows 11 — all paths, hooks, commands work
- [ ] Test: `clawd-lobster serve --daemon` starts and stays running
- [ ] Test: Web UI works in Chrome, Firefox, Edge
- [ ] Run Codex adversarial review on final state
- [ ] Fix all issues found
- [ ] Final commit and push
