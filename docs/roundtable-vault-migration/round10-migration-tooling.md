# Round 10 — Migration Tooling: From Theory to Executable Plan

> **Date:** 2026-04-07
> **Participants:** Claude Opus 4.6 (CIO, 0.91), Codex GPT-5.4 (Developer, 0.86), Gemini 2.5 Pro (Consultant, 0.92)
> **Focus:** Final tooling architecture, parser specifications, remaining disputes, Ted's data inventory

---

## Topic A: Ted 的完整資料盤點

### 三方共同確認 Ted 目前的資料來源：

| # | Source | Location | Volume Estimate | Parser Needed |
|---|--------|----------|-----------------|---------------|
| 1 | Work emails (FPC) | CLAUDE_MEMORY.EMAILS | 86,420 rows | SQL→vault (已有) |
| 2 | Daily reports | CLAUDE_MEMORY.DAILY_REPORTS | 1,865 rows | SQL→vault |
| 3 | Knowledge articles | OPENCLAW_APP.KNOWLEDGE | 152 rows (149 migrated) | SQL→vault (已做) |
| 4 | Action logs | OPENCLAW_APP.ACTIVITY_LOGS | ~3,000 rows | SQL→vault |
| 5 | Contacts | OPENCLAW_APP.CONTACTS | 5 rows | SQL→vault_entities |
| 6 | Decisions | OPENCLAW_APP.DECISIONS | 4 rows | SQL→vault_facts |
| 7 | Questions | OPENCLAW_APP.QUESTIONS | 13 rows | SQL→vault_facts |
| 8 | SOPs | OPENCLAW_APP.SOPS | 11 rows | SQL→vault |
| 9 | Desktop files | C:\Users\detna\ 各處 | 未估計 | FileScanner |
| 10 | Research PDFs | 各處 | 未估計 | PdfParser |
| 11 | LINE 對話 | LINE export (.txt) | 多年 | LineParser |
| 12 | Facebook posts | FB data export (JSON) | 多年 | FacebookParser |
| 13 | Photos | OneDrive / local | 數千張 | ImageParser |
| 14 | Debate transcripts | clawd-lobster/docs/ | 14 files | FileScanner / DebateParser |
| 15 | Voice memos | 手機匯出 | 未估計 | VoiceMemoParser |
| 16 | Meeting recordings | Zoom/Teams exports | 未估計 | MeetingParser |
| 17 | Web bookmarks | Browser exports | 未估計 | WebParser |

### Claude 的分析：

Phase 1（立即可做）= Sources 1-8：全在 Oracle，SQL 直接搬。這是 vault_migrate.py 的擴充。
Phase 2（需要 parsers）= Sources 9-17：需要 file system access + format-specific parsing。

**建議**：先完成 Phase 1，驗證 schema 正確性。Phase 2 的 parsers 逐步開發。

### Codex 同意，但補充：
"Phase 1 裡面 Source 1（86K emails）是最大的挑戰。不是技術問題，是效能問題。86K rows 要做：INSERT + chunking + embedding。如果一個 email 平均切 3 chunks，就是 260K chunks。每個 chunk 要 embedding API call。"

### Gemini 回應：
"Embedding 不一定要在 migration 時做。Migration 先把 documents 進去，lifecycle='raw'。Embedding 用 background job 慢慢跑。這樣 migration 只需要 INSERT，幾分鐘就好。"

**共識**：Migration = INSERT only（fast）。Enrichment（chunking + embedding + entity extraction）= 後續 background pipeline。分離 migration 和 enrichment 的關注點。

---

## Topic B: vault_migrate.py 的擴充設計

### Claude 提出 Migration Runner 架構：

```python
class VaultMigrationRunner:
    """Unified migration runner for all Oracle legacy data."""
    
    def __init__(self, source_conn, target_conn, mode='dry-run'):
        self.source = source_conn      # CLAUDE_MEMORY or OPENCLAW_APP
        self.target = target_conn      # OPENCLAW_APP (vault tables)
        self.mode = mode               # dry-run | execute | rollback
        self.migrators = []
    
    def register(self, migrator: BaseMigrator):
        self.migrators.append(migrator)
    
    def run_all(self):
        for m in self.migrators:
            m.pre_check()       # verify source data exists
            m.transform()       # map to vault schema
            m.load()            # INSERT into vault
            m.verify()          # count check
            m.log()             # vault_sync_log entry
```

