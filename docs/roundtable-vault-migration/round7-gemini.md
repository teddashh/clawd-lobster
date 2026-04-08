# Round 7 — Gemini (2.5 Pro): Universal Ingestion Architecture

This round of analysis moves from the theoretical soundness of our 11-table schema to its practical application against the ultimate stress test: Ted's goal of a universal "everything store." The consensus schema is flexible, with `vault_documents` as the central hub and `doc_type` as the primary differentiator. Now, we must scrutinize the architectural patterns and ancillary systems required to make this schema performant, reliable, and useful as it scales from 86,000 emails to over a million heterogeneous documents. My analysis focuses on the journey of data—from the outside world into the vault, how it lives and changes within the vault, and how it is ultimately retrieved.

### 1. Data Lifecycle Management: The Challenge of Mutability

The current schema, at first glance, appears optimized for immutable, point-in-time artifacts like emails, photos, and financial transactions. An email, once sent, does not change. This is a solved problem. The greater challenge lies with "living documents": a personal wiki page in Obsidian, a project plan in a Google Doc, a script in a code repository, or even the transcript of this very debate. These documents evolve.

A simple `UPDATE` on a document row is insufficient as it destroys history, which is antithetical to the vault's purpose. We must treat every document as an event stream.

**Proposed Architecture:**
I propose a formal versioning system within `vault_documents`.
*   **Stable Identifier (`document_id`):** This UUID represents the conceptual document (e.g., the "Project Phoenix Spec"). It never changes.
*   **Version Pointer (`row_id`, `version_number`):** Each save/edit creates an entirely *new row* in `vault_documents`. This new row gets a new primary key (`row_id`) but shares the same `document_id` as all other versions of that document. A `version_number` column, incremented on each new entry, provides explicit ordering.
*   **Current Version Flag (`is_latest`):** A boolean flag, `is_latest`, is critical for performance. For any given `document_id`, only one row will have `is_latest = TRUE`. This allows agents to quickly retrieve the most current version without scanning all previous versions. When a new version is ingested, a transaction must update the previous "latest" to `FALSE` and insert the new version with `TRUE`.

This approach naturally extends to `vault_chunks`. Chunks must be associated not just with a `document_id`, but with a specific `row_id` (the document version). This prevents a query from retrieving a chunk of text from version 1 that was deleted in version 5. It ensures that any reconstructed document is a perfect snapshot of a specific point in time. The cost is increased storage, but the benefit is a complete, auditable history of all information, which is a core requirement.

### 2. Ingestion Pipeline Design: From Chaos to Coherence

The `absorb` skill is the gatekeeper to the vault. It cannot be a monolithic function but must be a sophisticated routing and processing engine—a system of specialized adapters.

**Conceptual Pipeline Stages:**
1.  **Triage:** The `absorb` function receives an input (URL, file path, text blob, API object). It first identifies the input's nature. A URL for `github.com` is different from `youtube.com`. A file ending in `.pdf` requires a different handler than `.eml` or `.m4a`. This is a router, mapping input signatures to specific parsers.
2.  **Extraction:** Each parser is a specialist:
    *   **Emails (.eml, .mbox, IMAP):** Extract `From`, `To`, `CC`, `Subject`, `Date`, and body (HTML and plain text). These key fields are promoted to dedicated columns in `vault_documents`, while the full headers go into `metadata_json`.
    *   **Chats (LINE/FB JSON exports):** Parse conversation threads, identifying participants, timestamps for each message, and reactions. Each chat log could be one document, or a long-running chat could be chunked by time (e.g., one document per day/week).
    *   **PDFs/Images/Scanned Notes:** This is an OCR-first workflow. The file is sent to an OCR engine (e.g., Tesseract or a cloud vision API). The extracted text becomes the document's content. The `metadata_json` should store OCR confidence scores and bounding box information, and a link to the original file in an object store is essential.
    *   **Voice Memos/Videos:** A Speech-to-Text (STT) workflow, using a model like Whisper. The resulting transcript is the primary content. The original media file is archived and linked.
    *   **Code Repositories:** On `absorb(git_url)`, the pipeline should `git clone` the repo. It should then iterate through every file, treating each as a potential document. The file's path, and maybe even its `git blame` information, become valuable metadata. A `git log` could be ingested as its own separate document summarizing the project's history.
