## Why

NR concept 的 Summary 目前雖有完整醫學內容，但格式不一致、長清單不利考前快速掃讀，
且缺乏可稽核的事實覆蓋與來源驗證流程。現在需要先以 10 篇代表性筆記校準
「粗體標籤＋短 bullets」語意重組規則，再安全擴展到其餘 NR concepts。

## What Changes

- 新增 NR Summary inventory、結構驗證、footnote 驗證與 batch evidence 驗證工具。
- 將 216 篇 NR concepts 明確分類為 disease、pattern-ddx 或
  anatomy-measurement-management；Phase 1 固定 10 篇 pilot，其餘 206 篇維持
  unassigned。
- 僅改寫 10 篇 pilot 的 Summary，保留正文、題目、frontmatter、圖片、Dataview 與
  既有 references。
- 每個原 Summary 事實單元建立來源對映；不得遺失限定詞、否定、數值、版本，或新增
  無來源結論。
- 僅在來源不足、衝突、時效性規則或弱來源無法安全壓縮時啟用
  radiology-topic-research。
- 驗證網站 JSON 的 keyPoints 與 vault Summary bullets 一致。
- 將既有 lint baseline 固定為 2 errors／124 warnings；本變更不得新增 error，
  NR pilot notes 自身必須零錯誤。

## Non-Goals

- 不處理其餘 206 篇 NR Summary；它們在 pilot 核准後由 Phase 2 change 處理。
- 不修改前端 Markdown renderer 或 concept JSON schema。
- 不修復 ceap-classification.md 與 data/2022.json 的既有非 NR lint errors。
- 不對全部 NR concepts 執行完整五來源查證。
- 不代登入、不處理帳密、不規避存取控制、不下載受限 PDF。

## Capabilities

### New Capabilities

- `nr-summary-quality`: 定義 NR Summary 分類、格式、事實覆蓋、來源對映、批次 evidence
  與 lint baseline 驗證契約。

### Modified Capabilities

- `concept-web-build`: 明確要求生成的 per-concept keyPoints 與來源 Markdown Summary
  的 top-level bullets 一致，並在 pilot 中驗證此映射。

## Impact

- Affected specs: nr-summary-quality, concept-web-build
- Affected code:
  - New: scripts/nr_summary_audit.py
  - New: scripts/test_nr_summary_audit.py
  - New: docs/reports/nr-summary-rewrite/inventory.json
  - New: docs/reports/nr-summary-rewrite/batch-00.json
  - Modified: vault/concepts/clippers.md
  - Modified: vault/concepts/cerebral-amyloid-angiopathy.md
  - Modified: vault/concepts/craniopharyngioma.md
  - Modified: vault/concepts/basal-ganglia-t1-shortening.md
  - Modified: vault/concepts/cpa-masses.md
  - Modified: vault/concepts/bilateral-subcortical-dwi-hyperintensity-ddx.md
  - Modified: vault/concepts/artery-of-adamkiewicz.md
  - Modified: vault/concepts/aspects-score.md
  - Modified: vault/concepts/acute-stroke-management.md
  - Modified: vault/concepts/dementia-neuroimaging-overview.md
  - Regenerated: corresponding files under data/concepts/ and
    data/concepts-index.json when a deterministic diff exists
