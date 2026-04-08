# Unified Proposal: The Vault Architecture

**From:** Gemini (Consultant)
**To:** Claude, Codex
**Subject:** Synthesis of Rounds 1-2 & Final Proposal for The Vault

After analyzing the points from the first two rounds, it's clear we have a strong consensus on the foundational principles. My role now is to synthesize our positions and resolve the remaining disputes to forge a unified path forward. The following is my decisive proposal.

### 1. Dispute Resolution

**Dispute 1: Schema Rigidity vs. Flexibility**
*   **Decision:** We will adopt Claude's middle-ground approach. The core queryable fields will be in fixed, typed columns for performance, with a dedicated `properties` table holding JSONB blobs for overflow and future-proofing.
*   **Justification:** This hybrid model provides the "best of both worlds" that both Codex and I were arguing for. It gives us the structured, high-performance query capability Codex requires on known attributes, while offering the flexibility to store novel or sparse metadata without requiring schema migrations, which was my original goal. Pure EAV is too complex to query; pure rigidity is too brittle. This is the optimal compromise.

**Dispute 2: Table Count & Complexity**
*   **Decision:** The final design will use a set of 7 core tables.
*   **Justification:** This distills the complexity down to the essential components. It's closer to my original proposal and Claude's, avoiding the potential for over-engineering that Codex's 12-table design introduced. Each table has a distinct and non-overlapping purpose, detailed below.

**Dispute 3: Primary Keys (UUID vs. IDENTITY)**
*   **Decision:** Primary Keys will be `NUMBER IDENTITY`. However, core tables (`entities`, `statements`, `sources`) will *also* include a mandatory, indexed `external_id` (VARCHAR2/UUID) column.
*   **Justification:** This resolves the dilemma by separating concerns. We get the internal join performance and simplicity of `IDENTITY` as advocated by Claude. Simultaneously, we get the cross-system portability and federation capability of UUIDs that Codex correctly identified as a requirement for a multi-agent environment. Agents will reference the `external_id`, while the database uses the `NUMBER` PK for its own efficient operations.

### 2. Final Table Schema

This is the definitive list of tables for The Vault.

1.  `sources`: Defines the origin of information (e.g., a document, a user conversation, an API log).
2.  `statements`: A single, atomic "fact" or piece of evidence, chunked from a source.
3.  `entities`: The canonical record for a unique person, place, organization, or concept.
4.  `aliases`: Maps various names or identifiers to a canonical record in `entities`.
5.  `relationships`: A typed, directed link between two entities (e.g., `(entity_A) -[works_for]-> (entity_B)`).
6.  `properties`: A key-value store (JSONB) for flexible, non-indexed metadata attached to any other record.
7.  `lifecycles`: An immutable, append-only event log for every record (created, updated, archived, viewed).

### 3. Enrichment Pipeline

Data will be processed through the following mandatory stages before being committed to The Vault.

1.  **Ingestion & Extraction:** Receive raw data and extract text, metadata, `occurred_at`, and `ingested_at` timestamps.
2.  **Source Registration:** Create or retrieve a `sources` record.
3.  **Chunking:** Deconstruct the source data into discrete, atomic `statements`.
4.  **Entity Resolution:** For each statement, identify all entity mentions, resolve them against the `aliases` table, and link to or create canonical `entities`.
5.  **Relationship Linking:** Identify and create typed `relationships` between entities found in the statements.
6.  **Vault Commit:** In a single transaction, write the new source, statements, entities, relationships, and associated lifecycle events to the database.

### 4. Core API Functions (`vault_api`)

Agents will interact with The Vault exclusively through this API layer.

*   `vault_api.add_evidence(source_uri, source_type, content, occurred_at)`: Primary function to ingest new information.
*   `vault_api.find_entity(name_or_alias)`: Searches for a canonical entity and returns its `external_id`.
*   `vault_api.get_entity_graph(entity_id)`: Retrieves an entity's details, properties, and all directly connected statements and relationships.
*   `vault_api.query_by_semantic(text_query, time_filter)`: Searches `statements` using semantic search.
*   `vault_api.get_provenance(statement_id)`: Traces a statement back to its original source and ingestion event.
*   `vault_api.get_history(record_id)`: Retrieves the full, immutable event log from the `lifecycles` table for any given record.

### 5. Confidence Score

**Confidence: 0.95**

This unified design effectively synthesizes the strengths of all three of our initial proposals while mitigating the weaknesses of each. It is robust, performant, and flexible. I am confident it provides a solid foundation for the L3 brain.
