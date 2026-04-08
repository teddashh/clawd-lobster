# Absorb + Vault Integration — Software Design Document

> **Status:** DRAFT
> **Date:** 2026-04-07
> **Author:** Claude (CIO)
> **Spec Type:** OpenSpec SDD
> **Depends on:** VAULT-ARCHITECTURE.md, Round 11 Final Consensus

---

## 1. Problem Statement

The existing `absorb` skill extracts knowledge from codebases/repos/URLs and stores it in L1 (SQLite) + L2 (Git Wiki) via memory-server. It cannot:

- Ingest arbitrary file types (PDF, images, chat exports, emails, voice memos)
- Store structured entities, facts, and relations (knowledge graph)
- Perform vector-based semantic search across all ingested content
- Handle versioning of living documents
- Classify content by ownership/privacy/fidelity

**Goal:** Make `absorb` the universal ingestion gateway that routes content through format-specific parsers into The Vault (Oracle L3), while maintaining backward compatibility with L1+L2 for users without Oracle.

---

## 2. Architecture Overview

```
User: "absorb ~/Desktop/important_docs/"
         │
         ▼
┌─────────────────────┐
│   absorb skill      │  (entry point — prompt-pattern + Python backend)
│   ┌─────────────┐   │
│   │ ParserRouter │   │  Detects source type → selects parser(s)
│   └──────┬──────┘   │
│          ▼          │
│   ┌─────────────┐   │
│   │ Parser(s)   │   │  Format-specific: PDF, LINE, Email, Image, etc.
│   │ → PreDoc[]  │   │  Each outputs List[PreDocument] (standard format)
│   └──────┬──────┘   │
│          ▼          │
│   ┌─────────────┐   │
│   │ DedupEngine │   │  3-layer: content_hash → original_path → new
│   └──────┬──────┘   │
│          ▼          │
│   ┌─────────────┐   │
│   │ vault_api   │   │  .ingest() / .bulk_ingest() → Oracle L3
│   │ .ingest()   │   │  Falls back to memory-server if no Oracle
│   └─────────────┘   │
└─────────────────────┘
```

### Layer Routing

| Oracle L3 available? | Where data goes |
|---------------------|-----------------|
| YES | vault_api.ingest() → Oracle vault_documents + entities + facts |
| NO | memory-server → SQLite L1 + Git Wiki L2 (existing behavior) |

The skill auto-detects which backend is available. Oracle is preferred when configured.

---

## 3. Data Model: PreDocument

Every parser produces `PreDocument` objects — the universal intermediate format.

```python
@dataclass
class PreDocument:
    """Standard output from any parser. Input to vault_api.ingest()."""
    title: str
    content: str                          # extracted text (always text, never binary)
    doc_type: str                         # from vault_doc_types registry
    occurred_at: datetime | None = None   # when the content was created/sent/posted
    ownership: str = 'self'               # self / work / external / shared
    privacy_level: str = 'internal'       # public / internal / restricted / secret
    fidelity: str = 'high'               # full / high / medium / low / metadata_only
    language: str = 'en'                  # ISO language code
    original_path: str | None = None      # where the source file lives (for dedup)
    source_info: dict | None = None       # {type, uri, display_name}
    metadata: dict | None = None          # type-specific fields (stored as metadata_json)
    chunks: list[str] | None = None       # pre-chunked content (optional)
    # Email promoted fields
    email_from: str | None = None
    email_importance: str | None = None   # high / normal / low
    email_direction: str | None = None    # inbound / outbound / internal
    # Versioning
    parent_doc_id: int | None = None      # for document updates
    version: int = 1
```

---

## 4. Parser Framework

### 4.1 BaseParser Interface

```python
class BaseParser:
    """All parsers inherit from this."""
    name: str = "base"
    supported_extensions: list[str] = []
    supported_mime_types: list[str] = []

    def can_handle(self, source: str, **kwargs) -> bool:
        """Return True if this parser can process the given source."""
        raise NotImplementedError

    def parse(self, source: str, **kwargs) -> list[PreDocument]:
        """Parse source into PreDocuments. Source is a file path, URL, or directory."""
        raise NotImplementedError
```

### 4.2 ParserRouter

