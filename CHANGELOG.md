# Changelog

## Unreleased

A cleanup and security pass in October 2026. No tag or release.

### Security

- The dashboard server (`clawd-lobster serve`) now checks every request before routing it. The Host header must be `127.0.0.1:<port>` or `localhost:<port>`; an Origin header, when present, must be the server's own origin; and every POST must send the per-process token in an `X-Clawd-Token` header. The token comes from `secrets.token_urlsafe` at startup, is injected into the served pages as `<meta name="clawd-token">`, is written to `~/.clawd-lobster/server-<port>.token` (mode 0600) for local scripts, and is compared with `hmac.compare_digest`. Failed checks and all CORS preflights get 403, and no `Access-Control-*` headers are sent. HTML pages are sent with `Cache-Control: no-store` and may not be framed. Before this, `POST /api/workspaces/create`, `/api/squad/chat` and `/api/squad/start` needed no token at all.
- The prototype servers in `scripts/legacy/` apply the same checks.

### Fixes

- `scripts/sync-all.sh` no longer stops when one of its safe file patterns matches nothing. `git add` stages nothing and exits non-zero in that case, and `set -e` then ended the run before commit and push. Each pattern is added on its own and a miss is skipped. Tracked updates are still staged with `git add -u`. A commit is created only when something is staged, and that commit is then pushed. The message stays `auto-sync` plus the date, with no host name. Ignored files are still left untracked (`git add -A` and `git add -f` are not used).
- `install.ps1` is UTF-8 with a BOM (bytes EF BB BF). Windows PowerShell 5.1 otherwise reads the file as the system ANSI code page, and bytes inside its Chinese, Japanese, and Korean text can become quotes that end a string early. ASCII-only `.ps1` files are unchanged. `.editorconfig` sets `charset = utf-8-bom` for `*.ps1`. The install instructions run the script by path (`.\install.ps1`), not by piping a download into `iex`.
- Scheduling: the evolve and heartbeat setup steps ran `echo ... | crontab -` as an argument list, so nothing was registered while the step reported success. A new `schedule` step kind registers the job from the skill's `runtime` section instead. It reads `crontab -l` (no crontab counts as empty), keeps the line if it is already there, replaces an outdated line for the same task, otherwise appends, writes the result back through stdin without a shell, checks every return code, and reports failures. The step now runs before the probe that checks the job.
- Windows scheduling builds the `schtasks` argument list explicitly, so `/TR` keeps paths with spaces in one argument, and command steps are no longer split with `cmd.split()`.
- Spec Squad: when the Reviewer has not approved after five rounds, the spec is still approved, but `.spec-squad.json` records `"approval": "round_limit"` (or `"reviewer"`), the turn log gets a `FORCED_APPROVAL` entry, a `forced_approval` event goes to the web view, and the terminal and web views say which kind of approval it was.
- The dashboard server no longer raises an error after answering `/api/onboarding/instructions`.
- The API Keys page (`/credentials`) no longer stays at "Loading...": its script did not parse because of the quote escaping in `pages_dashboard.py`.
- NotebookLM Bridge: `auto_remove_watermark` defaults to `false`, and the docs warn that removing the watermark may conflict with Google's terms.

### Privacy

- Host names are no longer written into files or commit messages that get pushed. evolve-tick proposals and commit messages and `knowledge/.pending/` correction notes name the machine only by the `machine_id` from local config, and not at all when it equals the host name. The install scripts no longer store the host name in the Hub's `clients/` records and suggest a random `machine-` label as the machine ID.
- `workspaces.json` is per-machine state and is no longer tracked; `workspaces.example.json` shows the format. The private Hub that the install scripts create still tracks its own copy, and the scripts treat a missing registry as empty.

### Other

- `templates/global-CLAUDE.md`, which the installers add to `~/.claude/CLAUDE.md`, now holds generic guidance only: the boot steps, the memory tools and basic safety rules. It no longer carries review and push rules meant for this repository's maintainers or the deploy command list. The installers append the template once and never rewrite an existing CLAUDE.md, so earlier installs keep their old copy; its "Code Review & Push Policy" section can be deleted.
- New tests for scheduler registration, the request checks, and the approval record (83 unit tests in all).
- Tests for `scripts/sync-all.sh` (a missing pattern, a partial match, a clean tree, and files that must stay untracked) and for the PowerShell BOM (89 unit tests in all).

