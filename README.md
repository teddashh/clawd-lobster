[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/github/license/teddashh/clawd-lobster)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Runtime](https://img.shields.io/badge/RAM-25MB-orange)

<p align="center">
<strong>你終究要用 Claude Code 的 — 為什麼不一開始就選最好的體驗？</strong><br>
<strong>You'll end up using Claude Code anyway — why not start with the best experience?</strong>
</p>

---

## The Problem

You've seen the AI agent frameworks. Maybe you've tried a few. Here's what actually happens:

**Problem 1: Claude Code is powerful, but you babysit it.**
Every session starts from zero. It forgets what it learned yesterday. You copy-paste context, re-explain architecture, re-describe conventions. You're the memory. You're the manager. You're the bottleneck.

**Problem 2: AI Agent frameworks are impressive demos, terrible experiences.**
300,000 lines of code. Custom adapters. Config files longer than your actual project. Breaks every time the underlying model updates. You spend more time maintaining the framework than building your product.

**Problem 3: The gray zone.**
Self-hosted agent loops that bypass safety. API calls billed per token with no ceiling. Frankenstein stacks where you're not sure if you're using the tool or the tool is using you.

## The Answer

Clawd-Lobster doesn't replace Claude Code. It **makes Claude Code remember, plan, review, build, and evolve** — using nothing but official Anthropic tools.

- **100% Claude Code CLI + Agent SDK.** No wrappers, no custom agent loops, no gray area. Runs on your existing Claude subscription. No extra API costs.
- **~9,000 lines of code.** Not 300,000. Still fits in your head. When Claude Code updates, you get the new features for free. Nothing to rewrite, nothing breaks.
- **5 minutes to start.** Open browser. Click twice. Done. No API keys, no Docker, no PhD in YAML.

```
  You describe what you want
       |
       v
  Claude asks smart questions (Discovery)
       |
       v
  +-------------------------------------+
  |         SPEC SQUAD                   |
  |                                      |
  |  [A] Architect    writes the spec    |
  |  [R] Reviewer     challenges it      |
  |  [C] Coder        builds it          |
  |  [T] Tester       verifies it        |
  |                                      |
  |  Each is a separate Claude session.  |
  |  The Reviewer has never seen the     |
  |  Architect's prompt.                 |
  |  That's why it catches real bugs.    |
  +-------------------------------------+
       |
       v
  Reviewed, tested, working code.
```

---

## Quick Start

### For Everyone (Web UI)

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster serve
```

Browser opens. Setup wizard guides you through everything.

### For Terminal People

```bash
clawd-lobster setup        # terminal onboarding
clawd-lobster squad start  # run Spec Squad in terminal
```

### Classic Install (power users)

```powershell
# Windows
.\install.ps1

# macOS / Linux
chmod +x install.sh && ./install.sh
```

---

## What You Get

### 1. Spec Squad — Your AI Development Team

You describe what you want. Four Claude sessions do the rest.

The **Architect** writes a complete spec with testable requirements. The **Reviewer** — a completely separate Claude session that has never seen the Architect's instructions — tears it apart. They loop until the Reviewer approves. Then the **Coder** builds exactly what the spec says. The **Tester** verifies every requirement.

This isn't a gimmick. In testing, the Reviewer found 11 real bugs in the first spec — issues that self-validation checklists would never catch. Return type conflicts, API inconsistencies, impossible Gherkin scenarios, library incompatibilities.

**Why it works:** Each agent runs in isolated context. The Reviewer can't be influenced by the Architect's reasoning. The Tester doesn't know what shortcuts the Coder took. Independent brains find independent problems.

Two interfaces, same engine:
- **Web:** Chat with Claude in the browser, then watch agents work on a live dashboard
- **Terminal:** Claude asks questions in your terminal, progress prints as agents run

### 2. A Brain That Doesn't Forget

Four layers of memory, from instant to global:

| Layer | Speed | What |
|-------|-------|------|
| L1.5 | Instant | Claude Code's native auto-memory |
| L2 | ~1ms | SQLite + MCP — per-workspace, salience-weighted |
| L3 | ~10ms | Markdown + Git — synced across machines |
| L4 | ~100ms | Cloud DB (optional) — cross-workspace search |

Important ideas float up. Noise sinks away. Skills that work get reinforced. Stale knowledge decays. You don't manage any of this — it happens automatically.

### 3. Always Alive

Close your laptop. Clawd-Lobster keeps working.

The heartbeat uses your OS scheduler (Task Scheduler / cron / launchd) — not a custom daemon, not a polling loop, not a token-burning process. If a session dies, it gets revived with full context. No babysitting.

### 4. All Your Machines, One Brain

GitHub is the control plane. Git is the protocol.

Machine A learns a pattern. It syncs to your private Hub. Machine B inherits it instantly. New machine? `install.ps1`, "Join Hub", paste URL, 2 minutes, fully operational.

### 5. Self-Evolution

After completing complex work, the system extracts reusable patterns and stores them as learned skills. Next time a similar task comes up, it remembers how it solved it last time.

Skills have effectiveness scores. Proven patterns get reinforced. Stale skills decay. The system gets smarter the more you use it — not because of magic, but because it writes down what worked.

---

## The Dashboard

`clawd-lobster serve` opens a persistent web dashboard at `localhost:3333`.

**Onboarding** — First-time wizard checks prerequisites, guides setup, creates your first workspace.

**Workspaces** — All your projects in one view. Status, spec progress, memory size, last activity.

**Spec Squad** — Chat with Claude to discover your requirements. Watch four agents work in real-time on a live dashboard with phase timeline and turn history.

---

## Skills

10 curated skills. Each does one thing well. Click the name for full documentation.

### [memory-server](skills/memory-server/README.md) — The Foundation
26 MCP tools for persistent memory across sessions. 4-layer architecture from instant local cache to cloud sync. Salience engine that surfaces important knowledge and lets noise decay. CJK-aware token estimation. This is the skill that makes Claude Code stop forgetting.

### [spec](skills/spec/README.md) — From Idea to Code
Guided workspace creation, OpenSpec document generation (3W1H), and Spec Squad multi-agent pipeline. Discovery interview extracts your requirements. Architect writes testable specs with Gherkin scenarios. Reviewer tears them apart. Coder builds to contract. Tester verifies every requirement. Terminal or web.

### [evolve](skills/evolve/README.md) — Self-Improvement
Runs every 2 hours. Scans completed work, extracts reusable patterns, stores them as learned skills. Skills have effectiveness scores — proven patterns get reinforced, stale ones decay. Your agent gets sharper the more you use it. No configuration needed.

### [absorb](skills/absorb/README.md) — Knowledge Intake
Point it at a GitHub repo, local folder, or web URL. It reads the codebase, extracts architecture decisions, conventions, and patterns, then stores them as searchable knowledge. Use it when onboarding to an existing project or studying a reference implementation.

### [heartbeat](skills/heartbeat/README.md) — Always Alive
OS-native keep-alive (Task Scheduler / cron / launchd). Checks every 30 minutes. Dead sessions get revived with full context via `claude --resume`. No custom daemons, no polling loops, no token burn. Close your laptop — your agent keeps working.

### [migrate](skills/migrate/README.md) — One-Time Import
Detects existing AI setups (`~/.claude/`, `~/.openclaw/`, `~/.hermes/`, `~/Documents/claude-setup/`) and imports memories, configs, and knowledge. Run once during onboarding, never again.

### [codex-bridge](skills/codex-bridge/README.md) — The Worker
Delegate bulk work to OpenAI Codex (runs on your ChatGPT Plus). Use it as a **worker** (parallel tasks, boilerplate, test generation) or as a **critic** (adversarial security review, architecture debate, code review). Claude decides when to delegate. Also syncs Claude's knowledge to Codex via AGENTS.md.

### [gemini-bridge](skills/gemini-bridge/README.md) — The Consultant
Call Google Gemini for a different perspective. Use it when you're **uncertain** (fact-checking, research validation), facing **complex decisions** (architecture trade-offs, tech stack choices), or need a **security review** from an independent brain. Supports three-way debate: Claude forms opinion → Codex reviews → Gemini validates → consensus.

### [connect-odoo](skills/connect-odoo/README.md) — ERP Integration
Bidirectional Odoo ERP connection via XML-RPC + MCP. 6 specialized tools for reading/writing Odoo data. Real-time polling for changes. Use it when your AI workflow needs to interact with business processes.

### [notebooklm-bridge](skills/notebooklm-bridge/README.md) — Document Generation
Auto-sync workspace docs to Google NotebookLM. Generate slides, infographics, podcasts, and reports from your codebase documentation. Built-in watermark removal with page-number stamping (multi-page) or date stamping (single-page). Consistent styling across all pages.

---

Every skill has a **trigger description** (Claude knows when to activate), a **Gotchas section** (common mistakes to avoid), and **dynamic `!command` injection** (runtime context on load).

---

## Architecture

```
Skills (the what)     ->  10 skills with manifests, instructions, gotchas
Tools (the how)       ->  32 MCP tools + Claude Code native tools
Hooks (the when)      ->  OS scheduler, git hooks, PostToolUse, Stop hooks
```

**Standing on the giant's shoulders.** Clawd-Lobster doesn't rebuild Claude Code. It uses Claude Code's native extension points (MCP servers, CLAUDE.md, hooks, settings.json) exactly as Anthropic designed them. When Claude Code ships a new feature, you get it for free. When the model improves, your agent improves. Zero adapter code.

```
Disk: ~830 KB    (code + configs)
RAM:  ~25 MB    (MCP server only)
CPU:  0% idle   (OS scheduler, not polling)
LOC:  ~9,000    (not 300,000)
```

For the full file tree and runtime details, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## CLI Reference

| Command | What It Does |
|---------|-------------|
| `clawd-lobster serve` | Start web dashboard (localhost:3333) |
| `clawd-lobster setup` | Terminal onboarding wizard |
| `clawd-lobster workspace create <name>` | Create a new workspace |
| `clawd-lobster squad start` | Run Spec Squad in terminal |
| `clawd-lobster status` | Show system health |

---

## Multi-Machine Setup

```
  clawd-lobster (this repo -- the generator)
       |
       |  install once
       v
  clawd-yourname (your private Hub on GitHub)
       |
       +-- Machine A -- skills + memory + heartbeat
       +-- Machine B -- skills + memory + heartbeat
       +-- Machine C -- skills + memory + heartbeat
            |
            All connected. All sharing knowledge.
```

First machine creates the Hub. Every machine after that joins in 2 minutes.

---

## Requirements

- Python 3.10+
- Claude Code CLI ([install](https://claude.ai/code))
- Git 2.x+
- Node.js 18+ (optional, for Codex Bridge)
- GitHub account (for Hub sync)

---

## Comparison

|  | Heavyweight Frameworks | Raw Claude Code | Clawd-Lobster |
|--|----------------------|----------------|---------------|
| Codebase | 300K+ lines | 0 (built-in) | ~9,000 lines |
| Setup | Hours/days | 0 | 5 minutes |
| Memory | Session-only | Session-only | 4-layer persistent |
| Multi-machine | Usually none | None | Git sync + Hub |
| Model updates | Breaks adapters | Automatic | Automatic |
| Token cost | API per-token | Subscription | Subscription |
| Multi-agent review | Some | None | Spec Squad (adversarial) |
| Self-evolution | None | None | Learned skills + salience |

---

## Philosophy

**1. Amplify, don't rebuild.**
Claude Code is the most capable coding agent in the world. We add a nervous system to it. We don't rebuild the brain.

**2. When the giant grows taller, you grow taller.**
Every Claude Code update makes your Clawd-Lobster better. Zero migration, zero rewrite.

**3. The plan is the product.**
Spec Squad doesn't write code first. It writes a spec, has it adversarially reviewed, then builds to spec. The plan is the contract.

---

## Contributing

PRs welcome. Read [ARCHITECTURE.md](ARCHITECTURE.md) before contributing.

## License

MIT — see [LICENSE](LICENSE).
