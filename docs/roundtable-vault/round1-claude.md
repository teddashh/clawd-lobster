# Round 1 — Claude (CIO) Proposal: The Vault Schema

## Philosophy

The Vault is not a knowledge base — it's a **memory palace with a nervous system**. 
It must answer: "What do I know about X?" across any dimension (time, person, project, topic).

The core insight: **documents are evidence, facts are beliefs, entities are anchors.**
A document (email, note, file) is immutable evidence. A fact is a belief extracted from one or more documents — it can be wrong, it can be superseded. An entity (person, company, project) is a stable anchor that connects documents and facts across time.

## 1. Schema Design

### Core Tables (6)

```sql
-- The raw materials: emails, files, notes, conversations, anything
CREATE TABLE vault_documents (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    doc_type        VARCHAR2(50)  NOT NULL,  -- email, note, file, conversation, webpage, code
    title           VARCHAR2(1000) NOT NULL,
    content         CLOB,
    content_hash    VARCHAR2(64),            -- SHA-256 for dedup
    
    -- Source metadata (type-specific, JSON)
    source_meta     CLOB,  -- {"from":"user@example.com","to":["david@..."],"thread_id":"...","date_sent":"2023-06-15"}
    source_path     VARCHAR2(1000),          -- original file path or URL
    source_system   VARCHAR2(100),           -- "outlook", "obsidian", "claude-session", "web"
    
    -- Temporal
    occurred_at     TIMESTAMP NOT NULL,      -- when the CONTENT happened (email sent date, meeting date)
    ingested_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- when we ate it
    
    -- Classification
    taxonomy_id     NUMBER REFERENCES taxonomy(id),
    privacy_level   VARCHAR2(20) DEFAULT 'internal',  -- public, internal, restricted, secret
    language        VARCHAR2(10) DEFAULT 'en',
    
    -- Vector
    embedding       VECTOR(1536, FLOAT32),
    
    -- Lifecycle
    lifecycle       VARCHAR2(20) DEFAULT 'raw',  -- raw, processed, archived
    
    CONSTRAINT chk_doc_type CHECK (doc_type IN ('email','note','file','conversation','webpage','code','image','receipt','document'))
);

-- Extracted entities: people, companies, projects, concepts, locations
CREATE TABLE vault_entities (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_type     VARCHAR2(50) NOT NULL,   -- person, company, project, concept, location, product
    canonical_name  VARCHAR2(500) NOT NULL,  -- "David Chen" (not "david" or "David C.")
    aliases         CLOB,                    -- JSON: ["david","David C.","陳大衛"]
    attributes      CLOB,                    -- JSON: {"role":"CTO","company":"Acme","phone":"+1..."}
    
    -- Optional link to contacts table (for people)
    contact_id      NUMBER REFERENCES contacts(id),
    taxonomy_id     NUMBER REFERENCES taxonomy(id),
    
    embedding       VECTOR(1536, FLOAT32),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_entity_type CHECK (entity_type IN ('person','company','project','concept','location','product','event'))
);

-- Extracted atomic facts with provenance
CREATE TABLE vault_facts (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    claim           VARCHAR2(2000) NOT NULL,  -- "David recommended Oracle for the new project"
    confidence      NUMBER(3,2) DEFAULT 0.8,  -- 0.0–1.0
    
    -- Provenance
    source_doc_id   NUMBER REFERENCES vault_documents(id),  -- primary source
    source_agent    VARCHAR2(50),             -- who extracted this (claude, codex, gemini, human)
    extraction_method VARCHAR2(50),           -- llm_extract, manual, regex, absorb
    
    -- Classification
    taxonomy_id     NUMBER REFERENCES taxonomy(id),
    
    -- Temporal
    fact_date       TIMESTAMP,               -- when the fact was true (not when extracted)
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Lifecycle
    lifecycle       VARCHAR2(20) DEFAULT 'extracted',  -- extracted, verified, accepted, superseded, retracted
    superseded_by   NUMBER REFERENCES vault_facts(id),
    
    embedding       VECTOR(1536, FLOAT32)
);

-- Relationships: entity↔entity, entity↔document, entity↔fact
CREATE TABLE vault_relations (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- Polymorphic endpoints
    subject_type    VARCHAR2(20) NOT NULL,  -- entity, document, fact
    subject_id      NUMBER NOT NULL,
    relation_type   VARCHAR2(100) NOT NULL, -- mentions, authored_by, about, replies_to, works_at, colleague_of
    object_type     VARCHAR2(20) NOT NULL,
    object_id       NUMBER NOT NULL,
    
    -- Metadata
    confidence      NUMBER(3,2) DEFAULT 1.0,
    attributes      CLOB,  -- JSON for extra context
    source_doc_id   NUMBER REFERENCES vault_documents(id),  -- which document this relation was extracted from
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_subject_type CHECK (subject_type IN ('entity','document','fact')),
    CONSTRAINT chk_object_type CHECK (object_type IN ('entity','document','fact'))
);

-- Sync ledger: tracks what L1/L2 data has been pushed to L3
CREATE TABLE vault_sync_log (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_layer    VARCHAR2(10) NOT NULL,   -- L1, L2
    source_id       VARCHAR2(200) NOT NULL,  -- SQLite row ID or wiki page path
    source_hash     VARCHAR2(64),            -- content hash at sync time
    vault_table     VARCHAR2(50) NOT NULL,   -- which vault table it landed in
    vault_id        NUMBER NOT NULL,
    synced_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_agent      VARCHAR2(50)
);
```

