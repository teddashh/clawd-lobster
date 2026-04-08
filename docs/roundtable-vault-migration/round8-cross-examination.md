# Round 8 — Cross-Examination: Edge Cases & Architecture Gaps

## Topic A: Document Versioning

### Codex challenges Claude:
"你提議加 `parent_doc_id`, `version`, `is_latest` 三個欄位。但這造成一個問題：vault_relations 連結的是 document ID。如果 doc v1 被 supersede 成 v2，所有指向 v1 的 relations 是否自動指向 v2？如果不自動，搜尋 v2 時會找不到相關 entities。如果自動，那麼 relations 就不再是 immutable 的。"

### Claude responds:
好問題。我的回答是：**relations 指向 document ID 不需要改**。

原因：搜尋時走的路徑是 entity → relations → document。relation 指向 v1 沒問題，因為 v1 仍然存在（is_latest=0 但資料還在）。如果 agent 需要最新版，follow parent chain 即可。

更好的做法：relation 指向的是**概念**（"這封 email 提到了 David"），不管版本如何這個事實都不變。所以 v1 的 relations 對 v2 一樣有效。

**結論**：不需要自動遷移 relations。文件版本化是 content 的更新，不是 identity 的改變。

### Gemini 的立場:
Gemini 同意。但建議加一個 convenience view：

```sql
CREATE OR REPLACE VIEW v_document_with_latest AS
SELECT d.*, 
       CASE WHEN d.is_latest = 1 THEN d.id
            ELSE (SELECT MAX(d2.id) FROM vault_documents d2 
                  WHERE d2.is_latest = 1 
                  START WITH d2.id = d.id 
                  CONNECT BY PRIOR d2.id = d2.parent_doc_id)
       END AS latest_version_id
FROM vault_documents d;
```

**共識**：加版本欄位，不遷移 relations，加 view 做便利查詢。

---

## Topic B: 對話粒度

### Gemini challenges Claude:
"你說 LINE 對話以『天』為單位切分。但如果 the owner 跟 David 連續三天討論同一件事（買房），切成三個 document 會丟失上下文。一個 agent 問 'the owner 和 David 討論買房的結論是什麼？' 會需要搜三個 document 再合併。"

### Claude responds:
確實。但另一個極端（三天對話合為一個 document）會造成 occurred_at 無法精確標記。

**修正立場**：對話切分應該是 **topic-based**，不是 time-based：
- 短對話（幾分鐘內的一來一回）→ 一個 document
- 長對話跨多天但同一話題 → 一個 document，occurred_at = 最早時間
- 同一天但不同話題 → 多個 document

**但 topic 切分需要 LLM**。初始匯入先用 time-based（每天），之後用 Full enrichment 重新切分。

### Codex 的立場:
"既然初始匯入用 time-based，那就務實點：一天一 document。之後的 topic-based 切分是 enrichment 的工作，不是 ingestion 的工作。不要讓完美阻礙進度。"

**共識**：初始匯入 = 一天一 document。Enrichment pipeline 可以日後重新切分。

---

## Topic C: 非文字資料的 Embedding

### Codex challenges:
"Claude 說未來可以用 multimodal embedding 處理純圖片。但目前 VECTOR(1536, FLOAT32) 是 OpenAI text-embedding 的維度。如果以後用 CLIP (512 維) 或 Gemini multimodal (768 維)，維度不同怎麼辦？一個 embedding 欄位只能存一種維度。"

### 三方討論:

**Claude**：這是一個真實問題。VECTOR(1536) 是 hardcoded 的。

**Gemini**：Oracle 23ai 的 VECTOR 類型支援動態維度（`VECTOR(*, FLOAT32)`），但 similarity search 只在相同維度間有效。

**Codex**：務實做法：加一個 `embedding_model` 欄位（已有）標記用了哪個模型。搜尋時按 model 分組。如果以後需要不同維度，加一個 `embedding_alt VECTOR(768, FLOAT32)` 欄位。

**共識**：目前維持 VECTOR(1536)。`embedding_model` 欄位已存在，用它區分。如果未來需要 multimodal embedding，再 ALTER ADD 一個新欄位。不要 over-engineer。

---

## Topic D: GDPR 刪除的連鎖效應