```python
class ParserRouter:
    """Routes sources to the correct parser(s)."""

    def __init__(self):
        self._parsers: list[BaseParser] = []

    def register(self, parser: BaseParser):
        self._parsers.append(parser)

    def route(self, source: str, **kwargs) -> list[PreDocument]:
        results = []
        for parser in self._parsers:
            if parser.can_handle(source, **kwargs):
                results.extend(parser.parse(source, **kwargs))
                break  # first match wins (parsers ordered by specificity)
        return results

    def route_directory(self, directory: str, recursive: bool = True, **kwargs) -> list[PreDocument]:
        """Walk a directory and parse each file."""
        results = []
        for root, dirs, files in os.walk(directory):
            # Skip known junk directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fname in files:
                fpath = os.path.join(root, fname)
                for parser in self._parsers:
                    if parser.can_handle(fpath, **kwargs):
                        try:
                            results.extend(parser.parse(fpath, **kwargs))
                        except Exception as e:
                            results.append(PreDocument(
                                title=f"[PARSE ERROR] {fname}",
                                content=f"Failed to parse: {e}",
                                doc_type='file',
                                fidelity='metadata_only',
                                original_path=fpath,
                            ))
                        break
            if not recursive:
                break
        return results
```

### 4.3 Parser Specifications (10 parsers)

| # | Parser | Input | Output doc_type | Priority |
|---|--------|-------|-----------------|----------|
| 1 | TextFileParser | .txt, .md, .csv, .json, .yaml, .log | note / code_artifact / file | P1 |
| 2 | PdfParser | .pdf | pdf / research_paper | P1 |
| 3 | EmailParser | .eml, .mbox | email | P2 |
| 4 | LineParser | LINE export .txt | conversation | P2 |
| 5 | FacebookParser | FB data export JSON | social_post | P2 |
| 6 | ImageParser | .jpg, .png, .heic, .webp | image | P2 |
| 7 | MeetingParser | .vtt, .srt | meeting_transcript | P3 |
| 8 | WebParser | URL or .html | webpage | P3 |
| 9 | VoiceMemoParser | .m4a, .wav, .mp3, .ogg | voice_memo | P3 |
| 10 | DebateParser | Roundtable markdown | debate_transcript | P3 |

**Priority**: P1 = ship with v1, P2 = next sprint, P3 = future

### 4.4 Detailed Parser Specs

#### TextFileParser (P1)
```
Extensions: .txt, .md, .rst, .csv, .json, .yaml, .yml, .toml, .ini, .cfg, .log,
            .py, .js, .ts, .go, .rs, .java, .c, .cpp, .h, .sh, .bat, .ps1, .sql
Rules:
  - Code files (.py, .js, etc.) → doc_type='code_artifact'
  - Markdown/RST → doc_type='note'
  - Config files → doc_type='file', metadata.config_type=extension
  - Log files → doc_type='file', metadata.log_type=true
  - Files > 100KB → chunk into ~4000 char segments
  - Content = raw text (preserves formatting)
Fidelity: 'full'
```

#### PdfParser (P1)
```
Extensions: .pdf
Dependencies: PyMuPDF (fitz)
Rules:
  - Extract text per page using PyMuPDF
  - If text extraction fails (scanned PDF) → fidelity='metadata_only'
    (OCR integration deferred to P2, requires Tesseract)
  - Chunk by page (one chunk per page)
  - metadata: {pages, author, creator, creation_date, file_size_bytes}
  - Academic papers (has "Abstract" section) → doc_type='research_paper'
  - Others → doc_type='pdf'
Fidelity: 'full' (text PDF), 'metadata_only' (scanned without OCR)
```

#### EmailParser (P2)
```
Extensions: .eml, .mbox
Dependencies: email (stdlib), mailbox (stdlib)
Rules:
  - Parse email headers: From, To, CC, Subject, Date, Message-ID, In-Reply-To
  - Extract body: prefer text/plain, fallback to text/html (strip tags)
  - email_from = From header
  - email_direction = 'inbound' if sender is external, 'outbound' if sender matches configured user
  - email_importance = X-Priority header or 'normal'
  - metadata: {to, cc, message_id, in_reply_to, thread_id, has_attachments}
  - Attachments: listed in metadata but NOT binary-ingested
  - .mbox → iterate messages, one PreDocument per email
Fidelity: 'full' (text/plain), 'high' (html stripped)
```

