## Why

Phase 2A 只完成 30 篇 NR concept Summary；以單一 10-note tranche 逐次提案會讓一千多份待評估筆記的處理速度不足。上一版 Phase 2B artifact 也因 PowerShell 管線編碼而寫入實際亂碼，必須先以 UTF-8 修復，才能成為可交接、可稽核的工作契約。

## What Changes

- 修復本 change 的 proposal、design、tasks 為正確 UTF-8 繁體中文；不改動既有醫療筆記或其來源。
- 將 Phase 2B 從單一 10-note 批次擴大為完整 100 篇疾病概念：`scheduled-disease-01` 至 `scheduled-disease-10`。每個既有子批次固定 10 篇，總數必須恰為 100。
- 每個疾病 Summary 以「**粗體標籤**＋短 bullets」呈現；有來源支持時採 Alzheimer’s disease 式的年齡／族群、臨床、病因／病理、檢查、影像、鑑別軸線，未支持的軸線必須省略。
- 每個 bullet 都必須回扣改寫前 Summary 的 fact unit 與既有 Obsidian `[^n]` 註腳。無法覆蓋、彼此衝突或需要額外登入查證的內容，必須留在 `research-needed` 或 `manual-review`，不得寫成新醫療結論。
- 每個 10-note 子批次各自建立 baseline lock、evidence report、scoped build 與兩次建置觀察；最後以 100-note tranche 驗收、獨立覆核與生成 JSON 一致性收束。

## Non-Goals

- 不重寫 anatomy 或 pattern-ddx scheduled 批次，也不修改 Phase 1／Phase 2A notes。
- 不在 vault 既有來源之外新增疾病知識、數值、診斷條件、影像特徵或引用。
- 不修改 frontmatter、Dataview、題庫、JSON schema、前端 renderer、全域 lint baseline，或手動編輯衍生 JSON。

## Capabilities

### New Capabilities

- `nr-summary-phase2b-disease-batch`: 定義 100 篇疾病 Summary 的分批來源鎖定、Alzheimer-style 短 bullet 結構、註腳／事實覆蓋、build 與 tranche 驗收。

### Modified Capabilities

- `vault-generation`: 從已驗證的 Phase 2B vault Summary 產生選定 concept JSON，且僅允許各子批次的 detail JSON 與 index 變動。

## Impact

- Affected specs: nr-summary-phase2b-disease-batch, vault-generation
- Affected code:
  - Modified: openspec/changes/restructure-nr-concept-summaries-phase2b/
  - Modified: docs/reports/nr-summary-rewrite/phase2-assignment.json
  - Modified: docs/reports/nr-summary-rewrite/phase2b/
  - Modified: scripts/nr_summary_audit.py
  - Modified: scripts/test_nr_summary_audit.py
  - Modified: scripts/build_concepts.py
  - Modified: vault/concepts/ (exactly the 100 members of scheduled-disease-01 through scheduled-disease-10)
  - Modified: data/concepts/ (only selected detail JSON files)
  - Modified: data/concepts-index.json
