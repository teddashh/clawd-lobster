Using the local `absorb` skill docs and current memory-server shape as context.

**Position**
Oracle should not be a bigger `knowledge_items` table. It should be an optional source-grounded evidence graph: raw artifacts, chunked text, extracted entities, typed relationships, dated assertions, and derivation lineage. Keep L1/L2 as the default product. L3 should be a power-user “deep recall” index and synthesis substrate, not the canonical operational store.

I disagree with two current assumptions:
- Calling Oracle “sync target” only is too weak for the owner’s use case. It can remain optional for public users, but when enabled it should own global long-term recall.
- A flat `knowledge` bag cannot answer “who discussed what, when, about which project” without hallucination-prone full-text search. You need provenance, temporal fields, participants, entities, and relationship edges.

## 1. Schema Design

Core design:

```text
sources -> artifacts -> chunks -> embeddings
                  |         |
                  |         -> entity_mentions -> entities
                  |         -> assertions -> facts/events/decisions
                  |
                  -> provenance + lifecycle_events

entities <-> relationships <-> entities
taxonomy_nodes classify artifacts/chunks/entities/assertions
```

Recommended Oracle DDL, compact but concrete:

```sql
CREATE TABLE vault_sources (
  source_id        VARCHAR2(64) PRIMARY KEY,
  source_type      VARCHAR2(32) NOT NULL, -- email_account, folder, repo, url, chat_export, manual
  source_uri_hash  VARCHAR2(128) NOT NULL,
  display_name     VARCHAR2(512),
  owner_scope      VARCHAR2(64) DEFAULT 'personal',
  trust_level      NUMBER(3,2) DEFAULT 0.80,
  created_at       TIMESTAMP DEFAULT SYSTIMESTAMP,
  UNIQUE (source_type, source_uri_hash)
);

CREATE TABLE vault_artifacts (
  artifact_id      VARCHAR2(64) PRIMARY KEY,
  source_id        VARCHAR2(64) REFERENCES vault_sources(source_id),
  artifact_type    VARCHAR2(32) NOT NULL, -- email, document, note, code, conversation, sop, decision
  external_id      VARCHAR2(512),
  title            VARCHAR2(1024),
  author_text      VARCHAR2(1024),
  occurred_at      TIMESTAMP,
  ingested_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
  content_hash     VARCHAR2(128) NOT NULL,
  mime_type        VARCHAR2(128),
  language         VARCHAR2(32),
  raw_ref          VARCHAR2(2048), -- path/object-store URI/message-id, not necessarily raw body
  metadata_json    CLOB CHECK (metadata_json IS JSON),
  lifecycle        VARCHAR2(32) DEFAULT 'raw',
  confidence       NUMBER(3,2) DEFAULT 1.00,
  UNIQUE (source_id, content_hash)
);

CREATE TABLE vault_chunks (
  chunk_id         VARCHAR2(64) PRIMARY KEY,
  artifact_id      VARCHAR2(64) REFERENCES vault_artifacts(artifact_id),
  chunk_index      NUMBER NOT NULL,
  text_content     CLOB NOT NULL,
  token_count      NUMBER,
  char_start       NUMBER,
  char_end         NUMBER,
  summary          CLOB,
  lifecycle        VARCHAR2(32) DEFAULT 'extracted',
  created_at       TIMESTAMP DEFAULT SYSTIMESTAMP,
  UNIQUE (artifact_id, chunk_index)
);

CREATE TABLE vault_chunk_vectors (
  chunk_id         VARCHAR2(64) PRIMARY KEY REFERENCES vault_chunks(chunk_id),
  embedding_model  VARCHAR2(128) NOT NULL,
  embedding_dim    NUMBER DEFAULT 1536,
  embedding        VECTOR(1536),
  embedded_at      TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE TABLE vault_entities (
  entity_id        VARCHAR2(64) PRIMARY KEY,
  entity_type      VARCHAR2(32) NOT NULL, -- person, org, project, product, place, system, topic
  canonical_name   VARCHAR2(512) NOT NULL,
  display_name     VARCHAR2(512),
  metadata_json    CLOB CHECK (metadata_json IS JSON),
  first_seen_at    TIMESTAMP,
  last_seen_at     TIMESTAMP,
  confidence       NUMBER(3,2) DEFAULT 0.80,
  lifecycle        VARCHAR2(32) DEFAULT 'extracted'
);

CREATE TABLE vault_entity_aliases (
  alias_id         VARCHAR2(64) PRIMARY KEY,
  entity_id        VARCHAR2(64) REFERENCES vault_entities(entity_id),
  alias_text       VARCHAR2(512) NOT NULL,
  alias_norm       VARCHAR2(512) NOT NULL,
  source           VARCHAR2(64) DEFAULT 'extraction',
  UNIQUE (entity_id, alias_norm)
);

CREATE TABLE vault_entity_mentions (
  mention_id       VARCHAR2(64) PRIMARY KEY,
  entity_id        VARCHAR2(64) REFERENCES vault_entities(entity_id),
  chunk_id         VARCHAR2(64) REFERENCES vault_chunks(chunk_id),
  mention_text     VARCHAR2(1024),
  mention_role     VARCHAR2(64), -- sender, recipient, author, subject, object, participant
  char_start       NUMBER,
  char_end         NUMBER,
  confidence       NUMBER(3,2) DEFAULT 0.80
);

CREATE TABLE vault_relationships (
  relationship_id  VARCHAR2(64) PRIMARY KEY,
  subject_entity_id VARCHAR2(64) REFERENCES vault_entities(entity_id),
  predicate        VARCHAR2(128) NOT NULL, -- discussed, works_on, reports_to, owns, depends_on
  object_entity_id VARCHAR2(64) REFERENCES vault_entities(entity_id),
  valid_from       TIMESTAMP,
  valid_to         TIMESTAMP,
  evidence_chunk_id VARCHAR2(64) REFERENCES vault_chunks(chunk_id),
  confidence       NUMBER(3,2) DEFAULT 0.80,
  lifecycle        VARCHAR2(32) DEFAULT 'extracted'
);

CREATE TABLE vault_assertions (
  assertion_id     VARCHAR2(64) PRIMARY KEY,
  assertion_type   VARCHAR2(32) NOT NULL, -- fact, decision, preference, sop_step, commitment, open_question
  subject_entity_id VARCHAR2(64) REFERENCES vault_entities(entity_id),
  statement        CLOB NOT NULL,
  occurred_at      TIMESTAMP,
  evidence_chunk_id VARCHAR2(64) REFERENCES vault_chunks(chunk_id),
  derived_from_id  VARCHAR2(64),
  confidence       NUMBER(3,2) DEFAULT 0.80,
  lifecycle        VARCHAR2(32) DEFAULT 'extracted', -- raw/extracted/synthesized/accepted/superseded
  supersedes_id    VARCHAR2(64),
  created_by       VARCHAR2(64) DEFAULT 'agent'
);

CREATE TABLE vault_taxonomy_nodes (
  taxonomy_id      VARCHAR2(64) PRIMARY KEY,
  parent_id        VARCHAR2(64),
  node_type        VARCHAR2(32), -- domain, project, topic, life_area
  name             VARCHAR2(256) NOT NULL,
  path             VARCHAR2(2048) NOT NULL,
  description      CLOB
);

CREATE TABLE vault_classifications (
  classification_id VARCHAR2(64) PRIMARY KEY,
  target_type       VARCHAR2(32) NOT NULL, -- artifact, chunk, entity, assertion
  target_id         VARCHAR2(64) NOT NULL,
  taxonomy_id       VARCHAR2(64) REFERENCES vault_taxonomy_nodes(taxonomy_id),
  confidence        NUMBER(3,2) DEFAULT 0.80,
  source            VARCHAR2(64) DEFAULT 'agent'
);

CREATE TABLE vault_lifecycle_events (
  event_id        VARCHAR2(64) PRIMARY KEY,
  target_type     VARCHAR2(32) NOT NULL,
  target_id       VARCHAR2(64) NOT NULL,
  from_state      VARCHAR2(32),
  to_state        VARCHAR2(32) NOT NULL,
  reason          CLOB,
  actor           VARCHAR2(64),
  created_at      TIMESTAMP DEFAULT SYSTIMESTAMP
);
```

