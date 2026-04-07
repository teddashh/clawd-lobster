# Memory Architecture v2 — The Thin Ledger Pattern

Synthesized from 5-round spiral roundtable (Claude + Codex GPT-5.4 + Gemini 3).
Incorporating concepts from: MemPalace (spatial structure + AAAK), Karpathy LLM Wiki (INGEST/QUERY/LINT).

## Core Principle

Two layers. Three operations. No external dependencies.

```
L1  SQLite (The Ledger) — structured operational state
L2  Git Wiki (The Library) — compiled human-readable synthesis
```

Search: ripgrep on markdown. Sync: Git. No ChromaDB. No vector DB. No cloud required.

## L1: SQLite (The Ledger)

What it owns:
- decisions, todos, audit_log, action_log (existing)
- learned_skills with salience (existing)
- **claim_challenge** records (NEW — correction workflow)
- **provenance** fields on all records (NEW — source refs, agent, timestamp, confidence)

Lifecycle states for knowledge: `raw → extracted → synthesized → accepted → superseded`

## L2: Git Wiki (The Library)

Spatial structure absorbed from MemPalace concept (no dependency):

```
knowledge/
├── index.md              ← catalog of all wiki pages (Karpathy)
├── log.md                ← append-only journal (Karpathy)
├── raw/                  ← immutable source materials
├── wiki/
│   ├── architecture/     ← "Wing" — system design decisions
│   ├── conventions/      ← "Wing" — coding standards, patterns
│   ├── decisions/        ← "Wing" — why we chose X over Y
│   ├── learnings/        ← "Wing" — mistakes and lessons
│   └── skills/           ← "Wing" — reusable patterns
└── .pending/             ← proposed corrections awaiting review
```

Each wiki page carries provenance:
```markdown
---
source: evolve-tick / absorb / query-feedback
agent: claude / codex / gemini
created: 2026-04-07
confidence: 0.85
upstream_ids: [L1:decision:abc123]
---
```

## Three Operations

### INGEST (absorb skill + shadow-write)
1. Raw source lands in `knowledge/raw/`
2. LLM summarizes → creates/updates wiki pages
3. L1 stores metadata, decisions, salience
4. High-salience L1 writes shadow-write to L2 immediately (not just cron)

### QUERY (memory_search + feedback loop)
1. ripgrep L2 wiki + SQLite L1 structured query
2. Synthesize answer with citations (`Ref: knowledge/wiki/decisions/auth-choice.md`)
3. **IF answer is durable + reusable → write back to L2 as new wiki page** (Karpathy)
4. IF answer reveals gap → create `claim_challenge` in L1

### LINT (evolve-tick Phase 4 — NEW)
1. Broken wiki links (pages reference non-existent pages)
2. Contradictions (two pages say opposite things)
3. Stale claims (not accessed in 90+ days, salience < 0.3)
4. Orphan pages (not linked from index.md)
5. DB/wiki drift (L1 decisions not reflected in L2)

## Correction Workflow (claim_challenge)

Agents cannot directly edit wiki. They propose corrections:

1. Agent calls `memory_propose_correction(page, issue, evidence, proposed_fix)`
2. Creates `knowledge/.pending/<page>-<timestamp>.md` with diff
3. Lead agent (Claude) or human reviews
4. Accept → update wiki page, mark old content as `superseded`
5. Reject → close with reason, keep wiki unchanged

## Role-Based Context Packs

sync-knowledge.py generates different briefings per agent role:

| Role | Gets | Doesn't Get |
|------|------|-------------|
| **Lead (Claude)** | Full L1 + L2 index + recent decisions | — |
| **Worker (Codex)** | Task brief + relevant wiki pages + TODOs | History, disputes |
| **Consultant (Gemini)** | L2 wiki + open disputes + assumptions | Implementation TODOs |

## What We Absorbed (not installed)

| Source | Concept Absorbed | How We Use It |
|--------|-----------------|---------------|
| MemPalace | Wing/Room spatial structure | knowledge/wiki/ subdirectories |
| MemPalace | AAAK compression idea | Future: compressed briefings for agents |
| MemPalace | Closet → Drawer (summary → verbatim) | wiki page = closet, raw/ = drawer |
| Karpathy | INGEST / QUERY / LINT operations | Three explicit lifecycle operations |
| Karpathy | index.md + log.md | knowledge/index.md + log.md |
| Karpathy | Query feeds back into wiki | Durable answers become wiki pages |
| Karpathy | Provenance + citations | Frontmatter on every wiki page |
| Roundtable | claim_challenge | Correction workflow, no direct wiki edits |
| Roundtable | Role-based context packs | sync-knowledge.py per-role output |
| Roundtable | Thin Ledger (SQLite + Wiki, no vector DB) | Core architecture: 2 layers not 4 |
