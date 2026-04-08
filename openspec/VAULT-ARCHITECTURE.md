# The Vault — Oracle L3 Deep Brain Architecture

> **Status: APPROVED** — 5-round spiral roundtable consensus (Claude 0.88 / Codex 0.88 / Gemini 0.95)
> **Date:** 2026-04-07
> **Participants:** Claude Opus 4.6 (CIO), Codex GPT-5.4 (Developer), Gemini 2.5 Pro (Consultant)

## Core Principle

Three layers. Optional depth. Zero mandatory cloud dependencies.

```
L1  SQLite (The Ledger)   — fast local operational state (default)
L2  Git Wiki (The Library) — compiled human-readable knowledge (default)
L3  Oracle (The Vault)     — deep brain: evidence graph + vector search (optional)
```

L1+L2 ship with clawd-lobster. L3 is a power-user upgrade for those with Oracle Cloud.

## The Vault Schema (9 tables)

### Design Decisions (from roundtable)

| Decision | Winner | Why |
|----------|--------|-----|
| Schema style | Typed tables + JSON overflow | EAV kills query performance; pure rigid is over-normalized |
| Table count | 9 vault tables | Codex's 12 had redundancy; Gemini's 7 missed chunking detail |
| Primary keys | NUMBER IDENTITY | Single-owner system; faster joins than UUID |
| Content splitting | Explicit chunks table | Long documents need individual chunk vectors for RAG |
| Entity resolution | First-class aliases table | JSON aliases can't be indexed for fast lookup |
| Lifecycle tracking | Immutable events log | Current-state-only loses history |

### DDL