3.  **Standardization:** Each parser must output a standardized object, let's call it a `PreDocument`, containing `content` (the extracted text), `doc_type`, and a `metadata` dictionary.
4.  **Loading & Asynchronous Post-Processing:** The `PreDocument` is used to create the entry in `vault_documents`. Once the document is saved, the system triggers *asynchronous* jobs for chunking, embedding, entity extraction (`vault_entities`, `vault_aliases`), and fact/relation extraction (`vault_facts`, `vault_relations`). This ensures the initial ingestion is fast and responsive, while the computationally intensive AI-driven analysis happens in the background.

### 3. Storage Efficiency: The Vector Tax

The promise of semantic search comes at a cost: storing vector embeddings. Let's quantify it.
*   A 1536-dimension vector using 4-byte floats (`FLOAT4`) requires `1536 * 4 = 6,144` bytes, or roughly **6 KB per vector**.
*   For **500,000 chunks**, the storage required for the vectors alone is `500,000 * 6 KB = 3,000,000 KB`, which is **3 GB**.

This calculation is conservative. It doesn't include the text of the chunks themselves, the main document content, other tables, indexes, or database WALs. A 3 GB vector index will immediately disqualify most "Always Free" database tiers, which often cap out at 500 MB to 1 GB of total storage. Ted must budget for a paid, dedicated database plan. This "vector tax" is a significant, recurring operational cost that scales linearly with the number of chunks.