### 每個 source 有自己的 Migrator：

```python
class EmailMigrator(BaseMigrator):
    """CLAUDE_MEMORY.EMAILS → vault_documents (doc_type='email')"""
    source_table = 'EMAILS'
    target_doc_type = 'email'
    
    def transform_row(self, row):
        return {
            'title': row['SUBJECT'],
            'content': row['BODY_TEXT'] or row['BODY_HTML'],
            'doc_type': 'email',
            'source_type': 'oracle_migration',
            'original_path': f"claude_memory://emails/{row['ID']}",
            'email_from': row['SENDER'],
            'email_importance': self._classify_importance(row),
            'email_direction': 'inbound' if row['FOLDER'] == 'Inbox' else 'outbound',
            'occurred_at': row['SENT_DATE'],
            'ownership': 'work',
            'privacy_level': 'internal',
            'fidelity': 'full',
            'metadata_json': json.dumps({
                'to': row['RECIPIENTS'],
                'cc': row['CC'],
                'folder': row['FOLDER'],
                'thread_id': row['THREAD_ID'],
                'has_attachments': bool(row['ATTACHMENT_COUNT']),
                'original_id': row['ID'],
                'storage_backend': 'oracle_claude_memory'
            })
        }

class DailyReportMigrator(BaseMigrator):
    """CLAUDE_MEMORY.DAILY_REPORTS → vault_documents (doc_type='daily_report')"""
    source_table = 'DAILY_REPORTS'
    target_doc_type = 'daily_report'

class ActionLogMigrator(BaseMigrator):
    """OPENCLAW_APP.ACTIVITY_LOGS → vault_documents (doc_type='action_log')"""
    source_table = 'ACTIVITY_LOGS'
    target_doc_type = 'action_log'

class ContactMigrator(BaseMigrator):
    """OPENCLAW_APP.CONTACTS → vault_entities (entity_type='person')"""
    # This one is different — goes to entities, not documents.

class DecisionMigrator(BaseMigrator):
    """OPENCLAW_APP.DECISIONS → vault_facts (fact_type='decision')"""
    # Goes to facts, not documents.

class QuestionMigrator(BaseMigrator):
    """OPENCLAW_APP.QUESTIONS → vault_facts (fact_type='question')"""

class SopMigrator(BaseMigrator):
    """OPENCLAW_APP.SOPS → vault_documents (doc_type='sop')"""
```

### Codex 的建議：
"加一個 `--source` flag 讓使用者選擇跑哪些 migrators：`--source all`、`--source emails`、`--source contacts,decisions`。86K emails 需要單獨跑，不要跟 5 筆 contacts 混在一起。"

### Gemini 的建議：
"每個 migrator 要有 `batch_size` 參數。86K emails 不能一次 INSERT。用 `executemany` + batch size 1000。加 progress bar（tqdm）和 estimated time remaining。"

**共識**：
- 擴充 vault_migrate.py 為 migration runner，支持 `--source` 選擇
- 每個 source 有獨立 migrator class
- Batch insert with configurable batch_size (default 1000)
- Progress reporting
- 每個 migrator 都有 dry-run / execute / rollback 三模式

---

## Topic C: Parser Plugin 架構 — 具體規格

### 三方共同制定 Parser Interface：

```python
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class PreDocument:
    """Standard output from any parser — input to vault_api.ingest()"""
    title: str
    content: str                        # extracted text
    doc_type: str                       # from vault_doc_types registry
    occurred_at: Optional[datetime]     # when the content was created
    ownership: str = 'self'             # self/work/external/shared
    privacy_level: str = 'internal'     # public/internal/restricted/secret
    fidelity: str = 'high'             # full/high/medium/low/metadata_only
    original_path: Optional[str] = None # where the source file lives
    metadata: Dict[str, Any] = None     # type-specific fields
    chunks: Optional[List[str]] = None  # pre-chunked content (optional)

class BaseParser:
    """All parsers inherit from this."""
    supported_extensions: List[str] = []
    supported_platforms: List[str] = []
    
    def can_handle(self, source: str, source_type: str, platform: str) -> bool:
        """Return True if this parser can process the given source."""
        raise NotImplementedError
    
    def parse(self, source: str, **kwargs) -> List[PreDocument]:
        """Parse source into one or more PreDocuments."""
        raise NotImplementedError
```