```sql
-- ============================================================
-- THE VAULT — Oracle L3 Deep Brain Schema v4
-- ============================================================

-- 1. SOURCES — where data came from
CREATE TABLE vault_sources (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_type     VARCHAR2(50) NOT NULL,   -- email_account, folder, repo, url, api, manual, legacy_import
    source_uri      VARCHAR2(2048) NOT NULL,
    source_uri_hash VARCHAR2(64) NOT NULL,   -- SHA-256 for dedup
    display_name    VARCHAR2(512),
    trust_level     NUMBER(3,2) DEFAULT 0.80,
    metadata_json   CLOB CHECK (metadata_json IS JSON),
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT uq_source_uri UNIQUE (source_type, source_uri_hash)
);

-- 2. DOCUMENTS — raw artifacts (emails, notes, files, conversations)
CREATE TABLE vault_documents (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id       NUMBER NOT NULL REFERENCES vault_sources(id),
    doc_type        VARCHAR2(50) NOT NULL,   -- email, note, file, conversation, webpage, code, receipt, image
    title           VARCHAR2(1000),
    content         CLOB,
    content_hash    VARCHAR2(64),            -- SHA-256 for dedup
    
    -- When the content HAPPENED (not when ingested)
    occurred_at     TIMESTAMP NOT NULL,
    ingested_at     TIMESTAMP DEFAULT SYSTIMESTAMP,
    
    -- Type-specific metadata (email headers, file metadata, etc.)
    metadata_json   CLOB CHECK (metadata_json IS JSON),
    -- Example for email: {"from":"ted@ted-h.com","to":["david@..."],"cc":[],"thread_id":"...","message_id":"..."}
    -- Example for file: {"path":"/docs/spec.md","size":1234,"mime":"text/markdown"}
    
    -- Classification
    taxonomy_id     NUMBER REFERENCES taxonomy(id),
    privacy_level   VARCHAR2(20) DEFAULT 'internal',
    language        VARCHAR2(10) DEFAULT 'en',
    
    -- Vector (for short documents; long ones use chunks)
    embedding       VECTOR(1536, FLOAT32),
    embedding_model VARCHAR2(128),
    
    -- Lifecycle
    lifecycle       VARCHAR2(20) DEFAULT 'raw',
    
    CONSTRAINT uq_doc_content UNIQUE (source_id, content_hash)
);

-- 3. CHUNKS — content split for RAG + individual vector search
CREATE TABLE vault_chunks (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id     NUMBER NOT NULL REFERENCES vault_documents(id),
    chunk_index     NUMBER NOT NULL,
    text_content    CLOB NOT NULL,
    token_count     NUMBER,
    char_start      NUMBER,
    char_end        NUMBER,
    summary         VARCHAR2(2000),
    
    -- Individual vector
    embedding       VECTOR(1536, FLOAT32),
    embedding_model VARCHAR2(128),
    
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    
    CONSTRAINT uq_chunk UNIQUE (document_id, chunk_index)
);

-- 4. ENTITIES — people, companies, projects, concepts, locations
CREATE TABLE vault_entities (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_type     VARCHAR2(50) NOT NULL,   -- person, company, project, concept, location, product, event
    canonical_name  VARCHAR2(500) NOT NULL,
    
    -- Structured attributes (queryable)
    metadata_json   CLOB CHECK (metadata_json IS JSON),
    -- Example for person: {"role":"CTO","company":"Acme","email":"david@acme.com"}
    -- Example for project: {"repo":"github.com/org/repo","status":"active"}
    
    -- Link to existing contacts table (for people)
    contact_id      NUMBER REFERENCES contacts(id),
    taxonomy_id     NUMBER REFERENCES taxonomy(id),
    
    -- Vector (for concept search)
    embedding       VECTOR(1536, FLOAT32),
    
    -- Temporal
    first_seen_at   TIMESTAMP,
    last_seen_at    TIMESTAMP,
    confidence      NUMBER(3,2) DEFAULT 0.80,
    lifecycle       VARCHAR2(20) DEFAULT 'extracted',
    
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    updated_at      TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- 5. ENTITY ALIASES — name variants for resolution
CREATE TABLE vault_entity_aliases (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_id       NUMBER NOT NULL REFERENCES vault_entities(id),
    alias_text      VARCHAR2(500) NOT NULL,
    alias_normalized VARCHAR2(500) NOT NULL,  -- lowercased, trimmed
    source          VARCHAR2(64) DEFAULT 'extraction',  -- extraction, manual, merge
    
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    
    CONSTRAINT uq_alias UNIQUE (entity_id, alias_normalized)
);

-- 6. FACTS — extracted atomic claims with provenance
CREATE TABLE vault_facts (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    claim           VARCHAR2(4000) NOT NULL,
    confidence      NUMBER(3,2) DEFAULT 0.80,
    
    -- Provenance
    source_doc_id   NUMBER REFERENCES vault_documents(id),
    source_chunk_id NUMBER REFERENCES vault_chunks(id),
    source_agent    VARCHAR2(50),             -- claude, codex, gemini, human
    extraction_method VARCHAR2(50),           -- llm_extract, manual, regex, absorb
    
    -- Classification
    taxonomy_id     NUMBER REFERENCES taxonomy(id),
    
    -- Temporal (when the fact was true, not when extracted)
    fact_date       TIMESTAMP,
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    
    -- Lifecycle
    lifecycle       VARCHAR2(20) DEFAULT 'extracted',
    -- States: raw → extracted → verified → accepted → superseded → retracted
    superseded_by   NUMBER REFERENCES vault_facts(id),
    
    -- Vector
    embedding       VECTOR(1536, FLOAT32)
);

-- 7. RELATIONS — typed edges between vault objects
CREATE TABLE vault_relations (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- Polymorphic endpoints
    subject_type    VARCHAR2(20) NOT NULL,    -- entity, document, fact, chunk
    subject_id      NUMBER NOT NULL,
    relation_type   VARCHAR2(100) NOT NULL,   -- mentions, authored_by, about, replies_to, works_at, colleague_of, discusses, depends_on
    object_type     VARCHAR2(20) NOT NULL,
    object_id       NUMBER NOT NULL,
    
    -- Provenance & confidence
    confidence      NUMBER(3,2) DEFAULT 1.0,
    source_doc_id   NUMBER REFERENCES vault_documents(id),
    metadata_json   CLOB CHECK (metadata_json IS JSON),
    -- Example: {"mention_role":"sender","char_start":0,"char_end":15}
    
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    
    CONSTRAINT chk_rel_subject CHECK (subject_type IN ('entity','document','fact','chunk')),
    CONSTRAINT chk_rel_object CHECK (object_type IN ('entity','document','fact','chunk'))
);

-- 8. EVENTS — immutable lifecycle event log
CREATE TABLE vault_events (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    target_type     VARCHAR2(50) NOT NULL,    -- source, document, chunk, entity, fact, relation
    target_id       NUMBER NOT NULL,
    from_state      VARCHAR2(30),
    to_state        VARCHAR2(30) NOT NULL,
    reason          VARCHAR2(2000),
    actor           VARCHAR2(64),             -- agent name or 'human'
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- 9. SYNC LOG — L1/L2 → L3 tracking
CREATE TABLE vault_sync_log (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_layer    VARCHAR2(10) NOT NULL,    -- L1, L2
    source_id       VARCHAR2(200) NOT NULL,   -- SQLite row ID or wiki page path
    source_hash     VARCHAR2(64),
    vault_table     VARCHAR2(50) NOT NULL,
    vault_id        NUMBER NOT NULL,
    synced_at       TIMESTAMP DEFAULT SYSTIMESTAMP,
    sync_agent      VARCHAR2(50),
    
    CONSTRAINT uq_sync UNIQUE (source_layer, source_id, vault_table)
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Documents
CREATE INDEX idx_vdoc_type ON vault_documents(doc_type);
CREATE INDEX idx_vdoc_occurred ON vault_documents(occurred_at);
CREATE INDEX idx_vdoc_source ON vault_documents(source_id);
CREATE INDEX idx_vdoc_taxonomy ON vault_documents(taxonomy_id);
CREATE INDEX idx_vdoc_hash ON vault_documents(content_hash);
CREATE INDEX idx_vdoc_lifecycle ON vault_documents(lifecycle);

-- Chunks
CREATE INDEX idx_vchunk_doc ON vault_chunks(document_id);

-- Entities
CREATE INDEX idx_ventity_type ON vault_entities(entity_type);
CREATE INDEX idx_ventity_name ON vault_entities(canonical_name);
CREATE INDEX idx_ventity_contact ON vault_entities(contact_id);

-- Aliases (critical for entity resolution)
CREATE INDEX idx_valias_norm ON vault_entity_aliases(alias_normalized);
CREATE INDEX idx_valias_entity ON vault_entity_aliases(entity_id);

-- Facts
CREATE INDEX idx_vfact_source ON vault_facts(source_doc_id);
CREATE INDEX idx_vfact_lifecycle ON vault_facts(lifecycle);
CREATE INDEX idx_vfact_date ON vault_facts(fact_date);
CREATE INDEX idx_vfact_agent ON vault_facts(source_agent);

-- Relations (critical for graph queries)
CREATE INDEX idx_vrel_subject ON vault_relations(subject_type, subject_id);
CREATE INDEX idx_vrel_object ON vault_relations(object_type, object_id);
CREATE INDEX idx_vrel_type ON vault_relations(relation_type);

-- Events
CREATE INDEX idx_vevent_target ON vault_events(target_type, target_id);
CREATE INDEX idx_vevent_time ON vault_events(created_at);

-- Sync log
CREATE INDEX idx_vsync_source ON vault_sync_log(source_layer, source_id);

-- ============================================================
-- CONVENIENCE VIEWS
-- ============================================================

CREATE OR REPLACE VIEW v_document_summary AS
SELECT d.id, d.doc_type, d.title, d.occurred_at, d.lifecycle, d.privacy_level,
       s.source_type, s.display_name AS source_name,
       t.path AS taxonomy_path,
       (SELECT COUNT(*) FROM vault_chunks c WHERE c.document_id = d.id) AS chunk_count,
       (SELECT COUNT(*) FROM vault_facts f WHERE f.source_doc_id = d.id) AS fact_count
FROM vault_documents d
JOIN vault_sources s ON s.id = d.source_id
LEFT JOIN taxonomy t ON t.id = d.taxonomy_id;

CREATE OR REPLACE VIEW v_entity_profile AS
SELECT e.id, e.entity_type, e.canonical_name, e.confidence, e.lifecycle,
       e.first_seen_at, e.last_seen_at,
       (SELECT LISTAGG(a.alias_text, ', ') WITHIN GROUP (ORDER BY a.alias_text)
        FROM vault_entity_aliases a WHERE a.entity_id = e.id) AS aliases,
       (SELECT COUNT(*) FROM vault_relations r 
        WHERE (r.subject_type='entity' AND r.subject_id=e.id)
           OR (r.object_type='entity' AND r.object_id=e.id)) AS relation_count
FROM vault_entities e;
```

