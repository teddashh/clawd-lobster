🌐 [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

<p align="center">
<strong>You'll end up using Claude Code (The Best) anyway.</strong><br>
<em>The ultimate agent experience — lightest weight, curated features, maximum performance.</em>
</p>

<p align="center">
<sub>Web-guided setup. Multi-layer memory. Multi-agent shared knowledge. Free evolution.</sub>
</p>

---

### This project does one thing.

Get you from zero to a fully-equipped AI agent fleet — fast.

Clawd-Lobster is a **generator**. You run it once, it creates your personal **Hub** — a private repo that becomes your command center. Your Hub manages all your machines, workspaces, memory, and skills.

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
             │
             ▼  then 9 automated steps
  [1] Prerequisites   — Node, Python, Git, Claude Code
  [2] Authentication  — Claude + GitHub (OAuth clicks)
  [3] Create Hub      — copies template → private GitHub repo
  [4] Config          — writes ~/.clawd-lobster/config.json
  [5] Memory Server   — installs 24-tool MCP server
  [6] Claude Code     — configures CLAUDE.md + .mcp.json + skill registry
  [7] Workspaces      — clones repos, inits memory.db each
  [8] Scheduler       — registers sync + heartbeat tasks
  [9] Migration       — absorbs OpenClaw/Hermes/etc (if chosen)
```

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

### Why install a bunch of stuff you don't need?

Other frameworks rebuild the entire AI agent from scratch — 300K lines of code, custom agent loops, custom tool systems, custom everything. Then when Anthropic ships a better model, they scramble to rewrite their adapters.

**Clawd-Lobster doesn't compete with Claude Code. It completes it.**

We start with Claude Code — the most advanced coding agent in the world — and add exactly what's missing: persistent memory, multi-agent orchestration, and curated skills. Nothing more. Nothing less.

> **Every memory persists.** Every trajectory is recorded. Every workspace is shared.
>
> Your agents grow together. Your knowledge compounds. Your work is never lost.

> *Zero bloat. Zero rewrites. Pure Claude Code, amplified.*

### The fatal flaw of other agent frameworks

Other frameworks rebuild Claude from scratch — then call Claude's API to do the actual thinking. Think about what that means:

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
  Claw-Lobster just keeps the session alive and manages skills.
```

We don't call Claude's API. We don't manage OAuth tokens. We don't handle rate limits. We schedule **Claude Code itself** — a tool Anthropic built, ships, and maintains. When they improve Claude Code, we get faster. When they change their API, we don't care.

Other frameworks are building a **remote control for someone else's car.** We're sitting **in the car.**

### "But you still need autonomous agents for 24/7 tasks!"

Yes — and we have them. The difference is **how**.

Other frameworks run a custom daemon process 24/7 that calls Claude's API per-token. A simple Discord greeting bot at 480 calls/day = $144/month in API costs. They solve this by falling back to local models (Ollama 7B) for cheap tasks — which means maintaining **two inference stacks**.

We solve it differently:

| | Other frameworks | **Clawd-Lobster** |
|---|---|---|
| **24/7 engine** | Custom daemon + API | OS scheduler + `claude --resume` |
| **Cost model** | Per-token API ($$$) | Pro subscription ($20/mo flat) |
| **Cheap tasks** | Ollama fallback (separate stack) | Same Claude Code session |
| **Auth model** | OAuth/API key (fragile) | Human login once (robust) |
| **Maintenance** | Two engines, two stacks | One CLI tool, zero custom code |
| **Anthropic updates** | Rewrite adapters | Auto-upgrade |

**Economics don't require two inference engines.** A flat subscription means the 480th call costs the same as the 1st — $0 marginal. The entire "expensive API vs cheap local model" tradeoff **disappears** when you're on a subscription.

The real question isn't "remote control vs autopilot." It's: **why build either when you can schedule the car itself?**

---

## The Difference

| | Heavyweight frameworks | Raw Claude Code | **Clawd-Lobster** |
|---|---|---|---|
| **Agent engine** | Custom (self-maintained) | Anthropic | **Anthropic** |
| **Codebase** | 300K+ lines | N/A | **~2K lines** |
| **Opus 4.7 drops** | Rewrite adapters | Auto-upgrade | **Auto-upgrade** |
| **Skill management** | Custom plugin SDK | N/A | **Manifest + Web UI + CLI** |
| **Persistent memory** | Single-layer or none | None | **4-layer + salience** |
| **Multi-machine** | Complex or impossible | No | **Built-in (MDM-style)** |
| **Onboarding** | Half a day | Manual | **5 minutes** |
| **Performance** | Overhead from custom engine | Native | **Native** |

### The Core Idea

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

**A skill is just 3 config entries.** No SDK. No plugin API. No framework lock-in.

---

## Features

### 4-Layer Memory System

Most AI agents forget everything between sessions. Clawd-Lobster gives Claude Code persistent, searchable, weighted memory.

| Layer | What | Speed | Scope |
|-------|------|-------|-------|
| **L1.5** | CC auto-memory (native) | Instant | Current project |
| **L2** | SQLite + 24 MCP tools | ~1ms | Per workspace |
| **L3** | Markdown knowledge base | ~10ms | Shared via git |
| **L4** | Cloud DB (optional) | ~100ms | Cross-workspace |

**Salience engine** — Important memories float up, stale ones sink:
- Each access: +5% salience boost
- Manual reinforce: +20% boost (capped at 2.0x)
- 30 days untouched: -5%/day decay (floor at 0.01, never deleted)

**CJK-aware token estimation** — Accurate compaction timing for multilingual workloads.

### Multi-Agent Shared Knowledge

This isn't just one agent. It's a fleet — and they all share the same brain.

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

### Agents That Evolve

Your agents don't just execute — they learn. Built-in self-evolution via 3 dedicated MCP tools:

```
Task completed (complex, multi-step)
    │
    ▼ memory_learn_skill()
    │ Extracts the reusable pattern
    │ Saves to L2 (SQLite) + skills/learned/ (file)
    │
    ▼ Next similar task arrives
    │ memory_list_skills() finds the pattern
    │ Agent follows the proven approach
    │
    ▼ Better approach discovered?
      memory_improve_skill() updates it
      Effectiveness score increases (+10%)
```

- **Learned skills persist** — stored in both database and git-synced skill files
- **Effectiveness tracking** — each use +2%, each improvement +10%, proven skills score > 2.0x
- **Cross-agent sharing** — skills learned on Agent A are available to Agent B via git sync
- **Natural retirement** — skills unused for 90+ days are flagged as potentially stale
- **Knowledge compounds** — decisions in one workspace inform work in another, solved problems are never solved twice

### Smart Migration

Already using another setup? Claude Code reads your existing files and imports them intelligently:

```
Detected environments:
  ✓ claude-setup     → 11 workspaces, Oracle config, soul files
  ✓ Raw Claude Code  → CLAUDE.md, auto-memory, sessions
  ✓ OpenClaw         → SOUL.md, MEMORY.md, skills, approvals
  ✓ Hermes Agent     → skills, memory, profiles
```

No parser scripts. Claude Code **is** the parser — it reads any format, understands the semantics, and stores what matters.

### Simple Workspace Management

Create workspaces with one command. The scheduler auto-syncs all git repos under your workspace root:

```powershell
.\scripts\new-workspace.ps1 -name "my-api"
# Creates folder, memory.db, CLAUDE.md, GitHub repo — done.
```

```
~/Documents/Workspace/
├── my-api/          ← registered, synced every 30 min
├── data-pipeline/   ← registered, synced every 30 min
└── random-notes/    ← not a git repo, ignored by sync
```

### Always Alive — Heartbeat Session Manager

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

- **Terminal open** → session alive → agent has full context, running 24/7
- **Terminal closed** → heartbeat detects → revives automatically
- **All sessions** → visible via Claude Code Remote on any device
- **No custom daemon** — OS scheduler is the watchdog. Never crashes. Zero maintenance.

Other frameworks run a custom 24/7 daemon (their own inferior engine). We let the OS ensure Claude Code sessions stay alive. **The best engine, always on.**

### Scheduled Automation

OS-level scheduler (Windows Task Scheduler / cron / launchd) — runs even when Claude Code isn't active:

- **Heartbeat** — Ensure all workspace sessions stay alive (revive if dead)
- **Git sync** — Pull and push all repos every 30 minutes
- **Salience decay** — Daily memory importance adjustment
- **Client status** — Track each machine's sessions, last heartbeat, deployed workspaces

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

### Second machine (join your Hub)

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
.\install.ps1    # or ./install.sh
# Choose "Join Hub" → paste your Hub URL → done
```

### What the 9 steps do

| Step | Action | Time |
|------|--------|------|
| 1 | Check prerequisites (Node, Python, Git) | 5s |
| 2 | Authenticate Claude Code + GitHub (2 OAuth clicks) | 30s |
| 3 | **Create your Hub** (private repo) or clone existing | 10s |
| 4 | Write config | 5s |
| 5 | Install MCP Memory Server (21 tools) | 10s |
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

---

## Skill Management Platform

Every skill is a self-contained module with a `skill.json` manifest — like a Chrome extension. Manage them via **Web UI** or **CLI**.

### Web Dashboard

Open `webapp/index.html` — a dark-theme management console with:
- **Card grid** with ON/OFF toggles, status indicators, category filters, search
- **Inline config** — edit settings and credentials per skill
- **Health checks** — green/yellow/red status for every enabled skill

### CLI Manager

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

### Adding a New Skill

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

No SDK. No plugin API. The manifest **is** the contract.

---

## Project Structure

```
clawd-lobster/
├── skills/                          Skill modules (each with skill.json manifest)
│   ├── memory-server/               24-tool MCP memory with salience + evolution
│   │   ├── mcp_memory/              Python package (pip install -e .)
│   │   └── skill.json               Manifest
│   ├── connect-odoo/                Odoo ERP integration (XML-RPC + poller)
│   │   ├── connect_odoo/            MCP server + poller
│   │   └── skill.json               Manifest
│   ├── evolve/                      Self-evolution prompt pattern
│   │   └── skill.json               Manifest
│   ├── heartbeat/                   Session keep-alive (cron)
│   │   └── skill.json               Manifest
│   ├── migrate/                     Import from existing setups
│   │   └── skill.json               Manifest
│   └── learned/                     Auto-generated skills from experience
│
├── scripts/
│   ├── skill-manager.py             Skill Management CLI
│   ├── sync-all.ps1                 Windows: auto git sync + decay
│   ├── sync-all.sh                  Linux/macOS: auto git sync + decay
│   ├── heartbeat.ps1                Windows: session keep-alive
│   ├── heartbeat.sh                 Linux/macOS: session keep-alive
│   ├── new-workspace.ps1            Create workspace + GitHub repo
│   ├── init_db.py                   Initialize memory database
│   └── security-scan.py             5-tool security scanner
│
├── templates/                       Config templates (no secrets)
│   ├── global-CLAUDE.md
│   ├── workspace-CLAUDE.md
│   ├── mcp.json.template
│   └── settings.json.template
│
├── webapp/                          Skill Management Dashboard
│   └── index.html                   3-tab UI: Skills + Setup + Settings
│
├── knowledge/                       Shared knowledge base (git-synced)
├── soul/                            Agent personality (optional)
├── workspaces.json                  Workspace registry
├── install.ps1                      Windows installer (4-phase)
├── install.sh                       Linux/macOS installer (4-phase)
├── Dockerfile                       Docker build
├── docker-compose.yml               Docker Compose config
├── LICENSE                          MIT
└── README.md
```

---

## Philosophy

### 1. The best agent already exists. Use it.

Claude Code is backed by the world's largest AI safety lab. Millions of engineering hours went into its agent loop, streaming, permissions, and tool system. Rebuilding that from scratch isn't ambition — it's waste. **Stand on the shoulders of giants.**

### 2. Less is more. Way more.

Every line of framework code is a line you have to maintain. Clawd-Lobster is ~2K lines because Claude Code's native extension points (MCP, hooks, CLAUDE.md) are already the best plugin system anyone could design. **Three config entries = one skill. Zero SDK.**

### 3. An agent that forgets is an agent that fails.

Most AI agents start every session from zero. They repeat mistakes, re-learn context, and waste your time. Clawd-Lobster's 4-layer memory with salience tracking ensures **the important stuff rises, the noise fades, and nothing critical is ever lost.**

### 4. Your agents should follow you everywhere.

One computer? Fine. Three machines? They should all share the same brain. GitHub as control plane, git sync as protocol. **Add a machine in 2 minutes. Zero infrastructure.**

### 5. Always ride the latest wave.

When Anthropic ships Opus 4.7, 1M context, new tools — you get them instantly. No adapter rewrites. No version pinning. No waiting for community patches. **The best time to use Claude Code was yesterday. The second best time is now.**

### 6. Never build what you can schedule.

Other frameworks build custom daemons to run agents 24/7. We use `cron` + `claude --resume`. Other frameworks manage OAuth tokens to call Claude's API. We let the user type `claude login` once. **Every line of auth code you write is a line that can break when the provider changes. Every line you don't write is a line that can't.** The OS scheduler has been running reliably since the 1970s. Your custom daemon was written last Tuesday.

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
| Agent evolution | No | No | Self-improving skills | **Yes (24 MCP tools)** |
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
- [ ] Codex Bridge — delegate heavy tasks to OpenAI Codex in the background
- [ ] SearXNG — private self-hosted web search, no data leaves your network
- [ ] Docker Sandbox — isolated code execution for untrusted operations
- [ ] Browser Automation — Playwright-powered web interaction

**Platform**
- [x] Linux installer (bash) + macOS installer (v0.3.0)
- [x] Skill Management Dashboard — Web UI + CLI for skill lifecycle (v0.4.0)
- [x] Skill manifest system — `skill.json` with config, credentials, health checks (v0.4.0)
- [ ] Supabase L4 — one-click cloud database (no Oracle wallet needed)

**Evolution**
- [ ] Skill marketplace — community-contributed skills, one-click install
- [x] Auto-skill generation — agent learns from successful patterns (v0.3.0 evolve skill)
- [ ] Team mode — multi-user shared workspaces with role-based access
- [ ] Agent-to-agent delegation — agents assign tasks to each other

---

## FAQ

### "Isn't this just Claude Code with a wrapper?"

Yes. That's the point.

Claude Code is the most capable coding agent available — backed by millions of engineering hours from Anthropic. OpenClaw rebuilds the engine from scratch (300K lines). Hermes rebuilds it again (50K lines). We add what's missing (2K lines) and keep the best engine.

When Anthropic ships the next breakthrough, we get it instantly. They have to rewrite their adapters.

### "But other agents run 24/7 and keep learning"

So does ours. The scheduler syncs knowledge every 30 minutes. Memory evolves daily via salience decay. Learned skills propagate across all machines via git. **The agent doesn't need to be running for knowledge to grow.**

And the heartbeat ensures sessions stay alive: if a terminal closes, the OS scheduler detects it and revives the session with `claude --resume` — full context restored. No custom daemon needed. No inferior engine running 24/7. Just Claude Code, always on.

### "Other agents have heartbeat and time awareness"

Ours do too — but smarter. Instead of running a custom daemon process, we use the OS scheduler (Task Scheduler / launchd / cron) as the heartbeat. It checks every 30 minutes:

- Is each workspace session alive? If not, revive it.
- Git sync needed? Do it.
- Salience decay due? Run it.
- Client status? Updated and pushed.

The OS scheduler never crashes, never needs debugging, and never burns tokens when idle. When Claude Code ships native 24/7 mode (KAIROS — it's in the codebase), we get it for free. Zero code change.

### "Won't Anthropic block this?"

We don't do anything Anthropic prohibits. Let's be precise:

- **What we do:** Schedule `claude` CLI commands via OS cron/Task Scheduler. Resume existing sessions with `claude --resume`. Use MCP servers that Anthropic's own protocol defines.
- **What we don't do:** Programmatic OAuth login. API key automation. Token scraping. Auth bypass. Reverse engineering.

The user runs `claude login` once — a human, in a browser, with their Pro subscription. After that, the OS scheduler keeps sessions alive using flags that Anthropic themselves ship in their CLI (`--resume`, `-p`, `--allowedTools`). This is no different from scheduling `git pull` via cron. **We automate a CLI tool. We don't impersonate a user.**

Other frameworks call Claude's API directly — they need API keys, manage OAuth refresh tokens, handle rate limits, and pray that pricing doesn't change. Every API change is a breaking change for them. For us, it's transparent — Claude Code handles its own auth.

### "What about API costs for heavy workloads?"

The "expensive API" argument assumes per-token pricing. With a Pro subscription ($20/month), **there is no per-token cost.** Your 1st task and your 480th task cost the same: $0 marginal.

This eliminates the entire "expensive model for thinking, cheap model for grunt work" architecture that other frameworks require. You don't need Ollama 7B running locally for cheap tasks. You don't need two inference stacks. You don't need a model router that decides which brain to use.

One subscription. One engine. One brain. Unlimited tasks.

When rate limits hit (they will), Clawd-Lobster's skill-manager gracefully queues work. No token budget panic. No surprise bills. **Predictable cost is a feature.**

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