### Parser 具體規格：

#### 1. EmailParser
```
Input:   .eml file, .mbox file, or Outlook export
Output:  1 PreDocument per email
Fields:  title=Subject, content=body_text, doc_type='email'
         metadata: {to, cc, bcc, thread_id, message_id, in_reply_to, has_attachments}
         email_from, email_direction auto-detected from sender address
Fidelity: 'full' (text emails), 'high' (HTML with embedded images)
```

#### 2. LineParser
```
Input:   LINE chat export (.txt file)
         Format: "YYYY/MM/DD\n...\nHH:MM\tSender\tMessage"
Output:  1 PreDocument per day of conversation
Fields:  title="LINE: {chat_name} - {date}", content=day's messages
         doc_type='conversation', ownership='shared'
         metadata: {platform:'line', participants:[], message_count, chat_name}
Fidelity: 'high' (sticker/image references become "[Sticker]"/"[Photo]")
Note:    Sticker-only messages marked fidelity='low'
```

#### 3. FacebookParser
```
Input:   Facebook data export (JSON from Settings > Download Your Information)
Output:  1 PreDocument per post
Fields:  title=first_50_chars_of_post, content=full_text
         doc_type='social_post', ownership='self'
         metadata: {platform:'facebook', post_id, likes, comments, shares, audience, media_urls}
Fidelity: 'full' (text posts), 'medium' (photo posts with caption), 'metadata_only' (shared links)
```

#### 4. PdfParser
```
Input:   .pdf file
Output:  1 PreDocument (full PDF) + optional chunks per page
Fields:  title=filename or extracted title, content=all_extracted_text
         doc_type='pdf' or more specific (research_paper, invoice, contract)
         metadata: {pages, author, created_date, file_size, ocr_used}
Fidelity: 'full' (text PDF), 'medium' (OCR), 'low' (scanned with poor quality)
Deps:    PyMuPDF (fitz) for text extraction, Tesseract for OCR fallback
```

#### 5. FileScanner
```
Input:   Directory path (recursive)
Output:  1 PreDocument per file (text-extractable files only)
Fields:  title=filename, content=extracted_text_or_metadata_summary
         doc_type='file' or inferred (code_file, spreadsheet, presentation, etc.)
         metadata: {path, size, mime_type, created_at, modified_at, extension}
Fidelity: varies by file type
Skip:    Binary executables, system files, node_modules, .git, __pycache__
```

#### 6. MeetingParser
```
Input:   .vtt or .srt transcript file
Output:  1 PreDocument per meeting
Fields:  title=meeting_name or filename, content=full_transcript
         doc_type='meeting_transcript'
         metadata: {duration, participants:[], platform:'zoom'/'teams', recording_date}
Fidelity: 'medium' (auto-transcription has errors)
```

#### 7. WebParser
```
Input:   URL or saved .html file
Output:  1 PreDocument per page
Fields:  title=page_title, content=extracted_article_text (readability)
         doc_type='webpage'
         metadata: {url, archived_at, domain, author}
Fidelity: 'high' (articles), 'medium' (dynamic pages)
Deps:    requests + beautifulsoup4 + readability-lxml
```

#### 8. ImageParser
```
Input:   .jpg, .png, .heic, .webp
Output:  1 PreDocument per image
Fields:  title=filename, content=EXIF_description + OCR_if_text_detected
         doc_type='image'
         metadata: {camera, gps_lat, gps_lon, dimensions, taken_at, faces_count}
Fidelity: 'metadata_only' (no text), 'low' (OCR text), 'medium' (good OCR or caption)
Deps:    Pillow for EXIF, Tesseract for OCR
```

#### 9. VoiceMemoParser
```
Input:   .m4a, .wav, .mp3, .ogg
Output:  1 PreDocument per memo
Fields:  title=filename or first_words, content=transcription
         doc_type='voice_memo'
         metadata: {duration, language, whisper_model, confidence}
Fidelity: 'medium' (whisper transcription)
Deps:    openai-whisper or Whisper API
```

### Codex 提出第 10 個 parser：

