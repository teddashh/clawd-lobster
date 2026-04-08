# Round 9 — Convergence: Accepting the Attacks, Hardening the Schema

## Codex 的 8 個攻擊 — 三方逐一回應

### Attack 1: Orphan File Pointers
**Codex**: original_path 會因為搬家/重灌而失效。
**Claude**: 接受。Vault 是 search index，不是 file manager。原始檔路徑是 best-effort。加 `last_verified_at` 太 over-engineer。
**Gemini**: 同意 Claude。但建議 metadata_json 裡用 `storage_backend` 標記（local/onedrive/s3），讓未來的驗證 cron 知道去哪查。
**共識**: 不改 schema。metadata_json convention 加 `storage_backend` 和 `original_path`。文件明確聲明：Vault 是知識索引，不保證原始檔案可達性。

### Attack 2: Real-Time / Streaming Data
**Codex**: 對話是永無止境的 stream，batch import 不夠。提議加 `doc_status` (draft/streaming/final/superseded)。
**Claude**: 部分接受。`doc_status` 跟 `lifecycle` 有重疊。我提議把這些狀態合併進 lifecycle：
```
lifecycle values (expanded):
  draft → raw → streaming → extracted → verified → accepted → noise → superseded → retracted
```
`streaming` 代表「這個 document 還在接收新內容」。當 time window 結束，轉為 `raw` 進入正常 pipeline。
**Gemini**: 同意合併進 lifecycle。不需要新欄位。
**共識**: 擴充 lifecycle 值，加入 `draft` 和 `streaming`。不加新欄位 `doc_status`。

### Attack 3: Cross-Platform Identity Resolution
**Codex**: alias 需要 confidence score + verified_by。entity 需要 merged_into_id。
**Claude**: 全部接受。這三個改動都很小但很重要。
**Gemini**: 同意。但 `merged_into_id` 應該是 soft redirect，不是硬刪除。查詢時遇到 `merged_into_id IS NOT NULL` 就自動 follow redirect。
**共識**: 
- vault_entity_aliases 加 `confidence` + `verified_by`
- vault_entities 加 `merged_into_id`
- vault_api 加 `merge_entities()` + `split_entity()` 方法

### Attack 4: Conversation Granularity
**Codex**: 一天一 document 會把「決定小孩學校」和「買菜清單」混在一起。
**Claude**: 接受問題描述。但解法不是改 schema — 現有的 vault_facts + vault_chunks 已經能處理：重要訊息被萃取為 fact 連結到 entity。瑣碎訊息留在 chunk 裡不被萃取。
**Gemini**: 同意。這是 enrichment pipeline 的責任，不是 schema 的問題。Schema 已經足夠。
**共識**: Schema 不變。Enrichment pipeline 設計文件需要明確描述：如何從對話 chunks 中萃取重要 facts。

### Attack 5: Fidelity Score
**Codex**: 加 `fidelity_score` 標記萃取品質（email=0.95, 純照片 EXIF=0.15）。
**Claude**: 這是個好主意。但 FLOAT 太精確了。我建議用分級：
```
fidelity VARCHAR2(10) — 'high' (text-native), 'medium' (OCR/transcript), 'low' (metadata-only)
```
比浮點數更好理解，agent 更容易用。
**Gemini**: 同意分級。但三級不夠，建議五級：`full`, `high`, `medium`, `low`, `metadata_only`。
**共識**: 加 `fidelity VARCHAR2(15) DEFAULT 'high'` 到 vault_documents。五級制。

### Attack 6: Document Versioning
**Codex**: 加 version_number, version_parent_id, is_current。
**Claude**: 我在 Round 7 提出了幾乎相同的方案（parent_doc_id, version, is_latest）。名稱不同但概念一致。
**Gemini**: Round 7 也提出了 document_id (stable) + version 模式。三方完全一致。
**共識**: 加三個欄位到 vault_documents：
```sql
parent_doc_id   NUMBER REFERENCES vault_documents(id)
version         NUMBER DEFAULT 1
is_latest       NUMBER(1) DEFAULT 1
```
加 view `v_current_documents`。

### Attack 7: GDPR 刪除
**Codex**: 無刪除機制。across 8/11 tables 的 cascade 問題。提議 `redacted_at` + `redaction_reason`。
**Claude**: 部分接受。`redacted_at` 是好的。但 `redaction_reason` 可以放 vault_events 裡（那就是 event log 的用途）。
**Gemini**: 同意 redacted_at 在 document 上。其他走 vault_events。
**Codex 的 participant_entities 在 chunks metadata**: 好主意。但這是 metadata_json convention，不是 schema 改動。
**共識**: 
- vault_documents 加 `redacted_at TIMESTAMP`
- 刪除操作記錄在 vault_events
- chunk metadata_json convention 加 `participant_entity_ids`
- vault_api 加 `gdpr_erase(entity_id)` 方法

