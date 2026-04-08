# Round 7 — Claude (Opus 4.6): Universal Ingestion Deep Dive

## The Core Question

the owner 要的不是「這些資料能不能放進去」— Round 6 已經證明 doc_type 模型可以。the owner 要確認的是：**放進去之後，agent 真的能用嗎？能找到嗎？能理解嗎？不會亂掉嗎？**

讓我從八個面向深入分析。

---

## 1. 版本控制：活文件怎麼辦？

**問題**：一份 Google Doc 被編輯了 50 次。一個 Obsidian 筆記每週更新。一個 wiki 頁面每天改。我們存 50 個 vault_document 嗎？

**分析**：vault_documents 目前沒有版本概念。每次 ingest 同一內容會被 `content_hash` dedup 擋掉。但如果內容變了，hash 不同，就會建新的 document。

**解決方案**：加一個 `superseded_by` 欄位（vault_facts 已經有這個概念）：

```sql
ALTER TABLE vault_documents ADD (
    parent_doc_id   NUMBER REFERENCES vault_documents(id),
    version         NUMBER DEFAULT 1,
    is_latest       NUMBER(1) DEFAULT 1
);
```

工作方式：
- 第一次 ingest → doc v1, is_latest=1
- 文件更新後重新 ingest → doc v2, parent_doc_id=v1.id, is_latest=1; v1.is_latest=0
- 查詢預設只看 `WHERE is_latest=1`
- 需要版本歷史時 `WHERE parent_doc_id IS NOT NULL` 走 parent chain

**影響**：所有 search 查詢要加 `AND is_latest = 1`，或建一個 view：

```sql
CREATE OR REPLACE VIEW v_current_documents AS
SELECT * FROM vault_documents WHERE is_latest = 1;
```

**風險**：如果不加這個，同一份文件每次更新都會出現在搜尋結果裡，造成重複干擾。

---

## 2. 非文字資料：純圖片、音檔、二進位檔

**問題**：一張沒有文字的風景照。一段沒有轉錄的語音。一個 .zip 檔。content CLOB 裡放什麼？

**分析**：Vault 的 content 欄位是 CLOB（文字）。對於「無法萃取文字」的資料：

| 資料類型 | content 存什麼 |
|----------|---------------|
| 風景照（無文字） | EXIF metadata 的文字表達："Photo taken 2024-03-15 at 35.6762°N 139.6503°E, iPhone 15 Pro, 4032x3024, sunset" |
| 純音檔（無轉錄） | 空字串或 metadata："Audio file, 3m42s, recorded 2024-01-05, source: Voice Memo app" |
| .zip 檔 | 檔案清單："Archive containing: report.pdf, data.xlsx, readme.txt (3 files, 2.4MB)" |
| 二進位程式 | metadata only："Binary executable, size: 1.2MB, hash: abc123..." |

**原則**：如果無法萃取文字，至少存 metadata 的文字描述。這樣搜尋 "2024 年去東京的照片" 可以透過 EXIF GPS + date 找到。

**未來**：當 multimodal embedding 普及，可以對圖片/音檔直接生成 embedding 存在 `embedding` 欄位，不需要文字中介。Schema 已經支持（`embedding VECTOR(1536)` 不依賴 content）。

---

## 3. 對話的粒度：一串 vs 一則

**問題**：LINE 對話五年下來可能有百萬則訊息。Facebook Messenger 同理。每則訊息一個 document？

**分析**：這是 Round 6 提到但沒深入的問題。

**我的立場**：**三層粒度模型**

```
Layer 1: vault_sources
  → source_type='chat_platform', uri='line://friend/david-chen'
  → 代表「the owner 和 David 在 LINE 上的所有對話」

Layer 2: vault_documents (per conversation segment)
  → doc_type='conversation'
  → 一個 document = 一天的對話 或 一個話題串
  → content = 完整對話文字（含時間戳記和發話者）
  
Layer 3: vault_chunks (per message or message group)
  → 每則重要訊息或每 5-10 則為一個 chunk
  → 個別 embedding 用於精準搜尋
```

**為什麼不是一則一 document？**
- 100 萬則訊息 = 100 萬個 vault_documents = 搜尋結果全是碎片
- 單則訊息缺乏 context（"好" 這個回覆沒有意義，要看前面在聊什麼）

**為什麼不是一整串一 document？**
- 五年的對話塞進一個 CLOB 太大了（可能幾十 MB）
- 無法標記時間範圍（occurred_at 只有一個值）

**最佳粒度**：依天或依話題切分。LINE export 已經有日期分隔。一天的對話 = 一個 document，occurred_at = 那天，chunks = 每則或每段。

---

## 4. 跨平台身份解析

**問題**：David Chen 在 email 是 `dchen@company.com`，LINE 上叫「大衛」，Facebook 是「David C.」，WhatsApp 是 `+886-912-345-678`。這四個是同一個人嗎？

**分析**：這是 vault_entity_aliases 設計來解決的問題。

**解決方案**：每個識別符都是一個 alias：

```
vault_entities:
  id=42, entity_type='person', canonical_name='David Chen', ownership='shared'

vault_entity_aliases:
  (42, 'David Chen', 'david chen', 'manual')
  (42, '大衛', '大衛', 'extraction')
  (42, 'David C.', 'david c.', 'extraction')
  (42, 'dchen@company.com', 'dchen@company.com', 'email')
  (42, '+886912345678', '+886912345678', 'phone')
  (42, 'line:david_tw', 'line:david_tw', 'platform_id')
  (42, 'fb:david.chen.123', 'fb:david.chen.123', 'platform_id')
```

