# Absorb

> Knowledge absorption engine -- feed it folders, repos, or URLs and it extracts knowledge, skills, and TODOs.

## What It Does

Absorb ingests external sources and distills them into structured memory entries. Point it at a codebase, a repository, or a URL, and it will extract decisions, knowledge patterns, learnable skills, and actionable TODO items. It writes everything through the memory-server, keeping your knowledge base growing automatically.

## How It Works

Absorb is a prompt-pattern skill -- it runs inline during a Claude Code session when invoked. It analyzes the target source at one of three scan depths:

- **Shallow** -- README and top-level docs only. Fast, minimal.
- **Normal** -- Key files (configs, main modules, docs). Default.
- **Deep** -- Full codebase traversal. Thorough but slower.

**Safety rules:**
- No secrets or credentials are ever stored.
- Verbatim content longer than 5000 characters is summarized, not copied.
- Dry-run mode previews what would be absorbed without writing anything.

When `auto_create_todos` is enabled, discovered tasks and follow-ups are automatically added as TODO items via memory-server.

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dry_run` | boolean | `false` | Preview what would be absorbed without writing anything |
| `depth` | string | `"normal"` | Scan depth: `shallow`, `normal`, or `deep` |
| `auto_create_todos` | boolean | `true` | Automatically create TODO items from discovered tasks |

## Dependencies

| Type | Requirement |
|------|-------------|
| Skills | `memory-server` |

No system-level or Python dependencies beyond what memory-server provides.

## Credentials

None required.

## Maintenance

- Always-on and enabled by default (`alwaysOn: true`).
- No health check -- this runs on demand as a prompt pattern, not as a background service.
- If you add new source types (e.g., API docs, wikis), extend the prompt pattern in `SKILL.md`.
- For large repos, prefer `depth: "normal"` to avoid excessive token usage.
- Review absorbed content periodically to ensure quality -- automated extraction can be noisy.

**Version:** 0.1.0 | **Kind:** prompt-pattern | **Category:** intelligence
