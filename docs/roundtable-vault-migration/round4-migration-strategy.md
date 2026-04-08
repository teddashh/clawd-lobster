# Round 4 — Migration Strategy & Implementation Details

## Consensus Schema: 11 Tables

```
vault_sources          — where data came from
vault_documents        — ALL documents (emails, notes, SOPs, daily reports, calendar events)
vault_chunks           — content splits for RAG
vault_entities         — people, companies, projects, concepts
vault_entity_aliases   — name variants
vault_facts            — claims, decisions, questions, traits, security assessments
vault_relations        — graph edges
vault_events           — lifecycle log
vault_sync_log         — migration tracking
vault_audit_trail      — operational telemetry (NEW)
vault_metrics          — quantified aggregates (NEW)
```

## Schema Modifications (DDL)

### 1. New columns on vault_documents
```sql
ALTER TABLE vault_documents ADD (
    ownership         VARCHAR2(20) DEFAULT 'self',
    email_from        VARCHAR2(500),
    email_importance  CHAR(1),
    email_direction   VARCHAR2(10),
    threat_score      NUMBER(3,2) DEFAULT 0,
    CONSTRAINT chk_doc_ownership CHECK (ownership IN ('self','work','external','shared'))
);
```

### 2. New column on vault_entities
```sql
ALTER TABLE vault_entities ADD (
    ownership         VARCHAR2(20) DEFAULT 'external',
    CONSTRAINT chk_ent_ownership CHECK (ownership IN ('self','work','external','shared'))
);
```

### 3. New column on vault_facts
```sql
ALTER TABLE vault_facts ADD (
    fact_type         VARCHAR2(30) DEFAULT 'claim',
    CONSTRAINT chk_fact_type CHECK (fact_type IN ('claim','question','decision','trait','observation','security_assessment'))
);
```

### 4. New table: vault_audit_trail
```sql
CREATE TABLE vault_audit_trail (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    trail_type      VARCHAR2(50) NOT NULL,
    workspace_id    VARCHAR2(64),
    agent           VARCHAR2(50),
    action          VARCHAR2(100) NOT NULL,
    target          VARCHAR2(500),
    result          VARCHAR2(20),
    detail_json     CLOB CHECK (detail_json IS JSON),
    tokens_in       NUMBER,
    tokens_out      NUMBER,
    occurred_at     TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE INDEX idx_vaudit_time ON vault_audit_trail(occurred_at);
CREATE INDEX idx_vaudit_agent ON vault_audit_trail(agent);
CREATE INDEX idx_vaudit_action ON vault_audit_trail(action);
CREATE INDEX idx_vaudit_type ON vault_audit_trail(trail_type);
```

### 5. New table: vault_metrics
```sql
CREATE TABLE vault_metrics (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    metric_name     VARCHAR2(200) NOT NULL,
    metric_value    NUMBER NOT NULL,
    unit            VARCHAR2(50),
    dimension_json  CLOB CHECK (dimension_json IS JSON),
    period_start    TIMESTAMP NOT NULL,
    period_end      TIMESTAMP NOT NULL,
    source_type     VARCHAR2(50),
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE INDEX idx_vmetric_name ON vault_metrics(metric_name);
CREATE INDEX idx_vmetric_period ON vault_metrics(period_start, period_end);
```

### 6. JSON functional indexes for email queries
```sql
CREATE INDEX idx_vdoc_email_from ON vault_documents (email_from)
    WHERE email_from IS NOT NULL;
CREATE INDEX idx_vdoc_email_imp ON vault_documents (email_importance)
    WHERE email_importance IS NOT NULL;
CREATE INDEX idx_vdoc_email_dir ON vault_documents (email_direction)
    WHERE email_direction IS NOT NULL;
CREATE INDEX idx_vdoc_ownership ON vault_documents (ownership);
CREATE INDEX idx_vdoc_threat ON vault_documents (threat_score)
    WHERE threat_score > 0;
```

---

## Migration Plan (10 Phases)

### Pre-flight
- Verify taxonomy tables match between schemas
- Backup both schemas
- Create migration tracking in vault_sync_log

### Phase 1: Schema Evolution
- Apply ALTERs (ownership, email_from, etc.)
- Create vault_audit_trail + vault_metrics
- Add indexes

### Phase 2: Contacts → vault_entities
Source: CLAUDE_MEMORY.CONTACTS (5 rows) + OPENCLAW_APP.CONTACTS (5 rows, likely same)
```
Ted Huang → vault_entities (entity_type='person', ownership='self')
  aliases: Ted, Ted Huang, Ted Theodore J Huang
  metadata_json: {email, phone, relationship, identity_level}
Annis → vault_entities (entity_type='person', ownership='shared')
  aliases: Annis
David → vault_entities (entity_type='person', ownership='shared')
...
```

### Phase 3: Workspaces → vault_sources
Source: CLAUDE_MEMORY.WORKSPACES (12 rows)
```
email-triage → vault_sources (source_type='workspace', display_name='Email Triage')
openclaw → vault_sources (source_type='workspace', display_name='OpenClaw')
...
```

