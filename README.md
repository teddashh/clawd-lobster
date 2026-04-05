🌐 [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-0.5.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Runtime](https://img.shields.io/badge/footprint-25MB_RAM-orange)

<p align="center">
<strong>You'll end up using Claude Code anyway.</strong><br>
<em>The ultimate agent experience — lightest weight, curated features, maximum performance.</em>
</p>

<p align="center">
<sub>Web-guided setup. Multi-layer memory. Multi-agent shared knowledge. Free evolution.</sub>
</p>

---

## What is Clawd-Lobster?

Claude Code is the brain. Clawd-Lobster is the nervous system.

Claude Code is the most capable coding agent available, but it forgets everything between sessions, runs on one machine, and has no skill management. Clawd-Lobster adds exactly what's missing: persistent memory, multi-machine orchestration, curated skills, and self-evolution. Nothing more. Nothing less.

**Clawd-Lobster is a generator.** You run it once, it creates your personal **Hub** — a private GitHub repo that becomes your command center. Your Hub manages all your machines, workspaces, memory, and skills.

```
  clawd-lobster (this repo — the generator)
       │
       │  run install.ps1 once
       │
       ▼
  clawd-yourname (YOUR private Hub — generated for you)
       │
       │  this is what you actually use day-to-day
       │
       ├── Machine A ── Claude Code + skills + memory
       ├── Machine B ── Claude Code + skills + memory
       └── Machine C ── Claude Code + skills + memory
            │
            All connected. All sharing knowledge.
            All always alive via heartbeat.
```

GitHub is the control plane. Git is the protocol. Every piece of state — skills, knowledge, workspace registry, heartbeat status — lives in git and syncs automatically.

**Runtime footprint: 25 MB RAM, 672 KB disk.** One Python process (MCP Memory Server) plus SQLite. Everything else runs-and-exits via OS scheduler or lives in the browser. Zero polling, zero daemon, zero bloat.

```
Disk: 672 KB (code + configs, excluding .git and image assets)
RAM:  ~25 MB (MCP server, the only always-on process)
CPU:  0% idle (no polling, no daemon — OS scheduler wakes things up)
```

---

## Requirements

- **Node.js** 18+ and **Python** 3.11+ and **Git** 2.x+
- **Claude Code** CLI ([install guide](https://docs.anthropic.com/en/docs/claude-code/getting-started))
- A **GitHub** account (for your private Hub repo)

---

## Quick Start

### First machine (create your Hub)

**Windows**
```powershell
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
.\install.ps1
# Answer 4 questions → your private Hub is created → everything is set up
```

**macOS / Linux**
```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
chmod +x install.sh && ./install.sh
```

**Docker**
```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
docker compose up -d && docker compose exec clawd bash
```

### How the setup works

The installer asks you 4 questions. That's it. Everything else is automatic.

```
  ┌──────────────────────────────────────────────────┐
  │  1. Language?                                     │
  │     English / 繁體中文 / 简体中文 / 日本語 / 한국어   │
  │                                                   │
  │  2. First machine or joining?                     │
  │     → New Hub (I'm the first)                     │
  │     → Join Hub (I have the URL)                   │
  │                                                   │
  │  3. Fresh or importing?                           │
  │     → Fresh start                                 │
  │     → Absorb existing system                      │
  │                                                   │
  │  4. Name your Hub / Machine                       │
  │     → Hub: clawd-yourname (becomes private repo)  │
  │     → Machine: home-pc / office-vm / laptop       │
  │     → Domain: work / personal / hybrid            │
  └──────────────────────────────────────────────────┘
```

Then 9 automated steps run:

| Step | Action | Time |
|------|--------|------|
| 1 | Check prerequisites (Node, Python, Git) | 5s |
| 2 | Authenticate Claude Code + GitHub (2 OAuth clicks) | 30s |
| 3 | **Create your Hub** (private repo) or clone existing | 10s |
| 4 | Write config | 5s |
| 5 | Install MCP Memory Server (26 tools) | 10s |
| 6 | Configure Claude Code (CLAUDE.md + .mcp.json) | 5s |
| 7 | Deploy workspaces (clone repos, init memory.db) | varies |
| 8 | Register scheduler + heartbeat | 5s |
| 9 | Absorb existing system (if chosen) | varies |

| Platform | Sync | Heartbeat |
|----------|------|-----------|
| Windows | Task Scheduler (30 min) | Task Scheduler (30 min) |
| macOS | launchd | launchd |
| Linux | cron | cron |
| Docker | Container lifecycle | Container lifecycle |

**Total credentials: 2 OAuth clicks.** No API keys unless you want Oracle L4.

### Adding another machine later

Once your Hub exists on GitHub, adding a machine is even simpler:

```bash
git clone https://github.com/you/clawd-lobster
cd clawd-lobster
./install.ps1   # or ./install.sh

  → Join existing Hub
  → paste your Hub URL
  → name this machine
  → done (clones Hub, deploys workspaces, starts heartbeat)
```

---

## Chapter 1: Memory — Your Agent Remembers

Why this matters: most AI agents start every session from zero. They repeat mistakes, re-learn context, and waste your time.

### 4-Layer Memory System

| Layer | What | Speed | Scope |
|-------|------|-------|-------|
| **L1.5** | CC auto-memory (native) | Instant | Current project |
| **L2** | SQLite + 32 MCP tools | ~1ms | Per workspace |
| **L3** | Markdown knowledge base | ~10ms | Shared via git |
| **L4** | Cloud DB (optional) | ~100ms | Cross-workspace |

### Salience Engine

Important memories float up, stale ones sink:
- Each access: +5% salience boost
- Manual reinforce: +20% boost (capped at 2.0x)
- 30 days untouched: -5%/day decay (floor at 0.01, never deleted)

**CJK-aware token estimation** — Accurate compaction timing for multilingual workloads.

### How It Works in Practice

Memory is not a passive store — it actively shapes how your agent works.

```
You make a decision
  → memory_record_decision("chose SQLite over Postgres", "local-first, no server needed")

Next session starts
  → Boot protocol loads salient decisions + knowledge
  → Claude remembers the decision and its rationale

30 days later
  → Important decisions still salient (accessed often → boosted)
  → Trivial context has decayed naturally (but never deleted)
```

Every trajectory is recorded. Every workspace is shared. Your agents grow together. Your knowledge compounds. Your work is never lost.

---

## Chapter 2: Workspaces — Where Your Agent Works

Why this matters: without a structured place to work, agents lose context, mix up projects, and can't share knowledge across machines.

A workspace is a project directory with memory, skills, and spec support. Every workspace is a git repo (usually private on GitHub).

### Creating a Workspace

Two ways:

1. **`/spec new`** — guided creation with full spec (recommended). See [Chapter 4](#chapter-4-spec--how-your-agent-plans) for details.
2. **`workspace-create.py`** — quick creation without spec:

```powershell
.\scripts\new-workspace.ps1 -name "my-api"
# Creates folder, memory.db, CLAUDE.md, GitHub repo — done.
```

### Workspace Structure

```
my-project/
├── CLAUDE.md              ← project-specific instructions
├── .claude-memory/
│   └── memory.db          ← L2 memory (SQLite)
├── knowledge/             ← L3 knowledge (git-synced)
├── skills/learned/        ← auto-generated skills
├── openspec/              ← spec artifacts (if using /spec)
│   ├── project.md
│   ├── changes/
│   └── specs/
└── .blitz-active          ← present during blitz execution
```

### Activating and Syncing Workspaces

```
~/Documents/Workspace/
├── my-api/          ← registered, synced every 30 min
├── data-pipeline/   ← registered, synced every 30 min
└── random-notes/    ← not a git repo, ignored by sync
```

- Every active workspace syncs via git every 30 minutes
- Toggle workspaces on/off in the Web UI Workspaces tab
- Inactive workspaces stop syncing but keep their data
- The scheduler auto-syncs all git repos under your workspace root

### Multi-Machine Sharing

This is not just one agent. It is a fleet — and they all share the same brain.

```
        ┌─────── GitHub (Control Plane) ───────┐
        │  skills, knowledge, workspace registry │
        └──────────┬────────────┬───────────────┘
                   │            │
     ┌─────────────▼──┐  ┌─────▼─────────────┐
     │  Agent A        │  │  Agent B           │
     │  (office)       │  │  (cloud VM)        │
     │  Claude Code    │  │  Claude Code       │
     │  + local L2 ────┼──┼──► shared L3/L4    │
     └────────────────┘  └───────────────────┘
                   │            │
              ┌────▼────────────▼────┐
              │  Agent C (laptop)    │
              │  joins in 2 minutes  │
              └──────────────────────┘

Every agent contributes memories → shared knowledge grows
Any agent retrieves memories → collective intelligence available
```

- **L2** stays local (fast, per-workspace) — each agent has its own cache
- **L3** syncs via git — every agent reads and writes to the same knowledge base
- **L4** unifies everything — cross-workspace search, audit trail, full history
- **New agent joins?** `git clone + install.ps1` — inherits all accumulated knowledge instantly

### Always Alive — Heartbeat

Your agents never die. The OS scheduler checks every 30 minutes: is each workspace session alive? If not, it revives it with `claude --resume` — full context restored.

```
OS Scheduler (every 30 min)
    │
    ▼ heartbeat.ps1 / heartbeat.sh
    │
    For each workspace in workspaces.json:
    ├─ Session alive? → skip
    └─ Session dead?  → claude --resume → context restored
    │
    ▼ All sessions visible via Claude Code Remote / App
```

- **Terminal open** — session alive, agent has full context, running 24/7
- **Terminal closed** — heartbeat detects, revives automatically
- **All sessions** — visible via Claude Code Remote on any device
- **No custom daemon** — OS scheduler is the watchdog. Never crashes. Zero maintenance.

### Scheduled Automation

OS-level scheduler (Windows Task Scheduler / cron / launchd) — runs even when Claude Code is not active:

- **Heartbeat** — Ensure all workspace sessions stay alive (revive if dead)
- **Git sync** — Pull and push all repos every 30 minutes
- **Salience decay** — Daily memory importance adjustment
- **Client status** — Track each machine's sessions, last heartbeat, deployed workspaces

---

## Chapter 3: Skills — What Your Agent Can Do

Why this matters: Claude Code ships with built-in skills, but you cannot add your own, modify them, or share them with your team. Skills are your competitive advantage.

Skills are self-contained modules. Think Chrome extensions for your AI agent.

### Three Sources of Skills

| Tab | What | Toggle? |
|---|---|---|
| **Claude Native** | Built-in: `/batch`, `/loop`, `/simplify`, `/compact`, etc. | Skills: yes (via permissions). Commands: read-only. |
| **Clawd-Lobster** | Managed: memory, heartbeat, evolve, absorb, spec, connect-odoo | Yes — full lifecycle |
| **Custom / Hub** | Your own + community downloads from ClawHub | Yes — full lifecycle |

One unified view. Three sources. Every skill on your system — whether it came from Anthropic, from Clawd-Lobster, or from you — visible and manageable in one place.

### Core Skills (locked — cannot be disabled)

| Skill | What | Why locked |
|---|---|---|
| Memory Server | 32-tool MCP memory + SQLite | No memory = no agent |
| Heartbeat | Session keep-alive via OS scheduler | No heartbeat = sessions die |
| Evolve | System-level learning + proposal generation | Core differentiator |
| Absorb | Knowledge ingestion from any source | Core learning ability |
| Spec | Guided planning + blitz execution (3W1H) | Core development workflow |

### Optional Skills

| Skill | What | Default |
|---|---|---|
| Migrate | Import from other AI setups | Enabled |
| Connect-Odoo | Odoo ERP integration (XML-RPC) | Disabled |
| Codex Bridge | Delegate work to OpenAI Codex (worker + critic) | Disabled |
| NotebookLM Bridge | Free RAG + content engine via Google NotebookLM | Disabled |

### Skill Management

Every skill is a self-contained module with a `skill.json` manifest. Manage them via **Web UI** or **CLI**.

**Web Dashboard** — Open `webapp/index.html`:
- Card grid with ON/OFF toggles, status indicators, category filters, search
- Inline config — edit settings and credentials per skill
- Health checks — green/yellow/red status for every enabled skill

**CLI Manager:**

```bash
python scripts/skill-manager.py list                     # table of all skills
python scripts/skill-manager.py enable connect-odoo      # enable a skill
python scripts/skill-manager.py disable connect-odoo     # disable a skill
python scripts/skill-manager.py status                   # detailed status
python scripts/skill-manager.py config connect-odoo      # view/edit config
python scripts/skill-manager.py credentials connect-odoo # manage credentials
python scripts/skill-manager.py health                   # run all health checks
python scripts/skill-manager.py reconcile                # regenerate .mcp.json + settings.json
```

### Adding Your Own Skill

1. Create `skills/my-skill/skill.json` — the manifest declares everything:

```jsonc
{
  "id": "my-skill",
  "name": "My Skill",
  "description": "What it does",
  "version": "0.1.0",
  "category": "utility",       // core | integration | automation | intelligence | utility
  "kind": "mcp-server",        // mcp-server | prompt-pattern | cron | poller
  "alwaysOn": false,
  "defaultEnabled": true,
  "mcp": {
    "serverName": "my-skill",
    "command": "python",
    "args": ["-m", "my_skill.server"],
    "cwd": "."
  },
  "permissions": { "allow": ["mcp__my-skill__my_tool"] },
  "credentials": [],
  "configSchema": { ... },
  "healthCheck": { "type": "mcp-ping", "intervalSeconds": 300 },
  "dependencies": { "skills": [], "system": ["python>=3.11"], "python": ["fastmcp>=3.0"] }
}
```

2. Implement the skill (MCP server, script, or SKILL.md)
3. Run `skill-manager.py reconcile` — it auto-registers and updates `.mcp.json` + `settings.json`

**A skill is just 3 config entries.** No SDK. No plugin API. No framework lock-in. The manifest **is** the contract.

---

## Chapter 4: Spec — How Your Agent Plans

Why this matters: without a plan, autonomous execution is just random code generation. Spec-Driven Development gives Claude a blueprint to follow.

Based on the OpenSpec methodology. Claude leads you through planning, then executes autonomously.

### The Flow

```
You: "I want to build a membership site"
  ↓ /spec new
Claude asks questions (3W1H: Why, What, Who, How)
  ↓ you answer (typically 3-6 exchanges)
Claude creates:
  ├── GitHub repo + workspace
  ├── project.md (context capture)
  ├── proposal.md (Why + What + scope)
  ├── design.md (Architecture + data model)
  ├── specs/ (Gherkin scenarios with SHALL/MUST requirements)
  └── tasks.md (100-300 phased tasks, each 5-30 min)
  ↓ you review
"Ready to blitz?"
  ↓ yes
Claude executes all tasks autonomously
  ↓ blitz complete
V1 is ready. Evolution begins.
```

### 3W1H Standard

Every artifact follows Why, What, Who, How — at its appropriate level:

| Artifact | Level |
|---|---|
| project.md | Broad context capture |
| proposal.md | Scope definition |
| design.md | Architecture blueprint |
| specs/ | Testable requirements (SHALL/MUST + Gherkin) |
| tasks.md | Execution plan (phased, file-referenced) |

The same standard applies from planning to decisions to logs to archives.

### Blitz Mode

Full-speed autonomous execution. The spec is the plan — no questions asked.

- **Branch isolation** — all work on `blitz/v1`, main stays clean until verified
- **Phase commits** — `git commit` after each phase completes
- **Evolve paused** — `.blitz-active` marker tells evolve-tick to skip this workspace
- **Delegation markers** — tasks prefixed `[codex]` are skipped for external execution
- **Post-blitz** — merge to main, store spec as knowledge, suggest next steps

### Validation

- Self-validation runs after each artifact (proposal, design, specs, tasks)
- Requirements must use SHALL or MUST — never "should", "could", or "might"
- Every requirement has at least one Gherkin scenario
- Every task includes a file path and fits in 5-30 minutes
- The artifact DAG is strict: project → proposal → design → specs → tasks

### Commands

| Command | What |
|---|---|
| `/spec new` | Guided workspace + spec creation |
| `/spec:status` | Show progress (phase-by-phase with progress bars) |
| `/spec:add "feature"` | Add to existing spec (delta operations) |
| `/spec:blitz` | Start/resume blitz execution |
| `/spec:archive` | Archive completed change + store as knowledge |

---

## Chapter 5: Evolution — How Your Agent Improves

Why this matters: v1 is just the beginning. An agent that cannot learn from its own work is an agent that plateaus.

After v1 is built, your agent keeps getting better — automatically.

### The Evolution Loop

Evolve now generates **proposals** as git-synced markdown files (not executing TODOs directly). Proposals use 3W1H format with effort estimates and are stored in `openspec/proposals/`. Any machine can review proposals; approved ones become TODOs for the next blitz.

```
/absorb (input)
  ├── Scan folder → extract knowledge, decisions, TODOs
  ├── Read GitHub repo → learn patterns + skills
  └── Fetch URL → store insights
       ↓
evolve-tick (every 2 hours)
  ├── Extract patterns from completed work
  ├── Generate improvement proposals (git-synced files)
  ├── Apply salience decay to stale knowledge
  └── Sync knowledge across machines
       ↓
Review (you decide)
  ├── Review proposals in openspec/proposals/
  ├── Approve → becomes TODO for next blitz
  └── Reject → archived with learning captured
```

### Absorb

Feed it anything — folders, GitHub repos, URLs. Claude classifies everything it finds:

```
Detected environments:
  ✓ claude-setup     → 11 workspaces, Oracle config, soul files
  ✓ Raw Claude Code  → CLAUDE.md, auto-memory, sessions
  ✓ OpenClaw         → SOUL.md, MEMORY.md, skills, approvals
  ✓ Hermes Agent     → skills, memory, profiles
```

No parser scripts. Claude Code **is** the parser — it reads any format, understands the semantics, and stores what matters. Three scan depths:

| Depth | What |
|---|---|
| `shallow` | README, CLAUDE.md, top-level config files |
| `normal` | Everything in shallow + key source files, skill definitions, important docs |
| `deep` | Full codebase analysis — all source files, tests, CI configs, scripts |

Items are classified into knowledge (facts, architecture), decisions (lessons, pitfalls), skills (reusable patterns), and TODOs (action items).

### Evolve (Automatic)

Every 2 hours, `evolve-tick.py` reviews completed work and generates improvement proposals. Key properties:

- **Proposals, not TODOs** — evolve generates proposals as git-synced files, not executing directly
- **Never auto-merges** — all proposals stay in `openspec/proposals/` for review
- **Learned skills persist** — stored in both database and git-synced skill files
- **Effectiveness tracking** — each use +2%, each improvement +10%, proven skills score > 2.0x
- **Cross-agent sharing** — skills learned on Agent A are available to Agent B via git sync
- **Natural retirement** — skills unused for 90+ days are flagged as potentially stale
- **Knowledge compounds** — decisions in one workspace inform work in another, solved problems are never solved twice

### Blitz vs Evolve

| | Blitz | Evolve |
|---|---|---|
| When | Building v1 from spec | After v1, improving |
| Speed | All tasks, non-stop | One TODO every 2 hours |
| Scope | Entire project | Single improvement |
| Branch | `blitz/v1` (merged at end) | `evolve/<id>` (review each) |
| Auto-merge | Yes (within blitz branch) | Never — human reviews |

---

## Architecture

For engineers who want to understand the internals.

### How It Works Under the Hood

```
┌──────────────────────────────────────────────┐
│          Clawd-Lobster (Skills Layer)         │
│                                              │
│  Memory System    Workspace Manager          │
│  Scheduler        Migration Tool             │
│  Self-Evolution   (your custom skills)       │
│                                              │
│  Installed via: .mcp.json + settings.json    │
│                 + CLAUDE.md                  │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│            Claude Code (The Brain)            │
│                                              │
│  Agent Loop · Streaming · Tools · Permissions │
│  Maintained by Anthropic. Auto-upgrades.     │
└──────────────────────────────────────────────┘
```

### What's Actually Running?

The repo is ~13K lines total, but most of that is setup files, docs, and instructions for Claude to read. Here is what is actually in memory when your agent is working:

| Layer | What | Lines | RAM | When |
|-------|------|-------|-----|------|
| **Runtime** | MCP Memory Server (26 tools + SQLite) | ~1,400 | ~25 MB | Always on |
| **Runtime** | Odoo Connector (if enabled) | ~280 | ~22 MB | When enabled |
| **Cron** | evolve-tick (proposal generator) | ~465 | ~20 MB peak | Every 2h, then exits |
| **Cron** | heartbeat + sync | ~300 | ~5 MB peak | Every 30min, then exits |
| **Cron** | NotebookLM sync (if enabled) | ~200 | ~15 MB peak | After blitz, then exits |
| **Static** | Web UI (browser renders it) | ~1,900 | 0 on server | On demand |
| **Setup** | Installers, workspace-create, skill-manager | ~2,800 | 0 | Run once |
| **Docs** | SKILL.md files, README, CHANGELOG | ~3,500 | 0 | Claude reads on demand |
| **Config** | skill.json manifests, templates | ~900 | 0 | Read at startup |

**Resident footprint: one Python process (~25 MB) + SQLite.** Everything else either runs-and-exits (cron scripts), lives in the browser (Web UI), or is just files that Claude reads when it needs context.

### The Relationship with Claude Code

Other frameworks rebuild Claude from scratch — then call Claude's API to do the actual thinking:

```
Heavyweight framework approach:
  Custom Engine (300K LOC) ──API call──→ Claude Model
                                ↑
                    Anthropic can change pricing,
                    revoke OAuth, rate-limit,
                    or deprecate endpoints — at any time.
                    Your 300K lines are at their mercy.

Clawd-Lobster approach:
  User runs: claude login          ← human authenticates once
  OS scheduler runs: claude --resume  ← Anthropic's own CLI, their own flag
  Clawd-Lobster just keeps the session alive and manages skills.
```

We do not call Claude's API. We do not manage OAuth tokens. We do not handle rate limits. We schedule **Claude Code itself** — a tool Anthropic built, ships, and maintains. When they improve Claude Code, we get faster. When they change their API, we do not care.

Other frameworks are building a **remote control for someone else's car.** We are sitting **in the car.**

### The Relationship with GitHub

GitHub is the control plane for everything:

- **Hub repo** — your private command center
- **Workspace repos** — each project is a private repo
- **Git sync** — knowledge, skills, and state sync every 30 min
- **Heartbeat status** — machine health pushed to git
- **Spec artifacts** — committed to workspace repos

### Philosophy

**1. Stand on the shoulders of giants.** Claude Code has millions of engineering hours behind it. Rebuilding that from scratch is not ambition — it is waste. We add what's missing (~2K lines) and keep the best engine.

**2. Less code, less breakage.** Three config entries = one skill. Zero SDK. The OS scheduler has been reliable since the 1970s — we use `cron` + `claude --resume` instead of custom daemons. Every line you don't write is a line that can't break.

**3. When the giant grows, you grow.** When Anthropic ships native memory, 24/7 agents, or multi-agent coordination — we don't rewrite, we retire code. Other frameworks compete with Claude Code. We complement it. **Our codebase shrinks over time. Theirs grows.**

### Project Structure

```
clawd-lobster/
├── skills/          9 skill modules (each with skill.json manifest)
├── scripts/         CLI tools: skill-manager, heartbeat, sync, evolve-tick, etc.
├── templates/       Config templates (no secrets)
├── webapp/          Skill Management Dashboard (3-tab Web UI)
├── knowledge/       Shared knowledge base (git-synced)
├── install.ps1/sh   Installers (Windows / macOS / Linux)
└── Dockerfile       Docker support
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full file tree and internals.

---

## Comparison

| | Claude Code (raw) | OpenClaw | Hermes Agent | **Clawd-Lobster** |
|---|---|---|---|---|
| Agent engine | Anthropic | Custom (300K LOC) | Custom (50K LOC) | **Anthropic (native)** |
| Auth model | Human login | OAuth/API key | API key | **Human login once** |
| Cost model | Subscription | Per-token API | Per-token API | **Subscription (flat)** |
| Always alive | No | Custom daemon | Custom daemon | **OS heartbeat + auto-revive** |
| Persistent memory | None | Hybrid search | FTS5 + LLM | **4-layer + salience** |
| Multi-agent shared memory | No | No | No | **Yes (git-synced)** |
| Skill management | N/A | CLI only | Manual | **Web UI + CLI + manifest** |
| Agent evolution | No | No | Self-improving skills | **Yes (proposals + learned skills)** |
| Multi-machine | No | No | No | **Yes (MDM-style)** |
| Session management | Manual | Gateway process | Manual | **Auto-revive all sessions** |
| Onboarding | Manual | Complex | Moderate | **Web wizard, 5 languages** |
| Auto-upgrades | Yes | No | No | **Yes** |
| Codebase to maintain | 0 | ~300K LOC | ~50K LOC | **~2K LOC** |
| Anthropic API change | Transparent | Breaking | Breaking | **Transparent** |
| Audit trail | No | Security audit | No | **Full (every action)** |
| Skill install | — | Plugin SDK | 3-file change | **1 manifest + reconcile** |

---

## Roadmap

**Skills**
- [x] Odoo ERP Connector — XML-RPC integration with poller (v0.4.0)
- [x] Codex Bridge — delegate work to OpenAI Codex, worker + critic roles (v0.5.0)
- [x] NotebookLM Bridge — free RAG + content engine via Google NotebookLM (v0.5.0)
- [x] Spec-Driven Development — guided planning with OpenSpec methodology (v0.5.0)
- [ ] SearXNG — private self-hosted web search, no data leaves your network
- [ ] Docker Sandbox — isolated code execution for untrusted operations
- [ ] Browser Automation — Playwright-powered web interaction

**Platform**
- [x] Linux installer (bash) + macOS installer (v0.3.0)
- [x] Skill Management Dashboard — Web UI + CLI for skill lifecycle (v0.4.0)
- [x] Skill manifest system — `skill.json` with config, credentials, health checks (v0.4.0)
- [ ] Supabase L4 — one-click cloud database (no Oracle wallet needed)

**Evolution**
- [x] Evolution Loop with proposals — evolve generates git-synced proposals, not direct TODOs (v0.5.0)
- [ ] Skill marketplace — community-contributed skills, one-click install
- [x] Auto-skill generation — agent learns from successful patterns (v0.3.0 evolve skill)
- [ ] Team mode — multi-user shared workspaces with role-based access
- [ ] Agent-to-agent delegation — agents assign tasks to each other

---

## FAQ

### "Isn't this just Claude Code with a wrapper?"

Yes. That is the point.

Claude Code is the most capable coding agent available — backed by millions of engineering hours from Anthropic. OpenClaw rebuilds the engine from scratch (300K lines). Hermes rebuilds it again (50K lines). We add what is missing (2K lines) and keep the best engine.

When Anthropic ships the next breakthrough, we get it instantly. They have to rewrite their adapters.

### "But other agents run 24/7 and keep learning"

So does ours. The scheduler syncs knowledge every 30 minutes. Memory evolves daily via salience decay. Learned skills propagate across all machines via git. **The agent does not need to be running for knowledge to grow.**

The heartbeat ensures sessions stay alive: if a terminal closes, the OS scheduler detects it and revives the session with `claude --resume` — full context restored. No custom daemon needed. Just Claude Code, always on. See the [Architecture](#the-relationship-with-claude-code) section for the full comparison of how we handle 24/7 differently from per-token API frameworks.

### "Claude Code already has built-in skills and MCP. Why do I need more?"

Claude Code's built-in skills are **closed** — you can't add, modify, or share them. That's the built-in apps on your phone. Clawd-Lobster is the App Store.

MCP gives you a protocol for tool servers, but no lifecycle management. Installing a skill means editing 3 JSON files. Disabling one means deleting entries from 2 files and hoping you got them all. Second machine? Redo everything.

**MCP is the protocol. We are the package manager.** What we add:

| MCP (raw) | Skill Management (ours) |
|---|---|
| Flat JSON config | `skill.json` manifest with schema, credentials, health checks, dependencies |
| Manual edit to install | `skill-manager.py enable <id>` — one command |
| Manual edit to remove | `skill-manager.py disable <id>` — one command, clean removal |
| No credential standard | Centralized `~/.clawd-lobster/credentials/`, per-skill field definitions |
| No health monitoring | Built-in health checks (mcp-ping, command, HTTP) |
| No UI | Web dashboard with card grid, toggles, search, category filters |
| Per-machine config | Registry syncs across machines via git |
| No dependency tracking | Skills declare what they need — other skills, system tools, Python packages |

See [Chapter 3](#chapter-3-skills--what-your-agent-can-do) for the full skill management system.

### "Won't Anthropic block this?"

We schedule `claude` CLI commands via OS cron — the same way you'd schedule `git pull`. We use `claude --resume`, `--allowedTools`, and MCP servers — all flags Anthropic ships in their own CLI. No API key automation. No OAuth token scraping. No reverse engineering. **We automate a CLI tool. We don't impersonate a user.**

### "What about costs?"

With a Pro subscription ($20/month), there is no per-token cost. No need for "cheap model for grunt work" architectures, no model routers, no dual inference stacks. One subscription. One engine. **Predictable cost is a feature.**

---

## Contributing

Contributions welcome! The easiest way to contribute:

1. **Add a skill** — create a folder in `skills/` with a `SKILL.md` or MCP server
2. **Improve templates** — better defaults in `templates/`
3. **Platform support** — help with Linux/macOS installers

---

## License

MIT — use it however you want.

---

<p align="center">
<sub>Not affiliated with Anthropic. Built on top of <a href="https://claude.ai/code">Claude Code</a>.</sub>
</p>
