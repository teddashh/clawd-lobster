# Round 2 — Claude (CIO) Cross-Review

## Review of Proposal B (Codex)

### Scores
| Dimension | Score | Notes |
|-----------|-------|-------|
| Practicality | 7 | Solid but 12 tables is a lot to maintain |
| Completeness | 9 | Most thorough — covers entity aliases, mentions, lifecycle events |
| Query Power | 9 | Chunk-level entity mentions enable precise citation |
| Simplicity | 5 | Too many tables, VARCHAR2(64) UUIDs add friction vs NUMBER IDENTITY |
| Migration Ease | 7 | Staged approach is sound |

### Strongest Ideas to Keep
1. **Explicit chunking layer** — splitting content into chunks with individual vectors is essential for long documents (emails are short, but reports and code files need chunking). My proposal missed this.
2. **Entity aliases table** — critical for name resolution ("David", "David Chen", "陳大衛" should all resolve to one entity). My proposal put aliases in a JSON column, which is harder to query.
3. **vault_lifecycle_events as immutable audit trail** — better than my approach of just storing current lifecycle state. History matters.

### Biggest Weakness
- **12 tables is over-engineered for Day 1.** `vault_classifications` as a separate junction table adds complexity when a simple `taxonomy_id` FK on each table works. `vault_lifecycle_events` is nice-to-have but can be added later. Start with 7-8 tables, not 12.
- **VARCHAR2(64) UUIDs vs NUMBER IDENTITY** — UUIDs are good for cross-machine sync but Oracle's IDENTITY columns are faster for local joins. For a single-owner Vault, IDENTITY is simpler.
- **No clear view/materialized-view strategy** — with 12 tables, common queries will need 5+ JOINs. Need `VAULT_ARTIFACT_SUMMARY` view at minimum.

## Review of Proposal C (Gemini)

### Scores
| Dimension | Score | Notes |
|-----------|-------|-------|
| Practicality | 6 | Graph model is elegant but EAV properties are a query nightmare |
| Completeness | 6 | Missing entity aliases, no chunking strategy, lifecycle only on nodes |
| Query Power | 7 | Flexible but slow — key-value properties can't be indexed efficiently |
| Simplicity | 8 | Fewest tables, most conceptually clean |
| Migration Ease | 7 | Simple node creation, but lacks type-specific handling |

### Strongest Ideas to Keep
1. **Everything is a node** — the philosophical simplicity is appealing. A Decision is just a node with type='Decision'. This makes the graph truly universal.
2. **Edges with provenance** — every relationship carries its own source_id. This is cleaner than my approach.
3. **content_chunks separate from nodes with VECTOR INDEX** — explicit vector index syntax.

### Biggest Weakness
- **EAV (Entity-Attribute-Value) properties tables are an anti-pattern for querying.** To find "all emails from David in 2023" you need: nodes JOIN node_properties (for sender) JOIN node_properties (for date) — each property is a separate row, so queries get exponentially complex. Fixed columns with JSON overflow is much better.
- **No distinction between documents and entities** — both are "nodes." But a Document has content, a Person has attributes. Forcing them into the same table either wastes columns or pushes everything to key-value.
- **Missing entity resolution** — no alias table, no mention tracking. How do you know "David" in email #123 is the same person as "David Chen" in email #456?

## Non-Negotiables I'll Defend in Round 3

1. **Chunking is required** — long documents must be split for accurate vector search. Codex is right here.
2. **Entity aliases must be first-class** — not JSON, not properties. A real table with normalized lookup.
3. **No EAV for core attributes** — use fixed columns + JSON overflow column. Properties tables kill query performance.
4. **API layer is mandatory** — agents never write SQL. `vault_api.py` or MCP tools.
5. **Lifecycle state on every record type** — not just nodes.
6. **Occurred_at vs ingested_at distinction** — temporal queries need the real event date.