Add indexes:

```sql
CREATE INDEX ix_artifacts_time ON vault_artifacts(occurred_at, artifact_type);
CREATE INDEX ix_entities_type_name ON vault_entities(entity_type, canonical_name);
CREATE INDEX ix_relationship_pred_time ON vault_relationships(predicate, valid_from, valid_to);
CREATE INDEX ix_assertions_time_type ON vault_assertions(assertion_type, occurred_at, lifecycle);
CREATE VECTOR INDEX ix_chunk_vectors ON vault_chunk_vectors(embedding)
  ORGANIZATION INMEMORY NEIGHBOR GRAPH
  DISTANCE COSINE;
```

## 2. Absorb Skill Integration

`absorb` should become a three-target pipeline:

```text
Input source
  -> classify source and scan
  -> L1: operational records, todos, decisions
  -> L2: human-readable wiki synthesis
  -> L3: raw artifact metadata, chunks, vectors, entities, relationships, assertions
```

Concrete flow:

```text
/absorb ./folder --depth normal --l3 auto

1. Register source in vault_sources
2. Create artifact per file/email/page/conversation
3. Chunk artifact text with stable content_hash + chunk_index
4. Embed chunks into vault_chunk_vectors
5. Extract entities: people, orgs, projects, products, systems, dates
6. Link aliases to existing entities with human-review queue for uncertain matches
7. Extract assertions: decisions, SOP steps, commitments, facts, preferences
8. Extract relationships: person discussed project, project uses system, SOP belongs to domain
9. Write accepted summaries to L2 only after synthesis
10. Write L1 lightweight pointers: source id, salient decisions, todos, lifecycle state
```