#### LineParser (P2)
```
Extensions: .txt (with LINE format detection)
Format detection: file contains lines matching "^\d{4}/\d{2}/\d{2}" + tab-separated HH:MM\tSender\tMessage
Rules:
  - Group messages by date → one PreDocument per day
  - title = "LINE: {chat_name} - {date}"
  - Stickers/images → "[Sticker]", "[Photo]", "[Video]"
  - metadata: {platform:'line', participants:[], message_count, chat_name}
  - ownership='shared', privacy_level='internal'
Fidelity: 'high'
```

#### FacebookParser (P2)
```
Input: Facebook data export JSON (posts/your_posts_*.json)
Rules:
  - Iterate posts array
  - title = first 80 chars of post text
  - content = full post text + any attached link descriptions
  - occurred_at = timestamp from JSON
  - metadata: {platform:'facebook', post_url, media_count, tagged_people}
  - ownership='self', privacy_level='public' (or per audience setting)
Fidelity: 'full' (text posts), 'medium' (photo posts with caption)
```

#### ImageParser (P2)
```
Extensions: .jpg, .jpeg, .png, .heic, .webp, .gif, .bmp, .tiff
Dependencies: Pillow
Rules:
  - Extract EXIF metadata (camera, GPS, dimensions, datetime)
  - content = EXIF description + user comment (if available)
  - If no text content → fidelity='metadata_only', content="[Image: {filename}]"
  - metadata: {width, height, camera_make, camera_model, gps_lat, gps_lon, taken_at}
  - OCR deferred to P3 (requires Tesseract or cloud API)
Fidelity: 'metadata_only' (most images), 'low' (has EXIF description)
```

#### MeetingParser (P3)
```
Extensions: .vtt, .srt
Rules:
  - Parse WebVTT/SRT format → extract speaker + text
  - Merge adjacent segments from same speaker
  - title = first speaker line or filename
  - metadata: {format, segment_count, speakers:[], duration_estimate}
Fidelity: 'medium' (auto-transcription)
```

#### WebParser (P3)
```
Input: URL (http/https) or .html file
Dependencies: requests, beautifulsoup4
Rules:
  - Fetch URL or read local .html
  - Extract article text (strip nav, footer, ads)
  - title = <title> tag or first <h1>
  - metadata: {url, domain, author, published_date, fetched_at}
  - ownership='external'
Fidelity: 'high' (articles), 'medium' (dynamic pages)
```

#### VoiceMemoParser (P3)
```
Extensions: .m4a, .wav, .mp3, .ogg, .flac
Dependencies: openai-whisper or Whisper API
Rules:
  - Transcribe audio → text
  - title = first 80 chars of transcription or filename
  - metadata: {duration_seconds, language, whisper_model, confidence}
Fidelity: 'medium'
Note: Requires Whisper model or API key. Falls back to metadata_only without it.
```

#### DebateParser (P3)
```
Extensions: .md (with debate format detection)
Format detection: file contains "Round" in title + "Participants:" or "Consensus"
Rules:
  - Parse markdown structure
  - Extract participant names, round number, topics
  - Extract consensus items as PreDocuments with doc_type='debate_transcript'
  - Optionally extract facts from "共識" / "Consensus" sections → vault_facts
  - metadata: {participants:[], round_number, topics:[], has_consensus}
Fidelity: 'full'
```

---

## 5. Dedup Engine (3-Layer)

```python
class DedupEngine:
    """Three-layer deduplication for absorb."""

    def __init__(self, vault: Vault):
        self.vault = vault

    def check(self, pre_doc: PreDocument) -> tuple[str, int | None]:
        """Returns (action, existing_doc_id).
        action: 'skip' | 'version' | 'new'
        """
        content_hash = sha256(pre_doc.content)

        # Layer 1: exact content match → skip
        existing = self.vault.find_by_hash(content_hash)
        if existing:
            return ('skip', existing['id'])

        # Layer 2: same path, different content → new version
        if pre_doc.original_path:
            prev = self.vault.find_by_path(pre_doc.original_path)
            if prev:
                return ('version', prev['id'])

        # Layer 3: no match → new document
        return ('new', None)
```

