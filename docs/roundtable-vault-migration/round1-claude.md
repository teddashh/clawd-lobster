# Round 1 — Claude (Opus 4.6): CIO/Architect Position

## Executive Summary

The current 9-table Vault schema is **70% there** but needs targeted expansions to serve as Ted's permanent deep brain. I propose adding 3 new tables and modifying 2 existing ones — a total of 12 vault tables. The principle: **everything is a document, entity, or fact — but not everything is the same KIND of document.**

---

## Q1: Schema Completeness — Can 9 Tables Absorb Everything?

**Position: Mostly yes, with 3 additions.**

The document/entity/fact/relation model is powerful enough for most data types. Here's my mapping:

| Source Data | Target | How |
|-------------|--------|-----|
| 86K emails (AUDIT_LOG) | `vault_documents` (doc_type='email') | Direct migration, metadata_json carries WHAT/WHY/HOW |
| Daily reports (DAILY_REPORTS) | `vault_documents` (doc_type='daily_report') | Narrative → content, stats → metadata_json |
| Knowledge items | `vault_documents` (doc_type='note') | Already done (149 migrated) |
| SOPs | `vault_documents` (doc_type='sop') | Content + steps in metadata_json |
| Decisions | `vault_facts` | A decision IS an atomic claim with provenance |
| Open questions | **NEW: `vault_questions`** | Active items need state management, not just storage |
| Contacts | `vault_entities` (entity_type='person') | With all contact fields in metadata_json |
| Workspaces | `vault_sources` (source_type='workspace') | Workspace = a source of data |
| Personality traits | `vault_facts` (extraction_method='behavioral_observation') | Traits are claims about Ted |
| Action logs | **NEW: `vault_audit_trail`** | Operational logs need a dedicated fast-write table |
| Activity logs | `vault_audit_trail` | Same table, different log_type |

### Tables that DON'T fit in vault_documents

**Action/Audit logs** are fundamentally different from documents:
- They're high-volume, append-only, time-series data
- They don't need chunking, embedding, or entity extraction
- They need fast writes and time-range queries
- Mixing them into vault_documents would pollute search results

**Open questions** have active state (open/resolved/deferred) that documents don't.

### Proposed New Tables

```sql
-- 10. AUDIT TRAIL — operational event log (high-volume, append-only)
CREATE TABLE vault_audit_trail (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    trail_type      VARCHAR2(50) NOT NULL,   -- agent_action, system_event, user_action, cron_job
    workspace_id    VARCHAR2(64),
    agent           VARCHAR2(50),            -- which agent did this
    action          VARCHAR2(100) NOT NULL,  -- TASK_START, HEALTH_CHECK, EMAIL_SEND, etc.
    target          VARCHAR2(500),
    result          VARCHAR2(20),            -- ok, error, skipped, timeout
    detail_json     CLOB CHECK (detail_json IS JSON),
    tokens_in       NUMBER,
    tokens_out      NUMBER,
    occurred_at     TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    
    -- Partition-friendly: year/month for fast time-range queries
    year            NUMBER GENERATED ALWAYS AS (EXTRACT(YEAR FROM occurred_at)) VIRTUAL,
    month           NUMBER GENERATED ALWAYS AS (EXTRACT(MONTH FROM occurred_at)) VIRTUAL
);

-- 11. QUESTIONS — active items needing resolution
CREATE TABLE vault_questions (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    question        VARCHAR2(4000) NOT NULL,
    context         CLOB,
    priority        NUMBER(1) DEFAULT 3,     -- 1=critical, 5=someday
    status          VARCHAR2(20) DEFAULT 'open',  -- open, investigating, resolved, deferred
    raised_by       VARCHAR2(64),            -- agent or 'human'
    raised_at       TIMESTAMP DEFAULT SYSTIMESTAMP,
    resolved_at     TIMESTAMP,
    resolution      CLOB,
    related_doc_id  NUMBER REFERENCES vault_documents(id),
    tags_json       CLOB CHECK (tags_json IS JSON),
    
    CONSTRAINT chk_q_status CHECK (status IN ('open','investigating','resolved','deferred'))
);

-- 12. METRICS — quantified tracking over time
CREATE TABLE vault_metrics (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    metric_name     VARCHAR2(200) NOT NULL,  -- email_count, response_time_avg, meetings_per_week, etc.
    metric_value    NUMBER NOT NULL,
    unit            VARCHAR2(50),            -- count, minutes, percentage, tokens
    dimension_json  CLOB CHECK (dimension_json IS JSON),
    -- Example: {"workspace":"email-triage","direction":"in","importance":"H"}
    period_start    TIMESTAMP NOT NULL,
    period_end      TIMESTAMP NOT NULL,
    source_type     VARCHAR2(50),            -- computed, observed, imported
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP
);
```