Important rule: L3 stores evidence first, conclusions second. Do not let `absorb` write “accepted” life knowledge directly from first-pass extraction. Default lifecycle should be `raw` for artifacts, `extracted` for chunks/assertions, and only `accepted` after review, repeated corroboration, or L2 synthesis.

## 3. Migration Plan

Migration should be lossless and staged.

1. Snapshot existing Oracle tables.
2. Create new `vault_*` schema alongside the old schema.
3. Insert one `vault_source` for the legacy Oracle import.
4. Convert each old `knowledge` row into a `vault_artifact` with `artifact_type = 'legacy_knowledge'`.
5. Convert old `content` into one or more `vault_chunks`.
6. Copy old embeddings to `vault_chunk_vectors` if dimension/model matches; otherwise mark for re-embedding.
7. Convert old `taxonomy_id` into `vault_classifications`.
8. Convert old tags into `metadata_json.tags` plus optional taxonomy candidates.
9. Run entity/assertion extraction as a backfill job, not inline migration.
10. Keep `legacy_id` in metadata and create a `vault_migration_map`.

Example mapping table:

```sql
CREATE TABLE vault_migration_map (
  old_table       VARCHAR2(128) NOT NULL,
  old_id          VARCHAR2(256) NOT NULL,
  new_target_type VARCHAR2(32) NOT NULL,
  new_target_id   VARCHAR2(64) NOT NULL,
  migrated_at     TIMESTAMP DEFAULT SYSTIMESTAMP,
  notes           CLOB,
  PRIMARY KEY (old_table, old_id, new_target_type)
);
```

Backfill phases:

```text
Phase A: structure-only migration, no interpretation
Phase B: chunk/vector validation
Phase C: entity extraction
Phase D: assertion/relationship extraction
Phase E: review high-salience or low-confidence items
Phase F: freeze old table as read-only compatibility view
```

Compatibility view:

```sql
CREATE OR REPLACE VIEW knowledge_legacy_view AS
SELECT
  a.artifact_id AS id,
  a.title,
  a.artifact_type AS category,
  a.metadata_json AS tags,
  c.text_content AS content,
  v.embedding,
  a.lifecycle
FROM vault_artifacts a
JOIN vault_chunks c ON c.artifact_id = a.artifact_id AND c.chunk_index = 0
LEFT JOIN vault_chunk_vectors v ON v.chunk_id = c.chunk_id;
```

## 4. Onboarding UX

Do not lead with Oracle. Lead with the zero-dependency baseline.

Recommended wording:

```text
Clawd-Lobster works out of the box with:
- L1 SQLite: fast local memory
- L2 Git Wiki: portable human-readable knowledge

Optional:
- L3 Oracle Vault: private deep recall across years of email, docs, notes, and work history.
```

Setup modes:

```text
Basic: SQLite + Git Wiki only
Power User: enable embeddings for local/L3 search
Vault: connect Oracle Autonomous DB and run schema check
```

Painless setup checklist:

```text
1. Ask: “Enable optional Oracle Vault? You can skip this.”
2. If yes, collect wallet path, DSN, username through existing credential manager.
3. Read passwords from environment/credential store only.
4. Run `vault doctor`: connection, VECTOR support, schema version, embedding model.
5. Run `vault init`: create tables if missing.
6. Run `vault sample`: ingest one small markdown file and query it.
```