#### 10. DebateParser (Meta!)
```
Input:   Markdown debate files (like this very roundtable)
Output:  1 PreDocument per round
Fields:  title="Vault Roundtable: Round {N}", content=full_markdown
         doc_type='debate_transcript'
         metadata: {participants:[], round_number, topics:[], consensus_items:[]}
Fidelity: 'full'
Note:    This parser also extracts vault_facts from "共識" sections
         fact_type='decision', confidence=1.0
```

**Claude**: 好主意。我們自己的辯論紀錄當然要進 Vault。

**Gemini**: 同意。而且 DebateParser 萃取出的 consensus facts 可以當 vault_facts 的 golden reference — 這些是三個 AI 一致同意的高品質結論。

**共識**：加 DebateParser。共 10 個 parsers。初始 release 先做 Priority 1（SQL migrators + FileScanner + PdfParser），其他根據 Ted 的需求逐步加。

---

## Topic D: absorb Skill 整合

### Claude 提出 absorb 的完整 flow：

```
User: "absorb ~/Desktop/important_docs/"

absorb skill:
  1. ParserRegistry.detect(source) → FileScanner (directory)
  2. FileScanner.parse(source) → List[PreDocument] (e.g., 47 files)
  3. For each PreDocument:
     a. vault_api.ingest(pre_doc) → doc_id
     b. vault_events.log(event_type='ingested', doc_id=doc_id)
  4. If enrich_mode='full':
     a. Queue: chunking → embedding → entity extraction → fact extraction
  5. Return summary: "Absorbed 47 documents (12 PDFs, 23 code files, 8 notes, 4 images)"
```

### Codex 的擔憂：
"如果 absorb 跑到一半斷了怎麼辦？47 個檔案進了 30 個就 crash。重跑會不會重複進 30 個？"

### Claude 回應：
`content_hash` dedup 會擋住已經進去的 30 個。剩下 17 個會繼續。這是冪等設計（idempotent）。

### Gemini 補充：
"content_hash dedup 不夠。如果同一個 file 被修改後重新 absorb，hash 不同，會建新 document。這時候應該用 `original_path` 比對，找到 parent_doc_id，建新版本。"

### Claude 接受：
```python
def absorb_file(self, path, **kwargs):
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    # Check 1: exact content match → skip
    existing = self.find_by_hash(content_hash)
    if existing:
        return {'status': 'skipped', 'reason': 'duplicate_content', 'doc_id': existing.id}
    
    # Check 2: same path, different content → new version
    prev = self.find_by_path(path)
    if prev:
        return self.ingest(pre_doc, parent_doc_id=prev.id, version=prev.version + 1)
    
    # Check 3: new document
    return self.ingest(pre_doc)
```

**共識**：absorb 有三層 dedup 邏輯：
1. content_hash match → skip
2. original_path match + different hash → new version
3. No match → new document

---

## Topic E: Remaining Disputes from Round 9

### Dispute 1: vault_doc_types — 初始清單

Codex 提出需要確定初始 doc_types。三方共同制定：

```sql
INSERT ALL
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('email', 'Electronic mail message', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('conversation', 'Chat/messaging conversation', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('social_post', 'Social media post', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('daily_report', 'Daily work summary report', 'report')
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('report', 'Generic report', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('note', 'Personal or work note', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('sop', 'Standard operating procedure', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('pdf', 'PDF document', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('image', 'Photograph or image', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('voice_memo', 'Audio recording with transcription', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('meeting_transcript', 'Meeting recording transcript', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('action_log', 'Agent or human action log entry', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('debate_transcript', 'AI roundtable debate record', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('code_artifact', 'Source code file or snippet', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('webpage', 'Archived web page', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('file', 'Generic file', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('financial_record', 'Invoice, receipt, statement', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('health_record', 'Medical or health document', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('legal_document', 'Contract, agreement, legal filing', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('news_article', 'News or press article', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('scan', 'Scanned document or handwritten note', NULL)
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('research_paper', 'Academic or research publication', 'pdf')
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('presentation', 'Slide deck or presentation', 'file')
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('spreadsheet', 'Excel or data spreadsheet', 'file')
  INTO vault_doc_types (doc_type, description, parent_type) VALUES ('knowledge', 'Knowledge base article', 'note')
SELECT 1 FROM DUAL;
```