## Enrichment Pipeline

```
                    ┌─────────┐
                    │  Input  │  file / URL / email export / manual
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │ Source   │  deduplicate by URI hash
                    │ Register │  → vault_sources
                    └────┬────┘
                         │
                    ┌────▼──────┐
                    │ Document   │  raw content + metadata JSON + occurred_at
                    │ Create     │  → vault_documents
                    └────┬──────┘
                         │
              ┌──────────┼──────────┐
              │                     │
         ┌────▼────┐          ┌────▼────┐
         │ Chunk   │          │ Embed   │  document-level embedding
         │ Split   │          │ (short) │  (for docs < 1000 tokens)
         └────┬────┘          └─────────┘
              │
         ┌────▼────┐
         │ Chunk   │  per-chunk VECTOR(1536)
         │ Embed   │  → vault_chunks
         └────┬────┘
              │
     ═════════╧═════════  FAST MODE STOPS HERE  ═════════
              │
         ┌────▼──────┐
         │ Entity    │  LLM NER → people, companies, concepts
         │ Extract   │  → vault_entities + vault_entity_aliases
         └────┬──────┘
              │
         ┌────▼──────┐
         │ Fact      │  LLM → atomic claims with confidence
         │ Extract   │  → vault_facts (source_doc_id, source_chunk_id)
         └────┬──────┘
              │
         ┌────▼──────┐
         │ Relation  │  entity↔doc, entity↔entity, entity↔chunk
         │ Build     │  → vault_relations
         └────┬──────┘
              │
         ┌────▼──────┐
         │ Event     │  log each stage transition
         │ Log       │  → vault_events
         └──────────┘
```

