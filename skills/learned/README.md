# Learned Skills — Living Pattern Library

Auto-populated directory of reusable patterns extracted from your completed work.

## What It Does

`skills/learned/` is not a skill you invoke — it's the **output** of the evolution loop. When you complete meaningful work and the `evolve` system detects a reusable pattern, it promotes that pattern into a learned skill. Future sessions can reuse it instead of rediscovering it.

The key distinction: a learned skill is a **pattern to follow** — a trigger condition, an approach that worked, and enough structure to apply it again. One-off fixes and project-specific hacks stay as knowledge, not skills.

## How Patterns Become Skills

1. You complete substantial work in a workspace
2. `evolve` runs (every 2 hours or on-demand via `/evolve`)
3. Claude reviews completed tasks and recent actions
4. If a reusable pattern is found, it's stored as a learned skill
5. The skill gets an effectiveness score that changes over time

## Lifecycle

| State | Score | What Happens |
|-------|-------|--------------|
| New | 1.0x | Just extracted, untested |
| Proven | 1.0-3.0x | Each successful reuse: +2%. Each improvement: +10%. Cap at 3.0x. |
| Stale | Decaying | Unused for 90+ days, suggested for retirement |
| Archived | — | Moved out of active path |

## Directory Structure

```
skills/learned/
  pattern-name.md     # Each learned pattern as a markdown file
  archive/            # Retired patterns (90+ days unused)
```

## Related Skills

- **[evolve](../evolve/README.md)** — The system that extracts patterns and populates this directory
- **[memory-server](../memory-server/README.md)** — Stores skill metadata and effectiveness scores