### Keep Existing Tables (operational, don't migrate)
- `contacts` — stays as-is, linked via `vault_entities.contact_id`
- `tasks`, `channels`, `sop` — operational dispatch, not knowledge
- `action_log`, `history` — audit trail, stays
- `taxonomy` — EXPAND it (add life categories beyond projects)

### Indexes
```sql
-- Documents
CREATE INDEX idx_vdoc_type ON vault_documents(doc_type);
CREATE INDEX idx_vdoc_occurred ON vault_documents(occurred_at);
CREATE INDEX idx_vdoc_taxonomy ON vault_documents(taxonomy_id);
CREATE INDEX idx_vdoc_source ON vault_documents(source_system);
CREATE INDEX idx_vdoc_hash ON vault_documents(content_hash);

-- Entities
CREATE INDEX idx_ventity_type ON vault_entities(entity_type);
CREATE INDEX idx_ventity_name ON vault_entities(canonical_name);
CREATE INDEX idx_ventity_contact ON vault_entities(contact_id);

-- Facts
CREATE INDEX idx_vfact_source ON vault_facts(source_doc_id);
CREATE INDEX idx_vfact_lifecycle ON vault_facts(lifecycle);
CREATE INDEX idx_vfact_date ON vault_facts(fact_date);

-- Relations (critical for graph queries)
CREATE INDEX idx_vrel_subject ON vault_relations(subject_type, subject_id);
CREATE INDEX idx_vrel_object ON vault_relations(object_type, object_id);
CREATE INDEX idx_vrel_type ON vault_relations(relation_type);
```

## 2. Absorb Skill Integration

Current absorb flow: `file → L1 SQLite + L2 Wiki`

New flow with Vault:
```
file → absorb skill
  ├── L1: SQLite (decisions, metadata, salience)
  ├── L2: Wiki (markdown synthesis, human-readable)
  └── L3: Oracle Vault (if configured)
        ├── vault_documents (raw content + source_meta)
        ├── vault_entities (LLM extraction: people, companies, concepts)
        ├── vault_facts (LLM extraction: atomic claims with provenance)
        ├── vault_relations (LLM extraction: who↔what↔where)
        └── embeddings (on documents + facts)
```