Also fix naming. The repo currently says Oracle “L4” in UI/docs. If the new architecture says Oracle is L3, rename it consistently before public onboarding. Mixed L3/L4 wording will confuse users and future agents.

## 5. Query Architecture

Agents should not query Oracle directly. Use an API layer through memory-server/MCP tools.

Recommended tools:

```text
memory_search(query, scope=local|all|vault, limit=10)
vault_search(query, filters_json, limit)
vault_entity_lookup(name_or_alias)
vault_timeline(entity_or_topic, start, end)
vault_evidence(assertion_id)
vault_ingest_status(source_id)
vault_propose_accept(assertion_id)
vault_supersede(assertion_id, reason)
```

Query-time architecture:

```text
Agent question
  -> L1 search: recent decisions/todos/action state
  -> L2 ripgrep: accepted human-readable synthesis
  -> L3 vault search: semantic + graph + temporal evidence
  -> rerank by lifecycle, recency, salience, confidence
  -> answer with citations to artifact/chunk/assertion IDs
```

For a question like “What did person X and I discuss about Project Y in 2023?”:

```sql
SELECT
  a.occurred_at,
  a.title,
  c.chunk_id,
  DBMS_LOB.SUBSTR(c.text_content, 1000, 1) AS excerpt,
  VECTOR_DISTANCE(v.embedding, :query_vec, COSINE) AS distance
FROM vault_entities p
JOIN vault_entity_mentions pm ON pm.entity_id = p.entity_id
JOIN vault_chunks c ON c.chunk_id = pm.chunk_id
JOIN vault_artifacts a ON a.artifact_id = c.artifact_id
JOIN vault_chunk_vectors v ON v.chunk_id = c.chunk_id
JOIN vault_entity_mentions topic_m ON topic_m.chunk_id = c.chunk_id
JOIN vault_entities topic ON topic.entity_id = topic_m.entity_id
WHERE p.entity_type = 'person'
  AND p.canonical_name = :person_name
  AND topic.canonical_name = :project_name
  AND a.occurred_at >= TIMESTAMP '2023-01-01 00:00:00'
  AND a.occurred_at <  TIMESTAMP '2024-01-01 00:00:00'
ORDER BY a.occurred_at, distance
FETCH FIRST 25 ROWS ONLY;
```

But the agent should call `vault_timeline(...)`, not emit SQL itself. The API should translate intent into safe parameterized SQL, enforce redaction rules, and return cited evidence.

**Bottom line:** Build L3 as an evidence graph with vector search, not as cloud sync for `knowledge_items`. Keep L1/L2 mandatory and simple. Make Oracle optional, powerful, and API-gated.

```json
{
  "agent": "codex",
  "role": "reviewer",
  "task": "Round 1 independent proposal for Oracle as optional L3 Vault deep-brain architecture covering schema, absorb integration, migration, onboarding, and query architecture.",
  "findings": [
    {
      "type": "risk",
      "description": "The current Oracle terminology appears inconsistent: local docs/UI refer to Oracle as L4 while the proposed architecture frames it as L3. This should be resolved before onboarding or schema work.",
      "file": "webapp/index.html"
    },
    {
      "type": "risk",
      "description": "The existing flat knowledge-item model is insufficient for temporal, entity-centric recall across emails/documents because it lacks first-class sources, artifacts, chunks, entity mentions, relationships, and assertion lifecycle.",
      "file": "skills/memory-server/mcp_memory/server.py"
    },
    {
      "type": "decision",
      "description": "Recommend keeping L1 SQLite and L2 Git Wiki as the default product baseline while making Oracle an optional API-gated evidence graph with vector search and lifecycle/provenance tracking.",
      "file": null
    }
  ],
  "summary": "Proposed an Oracle Vault design centered on source-grounded artifacts, chunks, vectors, entities, relationships, assertions, taxonomy classifications, and lifecycle events. Recommended extending absorb into a three-target pipeline that writes operational state to L1, accepted synthesis to L2, and evidence plus extracted graph data to L3. Proposed a lossless staged migration from the legacy knowledge table and an API/MCP query layer instead of direct agent SQL.",
  "disagreements": [
    "Oracle should not remain only a passive sync target for the owner’s deep-brain use case.",
    "A flat knowledge table plus tags is not an adequate knowledge-management schema for long-range personal/corporate recall.",
    "Agents should not directly query Oracle SQL except through vetted memory-server/Vault tools."
  ]
}
```
Using the local `absorb` skill docs and current memory-server shape as context.