### Attack 8: doc_type Controlled Vocabulary
**Codex**: 提議 vault_doc_types reference table + FK。
**Claude**: 反對新表。FK 約束會讓 ingestion pipeline 變脆弱 — 每次有新 data type 都要先 INSERT doc_type 才能 ingest。這對自動化不友好。
**Gemini**: 折中方案 — 加 vault_doc_types 做 reference，但 **不加 FK 約束**。它是一個 registry，不是一個 constraint。Agent 可以查它來知道有哪些標準 type，但不會被它擋住。
**共識**: 加 vault_doc_types 為 reference table（無 FK）。初始化時填入 20+ 標準 types。ingestion pipeline 建議查 registry，但不強制。

### Multimodal Embedding (Codex Attack 1 延伸)
**Codex**: 加 `mm_embedding VECTOR(1536)` 到 vault_documents。
**Claude**: 反對現在加。目前沒有 multimodal embedding pipeline，加了也是空欄位。
**Gemini**: 同意 Claude。未來需要時再 ALTER ADD。
**共識**: 不加。記錄為 future consideration。

---

## Gemini Round 7 新議題回應

### Storage / Vector Tax
**Gemini**: 500K chunks × 6KB = 3GB vector。Always Free 可能不夠。
**Claude**: the owner 的 Always Free tier 是 20GB（ATP），不是 500MB。3GB vectors + 3GB other = ~6GB total，在限制內。但 embedding policy 仍然重要 — 不是每個 chunk 都需要 embed。
**共識**: 維持 Always Free tier。加 embedding policy convention in metadata_json。

### Data Temperature (Hot/Warm/Cold)
**Gemini**: >1yr → compressed, >5yr → cold storage。
**Claude**: Oracle Always Free 沒有 object store。壓縮是 Oracle 自動做的（ATP 有自動壓縮）。不需要手動分層。
**共識**: 暫不實作。Oracle ATP 自動處理壓縮。未來如果超過 20GB 再考慮。

### Hybrid Search
**Gemini**: 必須先 SQL 過濾再 vector search。
**Claude + Codex**: 完全同意。這是 vault_api.search() 的實作策略，不需要改 schema。
**共識**: vault_api.search() 設計為 metadata filter first → vector search on pruned set。

---

## 最終 Schema Modifications (Round 7-9 累積)

### vault_documents 新增欄位
```sql
ALTER TABLE vault_documents ADD (
    parent_doc_id   NUMBER REFERENCES vault_documents(id),
    version         NUMBER DEFAULT 1,
    is_latest       NUMBER(1) DEFAULT 1,
    fidelity        VARCHAR2(15) DEFAULT 'high',
    redacted_at     TIMESTAMP,
    CONSTRAINT chk_fidelity CHECK (fidelity IN ('full','high','medium','low','metadata_only'))
);
```

### vault_entities 新增欄位
```sql
ALTER TABLE vault_entities ADD (
    merged_into_id  NUMBER REFERENCES vault_entities(id)
);
```

### vault_entity_aliases 新增欄位
```sql
ALTER TABLE vault_entity_aliases ADD (
    confidence      NUMBER(3,2) DEFAULT 1.0,
    verified_by     VARCHAR2(50) DEFAULT 'auto_extracted'
);
```

### lifecycle 擴充
```
原本: raw → extracted → verified → accepted → superseded → retracted
新增: draft, streaming, noise
完整: draft → streaming → raw → extracted → verified → accepted → noise → superseded → retracted
```

### 新 reference table
```sql
CREATE TABLE vault_doc_types (
    doc_type    VARCHAR2(50) PRIMARY KEY,
    description VARCHAR2(500),
    parent_type VARCHAR2(50),
    created_at  TIMESTAMP DEFAULT SYSTIMESTAMP
);
-- NO FK from vault_documents — advisory only
```

### 新 views
```sql
CREATE OR REPLACE VIEW v_current_documents AS
SELECT * FROM vault_documents WHERE is_latest = 1 AND redacted_at IS NULL;
```

### vault_api 新方法
- `merge_entities(source_id, target_id)`
- `split_entity(entity_id, alias_ids_to_split)`
- `gdpr_erase(entity_id)`
- `absorb(source, source_type, platform, ownership, enrich_mode)`

---

## Confidence Scores After Round 9

| Agent | Score | Movement | Note |
|-------|-------|----------|------|
| Claude | 0.91 | ↑ from 0.90 | Versioning + GDPR gaps addressed |
| Codex | 0.86 | ↑ from 0.78 | 6/8 attacks accepted, remaining 2 deferred wisely |
| Gemini | 0.92 | ↑ from 0.90 | Hybrid search + lifecycle expansion confirmed |