The L3 push is **async and optional**:
1. absorb writes L1+L2 immediately (fast, local)
2. If `oracle_enabled: true` in config, queue an L3 enrichment job
3. L3 enrichment: LLM extracts entities/facts/relations → bulk insert to Oracle
4. Extraction can use local QWEN (cheap, fast) or Claude (expensive, better)

## 3. Migration Plan

### Phase 1: Create new tables (non-destructive)
- Run schema v4 DDL alongside existing tables
- Zero downtime, zero risk

### Phase 2: Migrate knowledge → vault_documents + vault_facts
```python
for row in knowledge_table:
    # Each knowledge entry becomes a document
    doc_id = insert_vault_document(
        doc_type='note',  # or infer from category
        title=row.title,
        content=row.content,
        occurred_at=row.created_at,  # best we have
        taxonomy_id=row.taxonomy_id,
        source_system='legacy_knowledge',
        source_path=row.source_path
    )
    # Generate embedding if missing
    if not row.embedding:
        embedding = generate_embedding(row.content)
        update_embedding(doc_id, embedding)
```

### Phase 3: Migrate emails (already in knowledge table?)
- Need to parse source_meta from content (extract sender, recipients, dates)
- Re-type as doc_type='email'
- Set occurred_at to actual email date

### Phase 4: Entity extraction (batch, LLM-assisted)
- Run NER over all vault_documents
- Create vault_entities for each unique person/company/project
- Create vault_relations linking entities to documents

### Phase 5: Deprecate old knowledge table
- Keep read-only for 30 days
- Verify all data accessible via new tables
- Drop

## 4. Onboarding UX

In the onboarding wizard, after prerequisites page:
```
┌─────────────────────────────────────┐
│  Optional: Deep Memory (The Vault)  │
│                                     │
│  ○ Skip — use local memory only     │
│    (SQLite + Git Wiki, works great) │
│                                     │
│  ● Enable Oracle Vault              │
│    Store everything forever.        │
│    Semantic search across your      │
│    entire knowledge history.        │
│                                     │
│  [Oracle wallet path: ________]     │
│  [Connection string:   ________]    │
│  [Test Connection]                  │
└─────────────────────────────────────┘
```

With/without comparison in docs:
| Feature | Without Oracle | With Oracle (The Vault) |
|---------|---------------|------------------------|
| Agent memory | ✅ SQLite + Wiki | ✅ SQLite + Wiki + Oracle |
| Search | ripgrep (keyword) | ripgrep + vector semantic |
| Cross-machine | Git sync | Git + Oracle replication |
| Capacity | ~10K entries practical | Millions of entries |
| Email/doc archive | ❌ | ✅ Full lifecycle |
| Entity graph | ❌ | ✅ People/projects/concepts |
| "What did X say about Y?" | ❌ | ✅ Semantic + graph |

## 5. Query Architecture

**Don't let agents write SQL. Ever.**

```python
# vault_api.py — the ONLY way agents touch L3

def vault_search(query: str, filters: dict = None, limit: int = 10) -> list:
    """Hybrid search: vector similarity + keyword + filters."""

def vault_about(entity_name: str) -> dict:
    """Everything we know about an entity: documents, facts, relations."""

def vault_timeline(entity_name: str = None, topic: str = None, 
                   start: str = None, end: str = None) -> list:
    """Chronological view of documents/facts, optionally filtered."""

def vault_ingest(content: str, doc_type: str, meta: dict) -> int:
    """Ingest a new document into the vault."""

def vault_extract(doc_id: int) -> dict:
    """Run entity/fact/relation extraction on a document."""

def vault_graph(entity_id: int, depth: int = 2) -> dict:
    """Return relationship graph around an entity."""
```

Query flow:
```
Agent question → L1 SQLite (fast, recent)
  ↓ not enough?
L2 Wiki ripgrep (compiled knowledge)
  ↓ still not enough?
L3 Oracle Vault (deep, semantic, full history)
  ↓ merge results
Answer with citations
```

The key is **cascading**: most questions are answered by L1/L2. L3 is the fallback for deep/historical/semantic queries. This keeps latency low for common cases.