**Position**
Oracle should not be a bigger `knowledge_items` table. It should be an optional source-grounded evidence graph: raw artifacts, chunked text, extracted entities, typed relationships, dated assertions, and derivation lineage. Keep L1/L2 as the default product. L3 should be a power-user “deep recall” index and synthesis substrate, not the canonical operational store.

I disagree with two current assumptions:
- Calling Oracle “sync target” only is too weak for the owner’s use case. It can remain optional for public users, but when enabled it should own global long-term recall.
- A flat `knowledge` bag cannot answer “who discussed what, when, about which project” without hallucination-prone full-text search. You need provenance, temporal fields, participants, entities, and relationship edges.

## 1. Schema Design

Core design:

```text
sources -> artifacts -> chunks -> embeddings
                  |         |
                  |         -> entity_mentions -> entities
                  |         -> assertions -> facts/events/decisions
                  |
                  -> provenance + lifecycle_events

entities <-> relationships <-> entities
taxonomy_nodes classify artifacts/chunks/entities/assertions
```

Recommended Oracle DDL, compact but concrete:

```sql
CREATE TABLE vault_sources (
  source_id        VARCHAR2(64) PRIMARY KEY,
  source_type      VARCHAR2(32) NOT NULL, -- email_account, folder, repo, url, chat_export, manual
  source_uri_hash  VARCHAR2(128) NOT NULL,
  display_name     VARCHAR2(512),
  owner_scope      VARCHAR2(64) DEFAULT 'personal',
  trust_level      NUMBER(3,2) DEFAULT 0.80,
  created_at       TIMESTAMP DEFAULT SYSTIMESTAMP,
  UNIQUE (source_type, source_uri_hash)
);

CREATE TABLE vault_artifacts (
  artifact_id      VARCHAR2(64) PRIMARY KEY,
  source_id        VARCHAR2(64) REFERENCES vault_sources(source_id),
  artifact_type    VARCHAR2(32) NOT NULL, -- email, document, note, code, conversation, sop, decision
  external_id      VARCHAR2(512),
  title            VARCHAR2(1024),
  author_text      VARCHAR2(1024),
  occurred_at      TIMESTAMP,
  ingested_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
  content_hash     VARCHAR2(128) NOT NULL,
  mime_type        VARCHAR2(128),
  language         VARCHAR2(32),
  raw_ref          VARCHAR2(2048), -- path/object-store URI/message-id, not necessarily raw body
  metadata_json    CLOB CHECK (metadata_json IS JSON),
  lifecycle        VARCHAR2(32) DEFAULT 'raw',
  confidence       NUMBER(3,2) DEFAULT 1.00,
  UNIQUE (source_id, content_hash)
);

CREATE TABLE vault_chunks (
  chunk_id         VARCHAR2(64) PRIMARY KEY,
  artifact_id      VARCHAR2(64) REFERENCES vault_artifacts(artifact_id),
  chunk_index      NUMBER NOT NULL,
  text_content     CLOB NOT NULL,
  token_count      NUMBER,
  char_start       NUMBER,
  char_end         NUMBER,
  summary          CLOB,
  lifecycle        VARCHAR2(32) DEFAULT 'extracted',
  created_at       TIMESTAMP DEFAULT SYSTIMESTAMP,
  UNIQUE (artifact_id, chunk_index)
);

CREATE TABLE vault_chunk_vectors (
  chunk_id         VARCHAR2(64) PRIMARY KEY REFERENCES vault_chunks(chunk_id),
  embedding_model  VARCHAR2(128) NOT NULL,
  embedding_dim    NUMBER DEFAULT 1536,
  embedding        VECTOR(1536),
  embedded_at      TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE TABLE vault_entities (
  entity_id        VARCHAR2(64) PRIMARY KEY,
  entity_type      VARCHAR2(32) NOT NULL, -- person, org, project, product, place, system, topic
  canonical_name   VARCHAR2(512) NOT NULL,
  display_name     VARCHAR2(512),
  metadata_json    CLOB CHECK (metadata_json IS JSON),
  first_seen_at    TIMESTAMP,
  last_seen_at     TIMESTAMP,
  confidence       NUMBER(3,2) DEFAULT 0.80,
  lifecycle        VARCHAR2(32) DEFAULT 'extracted'
);

CREATE TABLE vault_entity_aliases (
  alias_id         VARCHAR2(64) PRIMARY KEY,
  entity_id        VARCHAR2(64) REFERENCES vault_entities(entity_id),
  alias_text       VARCHAR2(512) NOT NULL,
  alias_norm       VARCHAR2(512) NOT NULL,
  source           VARCHAR2(64) DEFAULT 'extraction',
  UNIQUE (entity_id, alias_norm)
);

CREATE TABLE vault_entity_mentions (
  mention_id       VARCHAR2(64) PRIMARY KEY,
  entity_id        VARCHAR2(64) REFERENCES vault_entities(entity_id),
  chunk_id         VARCHAR2(64) REFERENCES vault_chunks(chunk_id),
  mention_text     VARCHAR2(1024),
  mention_role     VARCHAR2(64), -- sender, recipient, author, subject, object, participant
  char_start       NUMBER,
  char_end         NUMBER,
  confidence       NUMBER(3,2) DEFAULT 0.80
);

CREATE TABLE vault_relationships (
  relationship_id  VARCHAR2(64) PRIMARY KEY,
  subject_entity_id VARCHAR2(64) REFERENCES vault_entities(entity_id),
  predicate        VARCHAR2(128) NOT NULL, -- discussed, works_on, reports_to, owns, depends_on
  object_entity_id VARCHAR2(64) REFERENCES vault_entities(entity_id),
  valid_from       TIMESTAMP,
  valid_to         TIMESTAMP,
  evidence_chunk_id VARCHAR2(64) REFERENCES vault_chunks(chunk_id),
  confidence       NUMBER(3,2) DEFAULT 0.80,
  lifecycle        VARCHAR2(32) DEFAULT 'extracted'
);

CREATE TABLE vault_assertions (
  assertion_id     VARCHAR2(64) PRIMARY KEY,
  assertion_type   VARCHAR2(32) NOT NULL, -- fact, decision, preference, sop_step, commitment, open_question
  subject_entity_id VARCHAR2(64) REFERENCES vault_entities(entity_id),
  statement        CLOB NOT NULL,
  occurred_at      TIMESTAMP,
  evidence_chunk_id VARCHAR2(64) REFERENCES vault_chunks(chunk_id),
  derived_from_id  VARCHAR2(64),
  confidence       NUMBER(3,2) DEFAULT 0.80,
  lifecycle        VARCHAR2(32) DEFAULT 'extracted', -- raw/extracted/synthesized/accepted/superseded
  supersedes_id    VARCHAR2(64),
  created_by       VARCHAR2(64) DEFAULT 'agent'
);

CREATE TABLE vault_taxonomy_nodes (
  taxonomy_id      VARCHAR2(64) PRIMARY KEY,
  parent_id        VARCHAR2(64),
  node_type        VARCHAR2(32), -- domain, project, topic, life_area
  name             VARCHAR2(256) NOT NULL,
  path             VARCHAR2(2048) NOT NULL,
  description      CLOB
);

CREATE TABLE vault_classifications (
  classification_id VARCHAR2(64) PRIMARY KEY,
  target_type       VARCHAR2(32) NOT NULL, -- artifact, chunk, entity, assertion
  target_id         VARCHAR2(64) NOT NULL,
  taxonomy_id       VARCHAR2(64) REFERENCES vault_taxonomy_nodes(taxonomy_id),
  confidence        NUMBER(3,2) DEFAULT 0.80,
  source            VARCHAR2(64) DEFAULT 'agent'
);

CREATE TABLE vault_lifecycle_events (
  event_id        VARCHAR2(64) PRIMARY KEY,
  target_type     VARCHAR2(32) NOT NULL,
  target_id       VARCHAR2(64) NOT NULL,
  from_state      VARCHAR2(32),
  to_state        VARCHAR2(32) NOT NULL,
  reason          CLOB,
  actor           VARCHAR2(64),
  created_at      TIMESTAMP DEFAULT SYSTIMESTAMP
);
```

