# Changelog

## v0.3.0 — OpenClaw-Hardened (2026-04-02)

### Context

This release was produced by a deep code review session between Ted (黃仁靖) and 蕾姐 (Claude Opus, the CIO of Ted's OpenClaw agent fleet). Ted built Clawd-Lobster v0.2.0 on his work computer with a separate Claude Code setup wrapper. He then brought it back to his home machine (the original OpenClaw installation — the most battle-tested environment with 300K+ LOC, 8 agents, 52 skills, and months of production experience) for a comprehensive audit.

The goal: take everything OpenClaw learned the hard way and harden Clawd-Lobster before it becomes the unified system across all of Ted's machines.

### Architecture Decisions

#### SQLite is primary, Oracle is sync target (not the other way around)

**Decision:** All data writes go to local SQLite first. Oracle L4 is an optional sync destination for cross-machine search.

**Why:** Most users will never install Oracle. The original v0.2.0 had 4 trail tools (`memory_audit_search`, `memory_audit_stats`, `memory_daily_report`, `memory_activity_log`) that returned "requires Oracle L4 connection" — making them useless for 99% of users. Now they all query local SQLite first, then merge Oracle results if available.

**Analogy:** Same as Active Directory event logs. Each domain controller has its own Security Event Log (fast, local). All push to central SIEM (comprehensive, cross-machine). You don't sync SIEM back down to each DC.

```
Machine A (SQLite) ──push──▶ Oracle L4 ◀──push── Machine B (SQLite)
     │                          │                       │
     │ query local → instant    │ query all → cross-DC  │ query local → instant
```

#### Learning type = knowledge_item with "learning" tag (not a new table)

**Decision:** `memory_store(type="learning")` stores to `knowledge_items` with auto-tag `["learning"]`, not a separate `learnings` table.

**Why:** Three options were considered:
1. New `memory_record_learning` MCP tool + new table — adds complexity, new table routing in `memory_list`
2. New type in `memory_store` + new table — same complexity
3. New type in `memory_store` + existing `knowledge_items` table with tag — **chosen**

Option 3 wins because:
- Claude Code's native auto-memory uses classification (user/feedback/project/reference), not separate databases per type
- `knowledge_items` already has `title` + `content` + `tags` — perfect fit
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
1. `memory_status()` — system state
2. `memory_list(limit=5)` — recent context
3. `memory_list_skills()` — available patterns
4. `memory_audit_search(limit=3)` — last actions (if resuming)
5. Report ready

#### Security scan as script, not just SKILL.md

**Decision:** `scripts/security-scan.py` is a real script, not just a SKILL.md instruction file.

**Why:** Originally considered making it just a SKILL.md (documentation for Claude Code to follow). But Ted noted that scan results often include encrypted file false positives, and a proper script can:
- Exclude binary/encrypted patterns (`*.db`, `*.wallet`, `*.p12`)
- Gracefully skip uninstalled tools (not all 5 will be available on every machine)
- Save structured JSON reports to `.claude-memory/security-scan.json`
- Run headless via cron without Claude Code involvement

Tools: bandit, pip-audit, gitleaks, semgrep, trivy. All optional — script runs whatever is installed.

#### Heartbeat session targeting

**Decision:** `heartbeat.ps1` now finds the most recent session file for each workspace before calling `claude --resume`.

**Why:** The original `claude --resume` without arguments resumes the last session globally — which might be from a different workspace. If workspace A's session died but workspace B was used more recently, `claude --resume` in workspace A's directory might resume workspace B's context. Now the heartbeat scans `~/.claude/projects/*/sessions/*.json`, finds the one matching the workspace ID, and passes the specific session ID.

### Bug Fixes

#### `_local_text_search` only searched `knowledge_items`

**Bug:** `memory_search` with no Oracle connection only searched the `knowledge_items` table. Decisions, resolved issues, and open questions were invisible to search.

**Fix:** Now searches all 4 tables (`knowledge_items`, `decisions`, `resolved`, `open_questions`). Results are tagged with type prefix (`[KNO]`, `[DEC]`, `[RES]`, `[Q]`) and sorted by salience across all tables.

#### `_local_text_search` opened all workspace connections eagerly

**Bug:** Every search opened SQLite connections to every registered workspace, even if the workspace didn't exist or had no data. With many workspaces, this was slow and could crash on missing `.claude-memory/memory.db`.

**Fix:** Lazy connection with `try/except` per workspace. Missing workspaces are silently skipped. Connection is closed immediately after each workspace's query.

#### `memory_compact` checked obsolete `session.md`

**Bug:** `memory_compact` looked for `.claude-memory/session.md` and checked its line count / token count. Claude Code hasn't used session.md for months — it manages sessions natively.

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
| Boot Protocol | `templates/global-CLAUDE.md` | — |
| Action Log (local audit trail) | `init_db.py`, `server.py` | `memory_log_action` |
| machine_id tagging | `config.py`, `init_db.py`, `server.py` | — |
| Learning type | `server.py`, `global-CLAUDE.md` | — (via `memory_store`) |
| Full-table search | `server.py` | — (enhanced `memory_search`) |
| SQLite-first trail | `server.py` | — (enhanced 4 trail tools) |
| Security scan | `scripts/security-scan.py` | — |
| Heartbeat health check | `scripts/heartbeat.ps1` | — |
| Hooks example | `templates/settings.json.template` | — |
| Learnings directory | `knowledge/learnings/README.md` | — |
| install.sh parity | `install.sh` | — |
| Docker cron | `Dockerfile` | — |
| Session targeting | `scripts/heartbeat.ps1` | — |

### Tool Count: 21 → 24

New tools:
- `memory_log_action` — log task actions with machine_id (TASK_START, SPEC, REVIEW, COMMIT, etc.)

Enhanced tools (now work without Oracle):
- `memory_audit_search` — searches local SQLite action_log + Oracle
- `memory_audit_stats` — aggregates from local action_log + Oracle
- `memory_daily_report` — summarizes from local action_log + Oracle
- `memory_activity_log` — queries local action_log + Oracle

Enhanced tools (broader scope):
- `memory_search` — now searches ALL 4 tables, not just knowledge_items
- `memory_store` — new `type="learning"` for pitfalls/lessons
- `memory_compact` — checks memory.db health instead of obsolete session.md
- `memory_status` — shows machine_id, version 0.3.0

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
| Multi-agent role system (蕾姐/小雞/小米...) | Too Ted-specific; every user's agent composition is different |
| Deep persona system (SOUL.md with personality/appearance/emotions) | Persona, not tooling; belongs in user's soul/ customization |
| Odoo / ARP integration | Business system, not general-purpose |
| Taiwan-specific (ECPay, TWSMS, gov open data) | Regional, not universal |
| Telegram bot integration | Communication platform binding; should be a separate skill |
| Gateway service (port 18789) | OpenClaw-specific architecture |
| NSFW content system | Not appropriate for public repo |
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
3. **Re-run init_db.py** on each workspace's memory.db — safe to re-run, uses ALTER TABLE with try/except:
   ```bash
   python scripts/init_db.py path/to/.claude-memory/memory.db
   ```
4. **Update CLAUDE.md:** The installer regenerates it, or manually copy from `templates/global-CLAUDE.md`
5. **Update settings.json:** Add new auto-allow entries from `templates/settings.json.template`
6. **Config:** Add `"machine_id": "your-machine-name"` to `~/.clawd-lobster/config.json`
