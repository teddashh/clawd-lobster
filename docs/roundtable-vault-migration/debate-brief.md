# Vault Schema Migration Debate — Full Deep Brain Architecture

## Context

Ted wants Oracle L3 (The Vault) to be his **permanent deep brain** — store EVERYTHING from his entire professional and personal life, searchable and well-organized. Currently there are TWO Oracle schemas:

### Schema 1: `OPENCLAW_APP` (operational)
| Table | Rows | Purpose |
|-------|------|---------|
| KNOWLEDGE | 152 | Knowledge articles (already migrated to vault_documents) |
| HISTORY | 90 | Agent execution history |
| ACTION_LOG | 1696 | OpenClaw action logs |
| CONTACTS | 5 | Contact info |
| SOP | 11 | Standard operating procedures |
| TAXONOMY | 37 | Classification tree |
| CHANNELS | 7 | Communication channels |
| PENDING_ITEMS | 13 | Pending approval items |
| TASKS | 0 | Task queue (empty) |
| + 9 vault_* tables | ~150 | New Vault schema (already deployed) |

### Schema 2: `CLAUDE_MEMORY` (deep memory)
| Table | Rows | Purpose |
|-------|------|---------|
| AUDIT_LOG | 86,420 | **Every email** — from/to/subject/snippet + LLM-extracted WHAT/WHY/HOW/people/keywords/importance/action_items/decisions |
| DAILY_REPORTS | 1,865 | Daily work narrative with stats (email count, top senders, calendar events, suspicious count) |
| ACTIVITY_LOG | 1,355 | Agent activity (patrol, health checks, stale warnings) |
| KNOWLEDGE_ITEMS | 252 | Knowledge with embeddings + salience scores |
| AUDIT_PROGRESS | 313 | Email import progress tracking |
| SYNC_LOG | 2,784 | Sync operation logs |
| CONTACTS | 5 | Same 5 contacts |
| WORKSPACES | 12 | Workspace definitions (email-triage, openclaw, annual goals, etc.) |
| TAXONOMY | 37 | Same classification tree |
| CHANNELS | 7 | Communication channels |
| DAILY_LOGS | 7 | High-level daily summaries |
| SOP | 11 | Same SOPs |
| DECISIONS | 4 | Architectural decisions with 3W1H |
| OPEN_QUESTIONS | 13 | Unresolved questions with priority |
| PERSONALITY_TRAITS | 0 | Empty — planned for Ted's behavioral patterns |
| CROSS_REFERENCES | 0 | Empty — planned for cross-table links |
| RESOLVED | 0 | Empty — resolved items |
| SYNC_WATERMARK | 1 | Sync state |

### Current Vault Schema (9 tables in OPENCLAW_APP)
1. vault_sources — data origin tracking
2. vault_documents — raw artifacts (emails, notes, files)
3. vault_chunks — content split for RAG
4. vault_entities — people, companies, projects, concepts
5. vault_entity_aliases — name variants for resolution
6. vault_facts — extracted atomic claims with provenance
7. vault_relations — typed edges between objects
8. vault_events — immutable lifecycle log
9. vault_sync_log — L1/L2→L3 sync tracking

## Questions for Debate

### Q1: Schema Completeness
The current 9-table vault schema was designed for document-centric storage. Can it absorb ALL data types from both schemas?
- 86K emails → vault_documents (doc_type='email')? Or do emails need special treatment?
- Daily reports → vault_documents or a separate reporting table?
- Action logs → vault_events? Or separate?
- Contacts → vault_entities (entity_type='person')?
- Decisions → vault_facts?
- SOPs → vault_documents (doc_type='sop')?
- Open questions → ?
- Personality traits → vault_facts (claim-based)?
- Workspaces → metadata? Or vault_sources?

### Q2: Data Separation (Ted's biggest concern)
Ted wants clear separation of:
- **My stuff vs. others' stuff** — Ted's emails vs. general knowledge
- **Work vs. personal** — FPC/corporate vs. personal life
- **Internal vs. external** — trusted internal data vs. external web/imports
- **Different time periods** — how to handle 5+ years of temporal data

Current `privacy_level` (public/internal/restricted/secret) may not be enough.

### Q3: The Suspicious Flag Problem
AUDIT_LOG has `IS_SUSPICIOUS` + `SUSPICIOUS_REASON` for phishing detection. Ted says "just putting suspicious there seems irresponsible." How should security/trust metadata be handled in the Vault?

### Q4: Daily Work Log / Action Log
Ted's tradition of daily work logs (from OpenClaw era). Where do these go?
- DAILY_REPORTS has 1,865 narrative summaries
- ACTIVITY_LOG has 1,355 agent actions
- ACTION_LOG (OPENCLAW_APP) has 1,696 agent actions
- These are audit trails, not knowledge per se

### Q5: Audit Trail Architecture
Ted wants:
- Daily action log (what happened today)
- Audit trail (who did what, when, why)
- Quantified memory (measurable tracking over time)

How should this coexist with the document/entity/fact model?

### Q6: Schema Location
Should everything be in ONE schema (OPENCLAW_APP) or keep two schemas? If one, which user owns it?

### Q7: The "Deep Brain" Principle
Goal: Store everything, forever, organized, searchable, quantifiable.
- Must handle: emails, documents, meeting notes, personal memories, code artifacts, web pages, images metadata, financial records, health records, relationship history
- Must support: temporal queries, entity resolution, fact verification, pattern detection, sentiment tracking
- Must scale: from 86K rows today to potentially millions

### Q8: What's Missing?
Looking at PERSONALITY_TRAITS (empty) and CROSS_REFERENCES (empty) — were these good ideas that just weren't implemented? Should the Vault absorb these concepts? What other tables might be needed?

## Data Samples

### Email (AUDIT_LOG)
```
TS: 2021-08-16 21:23
FROM: Josh Huang/FPC Management Center <jhuang@fpcusa.com>
TO: Alex Chuang, Jimmy Lien
SUBJECT: Re: Customer PO to Order Entry Automation - follow-up meeting
IMPORTANCE: M
WHAT: Re: Customer PO to Order Entry Automation - follow-up meeting
PEOPLE: ["Josh Huang/FPC Management Center"]
KEYWORDS: ["Customer", "Order", "Entry", "Automation", "follow-up"]
SNIPPET: Thanks, Alex. Jimmy, please provide the link to Peter...
```

### Daily Report (DAILY_REPORTS)
```
DATE: 2024-03-26 (Tuesday)
EMAIL_COUNT: 138
H_COUNT: high-importance count
NARRATIVE: 資安事件 Day 5，全公司 WFH。三路外部協調：Trifident、CISA Hunt、Dentons 法律顧問。
```

### Contact
```
NAME: Ted Huang | NICKNAME: Ted | EMAIL: ted@ted-h.com | RELATIONSHIP: owner | IDENTITY: owner
```

## Constraints
- Oracle Autonomous Database (cloud, always-free tier)
- VECTOR(1536, FLOAT32) support available
- Single owner (Ted) — no multi-tenancy needed
- Must be queryable by agents (Claude, Codex, Gemini, QWEN)
- Migration must be reversible (old data kept until verified)
- Performance matters for 86K+ email searches