## Q2: Data Separation

**Position: Use a multi-axis classification, not just privacy_level.**

Current `privacy_level` (public/internal/restricted/secret) is a single axis. Ted needs at least 3:

1. **Ownership axis** (`ownership`): `self` / `work` / `external` / `shared`
   - self = Ted's personal stuff
   - work = FPC corporate
   - external = from outside parties
   - shared = family, friends

2. **Domain axis** (already `taxonomy_id`): work/personal/creative/ops — the existing taxonomy tree handles this well.

3. **Privacy axis** (existing `privacy_level`): public/internal/restricted/secret — keep as-is.

**Proposed change to vault_documents:**
```sql
ALTER TABLE vault_documents ADD (
    ownership       VARCHAR2(20) DEFAULT 'self',
    CONSTRAINT chk_ownership CHECK (ownership IN ('self','work','external','shared'))
);
```

This means an email from Ted's boss at FPC gets: `ownership='work'`, `privacy_level='internal'`, `taxonomy_id=(work/emails)`. A personal health record gets: `ownership='self'`, `privacy_level='secret'`, `taxonomy_id=(personal/health)`.

## Q3: The Suspicious Flag

**Position: Replace the flag with a proper trust/threat assessment in vault_facts.**

A binary `IS_SUSPICIOUS` is lazy. Instead:

- When migrating emails, suspicious emails get a `vault_fact` with:
  - `claim`: "This email may be a phishing attempt: [reason]"
  - `confidence`: 0.0-1.0 (how sure the LLM was)
  - `source_agent`: 'email_triage_llm'
  - `extraction_method`: 'security_analysis'
  - `lifecycle`: 'extracted' (not yet verified)

- Create a **relation**: `(entity:sender) --[flagged_suspicious]--> (document:email)` in vault_relations

- This is MUCH more responsible because:
  - It's a claim with confidence, not a binary flag
  - It can be verified/accepted/retracted via lifecycle
  - The reason is preserved as provenance
  - Multiple agents can add their own assessments

## Q4: Daily Work Logs

**Position: Daily reports → vault_documents. Action logs → vault_audit_trail.**

- `DAILY_REPORTS` (1,865 narrative summaries) → `vault_documents (doc_type='daily_report')`
  - The narrative goes in `content`
  - Stats (email_count, inbox/sent/calendar counts, H/M/L counts) → `metadata_json`
  - Top senders, calendar events, H subjects → also `metadata_json`
  - These are **searchable documents** — "what happened on March 26, 2024?" should find the cybersecurity incident narrative

- `ACTIVITY_LOG` + `ACTION_LOG` (3,051 rows) → `vault_audit_trail`
  - These are **operational telemetry**, not knowledge
  - Fast time-range queries, not semantic search
  - No embedding needed

## Q5: Audit Trail Architecture

**Position: Three-tier approach.**