**共識**：25 個初始 doc_types，含 parent_type 繼承關係。

### Dispute 2: vault_audit_trail 的必要性

**Codex**: "vault_events 已經記所有事件了。vault_audit_trail 跟它有什麼差別？"

**Claude**: vault_events 是「資料生命週期事件」（ingested, extracted, accepted, retracted）。vault_audit_trail 是「操作層面的審計」（who called what API, when, with what parameters, success/fail）。前者是 domain events，後者是 ops events。

**Gemini**: 同意這個區分。但 audit_trail 在 Always Free tier 不需要太複雜。簡化為：

```sql
CREATE TABLE vault_audit_trail (
    id          NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    action      VARCHAR2(50) NOT NULL,    -- 'ingest', 'search', 'merge_entity', 'gdpr_erase'
    actor       VARCHAR2(100),            -- 'vault_migrate.py', 'claude', 'ted_manual'
    target_type VARCHAR2(50),             -- 'document', 'entity', 'fact'
    target_id   NUMBER,
    details     CLOB,                     -- JSON with parameters and result summary
    created_at  TIMESTAMP DEFAULT SYSTIMESTAMP
);
```

**Codex**: 接受。比我預期的簡單，但功能足夠。

**共識**：vault_audit_trail 保留，schema 如上。

### Dispute 3: vault_metrics 的 metric_type 清單

三方共同制定初始 metrics：

| metric_type | description | 典型值 |
|-------------|-------------|--------|
| doc_count | Total documents | 86420 |
| doc_count_by_type | Count per doc_type | {email: 86420, note: 149, ...} |
| entity_count | Total entities | 5000+ |
| fact_count | Total facts | 10000+ |
| chunk_count | Total chunks | 260000+ |
| embedding_coverage | % of chunks with embeddings | 0.0 → 1.0 |
| storage_bytes | Total DB storage used | 6GB |
| search_avg_ms | Average search latency | 150 |
| enrichment_backlog | Documents awaiting enrichment | 86420 → 0 |
| migration_progress | Migration completion % | 0.0 → 1.0 |

**共識**：vault_metrics 記這些 KPI。`vault_api.stats()` 讀它，background job 定期更新。

---

## Topic F: 安全性最終確認

### Codex 的最後安全檢查：

| Concern | Status | Resolution |
|---------|--------|------------|
| SQL injection | ✅ Mitigated | All queries use bind variables (`:1`, `:2`), never string concatenation |
| Credential storage | ✅ Acceptable | config.json in user home dir, not in repo. `.gitignore`d. |
| Wallet password in config | ⚠️ Risk | Low risk for personal use. In production would need keyring/vault. |
| Cross-schema access | ✅ Controlled | OPENCLAW_APP owns vault tables. CLAUDE_MEMORY read-only access for migration. |
| Content encryption | ❌ Not implemented | Privacy_level='secret' docs should ideally be encrypted at rest. Oracle ATP does TDE (Transparent Data Encryption) by default. |
| Embedding data leakage | ⚠️ Risk | Embeddings can theoretically be reverse-engineered to reconstruct content. Low practical risk for personal vault. |

**Claude**: Oracle ATP 已經做 TDE（全庫加密），所以 at-rest encryption 已經有了。embedding reverse-engineering 對個人 vault 來說風險極低。

**Gemini**: 同意。安全性對個人 deep brain 來說已經足夠。如果以後要做多用戶，再加 Row-Level Security (RLS)。

**共識**：安全性通過。不需要額外改動。

---

## Round 10 Confidence Scores

| Agent | Score | Movement | Note |
|-------|-------|----------|------|
| Claude | 0.93 | ↑ from 0.91 | Migration tooling architecture clear, parser specs complete |
| Codex | 0.90 | ↑ from 0.86 | Dedup + idempotent design + security review satisfied |
| Gemini | 0.93 | ↑ from 0.92 | Parser plugin interface well-defined, enrichment separation confirmed |

### 剩餘開放問題（Round 11 要收斂）
1. 完整 DDL — 合併所有 10 rounds 的 schema 變更為一份可執行 SQL
2. 遷移執行順序 — 哪些先跑、dependency 是什麼
3. 驗收標準 — 什麼條件下算 migration 完成
4. Ted 的 approval checklist