### Gemini challenges Claude:
"你的 GDPR erase 方法 retract 了 entity 和相關 documents。但如果 David Chen 發了一封 email 給 10 個人，這封 email 也提到了 the owner 的工作內容。Retract 這封 email 等於也刪了 the owner 的工作記錄。如何平衡？"

### Claude responds:
分層處理：
1. **Entity-level erase**：retract David 的 entity + aliases。不刪 documents。
2. **Content-level redaction**：在相關 documents 的 content 中，用 `[REDACTED]` 替換 David 的個人資訊（名字、email）。但保留 email 的其他內容。
3. **Fact-level retract**：retract 所有「關於 David 的 facts」。

這不是完美的 GDPR compliance（那需要律師），但對個人 deep brain 來說足夠了。the owner 的 Vault 不是公開服務，GDPR 壓力較小。

**共識**：GDPR erase = entity retract + content redaction + fact retract。三層級，不是全刪。

---

## Topic E: Ingestion Pipeline 的統一入口

### 所有人都同意需要一個統一 absorb 模式:

```python
# 統一入口
vault.absorb(
    source="line://export/david-chen-2024.txt",
    source_type="chat_export",
    platform="line",
    ownership="shared",
    enrich_mode="fast"  # or "full"
)

# 內部流程：
# 1. Parser registry 根據 source_type + platform 選擇 parser
# 2. Parser 切分成 documents (one per day/topic)
# 3. Each document → vault_api.ingest()
# 4. If enrich_mode="full" → entity extraction + fact extraction
```

**Parser Registry**（需要的 parsers）：

| Parser | Input | Output |
|--------|-------|--------|
| EmailParser | Outlook export / MBOX | vault_documents (email) |
| LineParser | LINE chat export (.txt) | vault_documents (conversation) per day |
| FacebookParser | Facebook data export (JSON) | vault_documents (social_post) per post |
| PdfParser | .pdf file | vault_documents (pdf) + vault_chunks per page |
| FileScanner | directory path | vault_documents (file) per file |
| MeetingParser | .vtt / .srt transcript | vault_documents (meeting_transcript) |
| WebParser | URL | vault_documents (webpage) |
| ImageParser | .jpg/.png | vault_documents (image) with EXIF |
| VoiceMemoParser | .m4a/.wav + Whisper | vault_documents (voice_memo) with transcription |

**共識**：Parser 是 plugin 架構。每個 parser 不需要知道 vault schema 的細節。它只需要輸出 `{content, doc_type, meta, source_info, occurred_at}`，然後 `vault_api.ingest()` 處理剩下的。

---

## Topic F: 效能 — 搜尋 100K+ documents

### Codex 的壓力測試:

```
Scenario: Agent asks "2024年 Q3 跟 J. Smith 討論的 SOAR 專案最後結論是什麼？"

Query decomposition:
1. entity_resolve("J. Smith") → entity_id=123
2. Search vault_documents WHERE:
   - doc_type IN ('email', 'conversation', 'meeting_transcript')
   - occurred_at BETWEEN '2024-07-01' AND '2024-09-30'
   - (email_from LIKE '%jsmith%' OR content LIKE '%J. Smith%' OR content LIKE '%SOAR%')
3. Filter by relations: documents linked to entity 123
4. Extract relevant facts from matched documents
```

**Estimated execution time with indexes**:
- Step 1: < 1ms (alias index)
- Step 2: < 100ms (doc_type + occurred_at indexes, content LIKE on filtered subset ~3K docs)
- Step 3: < 10ms (relation index)
- Step 4: Application-level (no DB query)

**Total: < 200ms.** 完全可接受。

**共識**：100K documents 在 Oracle 上不是效能問題。索引策略正確就夠。

---

## Round 8 新共識

| 議題 | 決定 |
|------|------|
| 版本控制 | 加 parent_doc_id, version, is_latest + view |
| 對話粒度 | 初始匯入 = 一天一 document，日後可 topic-based 重切 |
| Embedding 維度 | 維持 1536，用 embedding_model 區分，未來需要再加欄位 |
| GDPR | entity retract + content redaction + fact retract (三層) |
| Parser | Plugin 架構，9+ parsers，統一 absorb 入口 |
| 效能 | 100K docs + proper indexes = < 200ms query |
| 非文字資料 | 存 metadata 文字描述 + 未來加 multimodal embedding |