| Tier | Table | Purpose | Retention |
|------|-------|---------|-----------|
| **Operational** | `vault_audit_trail` | Real-time agent actions, system events | 1 year hot, archive after |
| **Knowledge** | `vault_documents` (daily_report) | Synthesized daily narratives | Forever |
| **Metrics** | `vault_metrics` | Quantified aggregates | Forever |

The flow: Agents write to `vault_audit_trail` in real-time → Nightly cron synthesizes into a `daily_report` document → Weekly cron computes `vault_metrics` aggregates.

This gives Ted:
- "What did the agents do today?" → query audit_trail
- "What happened this week?" → search daily_report documents
- "How many emails did I get per month in 2023?" → query metrics

## Q6: Schema Location

**Position: ONE schema. Consolidate everything into OPENCLAW_APP.**

Reasons:
- Single owner system — no multi-tenancy need
- Simpler queries (no cross-schema joins needed)
- One connection string, one pool
- CLAUDE_MEMORY was a historical artifact from before the Vault existed

Migration path:
1. Deploy new tables in OPENCLAW_APP
2. Migrate all CLAUDE_MEMORY data into vault_* tables
3. Keep CLAUDE_MEMORY read-only for 30 days
4. Verify, then drop CLAUDE_MEMORY tables (keep user for backward compat)

## Q7: Deep Brain Principle

**Position: The Vault should be an evidence graph, not a document dump.**

Key architectural principle: **Every piece of data should eventually be connected to entities and facts.**

- Raw email comes in → it's a `vault_document`
- Entity extraction → creates/updates `vault_entities` (Josh Huang, Alex Chuang, FPC Management Center)
- Fact extraction → creates `vault_facts` ("Josh requested Jimmy to provide link to Peter", "Customer PO automation project exists")
- Relations → connects entities to documents to facts

This means an agent can ask:
- "Tell me about Josh Huang" → entity profile with all related emails, facts, relations
- "What decisions were made about the PO automation project?" → facts linked to that entity
- "Who did I interact with most in Q3 2023?" → metrics from relation counts

The 86K emails are the RAW MATERIAL. The real value is in the extracted entities, facts, and relations.

## Q8: What's Missing?

**Position: Add vault_metrics (proposed above), consider vault_tags.**

What the current schema lacks:
1. **Quantified tracking** (`vault_metrics`) — see Q5
2. **Tag/label system** — the taxonomy tree is hierarchical (good for categories), but tags are flat and many-to-many. Consider a `vault_tags` table or use `tags_json` CLOB on vault_documents.
3. **PERSONALITY_TRAITS** → I recommend absorbing into vault_facts. A trait IS a fact: "Ted prefers concise communication" (confidence: 0.92, observed_count: 47).
4. **CROSS_REFERENCES** → Already covered by vault_relations. That's exactly what relations are.
5. **Calendar events** → Currently embedded in DAILY_REPORTS as JSON. Should become vault_documents (doc_type='calendar_event') with occurred_at as the event time.

---

## Summary of Proposed Changes

| Action | Detail |
|--------|--------|
| **ADD** vault_audit_trail | High-volume operational log |
| **ADD** vault_questions | Active items with state |
| **ADD** vault_metrics | Quantified aggregates |
| **ADD** `ownership` column to vault_documents | self/work/external/shared axis |
| **KEEP** existing 9 vault tables | No structural changes needed |
| **MIGRATE** all CLAUDE_MEMORY data | Into vault_* tables |
| **CONSOLIDATE** into OPENCLAW_APP | Single schema |

**Final table count: 12 vault tables**

## Confidence Score: 0.82

### Top 3 Concerns

1. **86K email migration performance** — Inserting 86K documents with metadata JSON could take 10-30 minutes. Need batch commits and progress tracking.
2. **Entity extraction at scale** — Full enrichment (NER + fact extraction) on 86K emails would take weeks of LLM time. Need a practical phased approach.
3. **Taxonomy merging** — Two schemas have taxonomy tables (both 37 rows). Need to verify they're identical before consolidating, and all taxonomy_ids remain valid after migration.