### Pipeline Modes

| Mode | Stages | LLM Required | Use Case |
|------|--------|-------------|----------|
| **Fast** | Source → Document → Chunks + Embeddings | No (embedding API only) | Bulk import, email archive |
| **Full** | Fast + Entity/Fact/Relation extraction | Yes (local QWEN or Claude) | Important documents, analysis |
| **Batch** | Run Full on existing Fast-imported docs | Yes | Backfill enrichment on weekends |

## Absorb Skill Integration

Current absorb writes to L1 (SQLite) + L2 (Wiki). With Vault:

```python
# In absorb skill, after L1+L2 writes:
if config.get("oracle", {}).get("enabled", False):
    from clawd_lobster.vault_api import vault_ingest, vault_enrich
    
    doc_id = vault_ingest(
        content=extracted_content,
        doc_type=inferred_type,   # note, file, code, etc.
        meta={"source_path": source_path, ...},
        source_info={"type": "absorb", "uri": source_uri}
    )
    
    # Full enrichment if configured, otherwise Fast mode
    mode = config.get("vault", {}).get("enrich_mode", "fast")
    vault_enrich(doc_id, mode=mode)
```

L3 push is **async and non-blocking** — absorb returns immediately after L1+L2 writes. L3 enrichment runs in background.

## Query Architecture

```
Agent question
  ├── L1 SQLite: recent decisions, todos, action state
  ├── L2 ripgrep: compiled wiki knowledge
  └── L3 Vault (if enabled):
       ├── vault_search(): semantic vector + keyword + filters
       ├── vault_about(): entity-centric aggregation
       └── vault_timeline(): temporal range queries
  → Merge & rerank by: lifecycle, recency, salience, confidence
  → Answer with citations (L1:decision:abc, L2:wiki/page.md, L3:doc:123:chunk:4)
```

### API Functions (vault_api.py)

```python
# === Ingest ===
vault_ingest(content, doc_type, meta, source_info) → doc_id
vault_enrich(doc_id, mode="full") → enrichment_summary
vault_bulk_ingest(items: list[dict]) → {created, skipped, errors}

# === Search ===
vault_search(query, filters=None, limit=10) → [{doc, chunk, score, citations}]
vault_about(entity_name) → {entity, aliases, documents, facts, relations, timeline}
vault_timeline(entity=None, topic=None, start=None, end=None) → [dated_events]

# === Graph ===
vault_relations(entity_id, depth=2) → {nodes, edges}
vault_entity_resolve(name_or_alias) → entity_or_None

# === Lifecycle ===
vault_accept(fact_id) → updated_fact
vault_supersede(fact_id, new_fact_id, reason) → event
vault_retract(fact_id, reason) → event

# === Admin ===
vault_stats() → {table_counts, index_health, storage}
vault_doctor() → {connection_ok, schema_version, vector_support, embedding_model}
vault_init() → create tables if missing
```

