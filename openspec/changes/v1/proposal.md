# V1 Proposal: Unified User Experience

## Why

Users currently face:
- 15+ scripts with no clear entry point
- 3 competing Spec Squad implementations (subprocess, form UI, Agent SDK)
- No visual feedback during multi-agent operations
- Installation requires reading source code to understand what to do
- No way to know system health without running individual scripts

This wastes the product's best feature: **it's actually simple underneath** (~2,000 LOC). The complexity is in the UX, not the code.

## What Changes

### In Scope

1. **`clawd-lobster` CLI entry point** — single command that dispatches everything
   - `clawd-lobster serve` — start the web dashboard (persistent)
   - `clawd-lobster setup` — interactive terminal onboarding
   - `clawd-lobster workspace create <name>` — create workspace
   - `clawd-lobster squad start` — launch Spec Squad (terminal mode)
   - `clawd-lobster status` — show system health

2. **Web Dashboard** (`localhost:3333`, persistent)
   - Onboarding wizard (first-time only)
   - Workspace list with status
   - Spec Squad launcher (chat discovery → agent dashboard)
   - System health (heartbeat, memory, sync status)

3. **Unified Spec Squad** — merge 3 scripts into one
   - Terminal mode: Claude asks questions in terminal, agents run in background
   - Web mode: Chat UI for discovery, dashboard for agent monitoring
   - Same orchestration engine underneath (Agent SDK)

4. **Onboarding wizard** (web or terminal)
   - Step 1: Check prerequisites (Python, Node, Claude CLI, git)
   - Step 2: OAuth login (open browser)
   - Step 3: Choose persona (Noob / Expert / Tech)
   - Step 4: Create first workspace
   - Step 5: Run first spec (guided)

5. **Script consolidation** — retire redundant scripts
   - `spec-squad.py` (subprocess) → deprecated, kept for reference
   - `spec-squad-ui.py` (form) → absorbed into web dashboard
   - `spec-squad-sdk.py` (Agent SDK) → becomes the engine
   - `spec-squad-viewer.py` → absorbed into web dashboard

### Out of Scope

- Multi-user / team features
- Cloud deployment
- Plugin marketplace UI
- Mobile interface
- Custom model selection UI
- Real-time streaming in web chat (v1 uses request/response, not SSE)

## Who

- **Noob**: Uses web wizard exclusively. Never touches terminal.
- **Expert**: Uses terminal onboarding, switches to web for monitoring.
- **Tech**: Uses CLI directly, reads SKILL.md, extends the system.

## How

Consolidate around two surfaces:
1. **`clawd-lobster` CLI** — Python entry point, dispatches to existing scripts
2. **Web dashboard** — Single-page app served by Python stdlib http.server

Both surfaces use the same backend:
- Agent SDK for Claude interactions
- SQLite for state
- workspaces.json for registry
- .spec-squad.json for squad state
