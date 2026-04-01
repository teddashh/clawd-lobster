🌐 [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

<p align="center">
<strong>You'll end up using the best anyway.</strong><br>
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
  [5] Memory Server   — installs 21-tool MCP server
  [6] Claude Code     — configures CLAUDE.md + .mcp.json
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

---

## The Difference

| | Heavyweight frameworks | Raw Claude Code | **Clawd-Lobster** |
|---|---|---|---|
| **Agent engine** | Custom (self-maintained) | Anthropic | **Anthropic** |
| **Codebase** | 300K+ lines | N/A | **~2K lines** |
| **Opus 4.7 drops** | Rewrite adapters | Auto-upgrade | **Auto-upgrade** |
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
| **L2** | SQLite + 21 MCP tools | ~1ms | Per workspace |
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

## Adding a Skill

A skill = 3 config entries. That's it.

```jsonc
// 1. .mcp.json — register the MCP server
{ "mcpServers": { "my-skill": { "command": "python", "args": ["-m", "my_skill"] } } }

// 2. settings.json — auto-allow read tools
{ "permissions": { "allow": ["mcp__my-skill__my_tool"] } }
```

```markdown
<!-- 3. CLAUDE.md — teach the agent when to use it -->
## My Skill
Use my_tool when the user asks about X. Prefer it over Y for Z tasks.
```

No SDK to learn. No plugin interface. No build step. Just config.

---

## Project Structure

```
clawd-lobster/
├── skills/
│   ├── memory-server/        21-tool MCP memory with salience + evolution
│   │   └── mcp_memory/       Python package (pip install -e .)
│   ├── evolve/               Self-evolution skill specification
│   ├── learned/              Auto-generated skills from experience
│   └── migrate/              Import from existing setups
│
├── scripts/
│   ├── sync-all.ps1          Windows: auto git sync + decay
│   ├── sync-all.sh           Linux/macOS: auto git sync + decay
│   ├── new-workspace.ps1     Create workspace + GitHub repo
│   └── init_db.py            Initialize memory database
│
├── templates/                Config templates (no secrets)
│   ├── global-CLAUDE.md
│   ├── workspace-CLAUDE.md
│   ├── mcp.json.template
│   └── settings.json.template
│
├── webapp/                   Web-based setup wizard
│   └── index.html            6-step dark-theme onboarding
│
├── knowledge/                Shared knowledge base (git-synced)
├── soul/                     Agent personality (optional)
├── workspaces.json           Workspace registry
├── install.ps1               Windows installer
├── install.sh                Linux/macOS installer
├── Dockerfile                Docker build
├── docker-compose.yml        Docker Compose config
├── LICENSE                   MIT
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

---

## Comparison

| | Claude Code (raw) | OpenClaw | Hermes Agent | **Clawd-Lobster** |
|---|---|---|---|---|
| Agent engine | Anthropic | Custom (Pi Agent) | Custom (Python) | **Anthropic (native)** |
| Always alive | No | Custom daemon | Custom daemon | **OS heartbeat + auto-revive** |
| Persistent memory | None | Hybrid search | FTS5 + LLM | **4-layer + salience** |
| Multi-agent shared memory | No | No | No | **Yes (git-synced)** |
| Agent evolution | No | No | Self-improving skills | **Yes (21 MCP tools)** |
| Multi-machine | No | No | No | **Yes (MDM-style)** |
| Session management | Manual | Gateway process | Manual | **Auto-revive all sessions** |
| Onboarding | Manual | Complex | Moderate | **Web wizard, 5 languages** |
| Auto-upgrades | Yes | No | No | **Yes** |
| Codebase size | N/A | ~300K LOC | ~50K LOC | **~2K LOC** |
| Audit trail | No | Security audit | No | **Full (every action)** |
| Skill install | — | Plugin SDK | 3-file change | **3 config entries** |

---

## Roadmap

**Skills**
- [ ] Codex Bridge — delegate heavy tasks to OpenAI Codex in the background
- [ ] SearXNG — private self-hosted web search, no data leaves your network
- [ ] Docker Sandbox — isolated code execution for untrusted operations
- [ ] Browser Automation — Playwright-powered web interaction

**Platform**
- [ ] Linux installer (bash) + macOS installer (zsh/launchd)
- [ ] Supabase L4 — one-click cloud database (no Oracle wallet needed)
- [ ] Dashboard — real-time view of all agents, memories, and sync status

**Evolution**
- [ ] Skill marketplace — community-contributed skills, one-click install
- [ ] Auto-skill generation — agent learns from successful patterns, creates reusable skills
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
