# Migrate

> Import memories and configs from existing AI agent setups into clawd-lobster.

## What It Does

Migrate scans legacy AI agent installations and brings their accumulated knowledge into clawd-lobster's memory system. It handles four known source formats, extracting decisions, learned patterns, skills, and configuration choices so you do not lose institutional knowledge when switching frameworks.

## How It Works

Migrate is a prompt-pattern skill that runs inline during a Claude Code session. It scans configured legacy sources, parses their knowledge formats, and writes structured entries through memory-server.

**Supported sources (4 legacy systems):**

| Source | What It Scans |
|--------|--------------|
| `claude-setup` | Early Claude Code bootstrap configs and notes |
| `raw-claude` | Raw Claude Code sessions and MEMORY.md files |
| `openclaw` | OpenClaw framework knowledge bases and session logs |
| `hermes` | Hermes Agent configs, memory stores, and learned behaviors |

**Dry-run mode** previews all proposed migrations without writing anything -- recommended for first runs to verify what will be imported.

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dry_run` | boolean | `false` | Preview changes without writing anything |
| `sources` | array of strings | `["claude-setup", "raw-claude", "openclaw", "hermes"]` | Which legacy systems to scan |

## Dependencies

| Type | Requirement |
|------|-------------|
| Skills | `memory-server` |

No system-level or Python dependencies beyond what memory-server provides.

## Credentials

None required. Source scanning uses local filesystem access only.

## Maintenance

- Not always-on (`alwaysOn: false`) -- this is an onboarding/transition tool, enabled by default but expected to be run occasionally.
- As new AI agent frameworks emerge, add new source parsers to the skill and extend the `sources` enum in `skill.json`.
- After a successful migration, consider disabling this skill to avoid redundant re-scans.
- No health check -- runs on demand as a prompt pattern.
- If source format changes (e.g., OpenClaw restructures its knowledge base), the corresponding parser will need updating.

**Version:** 0.3.0 | **Kind:** prompt-pattern | **Category:** utility