## Migration Plan

### Phase 1: Deploy schema (non-destructive)
```bash
python vault_init.py  # Creates 9 tables alongside existing tables
```

### Phase 2: Migrate legacy knowledge → vault_documents
```python
for row in old_knowledge_table:
    source_id = get_or_create_source("legacy_import", f"oracle:knowledge:{row.id}")
    doc_id = insert_vault_document(
        source_id=source_id,
        doc_type=infer_type(row.category),  # note, sop, guideline, etc.
        title=row.title,
        content=row.content,
        occurred_at=row.created_at,  # best available
        taxonomy_id=row.taxonomy_id,
        embedding=row.embedding,     # keep existing
        lifecycle='accepted'         # trusted legacy data
    )
```

### Phase 3: Re-chunk and enrich (batch, LLM-assisted)
```python
for doc in vault_documents.where(lifecycle='accepted', chunk_count=0):
    vault_enrich(doc.id, mode="full")
    # Creates chunks, extracts entities/facts/relations
```

### Phase 4: Migrate emails (parse metadata from content)
```python
for doc in vault_documents.where(doc_type='email'):
    parsed = parse_email_headers(doc.content)
    doc.metadata_json = json.dumps(parsed)  # from, to, thread_id, date_sent
    doc.occurred_at = parsed['date_sent']   # fix temporal anchor
```

### Phase 5: Expand taxonomy
Add life-focused categories beyond projects:
```python
new_nodes = [
    ("work/emails", "Work Emails", "work"),
    ("work/meetings", "Work Meetings", "work"),
    ("personal/health", "Health", "personal"),
    ("personal/finance", "Finance", "personal"),
    ("learning/courses", "Courses", "learning"),
    ("learning/books", "Books", "learning"),
    ("relationships/family", "Family", "personal/contacts"),
    ("relationships/professional", "Professional Network", "personal/contacts"),
]
```

### Phase 6: Deprecate old knowledge table
- Keep read-only for 30 days
- Verify all data accessible via new vault tables
- Archive or drop

## Onboarding Integration

### Setup Modes
```
clawd-lobster setup
  ├── Basic: SQLite + Git Wiki (default, zero config)
  ├── Power: Basic + OpenAI embeddings (needs API key)
  └── Vault: Power + Oracle L3 (needs Oracle wallet + credentials)
```

### With/Without Comparison

| Feature | Basic (L1+L2) | Vault (L1+L2+L3) |
|---------|--------------|-------------------|
| Agent memory | SQLite + Wiki | SQLite + Wiki + Oracle |
| Search | ripgrep (keyword) | ripgrep + vector semantic |
| Cross-machine sync | Git push/pull | Git + Oracle replication |
| Capacity | ~10K entries | Millions |
| Email/doc archive | Not designed for this | Full lifecycle management |
| Entity graph | None | People, projects, concepts linked |
| "What did X say about Y in 2023?" | Cannot answer | Semantic + graph + temporal |
| Time-travel queries | None | occurred_at timeline |

### Terminology Migration
Rename all references from "L4" to "L3" across:
- webapp/index.html
- skills/memory-server/ (config, server.py, README)
- CHANGELOG.md
- install.sh / install.ps1
- scripts/sync-all.ps1

## Non-Blocking Improvements (post-launch)

From Codex:
- Add `embedding_model` + `embedding_version` columns for re-embedding tracking
- Define retention/immutability rules for vault_events
- Add strict CHECK constraints on vault_relations subject_type/object_type

From Gemini:
- Benchmark polymorphic relations at scale; consider indexed views
- Add `disputed` and `retracted` to vault_facts lifecycle states
- API versioning (v1 prefix)

---

*Architecture synthesized from 5-round spiral roundtable. Full debate transcripts in `docs/roundtable-vault/`.*
