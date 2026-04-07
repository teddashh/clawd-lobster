# Evolve

> System-level learning engine that extracts reusable patterns from completed work and consolidates knowledge.

## What It Does

Evolve runs every 2 hours to review completed work, extract patterns worth remembering, apply salience decay to aging memories, and sync knowledge across machines. It generates improvement proposals as git-synced files but never auto-merges -- a human or authorized agent must approve changes.

## How It Works

The main script `scripts/evolve-tick.py` executes a 6-phase cycle:

1. **Scan** -- review recently completed work and session logs.
2. **Extract** -- identify reusable patterns and skill-worthy behaviors.
3. **Decay** -- apply salience decay to existing memories (keeps the knowledge base fresh).
4. **LINT** -- wiki health check: broken links, orphan pages, stale claims (>90 days), pending corrections, DB/wiki drift. *(Karpathy pattern)*
5. **Sync** -- push consolidated knowledge to Hub for cross-machine availability.
6. **Log** -- record what was learned, proposed, and lint issues found.

**Key behaviors:**
- Respects `.blitz-active` marker file -- pauses evolution during active blitz sessions.
- Tracks skill effectiveness: +2% salience per use, +10% per improvement.
- Proposals land as git-synced files for review; nothing is auto-merged.
- Timeout: 600 seconds per tick, with 1 retry (60-second backoff).

**Cron expression:** `0 */2 * * *` (every 2 hours)

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `auto_detect` | boolean | `true` | Automatically detect skill-worthy patterns after task completion |
| `retirement_days` | integer | `90` | Days of inactivity before suggesting skill retirement |
| `cron_enabled` | boolean | `true` | Enable automatic TODO processing every 2 hours |
| `max_todo_timeout` | integer | `300` | Max seconds Claude gets per TODO item |

## Dependencies

| Type | Requirement |
|------|-------------|
| Skills | `memory-server` |
| System | `git`, `claude` CLI |

## Credentials

None required.

## Maintenance

- `evolve-tick.py` is the sole entrypoint -- all logic flows through it.
- If Claude Code CLI syntax changes (especially `claude` invocation flags), update the script accordingly.
- Adjust `retirement_days` if skills are being suggested for retirement too aggressively.
- Monitor the git-synced proposal files to ensure they are being reviewed and not piling up.
- No health check is configured; failures surface in cron logs.

*LINT phase absorbed from [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). See `openspec/MEMORY-ARCHITECTURE.md` for the full Thin Ledger design.*

**Version:** 0.5.0 | **Kind:** cron | **Category:** intelligence