Add indexes:

```sql
CREATE INDEX ix_artifacts_time ON vault_artifacts(occurred_at, artifact_type);
CREATE INDEX ix_entities_type_name ON vault_entities(entity_type, canonical_name);
CREATE INDEX ix_relationship_pred_time ON vault_relationships(predicate, valid_from, valid_to);
CREATE INDEX ix_assertions_time_type ON vault_assertions(assertion_type, occurred_at, lifecycle);
CREATE VECTOR INDEX ix_chunk_vectors ON vault_chunk_vectors(embedding)
  ORGANIZATION INMEMORY NEIGHBOR GRAPH
  DISTANCE COSINE;
```

## 2. Absorb Skill Integration

`absorb` should become a three-target pipeline:

```text
Input source
  -> classify source and scan
  -> L1: operational records, todos, decisions
  -> L2: human-readable wiki synthesis
  -> L3: raw artifact metadata, chunks, vectors, entities, relationships, assertions
```

Concrete flow:

```text
/absorb ./folder --depth normal --l3 auto

1. Register source in vault_sources
2. Create artifact per file/email/page/conversation
3. Chunk artifact text with stable content_hash + chunk_index
4. Embed chunks into vault_chunk_vectors
5. Extract entities: people, orgs, projects, products, systems, dates
6. Link aliases to existing entities with human-review queue for uncertain matches
7. Extract assertions: decisions, SOP steps, commitments, facts, preferences
8. Extract relationships: person discussed project, project uses system, SOP belongs to domain
9. Write accepted summaries to L2 only after synthesis
10. Write L1 lightweight pointers: source id, salient decisions, todos, lifecycle state
```