**Mitigation Strategies:**
*   **Intelligent Chunking:** Don't embed everything. Short, non-descriptive chunks or boilerplate can be excluded.
*   **Embedding Model Selection:** Newer models (like OpenAI's `text-embedding-3-small`) offer strong performance with smaller dimensions (512), reducing storage by 66%.
*   **Quantization:** Advanced vector databases support techniques like Scalar or Product Quantization, which compress vectors by trading a small amount of precision for a massive reduction in storage size (up to 90%+). This should be a key requirement when choosing the database technology.

### 4. Query Patterns: The Search for the Holy Grail

The schema can store anything, but can agents *find* anything? A user query like, "What was the final decision about Project Arc from the meeting with legal in Q4 last year?" is a complex multi-stage operation.

A successful query engine cannot rely solely on vector search. It must be a **hybrid search** system:
1.  **Metadata Filtering (The SQL Pass):** The agent first deconstructs the query to identify metadata filters.
    *   "final decision" -> `JOIN vault_facts ON ... WHERE fact_type = 'decision'`
    *   "Project Arc" -> `JOIN vault_entities ON ... WHERE vault_entities.name = 'Project Arc'`
    *   "meeting" -> `WHERE doc_type = 'meeting_transcript'`
    *   "legal" -> `JOIN vault_entities ...` (resolving "legal" to a specific team or person entity)
    *   "Q4 last year" -> `WHERE created_at BETWEEN '2025-10-01' AND '2025-12-31'`
    This initial pass dramatically narrows the search space from millions of chunks to perhaps a few hundred relevant ones.
2.  **Semantic Search (The Vector Pass):** Only now, on this much smaller, pre-filtered set of chunks, does the agent perform the vector search. This makes the search faster and vastly more accurate, as it's not being distracted by semantically similar but contextually irrelevant chunks from other domains.

This proves the synergy between the structured tables (`vault_entities`, `vault_facts`) and the unstructured `vault_chunks` is not just beneficial; it's the only viable path to success at scale.

### 5. The 'absorb' Skill Revisited

Based on the above, the `absorb` skill is the public-facing API for the ingestion pipeline. Its interface should be simple, but its implementation complex and asynchronous.

`job_id = absorb(source: Union[URL, FilePath, RawText], params: Dict)`

It immediately returns a `job_id`. The agent can then use `get_job_status(job_id)` to poll the progress. This prevents blocking and allows for the ingestion of large sources (like a full code repository) without timing out. The `params` dictionary could contain hints for the pipeline, e.g., `{ "doc_type": "legal_contract" }` to bypass heuristics, or `{ "priority": "high" }` to move it up the queue.

### 6. Cross-Platform Entity Resolution

The `vault_entity_aliases` table is the correct tool, but automating its population is a grand challenge. My proposed strategy is a continuous, iterative process:

1.  **Heuristic Linking:** On ingestion, extract obvious alias candidates (email addresses, phone numbers, profile URLs). If a new document contains an alias already linked to an entity, provisionally link the new document to that entity.
2.  **Probabilistic Clustering:** A background agent continuously analyzes the `vault_entity_aliases` table. It looks for clusters. For example, if alias "Dr. Robert Smith", alias "Bob S.", and alias "r.smith@hospital.com" frequently co-occur in the same documents (especially with other entities like "Cardiology Dept"), the agent can propose a high-confidence merge.
3.  **Human-in-the-Loop:** The system will make mistakes. There *must* be a simple interface for Ted to confirm or deny proposed entity merges. "Is 'Bobby' (from LINE) the same person as 'Robert Jones' (from email)?" Every manual confirmation becomes high-quality training data that makes the probabilistic clustering agent smarter over time.

### 7. Retention and Archival: Data Temperature

Not all data has equal value over time. A 15-year-old news clipping is less likely to be needed instantly than this week's meeting notes. We should introduce the concept of "data temperature."

*   **Hot:** Recent documents, frequently accessed documents, or documents manually marked as "core memory." All data (content, chunks, vectors) resides in the primary, high-performance database.
*   **Warm:** Documents not accessed for >1 year. The full text `content` could be compressed within the database to save space.
*   **Cold:** Documents not accessed for >5 years. The `vault_chunks` and their embeddings can be deleted. The primary `content` can be moved to a cheap, slow object store (like AWS S3 Glacier Deep Archive). The document row remains, but the `content` field is replaced by a URI pointing to the archived file. A query might still find the document via its metadata, but retrieving the content would be a slow, manual "rehydration" process.

This requires adding `last_accessed_at` and `access_count` columns to `vault_documents` and a background process to manage the data lifecycle based on defined policies.

### 8. The Biggest Risk: The Semantic Haystack

At 1 million documents and perhaps 20-30 million chunks, the single greatest risk of architectural failure is **query relevance**.

The problem is not finding a needle in a haystack; it's being handed a thousand needles when you only asked for one. As the vault grows, so does the semantic "surface area." More chunks mean a higher probability that any given query vector will have spurious matches with contextually nonsensical but semantically adjacent chunks. "What did the board decide?" could match a chunk from a chess blog about a move on a board.

The only defense against this is the aggressive, multi-stage hybrid query strategy outlined in point #4. If the implementation of the query agent is naive—if it relies too heavily on vector search without first ruthlessly pruning the search space with metadata filters—the entire vault will collapse under the weight of its own irrelevance. The user experience will be death by a thousand "related" but useless results. The architecture will have succeeded in storing everything but failed at finding anything. A digital landfill.

---
**Confidence Score:** 8/10 on the schema's long-term viability.
**Top 3 Concerns:**
1.  **Query Relevance Collapse:** Failure to implement a sophisticated hybrid search engine will render the vault useless at scale.
2.  **Ingestion Pipeline Brittleness:** The `absorb` skill and its many parsers are a massive, ongoing development and maintenance burden. If data isn't parsed and structured correctly on entry, it's garbage in, garbage out.
3.  **Unchecked Operational Costs:** The cost of embedding APIs, vector storage, and potential proprietary OCR/STT services will scale linearly and can easily become prohibitive if not carefully managed and budgeted for from day one.
