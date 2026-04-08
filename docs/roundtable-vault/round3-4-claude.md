# Round 3-4 — Claude (CIO) Synthesis

## Dispute Resolutions

### DISPUTE 1: Schema rigidity vs flexibility → **Typed tables + JSON overflow (Claude's position wins)**

**Decision:** Fixed columns for all queryable fields. A `metadata_json CLOB CHECK (IS JSON)` column on each table for extensible attributes. No EAV properties tables.

**Why:** 
- Gemini's EAV requires N JOINs per N properties — unacceptable for a query-heavy system
- Codex's 12 rigid tables are complete but over-normalized for Day 1
- JSON overflow gives flexibility WITHOUT killing query performance
- Oracle 23ai has native JSON_TABLE and JSON_VALUE indexing — we get the best of both worlds

### DISPUTE 2: Table count → **9 tables (compromise)**

**Decision:** 9 vault tables + existing operational tables:

| # | Table | Purpose |
|---|-------|---------|
| 1 | `vault_sources` | Where data came from (email account, folder, API, manual) |
| 2 | `vault_documents` | Raw artifacts — emails, notes, files, conversations |
| 3 | `vault_chunks` | Chunked content with individual vector embeddings |
| 4 | `vault_entities` | People, companies, projects, concepts, locations |
| 5 | `vault_entity_aliases` | Name variants for entity resolution |
| 6 | `vault_facts` | Extracted atomic claims/assertions with provenance |
| 7 | `vault_relations` | Typed edges between any vault objects |
| 8 | `vault_events` | Immutable lifecycle event log |
| 9 | `vault_sync_log` | L1/L2 → L3 sync tracking |

**What was cut from Codex's 12:**
- `vault_entity_mentions` → merged into `vault_relations` (entity→chunk relation with mention_role)
- `vault_chunk_vectors` → merged into `vault_chunks` (embedding column directly on chunk)
- `vault_classifications` → `taxonomy_id` FK on documents/entities/facts
- `vault_taxonomy_nodes` → reuse existing `taxonomy` table (just expand it)

### DISPUTE 3: UUID vs IDENTITY → **NUMBER IDENTITY (Claude's position wins)**

**Decision:** `NUMBER GENERATED ALWAYS AS IDENTITY` for all PKs.

**Why:**
- Single owner system — no cross-machine PK collision risk
- Oracle IDENTITY is 8 bytes vs UUID's 36 bytes — faster joins, smaller indexes
- The `vault_sync_log` already handles L1↔L3 mapping — no need for UUIDs
- If multi-machine is needed later, add a `machine_id + local_id` composite

## Enrichment Pipeline

```
Source → vault_sources (deduplicate by URI hash)
  → vault_documents (raw artifact, occurred_at, source metadata)
    → vault_chunks (split long content, generate embeddings)
      → LLM extraction:
        → vault_entities + vault_entity_aliases (NER)
        → vault_facts (atomic claims with confidence)
        → vault_relations (entity↔document, entity↔entity, fact↔document)
      → vault_events (log each stage transition)
```

Pipeline modes:
- **Fast**: Source → Document → Chunks + Embeddings (no LLM, just storage + vectors)
- **Full**: Fast + Entity extraction + Fact extraction + Relations (LLM required)
- **Batch**: Run Full enrichment on existing documents that were ingested in Fast mode

## Vault API Functions

```python
# Core CRUD
vault_ingest(content, doc_type, meta, source_info) → doc_id
vault_enrich(doc_id, mode="full") → enrichment_summary

# Search
vault_search(query, filters=None, limit=10) → [{doc, chunk, score, citations}]
vault_about(entity_name) → {entity, documents, facts, relations, timeline}
vault_timeline(entity=None, topic=None, start=None, end=None) → [events]

# Graph
vault_relations(entity_id, depth=2) → {nodes, edges}
vault_entity_resolve(name_or_alias) → entity

# Lifecycle
vault_accept(fact_id) → updated_fact
vault_supersede(fact_id, new_fact_id, reason) → event

# Admin
vault_stats() → {counts, health}
vault_doctor() → {connection, schema_version, index_health}
```

## Confidence: 0.88

High confidence on the core design. Remaining uncertainty:
- Exact chunking strategy (fixed-size vs semantic) needs empirical testing
- Embedding model choice (text-embedding-3-small vs local alternatives) 
- LLM extraction prompt quality will need iteration