Important rule: L3 stores evidence first, conclusions second. Do not let `absorb` write “accepted” life knowledge directly from first-pass extraction. Default lifecycle should be `raw` for artifacts, `extracted` for chunks/assertions, and only `accepted` after review, repeated corroboration, or L2 synthesis.

## 3. Migration Plan

Migration should be lossless and staged.

1. Snapshot existing Oracle tables.
2. Create new `vault_*` schema alongside the old schema.
3. Insert one `vault_source` for the legacy Oracle import.
4. Convert each old `knowledge` row into a `vault_artifact` with `artifact_type = 'legacy_knowledge'`.
5. Convert old `content` into one or more `vault_chunks`.
6. Copy old embeddings to `vault_chunk_vectors` if dimension/model matches; otherwise mark for re-embedding.
7. Convert old `taxonomy_id` into `vault_classifications`.
8. Convert old tags into `metadata_json.tags` plus optional taxonomy candidates.
9. Run entity/assertion extraction as a backfill job, not inline migration.
10. Keep `legacy_id` in metadata and create a `vault_migration_map`.

Example mapping table:

```sql
CREATE TABLE vault_migration_map (
  old_table       VARCHAR2(128) NOT NULL,
  old_id          VARCHAR2(256) NOT NULL,
  new_target_type VARCHAR2(32) NOT NULL,
  new_target_id   VARCHAR2(64) NOT NULL,
  migrated_at     TIMESTAMP DEFAULT SYSTIMESTAMP,
  notes           CLOB,
  PRIMARY KEY (old_table, old_id, new_target_type)
);
```

Backfill phases:

```text
Phase A: structure-only migration, no interpretation
Phase B: chunk/vector validation
Phase C: entity extraction
Phase D: assertion/relationship extraction
Phase E: review high-salience or low-confidence items
Phase F: freeze old table as read-only compatibility view
```

Compatibility view:

```sql
CREATE OR REPLACE VIEW knowledge_legacy_view AS
SELECT
  a.artifact_id AS id,
  a.title,
  a.artifact_type AS category,
  a.metadata_json AS tags,
  c.text_content AS content,
  v.embedding,
  a.lifecycle
FROM vault_artifacts a
JOIN vault_chunks c ON c.artifact_id = a.artifact_id AND c.chunk_index = 0
LEFT JOIN vault_chunk_vectors v ON v.chunk_id = c.chunk_id;
```

## 4. Onboarding UX

Do not lead with Oracle. Lead with the zero-dependency baseline.

Recommended wording:

```text
Clawd-Lobster works out of the box with:
- L1 SQLite: fast local memory
- L2 Git Wiki: portable human-readable knowledge

Optional:
- L3 Oracle Vault: private deep recall across years of email, docs, notes, and work history.
```

Setup modes:

```text
Basic: SQLite + Git Wiki only
Power User: enable embeddings for local/L3 search
Vault: connect Oracle Autonomous DB and run schema check
```

Painless setup checklist:

```text
1. Ask: “Enable optional Oracle Vault? You can skip this.”
2. If yes, collect wallet path, DSN, username through existing credential manager.
3. Read passwords from environment/credential store only.
4. Run `vault doctor`: connection, VECTOR support, schema version, embedding model.
5. Run `vault init`: create tables if missing.
6. Run `vault sample`: ingest one small markdown file and query it.
```

