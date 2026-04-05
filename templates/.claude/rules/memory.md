# Memory System Rules

<important if="reading or writing to memory, knowledge base, or learned skills">

## 4-Layer Memory Architecture

**L1.5 — CC Auto-Memory (native)**
- Claude Code's built-in memory — no custom handling needed

**L2 — Structured Memory (SQLite + MCP)**
- Per-workspace `memory.db` with salience tracking
- Use MCP tools to read/write — never touch .db directly
- Salience: access +5%, reinforce +20%, 30-day decay -5%/day
- All records tagged with `machine_id` for multi-machine traceability

**L3 — Knowledge Base (Markdown + Git)**
- Read INDEX.md first, then specific topic files
- Don't read multiple unrelated files at once

**L4 — Cloud (optional)**
- Cross-workspace search via `memory_search`
- Falls back to local text search across ALL tables

## Learnings vs Skills

- **Learnings** record *mistakes to avoid* — use `memory_store(content, type="learning")`
- **Skills** record *patterns to follow* — use `memory_learn_skill()`
- Don't confuse them — learnings are defensive, skills are offensive

</important>
