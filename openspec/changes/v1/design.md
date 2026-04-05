# V1 Design: Unified User Experience

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                                                         │
│  Terminal (CLI)              Web (Browser)               │
│  ┌──────────────┐           ┌──────────────────────┐    │
│  │ clawd-lobster│           │ localhost:3333        │    │
│  │  setup       │           │  /           → home   │    │
│  │  serve       │           │  /onboarding → wizard │    │
│  │  workspace   │           │  /workspaces → list   │    │
│  │  squad       │           │  /squad      → chat+  │    │
│  │  status      │           │              dashboard│    │
│  └──────┬───────┘           └──────────┬───────────┘    │
│         │                              │                 │
│         └──────────┬───────────────────┘                 │
│                    │                                     │
├────────────────────┼─────────────────────────────────────┤
│              Core Engine                                 │
│                    │                                     │
│  ┌─────────────────┼──────────────────────────────────┐  │
│  │    clawd_lobster/ (Python package)                  │  │
│  │                                                     │  │
│  │  cli.py         — argparse entry point              │  │
│  │  server.py      — http.server + routing             │  │
│  │  onboarding.py  — setup wizard logic                │  │
│  │  squad.py       — unified squad orchestrator        │  │
│  │  dashboard.py   — workspace/health data provider    │  │
│  │  pages/         — HTML templates (inline strings)   │  │
│  └─────────────────┼──────────────────────────────────┘  │
│                    │                                     │
├────────────────────┼─────────────────────────────────────┤
│           External Dependencies                          │
│                    │                                     │
│  ┌─────────┐  ┌───┴─────┐  ┌──────────┐  ┌──────────┐  │
│  │Claude   │  │Agent SDK│  │ SQLite   │  │  Git     │  │
│  │Code CLI │  │(query())│  │memory.db │  │(Hub sync)│  │
│  └─────────┘  └─────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Why this architecture

- **Single Python package** (`clawd_lobster/`) instead of scattered scripts
- **No framework** — stdlib `http.server` + inline HTML (keeps zero-dependency promise)
- **CLI and Web share the same engine** — no logic duplication
- **Agent SDK is the only Claude interface** — no more `claude -p` subprocess calls

### What NOT to build

- No React/Vue/Angular — HTML strings in Python are fine for <5 pages
- No WebSocket — polling `/api/state` every 2s is simple and proven
- No database migration framework — SQLite schema is stable
- No Docker — this runs on the user's machine

## Data Model

No schema changes. Existing data stores:

| Store | Location | Purpose |
|-------|----------|---------|
| `memory.db` | `<workspace>/.claude-memory/` | Per-workspace memory (decisions, knowledge, skills, todos, audit) |
| `workspaces.json` | `<clawd-lobster>/` | Workspace registry |
| `.spec-squad.json` | `<workspace>/` | Squad progress state |
| `config.json` | `~/.clawd-lobster/` | Global config (workspace_root, machine_id) |

## API Design (Web Server)

All endpoints serve JSON or HTML. No authentication (localhost only).

| Method | Path | Returns | Purpose |
|--------|------|---------|---------|
| GET | `/` | HTML | Home page (redirect to /onboarding if first time, else /workspaces) |
| GET | `/onboarding` | HTML | Setup wizard |
| POST | `/api/onboarding/check` | JSON | Check prerequisites |
| POST | `/api/onboarding/complete` | JSON | Finalize setup |
| GET | `/workspaces` | HTML | Workspace list |
| GET | `/api/workspaces` | JSON | Workspace data |
| POST | `/api/workspaces/create` | JSON | Create workspace |
| GET | `/squad` | HTML | Spec Squad (chat + dashboard) |
| POST | `/api/squad/chat` | JSON | Discovery chat turn |
| POST | `/api/squad/start` | JSON | Launch squad agents |
| GET | `/api/squad/state` | JSON | Squad progress |
| GET | `/api/status` | JSON | System health |

## User Flows

### Flow 1: First-Time User (Noob)

```
1. User runs: pip install clawd-lobster (or git clone + pip install -e .)
2. User runs: clawd-lobster serve
3. Browser opens localhost:3333
4. Redirect to /onboarding (first time detected via missing config.json)
5. Step 1: Prerequisites check (green/red indicators)
6. Step 2: "Login to Claude" button → opens OAuth
7. Step 3: "What kind of user are you?" (Noob/Expert/Tech)
8. Step 4: "Name your first project" → creates workspace
9. Step 5: "Let's build something!" → opens /squad chat
10. Claude asks discovery questions in chat
11. User answers 3-5 questions
12. Claude says "Ready!" → dashboard shows agents working
13. Agents finish → user has a spec + code in their workspace
```

### Flow 2: Returning User

```
1. User runs: clawd-lobster serve (or it's already running as a service)
2. Browser shows /workspaces — list of all workspaces with status
3. User clicks a workspace → sees spec progress, recent activity
4. User clicks "New Squad" → enters /squad chat for that workspace
5. Or: user goes to terminal and runs claude in the workspace directly
```

### Flow 3: Terminal Expert

```
1. User runs: clawd-lobster setup (terminal onboarding)
2. Claude asks questions in terminal
3. User runs: clawd-lobster workspace create my-project
4. User runs: cd ~/Documents/Workspace/my-project && claude
5. Inside Claude: /spec:squad (runs squad in terminal mode)
6. Or: clawd-lobster squad start --workspace my-project
```

## Technology Choices

| Choice | Rationale |
|--------|-----------|
| Python stdlib http.server | Zero deps, ~200 LOC for full server |
| Inline HTML (no templates) | Same pattern as spec-squad-sdk.py, proven to work |
| Claude Agent SDK | Official Anthropic SDK, proper permission model |
| SQLite | Already in use, proven, no migration needed |
| 2s polling (not WebSocket) | Simpler, proven in spec-squad-viewer.py |

## Security Considerations

- Web server binds to `127.0.0.1` only (not `0.0.0.0`)
- No authentication needed (localhost)
- Agent SDK handles Claude permissions via `permission_mode`
- No secrets stored in web-accessible files
- `.spec-squad.json` contains no sensitive data

## Deployment

- `pip install clawd-lobster` (when published to PyPI)
- Or `git clone + pip install -e .` (development)
- `clawd-lobster serve` starts web server (foreground or as background daemon)
- Optional: OS service/startup item to auto-start on boot
