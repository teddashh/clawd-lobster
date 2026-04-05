[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/github/license/teddashh/clawd-lobster)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Runtime](https://img.shields.io/badge/footprint-25MB_RAM-orange)

<p align="center">
<strong>From idea to working code. One conversation.</strong><br>
<em>Spec Squad turns your description into a reviewed, tested codebase — powered by Claude Agent SDK.</em>
</p>

<p align="center">
<sub>Web dashboard + CLI. Multi-agent development. Persistent memory. Multi-machine sync.</sub>
</p>

---

## What is Clawd-Lobster?

Claude Code is the brain. Clawd-Lobster is the nervous system.

Claude Code is the most capable coding agent available, but it forgets everything between sessions, runs on one machine, and has no skill management. Clawd-Lobster adds exactly what's missing: a **Spec Squad** that plans, reviews, builds, and tests your code through adversarial multi-agent collaboration — plus persistent memory, multi-machine orchestration, curated skills, and self-evolution.

**Clawd-Lobster is a generator.** You run it once, it creates your personal **Hub** — a private GitHub repo that becomes your command center. Your Hub manages all your machines, workspaces, memory, and skills.

```
  clawd-lobster (this repo -- the generator)
       |
       |  pip install -e . && clawd-lobster setup
       |
       v
  clawd-yourname (YOUR private Hub -- generated for you)
       |
       |  this is what you actually use day-to-day
       |
       +-- Machine A -- Claude Code + skills + memory
       +-- Machine B -- Claude Code + skills + memory
       +-- Machine C -- Claude Code + skills + memory
            |
            All connected. All sharing knowledge.
            All always alive via heartbeat.
```

GitHub is the control plane. Git is the protocol. Every piece of state — skills, knowledge, workspace registry, heartbeat status — lives in git and syncs automatically.

**Runtime footprint: 25 MB RAM, 672 KB disk.** One Python process (MCP Memory Server) plus SQLite. Everything else runs-and-exits via OS scheduler or lives in the browser. Zero polling, zero daemon, zero bloat.

---

## Quick Start

Three ways to get started, depending on your style.

### Web UI (recommended for beginners)

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster serve
# Browser opens at http://localhost:3333
# Onboarding wizard walks you through everything
```

### Terminal (for experts)

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster setup
# 4-step interactive wizard: prerequisites -> persona -> workspace root -> first workspace
```

### Classic (install scripts)

**Windows**
```powershell
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
.\install.ps1
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

The installer checks prerequisites, authenticates Claude Code + GitHub, creates your Hub, installs the MCP Memory Server (32 tools), configures workspaces, and registers the scheduler + heartbeat. Total credentials: 2 OAuth clicks. No API keys required.

| Platform | Sync | Heartbeat |
|----------|------|-----------|
| Windows | Task Scheduler (30 min) | Task Scheduler (30 min) |
| macOS | launchd | launchd |
| Linux | cron | cron |
| Docker | Container lifecycle | Container lifecycle |

---

## The Web Dashboard

Start with `clawd-lobster serve` (default port 3333). The dashboard provides three main views:

### /onboarding — Setup Wizard

First-time visitors land here automatically. The wizard checks prerequisites (Python, Claude CLI, Git, pip), lets you pick a persona (Guided / Expert / Tech), set your workspace root, and create your first workspace — all in the browser.

### /workspaces — Workspace Manager

Lists all registered workspaces with real-time status. Each workspace card shows its path, memory database size, git sync status, and Spec Squad phase. Create new workspaces directly from the dashboard or toggle them on/off for syncing.

### /squad — Spec Squad

The multi-agent development interface. Start a discovery conversation, watch the Architect write specs, see the Reviewer challenge them, follow the Coder as it builds, and track the Tester's verification — all with live progress updates via SSE.

---

## Spec Squad — Multi-Agent Development

Spec Squad is the core v1.0 feature. Four specialized agents collaborate to turn your idea into reviewed, tested code — using the Claude Agent SDK.

### The Pipeline

```
You describe your project
  | clawd-lobster squad start (terminal)
  | or /squad page (web)
  v
Discovery Interview
  | Senior consultant asks 3-6 smart questions (3W1H: Why, What, Who, How)
  | When enough context is gathered: DISCOVERY_COMPLETE
  v
Architect
  | Writes complete OpenSpec: project.md -> proposal.md -> design.md
  | -> specs/ (SHALL/MUST + Gherkin) -> tasks.md (phased, 5-30 min each)
  v
Reviewer (adversarial)
  | Tears apart the spec. Finds gaps, ambiguities, weak decisions.
  | Verdict: REVISE (with issues) or APPROVED (with confidence score)
  | Up to 5 review rounds -- Architect must fix every issue
  v
Coder
  | Executes the approved spec task by task, phase by phase
  | Commits after each phase. Marks tasks done in tasks.md
  v
Tester
  | Verifies every SHALL/MUST requirement against the code
  | Runs Gherkin scenarios. Verdict: PASSED or ISSUES (with pass rate)
  v
Done -- reviewed, tested codebase ready
```

### How the adversarial review works

The Reviewer is instructed to be "ruthless but fair." It reads every file in `openspec/` and challenges the architecture, requirements, and task breakdown. If it finds issues, the Architect must revise. This loop runs up to 5 rounds until the Reviewer gives an APPROVED verdict with a confidence score. The result is a spec that has been stress-tested before a single line of code is written.

### Web mode vs terminal mode

| | Web (`/squad`) | Terminal (`clawd-lobster squad start`) |
|---|---|---|
| Discovery | Chat interface in browser | stdin/stdout |
| Progress | Live SSE events, visual phases | Phase labels printed to terminal |
| Build approval | Prompted in browser | `Build now? (y/n)` |
| State | Persisted in `.spec-squad.json` | Same file |
| Underlying engine | Same `squad.py` async core | Same `squad.py` async core |

Both modes use the same pipeline, same Agent SDK calls, same state file. Pick whichever fits your workflow.

---

## Skills

9 skill modules, each with a `skill.json` manifest. 32 MCP tools total.

### Core Skills (locked)

| Skill | Type | What it does |
|---|---|---|
| **Memory Server** | mcp-server | 26-tool MCP memory with SQLite, salience engine, CJK-aware compaction |
| **Heartbeat** | cron | Session keep-alive via OS scheduler — auto-revives dead sessions |
| **Evolve** | prompt-pattern | Pattern extraction, improvement proposals, salience decay |
| **Absorb** | prompt-pattern | Knowledge ingestion from folders, GitHub repos, URLs |
| **Spec** | prompt-pattern | Guided planning with OpenSpec methodology + blitz execution |

### Optional Skills

| Skill | Type | What it does | Default |
|---|---|---|---|
| **Migrate** | prompt-pattern | Import from existing AI setups (detects format automatically) | Enabled |
| **Connect-Odoo** | mcp-server | Odoo ERP integration — 6 MCP tools via XML-RPC + poller | Disabled |
| **Codex Bridge** | prompt-pattern | Delegate work to OpenAI Codex with worker + critic roles | Disabled |
| **NotebookLM Bridge** | prompt-pattern | Free RAG + content engine via Google NotebookLM | Disabled |

### Skill Management

Every skill is a self-contained module with a `skill.json` manifest. Manage them via **Web UI** or **CLI**:

```bash
clawd-lobster serve                                      # Web dashboard with toggles
python scripts/skill-manager.py list                     # Table of all skills
python scripts/skill-manager.py enable connect-odoo      # Enable a skill
python scripts/skill-manager.py disable connect-odoo     # Disable a skill
python scripts/skill-manager.py health                   # Run all health checks
python scripts/skill-manager.py reconcile                # Regenerate .mcp.json + settings.json
```

### Adding Your Own Skill

Create `skills/my-skill/skill.json` with the manifest, implement the skill (MCP server, script, or SKILL.md), run `skill-manager.py reconcile`. A skill is just 3 config entries — no SDK, no plugin API, no framework lock-in.

---

## Architecture

### 3-Layer Design

```
+----------------------------------------------+
|          Skills Layer (Clawd-Lobster)         |
|                                               |
|  Memory System    Workspace Manager           |
|  Spec Squad       Scheduler                   |
|  Self-Evolution   (your custom skills)        |
|                                               |
|  Installed via: .mcp.json + settings.json     |
|                 + CLAUDE.md                    |
+----------------------+------------------------+
                       |
+----------------------v------------------------+
|            Claude Code (The Brain)             |
|                                                |
|  Agent Loop - Streaming - Tools - Permissions  |
|  Maintained by Anthropic. Auto-upgrades.       |
+------------------------------------------------+
```

### 4-Layer Memory

| Layer | What | Speed | Scope |
|-------|------|-------|-------|
| **L1.5** | Claude Code auto-memory (native) | Instant | Current project |
| **L2** | SQLite + 26 MCP tools | ~1ms | Per workspace |
| **L3** | Markdown knowledge base | ~10ms | Shared via git |
| **L4** | Cloud DB (optional) | ~100ms | Cross-workspace |

The salience engine keeps important memories accessible: each access boosts salience by 5%, manual reinforcement by 20% (capped at 2.0x), and untouched items decay 5%/day after 30 days (floor at 0.01 — never deleted).

### What's Actually Running?

| Layer | What | Lines | RAM | When |
|-------|------|-------|-----|------|
| **Runtime** | MCP Memory Server (26 tools + SQLite) | ~1,400 | ~25 MB | Always on |
| **Runtime** | Odoo Connector (if enabled) | ~280 | ~22 MB | When enabled |
| **Runtime** | Web Dashboard (stdlib HTTP) | ~800 | ~15 MB | When serving |
| **Cron** | evolve-tick (proposal generator) | ~465 | ~20 MB peak | Every 2h, then exits |
| **Cron** | heartbeat + sync | ~300 | ~5 MB peak | Every 30 min, then exits |
| **Setup** | CLI + onboarding + squad orchestrator | ~1,200 | 0 | On demand |
| **Config** | skill.json manifests, templates | ~900 | 0 | Read at startup |

**Resident footprint: one Python process (~25 MB) + SQLite.** The web dashboard uses stdlib `http.server` — no Flask, no FastAPI, no external dependencies.

### Philosophy

1. **Stand on the shoulders of giants.** Claude Code has millions of engineering hours behind it. We add what's missing (~3K lines) and keep the best engine.

2. **Less code, less breakage.** Three config entries = one skill. Zero SDK. The OS scheduler has been reliable since the 1970s — we use `cron` + `claude --resume` instead of custom daemons.

3. **When the giant grows, you grow.** When Anthropic ships native memory, 24/7 agents, or multi-agent coordination — we don't rewrite, we retire code. **Our codebase shrinks over time. Theirs grows.**

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full file tree and internals.

---

## CLI Reference

| Command | What |
|---|---|
| `clawd-lobster serve` | Start the web dashboard on localhost:3333 |
| `clawd-lobster serve --port 8080` | Use a custom port |
| `clawd-lobster serve --daemon` | Run the server in background |
| `clawd-lobster setup` | Run the terminal onboarding wizard |
| `clawd-lobster workspace create <name>` | Create a new workspace |
| `clawd-lobster workspace create <name> --repo` | Create workspace + private GitHub repo |
| `clawd-lobster workspace create <name> --dry-run` | Preview without making changes |
| `clawd-lobster squad start` | Launch Spec Squad in terminal mode |
| `clawd-lobster squad start --workspace <path>` | Specify target workspace |
| `clawd-lobster status` | Show system health, workspaces, versions |
| `clawd-lobster --version` | Print version |

---

## Multi-Machine Setup

### The Hub Pattern

Your Hub is a private GitHub repo that acts as your command center. Every machine clones the Hub and syncs automatically.

```
        +------- GitHub (Control Plane) -------+
        |  skills, knowledge, workspace registry|
        +----------+------------+--------------+
                   |            |
     +-------------v--+  +-----v-------------+
     |  Agent A        |  |  Agent B           |
     |  (office)       |  |  (cloud VM)        |
     |  Claude Code    |  |  Claude Code       |
     |  + local L2 ----+--+---> shared L3/L4   |
     +----------------+  +-------------------+
                   |            |
              +----v------------v----+
              |  Agent C (laptop)    |
              |  joins in 2 minutes  |
              +---------------------+
```

### Adding another machine

```bash
git clone https://github.com/you/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster setup
# Choose "Join existing Hub" -> paste your Hub URL -> name this machine -> done
```

The new machine inherits all accumulated knowledge instantly. L2 (SQLite) stays local per workspace, L3 (markdown) syncs via git, L4 (optional cloud DB) unifies everything.

### Always Alive — Heartbeat

Your agents never die. The OS scheduler checks every 30 minutes: is each workspace session alive? If not, it revives with `claude --resume` — full context restored. No custom daemon. Just Claude Code, always on.

---

## Workspaces

A workspace is a project directory with memory, skills, and spec support.

### Workspace Structure

```
my-project/
+-- CLAUDE.md              <- project-specific instructions
+-- .claude-memory/
|   +-- memory.db          <- L2 memory (SQLite)
+-- knowledge/             <- L3 knowledge (git-synced)
+-- skills/learned/        <- auto-generated skills
+-- openspec/              <- spec artifacts (if using /spec or squad)
|   +-- project.md
|   +-- changes/
|   +-- specs/
+-- .spec-squad.json       <- squad state (if using squad)
+-- .blitz-active          <- present during blitz execution
```

### Scheduled Automation

OS-level scheduler (Windows Task Scheduler / cron / launchd) runs even when Claude Code is not active:

- **Heartbeat** — Ensure all workspace sessions stay alive (revive if dead)
- **Git sync** — Pull and push all repos every 30 minutes
- **Salience decay** — Daily memory importance adjustment
- **evolve-tick** — Pattern extraction + improvement proposals every 2 hours

---

## Memory System

### 26 MCP Tools

| Category | Tools |
|---|---|
| **Write** | `memory_store`, `memory_record_decision`, `memory_record_resolved`, `memory_record_question`, `memory_record_knowledge` |
| **Read** | `memory_list`, `memory_get`, `memory_get_summary` |
| **Delete** | `memory_delete` |
| **Search** | `memory_search` (vector + text, salience-weighted, all tables) |
| **Salience** | `memory_reinforce` |
| **Evolve** | `memory_learn_skill`, `memory_list_skills`, `memory_improve_skill` |
| **TODO** | `memory_todo_add`, `memory_todo_list`, `memory_todo_update`, `memory_todo_search` |
| **Audit Trail** | `memory_log_action`, `memory_audit_search`, `memory_audit_stats`, `memory_daily_report`, `memory_activity_log` |
| **Admin** | `memory_compact`, `memory_status`, `memory_oracle_summary` |

Memory is not a passive store — it actively shapes how your agent works. Every trajectory is recorded. Every workspace shares knowledge via git. Your agents grow together.

---

## Evolution System

After v1 is built, your agent keeps getting better — automatically.

### The Loop

```
/absorb (input)
  +-- Scan folder -> extract knowledge, decisions, TODOs
  +-- Read GitHub repo -> learn patterns + skills
  +-- Fetch URL -> store insights
       |
evolve-tick (every 2 hours)
  +-- Extract patterns from completed work
  +-- Generate improvement proposals (git-synced markdown files)
  +-- Apply salience decay to stale knowledge
  +-- Sync knowledge across machines
       |
Review (you decide)
  +-- Review proposals in openspec/proposals/
  +-- Approve -> becomes TODO for next blitz
  +-- Reject -> archived with learning captured
```

Evolve generates **proposals**, not direct changes. All proposals stay in `openspec/proposals/` for human review. Learned skills persist across sessions and machines via git sync.

---

## Requirements

- **Python** 3.10+ and **Git** 2.x+
- **Claude Code** CLI ([install guide](https://docs.anthropic.com/en/docs/claude-code/getting-started))
- A **GitHub** account (for your private Hub repo)
- **Node.js** 18+ (optional — needed if using MCP servers that require it)

---

## Installation (detailed)

### 1. Clone and install

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
```

This registers the `clawd-lobster` CLI command globally.

### 2. Run setup

Choose one:

```bash
clawd-lobster serve    # Web wizard at http://localhost:3333
clawd-lobster setup    # Terminal wizard
./install.ps1          # Windows classic installer
./install.sh           # macOS/Linux classic installer
```

### 3. Verify

```bash
clawd-lobster status
# Shows: Python version, Claude CLI, Git, workspaces, server status
```

### 4. Start building

```bash
clawd-lobster squad start                    # Describe your project -> spec -> build
clawd-lobster workspace create my-app --repo # Or create a workspace manually
```

---

## FAQ

### "Isn't this just Claude Code with a wrapper?"

Yes. That is the point.

Claude Code is the most capable coding agent available — backed by millions of engineering hours from Anthropic. Other frameworks rebuild the engine from scratch (50K-300K lines). We add what's missing (~3K lines) and keep the best engine.

When Anthropic ships the next breakthrough, we get it instantly. They have to rewrite their adapters.

### "How is Spec Squad different from just asking Claude to code something?"

Spec Squad adds **adversarial review** before coding starts. The Architect writes a complete spec, then the Reviewer tears it apart — finding gaps, ambiguities, and weak decisions. Up to 5 rounds of revision happen before the Coder touches anything. This means the code is built from a stress-tested blueprint, not from a casual prompt.

### "But other agents run 24/7 and keep learning"

So does ours. The scheduler syncs knowledge every 30 minutes. Memory evolves daily via salience decay. Learned skills propagate across all machines via git. The heartbeat ensures sessions stay alive: if a terminal closes, the OS scheduler revives it with `claude --resume` — full context restored.

### "Claude Code already has built-in skills and MCP. Why do I need more?"

Claude Code's built-in skills are closed — you can't add, modify, or share them. MCP gives you a protocol, but no lifecycle management. Installing a skill means editing 3 JSON files manually. Second machine? Redo everything.

**MCP is the protocol. We are the package manager.** What we add: `skill.json` manifests, one-command enable/disable, centralized credentials, health checks, web dashboard, and cross-machine registry sync via git.

### "Won't Anthropic block this?"

We schedule `claude` CLI commands via OS cron — the same way you'd schedule `git pull`. We use `claude --resume`, `--allowedTools`, and MCP servers — all flags Anthropic ships in their own CLI. No API key automation. No OAuth token scraping. No reverse engineering.

### "What about costs?"

With a Pro subscription ($20/month), there is no per-token cost. One subscription. One engine. Predictable cost is a feature.

---

## Comparison

| | Claude Code (raw) | Heavyweight Frameworks | **Clawd-Lobster** |
|---|---|---|---|
| Agent engine | Anthropic | Custom (50K-300K LOC) | **Anthropic (native)** |
| Multi-agent dev | No | Some | **Yes (Spec Squad: 4 agents)** |
| Adversarial review | No | No | **Yes (up to 5 rounds)** |
| Persistent memory | None | Varies | **4-layer + salience** |
| Multi-machine | No | No | **Yes (Hub + git sync)** |
| Always alive | No | Custom daemon | **OS heartbeat + auto-revive** |
| Skill management | N/A | CLI/SDK | **Web UI + CLI + manifest** |
| Self-evolution | No | Varies | **Yes (proposals + learned skills)** |
| Onboarding | Manual | Complex | **Web wizard or terminal, 5 languages** |
| Web dashboard | No | Varies | **Yes (localhost:3333)** |
| Codebase | 0 | 50K-300K LOC | **~3K LOC** |
| Cost model | Subscription | Per-token API | **Subscription (flat)** |
| Anthropic upgrade | Transparent | Breaking | **Transparent** |

---

## Roadmap

**Done in v1.0**
- [x] Unified CLI entry point (`clawd-lobster serve/setup/squad/workspace/status`)
- [x] Web Dashboard with onboarding wizard, workspace manager, Spec Squad UI
- [x] Spec Squad — multi-agent development via Claude Agent SDK
- [x] Three user personas (Guided / Expert / Tech)
- [x] 9 skills, 32 MCP tools, `skill.json` manifest system
- [x] 4-layer memory with salience engine
- [x] Multi-machine Hub pattern with git sync
- [x] Heartbeat auto-revive via OS scheduler
- [x] Evolution loop with git-synced proposals
- [x] Docker support

**Next**
- [ ] Supabase L4 — one-click cloud database (no Oracle wallet needed)
- [ ] SearXNG — private self-hosted web search
- [ ] Docker Sandbox — isolated code execution for untrusted operations
- [ ] Skill marketplace — community-contributed skills, one-click install
- [ ] Team mode — multi-user shared workspaces with role-based access
- [ ] Agent-to-agent delegation — agents assign tasks to each other

---

## Project Structure

```
clawd-lobster/
+-- clawd_lobster/       CLI + web server + squad orchestrator + onboarding
+-- skills/              9 skill modules (each with skill.json manifest)
+-- scripts/             Heartbeat, sync, evolve-tick, skill-manager, etc.
+-- templates/           Config templates (no secrets)
+-- knowledge/           Shared knowledge base (git-synced)
+-- install.ps1/sh       Classic installers (Windows / macOS / Linux)
+-- pyproject.toml       Package definition (pip install -e .)
+-- Dockerfile           Docker support
+-- docker-compose.yml   Docker Compose config
```

---

## Contributing

Contributions welcome! The easiest ways to contribute:

1. **Add a skill** — create a folder in `skills/` with a `skill.json` manifest
2. **Improve templates** — better defaults in `templates/`
3. **Platform support** — help with Linux/macOS testing
4. **Report bugs** — open an issue

---

## License

MIT — use it however you want.

---

<p align="center">
<sub>Not affiliated with Anthropic. Built on top of <a href="https://claude.ai/code">Claude Code</a>.</sub>
</p>