---

## v0.6.0: Spec Squad, the clawd-lobster Package, and Web Onboarding (2026-04-04 to 2026-04-09)

Summarised from the git history. The version number was set on 2026-04-05 and never tagged.

### Package and CLI

- New `clawd_lobster` Python package with a `clawd-lobster` command: `serve`, `setup`, `workspace create`, `squad start`, and `status`.
- The version briefly read 1.0.0 and was set to 0.6.0 to follow 0.5.0.

### Spec Squad

- Four roles (Architect, Reviewer, Coder, Tester), each turn a separate Claude Agent SDK session. The Reviewer can only read files and challenges the spec for up to five rounds.
- Web mode with a discovery chat and a live dashboard; terminal mode stops after the spec and asks before building.
- The earlier prototypes are kept in `scripts/legacy/`.

### Memory: the Thin Ledger

- SQLite ledger, git wiki under `knowledge/wiki/`, and an optional Oracle Vault for embeddings and cross-machine search.
- Knowledge records carry provenance (source agent, confidence, lifecycle state). `memory_propose_correction` files disputes instead of editing the wiki, and evolve-tick lints the wiki.
- Vault tooling: `vault_init.py`, `vault_api.py`, `vault_migrate.py`, an absorb parser framework, and a Vault MCP server.
- Local embedding support and a text search fallback.

### Web Onboarding

- Setup wizard with four foundations and a card per skill, in five languages, plus an onboarding guide page.
- Backend with a state machine, a controller lease, an intents API, health probes, a skill executor with scheduler registration, Claude Code handoff, and crash recovery.
- Session tokens on the onboarding API, 32 acceptance tests, and a scripted end-to-end HTTP test.

### Skills

- New gemini-bridge and deploy skills, and workspace types.
- NotebookLM Bridge watermark remover with page-number and date stamps.
- A model quality gate and a two-checkpoint pattern for the Codex and Gemini bridges.
- Knowledge sync from Claude to Codex and Gemini (`AGENTS.md`, `GEMINI.md`).
- An Agent SDK dispatch module, with evolve-tick refactored around it.

### Docs

- README rewritten and the four translations updated.

---

## v0.5.0: Evolution Loop + Spec-Driven Development (2026-04-03)

### Architecture Changes

#### Building vs Evolving: clear separation
- **Building** (workspace scope): /spec → blitz → execute TODOs. One machine, full speed.
- **Evolving** (system scope): review completed work → learn patterns → share. Every machine.
- evolve-tick.py completely rewritten: no longer executes TODOs, now focuses on pattern extraction, proposal generation, salience decay, and knowledge sync.

#### Proposals as git-synced files
- Evolve generates improvement proposals as markdown files in openspec/proposals/
- Proposals use 3W1H format (Why, What, Who, How) + effort estimate
- Dual storage: git files (sync across machines) + memory.db knowledge_items (searchable, Oracle L4)
- Any machine can review proposals; approved ones become TODOs for next blitz

### New Skills

| Skill | Type | Description |
|-------|------|-------------|
| **Spec** (core, locked) | prompt-pattern | Guided workspace + spec creation, 3W1H, blitz execution |
| **Absorb** (core, locked) | prompt-pattern | Knowledge ingestion from folders, repos, URLs |
| **Codex Bridge** (optional) | prompt-pattern | Delegate work to OpenAI Codex: worker + critic roles (installed + tested) |
| **NotebookLM Bridge** (optional) | prompt-pattern | Free RAG + content engine via Google NotebookLM: auto-sync, slides, podcasts |

### New Scripts

| Script | Purpose |
|--------|---------|
| `workspace-create.py` | Automated workspace creation (git, GitHub, memory.db, openspec/); also auto-creates NotebookLM notebook |
| `validate-spec.py` | Hard validation for spec artifacts (15+ checks) |
| `setup-hooks.sh/.ps1` | Install git pre-commit hook for spec validation |
| `evolve-tick.py` | Rewritten: pattern extraction + proposals + salience decay |
| `notebooklm-sync.py` | Auto-pushes entire workspace content to NotebookLM; JSON/TOML/YAML auto-wrapped as markdown for compatibility |

### New MCP Tools (Memory Server v0.4.0, 28 tools)