Also fix naming. The repo currently says Oracle “L4” in UI/docs. If the new architecture says Oracle is L3, rename it consistently before public onboarding. Mixed L3/L4 wording will confuse users and future agents.

## 5. Query Architecture

Agents should not query Oracle directly. Use an API layer through memory-server/MCP tools.

Recommended tools:

```text
memory_search(query, scope=local|all|vault, limit=10)
vault_search(query, filters_json, limit)
vault_entity_lookup(name_or_alias)
vault_timeline(entity_or_topic, start, end)
vault_evidence(assertion_id)
vault_ingest_status(source_id)
vault_propose_accept(assertion_id)
vault_supersede(assertion_id, reason)
```

Query-time architecture:

```text
Agent question
  -> L1 search: recent decisions/todos/action state
  -> L2 ripgrep: accepted human-readable synthesis
  -> L3 vault search: semantic + graph + temporal evidence
  -> rerank by lifecycle, recency, salience, confidence
  -> answer with citations to artifact/chunk/assertion IDs
```

For a question like “What did person X and I discuss about Project Y in 2023?”:

```sql
SELECT
  a.occurred_at,
  a.title,
  c.chunk_id,
  DBMS_LOB.SUBSTR(c.text_content, 1000, 1) AS excerpt,
  VECTOR_DISTANCE(v.embedding, :query_vec, COSINE) AS distance
FROM vault_entities p
JOIN vault_entity_mentions pm ON pm.entity_id = p.entity_id
JOIN vault_chunks c ON c.chunk_id = pm.chunk_id
JOIN vault_artifacts a ON a.artifact_id = c.artifact_id
JOIN vault_chunk_vectors v ON v.chunk_id = c.chunk_id
JOIN vault_entity_mentions topic_m ON topic_m.chunk_id = c.chunk_id
JOIN vault_entities topic ON topic.entity_id = topic_m.entity_id
WHERE p.entity_type = 'person'
  AND p.canonical_name = :person_name
  AND topic.canonical_name = :project_name
  AND a.occurred_at >= TIMESTAMP '2023-01-01 00:00:00'
  AND a.occurred_at <  TIMESTAMP '2024-01-01 00:00:00'
ORDER BY a.occurred_at, distance
FETCH FIRST 25 ROWS ONLY;
```

But the agent should call `vault_timeline(...)`, not emit SQL itself. The API should translate intent into safe parameterized SQL, enforce redaction rules, and return cited evidence.

**Bottom line:** Build L3 as an evidence graph with vector search, not as cloud sync for `knowledge_items`. Keep L1/L2 mandatory and simple. Make Oracle optional, powerful, and API-gated.

```json
{
  "agent": "codex",
  "role": "reviewer",
  "task": "Round 1 independent proposal for Oracle as optional L3 Vault deep-brain architecture covering schema, absorb integration, migration, onboarding, and query architecture.",
  "findings": [
    {
      "type": "risk",
      "description": "The current Oracle terminology appears inconsistent: local docs/UI refer to Oracle as L4 while the proposed architecture frames it as L3. This should be resolved before onboarding or schema work.",
      "file": "webapp/index.html"
    },
    {
      "type": "risk",
      "description": "The existing flat knowledge-item model is insufficient for temporal, entity-centric recall across emails/documents because it lacks first-class sources, artifacts, chunks, entity mentions, relationships, and assertion lifecycle.",
      "file": "skills/memory-server/mcp_memory/server.py"
    },
    {
      "type": "decision",
      "description": "Recommend keeping L1 SQLite and L2 Git Wiki as the default product baseline while making Oracle an optional API-gated evidence graph with vector search and lifecycle/provenance tracking.",
      "file": null
    }
  ],
  "summary": "Proposed an Oracle Vault design centered on source-grounded artifacts, chunks, vectors, entities, relationships, assertions, taxonomy classifications, and lifecycle events. Recommended extending absorb into a three-target pipeline that writes operational state to L1, accepted synthesis to L2, and evidence plus extracted graph data to L3. Proposed a lossless staged migration from the legacy knowledge table and an API/MCP query layer instead of direct agent SQL.",
  "disagreements": [
    "Oracle should not remain only a passive sync target for the owner’s deep-brain use case.",
    "A flat knowledge table plus tags is not an adequate knowledge-management schema for long-range personal/corporate recall.",
    "Agents should not directly query Oracle SQL except through vetted memory-server/Vault tools."
  ]
}
```
