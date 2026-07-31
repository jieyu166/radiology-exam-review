## Why

Phase 1 已證明 10 篇 NR pilot 可以在不新增無來源結論的前提下，改寫為「粗體標籤＋短 bullets」，並由 inventory、fact ledger、footnotes、trusted baselines、scoped build 與獨立 review 驗證。Phase 2A 現在要把同一套契約擴展為可重複的 production batch，先處理剩餘 206 篇中的 30 篇，以三種筆記類型各一個 10-note batch 驗證量產能力。

## What Changes

- 建立完整 206-note Phase 2 assignment manifest；固定 Phase 2A 的三個 type-homogeneous batches，各 10 篇，其他 176 篇保持 scheduled-but-not-started。
- 為每個 batch 在改寫前建立 lossless baseline lock、原始 Summary、fact units、來源對映與獨立 trusted digest；每個 batch 必須能單獨驗證、重建及回滾。
- 依 Phase 1 核准格式改寫 10 篇 anatomy/measurement/management、10 篇 disease 與 10 篇 pattern-ddx Summary；不得修改正文、題目、frontmatter、圖片或 Dataview。
- 每個 batch 由獨立 implementer subagent 執行，並由另一個 reviewer subagent 做規格、事實覆蓋及來源審查；finding 必須在進入下一批前關閉。
- 將 exception-driven radiology-topic-research、Obsidian footnotes、manual-review queue 與 conservative wording 套用到每批；無法查證的 note 不得標為 verified，但不阻塞安全 sibling notes。
- 使用 batch-scoped build 只生成選定 10 篇的 concept JSON，並以 manifest 證明未改動其他 detail files 或 index metadata。
- Phase 2A 最終 gate 同時驗證 30 篇、三個 batch、全庫 lint baseline、完整 216-note inventory 與 978-entry generated corpus。

## Non-Goals

- 不在 Phase 2A 改寫其餘 176 篇 NR notes；它們由後續 Phase 2 tranches 處理。
- 不處理 NR 以外 subspecialties，也不把整個一千多份概念資料納入本 change。
- 不修復兩項既有非 NR lint errors，不修改前端 renderer 或 concept JSON schema。
- 不對每篇強制執行完整五來源研究；研究仍只由 unmapped、conflicted、time-sensitive 或 weak-source-dependent facts 觸發。
- 不代登入、不處理帳密、不規避存取控制或下載受限 PDF。

## Capabilities

### New Capabilities

- `nr-summary-production-batches`: 定義 Phase 2 assignment、type-homogeneous 10-note batches、baseline locks、subagent review gates、manual queues、tranche acceptance 與可繼續處理剩餘 notes 的契約。

### Modified Capabilities

- `concept-web-build`: 將 Phase 1 的單一 batch-scoped build 擴展為多個 production batch，仍須保持精確 keyPoints 映射、idempotence、index coherence 與非選定輸出零漂移。

## Impact

- Affected specs: nr-summary-production-batches, concept-web-build
- Affected code:
  - Modified: scripts/nr_summary_audit.py
  - Modified: scripts/test_nr_summary_audit.py
  - Modified: scripts/build_concepts.py
  - Modified: scripts/test_build_concepts.py
  - Modified: docs/reports/nr-summary-rewrite/inventory.json
  - New: docs/reports/nr-summary-rewrite/phase2-assignment.json
  - New: docs/reports/nr-summary-rewrite/phase2a/
  - Modified: vault/concepts/
  - Modified: data/concepts/
  - Modified: data/concepts-index.json

