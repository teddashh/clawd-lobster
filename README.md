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

Get you from zero to a fully-equipped Claude Code agent — fast — through a web interface.

**Step 1.** Web wizard walks you through installing Claude Code and authenticating in minutes.

**Step 2.** Web wizard sets up your multi-layer memory system and essential tools — click by click, green light by green light.

**Step 3.** A skills marketplace where you install what you need. Nothing you don't.

**Step 4.** Your agents evolve freely. Every memory persists. Every action is tracked. Every insight is shared.

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

### Scheduled Automation

OS-level scheduler (Windows Task Scheduler / cron / launchd) — runs even when Claude Code isn't active:

- **Git sync** — Pull and push all repos every 30 minutes
- **Salience decay** — Daily memory importance adjustment

---

## Quick Start

### Option A: Web Setup Wizard

Open `webapp/index.html` in your browser and follow the 6-step guided wizard.

### Option B: Command Line

**Windows (PowerShell)**
```powershell
git clone https://github.com/YOUR_USERNAME/clawd-lobster
cd clawd-lobster
.\install.ps1
```

**macOS / Linux (Bash)**
```bash
git clone https://github.com/YOUR_USERNAME/clawd-lobster
cd clawd-lobster
chmod +x install.sh && ./install.sh
```

**Docker**
```bash
git clone https://github.com/YOUR_USERNAME/clawd-lobster
cd clawd-lobster
docker compose up -d
docker compose exec clawd bash
# Then inside container: claude auth login
```

### What the installer does

| Step | Action | Time |
|------|--------|------|
| 1 | Check prerequisites (Node, Python, Git) | 5s |
| 2 | Authenticate Claude Code + GitHub (OAuth) | 30s |
| 3 | Install MCP Memory Server (21 tools) | 10s |
| 4 | Configure Claude Code (.mcp.json, settings.json, CLAUDE.md) | 5s |
| 5 | Register scheduled tasks (OS-native) | 5s |
| 6 | Done | --- |

| Platform | Scheduler | Method |
|----------|-----------|--------|
| Windows | Task Scheduler | `install.ps1` auto-registers |
| macOS | launchd | `install.sh` creates LaunchAgent |
| Linux | cron | `install.sh` adds crontab entry |
| Docker | Container restart | `docker compose` handles lifecycle |

**Total credentials needed: 2 OAuth clicks.** No API keys to paste (unless you want Oracle L4).

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
| Persistent memory | None | Hybrid search | FTS5 + LLM | **4-layer + salience** |
| Multi-agent shared memory | No | No | No | **Yes** |
| Agent evolution | No | No | Self-improving skills | **Yes (memory + skills)** |
| Multi-machine | No | No | No | **Yes (MDM-style)** |
| Onboarding | Manual | Complex | Moderate | **Web wizard, 5 min** |
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