**entity_resolve("大衛")** → 查 alias_normalized → 找到 entity 42 → 找到所有 David Chen 的 email、LINE 訊息、Facebook 互動。

**挑戰**：自動合併。如果 email 裡出現 "David Chen" 和 LINE 裡出現 "大衛"，系統怎麼知道是同一人？

**回答**：初始 migration 先**保守分開**（不確定的不合併）。之後用 LLM 或 human review 做 entity merge。vault_api 應該有一個 `merge_entities(source_id, target_id)` 方法：
- 把 source 的所有 aliases 移到 target
- 把 source 的所有 relations 移到 target
- 把 source 標記為 lifecycle='merged'
- 記一個 vault_event

---

## 5. 儲存容量分析

**問題**：Oracle Always Free Tier 有多少空間？夠嗎？

**計算**：
- Always Free ATP：20 GB storage
- 100K vault_documents：平均 content 2KB = ~200 MB
- 500K vault_chunks：平均 text 500 bytes = ~250 MB
- 500K embeddings (VECTOR 1536 float32)：每個 6KB = ~3 GB
- metadata_json：平均 1KB × 100K = ~100 MB
- indexes + overhead：~2 GB
- **Total estimate: ~6 GB**

20 GB 夠用，但如果 the owner 真的把所有東西都灌進來（加上 LINE 百萬則、FB 多年文章），可能到 10-15 GB。仍在限制內，但要注意 embedding 是最大的空間消耗者。

**建議**：
- 不是每個 document 都需要 embedding（日報的 stats 不需要向量搜尋）
- 可以設 `embedding_policy`：重要文件 = 即時 embed，一般文件 = 延遲或跳過
- 在 metadata_json 加 `"embedding_policy": "immediate" | "deferred" | "skip"`

---

## 6. 隱私與刪除權

**問題**：如果 David 要求 the owner 刪除他的所有資料（GDPR right to erasure），怎麼辦？

**分析**：vault_events 是 immutable 的。vault_documents 有 lifecycle。

**解決方案**：
1. 找到 entity David Chen
2. 查所有 vault_relations 指向 David 的 documents
3. 對這些 documents 執行 `lifecycle='retracted'`
4. 對 David 的 entity 執行 `lifecycle='retracted'`
5. 可選：清空 retracted documents 的 content（保留 metadata 做審計）

**不需要改 schema**。現有的 lifecycle + retract 機制就夠用。

但要加一個 **vault_api 方法**：
```python
def gdpr_erase(self, entity_name: str) -> dict:
    """Retract all documents and facts related to an entity."""
```

---

## 7. 搜尋在 100K+ 文件中還能用嗎？

**問題**：100K documents × 20 種 doc_type。agent 搜 "David 說的那個專案" 能找到嗎？

**分析**：目前 vault_api.search() 用 `LIKE` keyword search。100K rows 用 LIKE 掃全表會慢。

**解決方案分層**：

```
搜尋策略：
1. 先用 doc_type 過濾（如果 context 明確）
2. 再用 indexed columns（email_from, occurred_at, ownership）
3. 然後 keyword LIKE（在過濾後的子集上）
4. 最後 vector similarity（如果有 embedding）
```

**需要的索引**（部分已存在）：
```sql
CREATE INDEX idx_vdoc_doctype ON vault_documents(doc_type);
CREATE INDEX idx_vdoc_occurred ON vault_documents(occurred_at);
CREATE INDEX idx_vdoc_ownership ON vault_documents(ownership);
CREATE INDEX idx_vdoc_lifecycle_latest ON vault_documents(lifecycle, is_latest);
```

**100K rows 在 Oracle 上不是問題**。即使全表掃描也只要 1-2 秒。加上索引，毫秒級。

---

## 8. 萃取品質：garbage in = garbage out

**問題**：LINE 對話充滿貼圖、語助詞、無意義回覆。Facebook 有分享文、廣告互動。這些「垃圾」也要存嗎？

**分析**：Deep brain 的哲學是「存一切」。但 agent 需要的是「有意義的東西」。

**解決方案**：用 `lifecycle` 做品質分層：
- `raw` — 剛匯入，未審核
- `extracted` — LLM 已萃取 entities/facts
- `accepted` — 人工或自動審核為有價值
- `noise` — 被標記為低價值（貼圖、自動回覆、spam）

搜尋時預設 `WHERE lifecycle IN ('extracted', 'accepted')`。需要看全部時才包含 `raw` 和 `noise`。

**新增 lifecycle 值**：目前的 lifecycle 值 (raw → extracted → verified → accepted → superseded → retracted) 需要加 `noise`。

---

## Round 7 結論

### 需要的 Schema 修改

| 修改 | 原因 | 影響 |
|------|------|------|
| 加 `parent_doc_id`, `version`, `is_latest` 到 vault_documents | 版本控制 | 支持活文件更新 |
| 加 `noise` 到 lifecycle CHECK | 低價值資料標記 | 搜尋品質 |
| 加 entity merge API | 跨平台身份合併 | 不改 schema，改 API |
| 加 GDPR erase API | 隱私刪除權 | 不改 schema，改 API |
| 建 v_current_documents view | 搜尋只看最新版 | 查詢便利 |

### Confidence Score: 0.90

### Top 3 Concerns

1. **對話粒度決策需要人工介入** — 自動切分可能切錯地方。建議先用日為單位，日後可重新切分。
2. **Entity 自動合併風險** — 不同人同名（例如兩個 David）被錯誤合併。建議保守策略：只合併高確信度的。
3. **Embedding 儲存是最大的空間消耗** — 500K chunks × 6KB = 3GB。需要 embedding policy 控制哪些值得向量化。
