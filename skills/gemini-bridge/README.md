# Gemini Bridge — The Consultant

> Cross-model consultation with Google Gemini 3.1 Pro for research, validation, and architecture debates.

## What It Does

Gemini Bridge calls Google Gemini CLI when Claude needs an independent perspective. Four scenarios:
- **Uncertainty** — fact-checking, research validation
- **Complex decisions** — architecture trade-offs, tech stack choices
- **Security review** — independent audit from a different brain
- **Three-way debate** — Claude + Codex + Gemini reach consensus

Part of the **three-agent system**: Claude (lead) + Codex (worker/critic) + Gemini (consultant). See also [codex-bridge](../codex-bridge/README.md).

## Two-Checkpoint Pattern

Same as Codex Bridge — Gemini participates in both checkpoints:

1. **Plan Review** — "Gemini, what assumptions am I making?"
2. **Code Review** — "Gemini, does this logic hold up?"

Combined with Codex's adversarial review, you get two independent brains challenging every important decision.

## Model Quality Gate

| You (Lead) | Gemini 3.1 Pro | Gemini 3 Flash |
|-----------|---------------|---------------|
| Opus 4.6 | Peer | Quick research only |
| Sonnet 4.6 | **Upgrade** | Peer |

## Claude→Gemini Knowledge Sync

`scripts/sync-knowledge.py` generates `GEMINI.md` with consultant-focused briefing:
- Skill library directory
- Wiki pages + pending corrections (strategic context)
- Exit protocol (output JSON findings to stdout)

Gemini enters knowing the project context and open disputes.

## Quick Start

```bash
npm install -g @google/gemini-cli
gemini                      # OAuth login (Google One AI Pro)
gemini --version            # verify
```

## Usage

```bash
gemini -p "Is this the right approach for [X]?"
gemini -p "Review this auth code for vulnerabilities"
```

## Auth

Google One AI Pro subscription ($20/mo) via OAuth. Clear any `GEMINI_API_KEY` / `GOOGLE_API_KEY` env vars to use subscription instead of API key.

**Version:** 0.2.0 | **Kind:** prompt-pattern | **Default:** disabled (optional)