### Phase 4: Emails → vault_documents (THE BIG ONE)
Source: CLAUDE_MEMORY.AUDIT_LOG (86,420 rows)
```
For each email:
  1. Get or create source (workspace_id → vault_sources)
  2. Insert vault_documents:
     - doc_type = 'email'
     - title = subject
     - content = snippet (or log_line)
     - occurred_at = parse(ts)
     - metadata_json = {from_name, from_addr, to_addrs, category, what, why, how, people, keywords, action_items, decisions, source_file, folder}
     - email_from = from_addr
     - email_importance = importance
     - email_direction = direction
     - ownership = 'work'
     - privacy_level = 'internal'
     - threat_score = IS_SUSPICIOUS ? 0.7 : 0.0
     - lifecycle = 'accepted'
  3. If IS_SUSPICIOUS:
     - Create vault_fact: fact_type='security_assessment', claim=SUSPICIOUS_REASON
  4. Log in vault_sync_log
  
  Batch: 500 rows per commit, progress every 5000
```

### Phase 5: Daily Reports → vault_documents
Source: CLAUDE_MEMORY.DAILY_REPORTS (1,865 rows)
```
For each report:
  - doc_type = 'daily_report'
  - title = "Daily Report — {report_date}"
  - content = narrative
  - occurred_at = report_date
  - metadata_json = {email_count, inbox_count, sent_count, calendar_count, H/M/L counts, top_senders, calendar_events, key_subjects, day_of_week}
  - ownership = 'work'
  - lifecycle = 'accepted'
```

### Phase 6: Knowledge Items → vault_documents
Source: CLAUDE_MEMORY.KNOWLEDGE_ITEMS (252 rows)
```
Already partially covered (OPENCLAW_APP.KNOWLEDGE 152 rows migrated).
Additional 100 from CLAUDE_MEMORY need migration.
Check for duplicates by content_hash.
Preserve embeddings if present.
```

### Phase 7: SOPs → vault_documents
Source: CLAUDE_MEMORY.SOP (11 rows) + OPENCLAW_APP.SOP (11 rows, likely same)
```
For each SOP:
  - doc_type = 'sop'
  - title = title
  - content = steps
  - metadata_json = {sop_code, category, iso_mapping, nist_mapping}
  - ownership = 'work'
  - lifecycle = 'accepted'
```

### Phase 8: Decisions + Open Questions → vault_facts
Source: CLAUDE_MEMORY.DECISIONS (4) + OPEN_QUESTIONS (13)
```
Decisions:
  - fact_type = 'decision'
  - claim = what
  - metadata: {why, how, who, where_file, tags}
  - lifecycle = 'accepted'
  
Open Questions:
  - fact_type = 'question'
  - claim = question
  - metadata: {context, tags, priority}
  - lifecycle = 'open'
```

### Phase 9: Action/Activity Logs → vault_audit_trail
Source: CLAUDE_MEMORY.ACTIVITY_LOG (1,355) + OPENCLAW_APP.ACTION_LOG (1,696)
```
For each log:
  - trail_type = log_type or 'agent_action'
  - agent = agent
  - action = action
  - target = target
  - result = result_status
  - detail_json = {input_summary, output_summary, task_type}
  - tokens_in, tokens_out
  - occurred_at = logged_at
```

### Phase 10: Entity Extraction from Emails
Post-migration enrichment (can be background/async):
```
1. Extract unique senders: SELECT DISTINCT from_name, from_addr FROM vault_documents WHERE doc_type='email'
   → Create vault_entities for each unique person/org
   → Create vault_entity_aliases for name variants
   
2. Create vault_relations: (entity) --[sent_email]--> (document)
   
3. Extract unique recipients similarly
   
4. Compute vault_metrics: emails per month, top senders by quarter, etc.
```

---

## Migration Verification Checklist

After each phase:
- [ ] Row count matches source
- [ ] Content hash spot-check (10 random rows)
- [ ] vault_sync_log entries match
- [ ] Rollback tested

After all phases:
- [ ] Total vault_documents count = 152 (knowledge) + 86,420 (emails) + 1,865 (reports) + ~100 (additional knowledge) + 11 (SOPs) + calendar events
- [ ] Total vault_entities includes all contacts + email senders
- [ ] Total vault_facts includes decisions + questions + security flags
- [ ] Total vault_audit_trail = 1,355 + 1,696 = ~3,051
- [ ] Search works: "Josh Huang" returns emails, entity, relations
- [ ] Search works: "cybersecurity incident 2024" returns emails + daily report
- [ ] Time range works: emails from Q3 2023

---

## Post-Migration Cleanup

1. Keep CLAUDE_MEMORY read-only for 30 days
2. Keep OPENCLAW_APP legacy tables (knowledge, history, action_log, contacts, sop) read-only for 30 days
3. After verification period: DROP legacy tables
4. After 60 days: DROP CLAUDE_MEMORY user (optional)

## Consensus Scores

| Agent | Score | Key Win |
|-------|-------|---------|
| Claude | 0.88 | vault_documents for everything (generalized), vault_questions withdrawn |
| Codex | 0.85 | Email promoted fields accepted, forced performance discussion |
| Gemini | 0.90 | Minimal table count, JSON index strategy validated |