---

## 6. vault_api Extensions

New methods needed in vault_api.py:

| Method | Purpose |
|--------|---------|
| `absorb(source, **kwargs)` | Universal ingestion entry point |
| `find_by_hash(content_hash)` | Find doc by content hash (for dedup) |
| `find_by_path(original_path)` | Find doc by original_path (for versioning) |
| `merge_entities(source_id, target_id)` | Merge two entities (set merged_into_id) |
| `gdpr_erase(entity_id)` | Privacy deletion across all tables |
| `add_chunk(document_id, chunk_index, content)` | Add a chunk to a document |

---

## 7. CLI Interface

```bash
# Absorb a directory (recursive)
python vault_parsers.py absorb ~/Desktop/important_docs/

# Absorb a single file
python vault_parsers.py absorb ~/research/paper.pdf

# Absorb with options
python vault_parsers.py absorb ~/line-exports/ --parser line --ownership shared --privacy internal

# Dry run (show what would be ingested)
python vault_parsers.py absorb ~/Desktop/ --dry-run

# List available parsers
python vault_parsers.py parsers

# Absorb with depth control
python vault_parsers.py absorb ~/project/ --depth shallow
```

### Skill Integration (via /absorb)

```
User: /absorb ~/Desktop/important_docs/

absorb skill detects vault is available:
  1. ParserRouter scans directory
  2. Routes files to parsers
  3. Dedup check each PreDocument
  4. vault_api.ingest() for new/versioned docs
  5. Print summary report
```

---

## 8. Migration Runner Integration

The existing `vault_migrate.py` handles Oracle→Oracle migration (legacy tables → vault tables). The parser framework handles file→vault ingestion. They share the same destination (vault_api.ingest) but different entry points:

```
vault_migrate.py   → SQL rows → vault_api.ingest()    (Oracle legacy data)
vault_parsers.py   → files    → vault_api.ingest()    (file system data)
absorb skill       → mixed    → vault_parsers.py      (user-facing entry point)
```

---

## 9. Error Handling

| Scenario | Behavior |
|----------|----------|
| Parser throws exception | Log error, create metadata_only PreDocument with error note |
| Oracle connection fails | Fall back to memory-server (L1+L2) |
| File too large (>50MB) | Skip, log warning with file path and size |
| Binary file with no text extraction | Create metadata_only PreDocument |
| Encoding error | Try UTF-8, then latin-1, then skip with error |
| Dedup hash collision (different content, same hash) | SHA-256 collision is astronomically unlikely; treat as duplicate |

---

## 10. Testing Strategy

| Test | Type | What |
|------|------|------|
| PreDocument creation | Unit | Each parser produces valid PreDocuments |
| ParserRouter dispatch | Unit | Correct parser selected for each file type |
| DedupEngine 3-layer | Unit | Skip/version/new decisions correct |
| TextFileParser | Integration | Parse .md, .py, .json files |
| PdfParser | Integration | Parse text PDF + scanned PDF |
| End-to-end absorb | E2E | Directory → parsers → vault_api → Oracle rows |
| Idempotency | E2E | Re-absorb same directory → 0 new documents |

---

## 11. Rollout Plan

| Phase | What | When |
|-------|------|------|
| P1 | TextFileParser + PdfParser + ParserRouter + DedupEngine + vault_api extensions | Now |
| P2 | EmailParser + LineParser + FacebookParser + ImageParser | Next sprint |
| P3 | MeetingParser + WebParser + VoiceMemoParser + DebateParser | Future |
| P4 | Enrichment pipeline (chunking + embedding + entity extraction) | Future |

---

## 12. Approval Checklist

```
[ ] PreDocument dataclass covers all Round 11 fields
[ ] Parser interface is simple enough for future contributors
[ ] ParserRouter handles directories recursively
[ ] DedupEngine 3-layer logic matches Round 10 consensus
[ ] vault_api.py has all new methods
[ ] vault_init.py creates v11 schema (13 tables)
[ ] absorb skill routes to vault when available
[ ] Backward compatible — works without Oracle (L1+L2 fallback)
[ ] No secrets in parser output
[ ] Error handling doesn't crash on bad files
```
