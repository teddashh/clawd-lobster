# Round 6 — Universal Ingestion Stress Test

> **Question from the owner**: Can this schema truly absorb EVERYTHING? Debate transcripts, desktop files, research PDFs, Facebook posts, LINE chat history, and anything else imaginable?

## The Universe Test

Let's throw every conceivable data type at the 11-table schema and see if it breaks.

| # | Data Type | Example | Fits? | How? |
|---|-----------|---------|-------|------|
| 1 | **Work emails** | 86K from ACME | YES | vault_documents (doc_type='email') — already planned |
| 2 | **AI debate transcripts** | This very debate | YES | vault_documents (doc_type='debate_transcript'), source='clawd-lobster-roundtable' |
| 3 | **Desktop files** | Word docs, Excel, PPT | YES | vault_documents (doc_type='file'), metadata_json has {path, size, mime_type, modified_at} |
| 4 | **Research PDFs** | Academic papers, reports | YES | vault_documents (doc_type='pdf'), content = extracted text, vault_chunks for pages |
| 5 | **Facebook posts** | 所有發過的文章 | YES | vault_documents (doc_type='social_post'), metadata_json = {platform:'facebook', post_id, likes, comments, shares, audience} |
| 6 | **LINE 對話** | 跟朋友的聊天記錄 | YES | vault_documents (doc_type='chat_message' or 'conversation'), metadata_json = {platform:'line', participants, room_id} |
| 7 | **WhatsApp 對話** | 同上 | YES | Same pattern, platform='whatsapp' |
| 8 | **Photos** | 照片+metadata | YES | vault_documents (doc_type='image'), content = EXIF/description, metadata_json = {camera, gps, dimensions, faces_detected} |
| 9 | **Meeting recordings** | Zoom/Teams 錄影 | YES | vault_documents (doc_type='meeting_transcript'), content = transcription text |
| 10 | **Code repos** | Git commits, PRs | YES | vault_documents (doc_type='code_artifact'), metadata_json = {repo, branch, commit_sha, language} |
| 11 | **Financial records** | 發票、帳單、薪資單 | YES | vault_documents (doc_type='financial_record'), privacy_level='secret', ownership='self' |
| 12 | **Health records** | 體檢報告、處方 | YES | vault_documents (doc_type='health_record'), privacy_level='secret', ownership='self' |
| 13 | **Web bookmarks** | 收藏的網頁 | YES | vault_documents (doc_type='webpage'), metadata_json = {url, archived_at, tags} |
| 14 | **Voice memos** | 語音筆記 | YES | vault_documents (doc_type='voice_memo'), content = transcription |
| 15 | **Handwritten notes** | 掃描的筆記 | YES | vault_documents (doc_type='scan'), content = OCR text |
| 16 | **Tweets/X posts** | 社群媒體 | YES | vault_documents (doc_type='social_post'), platform='twitter' |
| 17 | **Slack/Discord** | 工作通訊 | YES | vault_documents (doc_type='chat_message'), platform='slack' |
| 18 | **Contracts/Legal** | 合約、法律文件 | YES | vault_documents (doc_type='legal_document'), privacy_level='restricted' |
| 19 | **Recipes/Personal** | 食譜、旅遊筆記 | YES | vault_documents (doc_type='note'), ownership='self', taxonomy=personal/* |
| 20 | **News articles** | 剪報、重要新聞 | YES | vault_documents (doc_type='news_article'), ownership='external' |

**Result: 20/20 pass.** Every data type maps to vault_documents with a different `doc_type`.

---

## Claude's Analysis

The schema works because of **three design principles**:

### 1. Content is always text (or extractable to text)
- PDF → extracted text
- Image → EXIF + description + OCR
- Audio → transcription
- Video → transcription + metadata
- Binary file → metadata only (size, type, hash)

The `content` CLOB stores the text representation. The original binary stays in its original storage (filesystem, cloud). The Vault stores the **knowledge extracted from it**, not the raw binary.

### 2. Structure varies, but metadata_json absorbs it
Every data type has unique fields:
- Email: from, to, cc, thread_id
- Facebook: likes, shares, audience
- Photo: GPS, camera, faces
- Financial: amount, currency, vendor

All of these go in `metadata_json`. No new columns needed per type.

### 3. The graph layer connects everything
Once content is in vault_documents, the enrichment pipeline extracts:
- **Entities**: people, places, companies, products mentioned
- **Facts**: atomic claims with confidence
- **Relations**: who said what to whom about what

This means "show me everything about David Chen" returns: emails he sent, LINE chats mentioning him, photos he's in, meetings he attended, Facebook posts about shared events — all unified through the entity graph.

---

## Codex's Adversarial Challenge

### Challenge 1: Chat messages are NOT documents
A LINE conversation with 5,000 messages — is each message a vault_document? That's massive overhead. 

**Resolution**: Two options:
- **Option A (per-conversation)**: One vault_document per conversation thread, content = full export. Then vault_chunks splits into individual messages. This is the recommended approach — matches how chat exports work (one file per conversation).
- **Option B (per-message)**: Each message is a vault_document. Only for high-value channels where individual message search matters.

**Consensus: Option A for bulk import. Option B only for real-time ingestion via bot.**

### Challenge 2: Binary files (images, PDFs)
The Vault stores TEXT, not binaries. Where do the original files live?

**Resolution**: The Vault is an **index**, not a file server. Original files stay wherever they are (filesystem, Google Drive, iCloud). vault_documents stores:
- `content`: extracted text (OCR, transcription, metadata)
- `metadata_json.original_path`: pointer to the original file
- `metadata_json.file_hash`: SHA-256 for integrity verification
- `embedding`: vector of the extracted text

This is the correct design. A database should store structured data, not blobs.

### Challenge 3: Scale projection
If the owner imports everything:
- 86K emails ✓ (already planned)
- 1,865 daily reports ✓
- ~5,000 LINE conversations (each = 1 doc + many chunks)
- ~2,000 Facebook posts
- ~10,000 files from desktop/Documents
- ~500 PDFs
- ~1,000 photos (metadata only)
- ~100 meeting transcripts

**Total: ~105,000 vault_documents, ~500,000 vault_chunks**

Oracle handles this easily. Even on Always Free tier, this is well within capacity.

### Challenge 4: Privacy collision
What if a LINE chat with a friend mentions work stuff? Or a work email has personal content?

**Resolution**: The `ownership` axis is about the DOCUMENT's origin, not its content:
- LINE chat with friend = ownership='shared', privacy='internal'
- Work email = ownership='work', privacy='internal'

If a work email discusses the owner's personal health → the document is `ownership='work'`, but any extracted health-related facts should be tagged `ownership='self'`, `privacy='secret'`.

**The ownership of extracted facts can differ from the source document.** This is by design.

---

## Gemini's Architecture Validation

### The Absorb Skill Pattern
Every new data source follows the same pipeline:

```
1. SOURCE REGISTRATION
   vault_sources: {type:'line_export', uri:'line://chat/david-chen', display_name:'LINE: David Chen'}

2. DOCUMENT CREATION  
   vault_documents: {doc_type:'conversation', content:full_export_text, metadata_json:{platform, participants, date_range}}

3. CHUNKING
   vault_chunks: split by message or by time window (e.g., per-day chunks)

4. ENRICHMENT (async, LLM-powered)
   vault_entities: extract mentioned people, places, topics
   vault_facts: extract claims, plans, promises
   vault_relations: link entities to documents and chunks

5. METRICS (nightly cron)
   vault_metrics: messages_per_day, top_contacts_by_month, sentiment_trend
```

This pattern works for ALL 20 data types listed above. **Zero schema changes needed per new source type.**

### The doc_type Registry
To keep things organized, we should maintain a registry of known doc_types:

| doc_type | Description | Source Examples |
|----------|-------------|----------------|
| email | Email message | Outlook, Gmail |
| conversation | Chat thread | LINE, WhatsApp, Slack, Discord |
| chat_message | Single chat message | Real-time bot ingestion |
| daily_report | Daily work narrative | OpenClaw cron |
| note | Knowledge article | Obsidian, manual |
| sop | Standard procedure | Manual |
| file | General file content | Desktop, cloud storage |
| pdf | PDF document | Research papers, reports |
| social_post | Social media post | Facebook, Twitter/X, LinkedIn |
| image | Photo/image metadata | Camera, screenshots |
| meeting_transcript | Meeting recording text | Zoom, Teams |
| code_artifact | Code-related content | Git, PRs, issues |
| calendar_event | Calendar entry | Outlook, Google Calendar |
| financial_record | Financial document | Invoices, receipts |
| health_record | Health document | Medical reports |
| legal_document | Legal/contract | Contracts, NDAs |
| news_article | News/article clip | RSS, web archive |
| voice_memo | Voice note transcript | Phone recordings |
| scan | Scanned document | OCR'd paper documents |
| debate_transcript | AI debate record | Roundtable outputs |
| webpage | Archived web page | Bookmarks, web clips |

This is NOT enforced by a CHECK constraint (that would be too rigid). It's a convention, documented in the spec. New types can be added without DDL changes.

---

## Final Verdict

### Can the schema absorb everything the owner has ever created or received?

**YES.** Unanimously confirmed.

The key insight: **The Vault doesn't store files. It stores KNOWLEDGE EXTRACTED FROM files.** The schema is type-agnostic at the storage layer (everything is a document with text content and JSON metadata) but type-aware at the enrichment layer (different doc_types get different extraction prompts).

### Remaining concern: Ingestion tooling

The schema is ready. What we DON'T have yet:
- LINE export parser
- Facebook data export parser  
- PDF text extractor (can use pymupdf or pdfplumber)
- Image metadata extractor (can use Pillow/exiftool)
- General file scanner (walk directory, extract text)

These are **absorb skill plugins**, not schema changes. Each parser converts its source format into the standard `vault_api.ingest()` call.

### Updated Confidence Scores

| Agent | Score | Note |
|-------|-------|------|
| Claude | 0.92 | Schema proven universal across 20+ data types |
| Codex | 0.88 | Concerns about chat message granularity resolved |
| Gemini | 0.93 | Architecture validated — ingestion pattern is repeatable |

**Overall consensus: 0.91 — APPROVED for implementation.**
