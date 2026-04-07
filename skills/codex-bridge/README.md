# Codex Bridge — The Worker

> Delegate bulk work, get adversarial reviews, and run two-checkpoint debates with Codex GPT-5.4.

## What It Does

Codex Bridge connects Claude Code to OpenAI Codex for two roles:
- **Worker** — parallel tasks, boilerplate, test generation, bulk refactoring
- **Critic** — adversarial security review, architecture debate, code review

Part of the **three-agent system**: Claude (lead) + Codex (worker/critic) + Gemini (consultant). See also [gemini-bridge](../gemini-bridge/README.md).

## Two-Checkpoint Pattern

For important tasks, Claude consults both Codex and Gemini at two checkpoints:

1. **Plan Review** (before building) — "Here's my plan. What's wrong?"
2. **Code Review** (before delivering) — "Here's the code. What breaks?"

Each checkpoint costs ~3 minutes but can save a 15-minute redo cycle.

## Model Quality Gate

| You (Lead) | GPT-5.4 Codex | GPT-4o |
|-----------|--------------|--------|
| Opus 4.6 | Peer | Review only |
| Sonnet 4.6 | **Upgrade** | Peer |

## Claude→Codex Knowledge Sync

`scripts/sync-knowledge.py` generates `AGENTS.md` with role-based briefing:
- Skill library directory (where to find SKILL.md files)
- Project context + recent decisions
- Exit protocol (output JSON findings to stdout)

Codex enters every session knowing what Claude knows.

## Commands

| Command | Purpose |
|---------|---------|
| `/codex:review` | Code review against local git state |
| `/codex:adversarial-review` | Challenge implementation approach |
| `/codex:rescue` | Delegate investigation or fix |
| `codex exec "prompt"` | Direct CLI |

## Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `auto_delegate` | boolean | `false` | Auto-delegate eligible tasks |
| `preferred_model` | string | `gpt-5.3-codex` | Model for Codex tasks |
| `default_effort` | string | `none` | Effort: none/low/medium/high/xhigh |

## Auth

ChatGPT Plus subscription ($20/mo) or OpenAI API key. Run `codex login`.

**Version:** 0.2.0 | **Kind:** prompt-pattern | **Default:** disabled (optional)
