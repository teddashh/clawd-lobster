# Evolve — System-Level Learning & Knowledge Consolidation

Evolve makes the entire Clawd-Lobster system smarter over time. It does NOT build features (that's `/spec:blitz`). Evolve reviews completed work, extracts reusable patterns, and shares learnings across all machines.

**Building** = workspace scope, one machine, `/spec:blitz`
**Evolving** = system scope, every machine, `evolve-tick.py`

---

## Automatic Mode (Cron — every 2 hours)

`scripts/evolve-tick.py` runs as a cron job and performs 5 phases:

### Phase 1: Scan Completed Work
- Reads `todo_items` table across all workspaces for `status='approved'` items
- Reads `action_log` for recent TASK_DONE, COMMIT, REVIEW_OK, BLITZ_COMPLETE events
- Collects what was done, where, and by which machine

### Phase 2: Extract Patterns (Claude reviews)
- Sends completed work summary to Claude via `claude -p`
- Claude calls `memory_learn_skill()` for reusable patterns it finds
- Claude calls `memory_record_knowledge()` for non-obvious insights
- Skips patterns that duplicate existing `learned_skills`
- Selective: only extracts genuinely reusable patterns, not one-off fixes

### Phase 3: Salience Decay
- Items not accessed for 30+ days: salience -= 5% per cycle
- Floor at 0.01 (never deleted, just sinks)
- Important memories stay afloat via access and reinforcement

### Phase 4: Sync to Hub
- `git push` knowledge changes to the Hub repo
- Other machines pull learnings on next sync-all cycle
- Machine A learns something → Machine B gets it within 30 minutes

### Phase 5: Log
- Records EVOLVE_CYCLE action with patterns learned and items decayed

---

## Blitz Gate

If a workspace has `.blitz-active` marker, evolve skips it entirely.

Why: Blitz is building v1 from spec. Evolving mid-build causes style inconsistency. Let spec finish first, then evolve reviews the completed work.

Override: `python evolve-tick.py --force`

---

## Interactive Mode (User-Invoked)

When you complete a complex task, evaluate if a reusable pattern was discovered:

**When to learn:**
- A non-trivial task was completed successfully (3+ tool calls)
- The approach involved a pattern applicable to future tasks
- No existing skill already covers this pattern

**How to learn:**
1. Call `memory_learn_skill(name, trigger_condition, approach, tools_used, category)`
2. The skill is stored in L2 (memory.db) AND synced to knowledge/ on next evolve cycle
3. Tell the user what was learned

**When to use learned skills:**
- Before starting a task, call `memory_list_skills()` to check for relevant patterns
- If a matching skill exists, follow its approach
- If you improved the approach, call `memory_improve_skill()` to update it

---

## Skill Effectiveness Tracking

- Each use: +2% effectiveness
- Each improvement: +10% effectiveness (cap 3.0x)
- Skills with effectiveness > 2.0 are proven patterns — trust them
- Skills unused for 90+ days: flagged as potentially stale

---

## Building vs Evolving

| | Building (Spec) | Evolving |
|---|---|---|
| **What** | Execute TODO items, write code | Review completed work, extract patterns |
| **Scope** | One workspace | All workspaces |
| **Who** | One machine, full speed | Every machine, independently |
| **Output** | Code, features, commits | Knowledge, skills, insights |
| **Trigger** | `/spec:blitz` (manual) | Cron (every 2 hours) |
| **Sync** | Workspace repo push | Hub knowledge/ push |
| **Gate** | .blitz-active blocks evolve | Evolve respects blitz |

---

## How Learnings Flow Across Machines

```
Machine A completes task → evolve-tick extracts pattern
  → memory_learn_skill() saves to local DB
  → evolve-tick pushes to knowledge/ in Hub
  → sync-all on Machine B pulls Hub
  → Machine B's Claude reads knowledge/ next session
  → Pattern available everywhere
```

No shared database needed. Git IS the sync protocol.