- `memory_todo_add`: Create TODO items
- `memory_todo_list`: List/filter TODOs by status
- `memory_todo_update`: Update TODO status, branch, notes
- `memory_todo_search`: Search TODOs by title/description

### NotebookLM Integration

- **NotebookLM Bridge** skill with `notebooklm-sync.py` auto-sync script
- `notebooklm-sync.py` auto-pushes entire workspace content to NotebookLM after blitz
- `workspace-create.py` auto-creates NotebookLM notebook for each new workspace
- 3-way AI debate (Claude + Codex + Gemini) produced 8 prompt rules + 3-stage content pipeline (Research → Debate → Generate)
- JSON/TOML/YAML files auto-wrapped as markdown for NotebookLM source compatibility
- `.notebooklm-id` auto-saved per workspace for zero-config syncing

### Web UI Updates

- **Workspaces tab**: 4th main tab, workspace cards, staged review panel
- **3 source tabs**: Claude Native / Clawd-Lobster / Custom Hub
- **Absorb + Spec + Codex Bridge** skills added to dashboard

### README

- Restructured into 5-chapter learning path (Memory → Workspaces → Skills → Spec → Evolution)
- Added Philosophy #7: "When the giant grows taller, you grow taller"
- Added runtime footprint breakdown (25 MB RAM, 672 KB disk)
- Added architectural thesis on scheduling Claude Code vs rebuilding it

### Boot Protocol

- Now checks for active spec (openspec/changes/*/tasks.md progress)
- Checks for .blitz-active marker → auto-resume blitz

---

## v0.4.0: Skill Management Platform (2026-04-02)

### Overview

Every skill is now a first-class module with a `skill.json` manifest. A new CLI tool (`skill-manager.py`) and Web UI dashboard provide unified skill lifecycle management: enable/disable, configure, credential management, health checks, and registry reconciliation.

### New: Skill Manifest System

Each skill now has a `skill.json` manifest declaring:
- **Identity**: id, name, description, version, icon, category, tags
- **Kind**: `mcp-server`, `prompt-pattern`, `cron`, or `poller`
- **MCP registration**: server name, command, args, cwd, env vars
- **Permissions**: auto-allowed tool list for `settings.json`
- **Credentials**: required fields with labels, types, placeholders, sensitivity flags
- **Config**: JSON Schema for skill-specific settings with defaults
- **Runtime**: entrypoint, cron schedule, timeout, retry policy (for pollers/crons)
- **Health check**: type (mcp-ping/command/none), interval, timeout
- **Dependencies**: other skills, system requirements, Python packages

The manifest is the single source of truth. `.mcp.json` and `settings.json` are derived artifacts.

### New: Skill Manager CLI

`scripts/skill-manager.py` is stdlib-only and cross-platform (Windows + Unix):

| Command | Description |
|---------|-------------|
| `list` | Table of all skills with status |
| `status [id]` | Detailed skill info |
| `enable <id>` | Enable + update .mcp.json + settings.json |
| `disable <id>` | Disable + clean up config files |
| `config <id>` | View/edit skill config (`--set key=value`) |
| `credentials <id>` | Manage skill credentials (`--set cred-id value`) |
| `health` | Run health checks on all enabled skills |
| `reconcile` | Regenerate .mcp.json + settings.json from registry |

Registry lives at `~/.clawd-lobster/skills/registry.json`. Credentials at `~/.clawd-lobster/credentials/` (chmod 600 on Unix).

### New: Web Dashboard

`webapp/index.html` rewritten from 292 to 1245 lines:
- **3-tab layout**: Skills (default) | Setup | Settings
- **Skill card grid**: responsive, category filters, search, ON/OFF toggles
- **Detail panels**: inline config editing, credential inputs (password masked), health badges
- **Toast notifications**, confirmation dialogs, smooth animations
- **Setup wizard** preserved as a tab (existing functionality intact)
- **Settings tab**: machine ID, platform info, credential summary table
- Dark theme consistent with existing design (#0d1117 palette)

### New: Odoo ERP Connector Skill

`skills/connect-odoo/` is an integration skill with:
- **6 MCP tools**: `odoo_search`, `odoo_read`, `odoo_create`, `odoo_write`, `odoo_execute`, `odoo_poll_tasks`
- **XML-RPC transport** using Python's built-in `xmlrpc.client` (zero external deps beyond FastMCP)
- **Poller** (`poller.py --once`) for cron-scheduled task polling
- **Health check** (`--health` flag) that tests connection + prints Odoo version
- **Credential template**: url, db, user, password (sensitive field encrypted at rest)
- Gracefully handles missing `arp.task` model (returns empty list)

### Skill Manifests Created

| Skill | Kind | Category | Always On |
|-------|------|----------|-----------|
| memory-server | mcp-server | core | yes |
| heartbeat | cron | core | yes |
| evolve | prompt-pattern | intelligence | no |
| migrate | prompt-pattern | utility | no |
| connect-odoo | poller | integration | no |

### Installer Integration

Both `install.ps1` and `install.sh` now run `skill-manager.py reconcile` after MCP server setup to initialize the skill registry automatically.

### Files Changed

```
 NEW  scripts/skill-manager.py                         (+842)
 NEW  skills/connect-odoo/skill.json
 NEW  skills/connect-odoo/connect_odoo/__init__.py
 NEW  skills/connect-odoo/connect_odoo/server.py       (+224)
 NEW  skills/connect-odoo/connect_odoo/poller.py       (+56)
 NEW  skills/connect-odoo/pyproject.toml
 NEW  skills/connect-odoo/SKILL.md
 NEW  skills/memory-server/skill.json
 NEW  skills/evolve/skill.json
 NEW  skills/heartbeat/skill.json
 NEW  skills/migrate/skill.json
 MOD  webapp/index.html                                (+1072/-173)
 MOD  templates/global-CLAUDE.md                       (+26)
 MOD  install.ps1                                      (+12)
 MOD  install.sh                                       (+9)
```

---

## v0.3.0: OpenClaw-Hardened (2026-04-02)

### Context

This release was produced by a deep code review session using Claude Opus as AI architect. Clawd-Lobster v0.2.0 was audited against a battle-tested OpenClaw installation (a private multi-agent framework with months of production experience) to identify gaps, bugs, and missing features.

The goal: take everything learned from real-world agent operations and harden Clawd-Lobster before wider deployment.

### Architecture Decisions

#### SQLite is primary, Oracle is sync target (not the other way around)

**Decision:** All data writes go to local SQLite first. Oracle L4 is an optional sync destination for cross-machine search.

**Why:** Most users will never install Oracle. The original v0.2.0 had 4 trail tools (`memory_audit_search`, `memory_audit_stats`, `memory_daily_report`, `memory_activity_log`) that returned "requires Oracle L4 connection", making them useless for 99% of users. Now they all query local SQLite first, then merge Oracle results if available.

**Analogy:** Same as Active Directory event logs. Each domain controller has its own Security Event Log (fast, local). All push to central SIEM (comprehensive, cross-machine). You don't sync SIEM back down to each DC.

```
Machine A (SQLite) ──push──▶ Oracle L4 ◀──push── Machine B (SQLite)
     │                          │                       │
     │ query local → instant    │ query all → cross-DC  │ query local → instant
```

#### Learning type = knowledge_item with "learning" tag (not a new table)

**Decision:** `memory_store(type="learning")` stores to `knowledge_items` with auto-tag `["learning"]`, not a separate `learnings` table.

**Why:** Three options were considered:
1. New `memory_record_learning` MCP tool + new table: adds complexity, new table routing in `memory_list`
2. New type in `memory_store` + new table: same complexity
3. New type in `memory_store` + existing `knowledge_items` table with tag: **chosen**

Option 3 wins because:
- Claude Code's native auto-memory uses classification (user/feedback/project/reference), not separate databases per type
- `knowledge_items` already has `title` + `content` + `tags`, a perfect fit
- Search with `memory_search("learning")` or tag filter works immediately
- No schema change needed = no `init_db.py` change = no migration
- Learnings ≠ Skills: learnings record *mistakes to avoid* (pitfalls, gotchas), skills record *patterns to follow* (successful approaches)

**Auto-detect keywords:** `learned, lesson, mistake, never again, pitfall, gotcha, watch out, 踩坑, 教訓, 原來, 別再`

#### machine_id on everything

**Decision:** All records (decisions, resolved, questions, knowledge, action_log) are tagged with `machine_id`.

**Why:** When multiple machines sync to the same Hub via git, you need to know which machine wrote what. Without machine_id, action logs from Machine A and Machine B would be indistinguishable. This is the same reason AD logs have ComputerName and SIEM has source_host.

**Resolution order:** config.json `machine_id` > env `CLAWD_MACHINE_ID` > `socket.gethostname()`

#### Boot Protocol in CLAUDE.md (not a separate file)

**Decision:** Boot protocol lives inside `templates/global-CLAUDE.md`, not a separate `BOOT_CLAUDE.md`.

**Why:** OpenClaw uses a separate `BOOT_CLAUDE.md` file, but that requires remembering to read it. By embedding boot steps directly in the global CLAUDE.md that Claude Code auto-injects every session, the boot protocol is unavoidable. 5 steps, < 10 seconds:
1. `memory_status()`: system state
2. `memory_list(limit=5)`: recent context
3. `memory_list_skills()`: available patterns
4. `memory_audit_search(limit=3)`: last actions (if resuming)
5. Report ready

#### Security scan as script, not just SKILL.md

**Decision:** `scripts/security-scan.py` is a real script, not just a SKILL.md instruction file.

**Why:** Originally considered making it just a SKILL.md (documentation for Claude Code to follow). But in practice, scan results often include encrypted file false positives, and a proper script can:
- Exclude binary/encrypted patterns (`*.db`, `*.wallet`, `*.p12`)
- Gracefully skip uninstalled tools (not all 5 will be available on every machine)
- Save structured JSON reports to `.claude-memory/security-scan.json`
- Run headless via cron without Claude Code involvement

Tools: bandit, pip-audit, gitleaks, semgrep, trivy. All optional; the script runs whatever is installed.

#### Heartbeat session targeting

**Decision:** `heartbeat.ps1` now finds the most recent session file for each workspace before calling `claude --resume`.

**Why:** The original `claude --resume` without arguments resumes the last session globally, which might be from a different workspace. If workspace A's session died but workspace B was used more recently, `claude --resume` in workspace A's directory might resume workspace B's context. Now the heartbeat scans `~/.claude/projects/*/sessions/*.json`, finds the one matching the workspace ID, and passes the specific session ID.

### Bug Fixes

#### `_local_text_search` only searched `knowledge_items`

**Bug:** `memory_search` with no Oracle connection only searched the `knowledge_items` table. Decisions, resolved issues, and open questions were invisible to search.

**Fix:** Now searches all 4 tables (`knowledge_items`, `decisions`, `resolved`, `open_questions`). Results are tagged with type prefix (`[KNO]`, `[DEC]`, `[RES]`, `[Q]`) and sorted by salience across all tables.

#### `_local_text_search` opened all workspace connections eagerly

**Bug:** Every search opened SQLite connections to every registered workspace, even if the workspace didn't exist or had no data. With many workspaces, this was slow and could crash on missing `.claude-memory/memory.db`.

**Fix:** Lazy connection with `try/except` per workspace. Missing workspaces are silently skipped. Connection is closed immediately after each workspace's query.

#### `memory_compact` checked obsolete `session.md`

**Bug:** `memory_compact` looked for `.claude-memory/session.md` and checked its line count / token count. Claude Code hasn't used session.md for months; it manages sessions natively.

**Fix:** Now checks `memory.db` health: file size, row counts per table, salience distribution (stale items with sal < 0.5), and recommends compaction if DB > 10MB or > 50 stale items.

#### `install.sh` was incomplete compared to `install.ps1`

**Bug:** The Unix installer was missing: i18n (5 languages), Hub creation flow, machine registration, workspace deployment, domain selection, fleet status display. It was a 6-step process vs Windows' 9-step.

**Fix:** Full rewrite to match `install.ps1`: 5-language i18n, Hub create/join, machine registration to `clients/{machine_id}.json`, workspace deploy with memory.db init, headless args support (`--lang`, `--hub`, `--env`, `--machine`, `--domain`).

#### Docker had no cron for heartbeat/sync

**Bug:** README claimed "Container lifecycle" for Docker scheduler, but the Dockerfile had no cron setup. Sync and heartbeat simply didn't run in Docker.

**Fix:** Install `cron` package, register `sync-all.sh` and `heartbeat.sh` as `/etc/cron.d/clawd-lobster` jobs (every 30 min). Entry point starts cron daemon before shell. Config includes `machine_id: "docker"`.

### New Features

| Feature | Files Changed | Tools Added |
|---------|--------------|-------------|
| Boot Protocol | `templates/global-CLAUDE.md` | none |
| Action Log (local audit trail) | `init_db.py`, `server.py` | `memory_log_action` |
| machine_id tagging | `config.py`, `init_db.py`, `server.py` | none |
| Learning type | `server.py`, `global-CLAUDE.md` | none (via `memory_store`) |
| Full-table search | `server.py` | none (enhanced `memory_search`) |
| SQLite-first trail | `server.py` | none (enhanced 4 trail tools) |
| Security scan | `scripts/security-scan.py` | none |
| Heartbeat health check | `scripts/heartbeat.ps1` | none |
| Hooks example | `templates/settings.json.template` | none |
| Learnings directory | `knowledge/learnings/README.md` | none |
| install.sh parity | `install.sh` | none |
| Docker cron | `Dockerfile` | none |
| Session targeting | `scripts/heartbeat.ps1` | none |

### Tool Count: 21 → 24

New tools:
- `memory_log_action`: log task actions with machine_id (TASK_START, SPEC, REVIEW, COMMIT, etc.)

Enhanced tools (now work without Oracle):
- `memory_audit_search`: searches local SQLite action_log + Oracle
- `memory_audit_stats`: aggregates from local action_log + Oracle
- `memory_daily_report`: summarizes from local action_log + Oracle
- `memory_activity_log`: queries local action_log + Oracle

Enhanced tools (broader scope):
- `memory_search`: now searches ALL 4 tables, not just knowledge_items
- `memory_store`: new `type="learning"` for pitfalls/lessons
- `memory_compact`: checks memory.db health instead of obsolete session.md
- `memory_status`: shows machine_id, version 0.3.0

### Files Changed

```
 Dockerfile                                  |  +21
 install.sh                                  | +495 (full rewrite)
 knowledge/learnings/README.md               |  NEW
 scripts/heartbeat.ps1                       |  +43
 scripts/init_db.py                          |  +18
 scripts/security-scan.py                    |  NEW (+150)
 skills/memory-server/mcp_memory/__init__.py |  version bump
 skills/memory-server/mcp_memory/config.py   |  +14
 skills/memory-server/mcp_memory/server.py   | +574/-161
 skills/memory-server/pyproject.toml         |  version bump
 templates/global-CLAUDE.md                  |  +32
 templates/settings.json.template            |  +20
```

### What Was NOT Added (and why)

These OpenClaw features were evaluated and intentionally excluded:

| Feature | Reason |
|---------|--------|
| Multi-agent role system | Too specific to one user's setup; every user's agent composition is different |
| Deep persona system (SOUL.md with personality/appearance/emotions) | Persona, not tooling; belongs in user's soul/ customization |
| Odoo / ARP integration | Business system, not general-purpose |
| Taiwan-specific (ECPay, TWSMS, gov open data) | Regional, not universal |
| Telegram bot integration | Communication platform binding; should be a separate skill |
| Gateway service (port 18789) | OpenClaw-specific architecture |
| Device pairing | Can be added later if needed |
| GitHub issue dispatch | Too opinionated; every user's workflow is different |
| 45+ business scripts | Most are tied to specific business logic |
| Daily report PDF generation | Too customized (bilingual CN/EN + SMTP + Telegram); daily-digest can be a future skill |
| Local model integration (QWEN) | Concept is good but needs to be provider-agnostic; deferred |
| Patrol systems (HR/PM/Compliance) | Too heavyweight for a ~2K LOC wrapper; concept absorbed into heartbeat health check |

### Migration Notes for Existing Installations

If you're running v0.2.0:

1. **Pull the update:** `git pull origin master`
2. **Reinstall MCP server:** `pip install -e skills/memory-server/` (version 0.2.0 → 0.3.0)
3. **Re-run init_db.py** on each workspace's memory.db (safe to re-run, uses ALTER TABLE with try/except):
   ```bash
   python scripts/init_db.py path/to/.claude-memory/memory.db
   ```
4. **Update CLAUDE.md:** The installer regenerates it, or manually copy from `templates/global-CLAUDE.md`
5. **Update settings.json:** Add new auto-allow entries from `templates/settings.json.template`
6. **Config:** Add `"machine_id": "your-machine-name"` to `~/.clawd-lobster/config.json`
