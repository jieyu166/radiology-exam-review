## Context

Phase 2A 已建立 inventory、baseline lock、evidence report、scoped build、獨立覆核與 tranche validation 的可追溯流程，但僅涵蓋 30 篇 notes。現有 `phase2-assignment.json` 已把疾病 notes 劃為固定的 10-note scheduled batches。`scheduled-disease-01` 至 `scheduled-disease-10` 恰有 100 篇，可在不打散既有分組的前提下擴大本次範圍。

vault 是醫師編修的事實來源；`data/concepts/` 和 `data/concepts-index.json` 是從 vault Summary 衍生的靜態網站輸出。上一版本 change 的繁體 artifact 經 PowerShell 管線後產生實際 `0x3F` replacement bytes，因此本次必須以 UTF-8 正確重建所有可讀 artifact。

## Goals / Non-Goals

**Goals:**

- 修復 Phase 2B change artifacts 的 UTF-8 可讀性，並以原始位元組檢查避免再次將 CJK 字元替換為 `0x3F`。
- 對完整 100 篇疾病 notes 建立可獨立驗證的 10 個子批次，並保留每篇原始 Summary、事實單位、現有註腳與審查狀態。
- 將疾病 Summary 壓縮為可快速掃讀的 **粗體標籤**＋短 bullets；只出現來源直接支持的 Alzheimer-style 軸線。
- 在每個子批次通過來源、格式、build 與獨立覆核後，再接受 100-note tranche。

**Non-Goals:**

- 不將任何子批次外 note 納入 baseline、evidence、rewrite、build 或 review。
- 不以格式需求補足年齡、症狀、檢查或鑑別欄位，不新增沒有原始來源支持的疾病結論。
- 不手動修改 concept JSON，不變更 renderer、schema、frontmatter、Dataview 或題庫。

## Decisions

### 1. 以十個完整 scheduled disease batches 構成精確 100-note 範圍

Phase 2B 的唯一成員是 `scheduled-disease-01` 至 `scheduled-disease-10`；每批 10 篇、總計 100 篇。接受既有 batch 邊界可讓 baseline、build 與 reviewer 一次只處理 10 篇，也不會產生 99 或 101 篇的非完整範圍。替代方案是取前 100 個 scheduled notes；該作法會混入 anatomy notes 或切斷一個 10-note batch，故不採用。

### 2. 以可選 Alzheimer-style 軸線呈現疾病 Summary

每份疾病 Summary 使用一個或多個 **粗體標籤** 區塊，每個區塊含短 bullets。可使用的軸線是年齡／族群、臨床、病因／病理、檢查、影像、鑑別，或與原始內容直接等價的標籤。沒有來源支持的軸線必須省略。替代方案是固定六欄模板；該作法容易因填空而產生未支持內容，故不採用。

### 3. 以 baseline fact units 和既有 Obsidian footnotes 限制內容

每個 rewritten bullet 必須對應改寫前 lock 的 fact unit，並保留其既有 `[^n]` source reference；`[^n]:` 定義仍須存在。若 fact unit 沒有可用來源、來源互相衝突、或查證需要尚未提供的登入，必須標記為 `research-needed` 或 `manual-review`，不可用外部常識補寫。替代方案是以通用醫學知識潤飾；該作法無法證明來源覆蓋，故不採用。

### 4. 並行處理內容、序列化接受產物

十個子批次的 baseline、evidence 與 Markdown 改寫可由獨立工作者處理，前提是每人只寫入分配的 10 篇及對應 evidence。每個 scoped build、generated-manifest seal 與 tranche 更新必須依 batch 順序序列化，避免共享 `data/concepts-index.json` 與 trust registry 互相覆寫。替代方案是同時對多個批次建置；因共享 index 和兩次建置觀察會互相干擾，故不採用。

### 5. 每個子批次採兩次 scoped build 與獨立覆核

第一輪 build 只允許該批次 10 個 detail JSON 與 index 變動；第二輪必須無 byte 或 mtime 變化。另一位 reviewer 必須重比 lock、fact disposition、Summary、footnote 與 generated manifest，通過後才可 seal 該批次。替代方案是以單次 build 或同一人自評；無法排除非冪等輸出或來源判讀偏差，故不採用。

## Implementation Contract

- **Artifact encoding:** Phase 2B proposal、design、tasks MUST be valid UTF-8 and MUST preserve Traditional Chinese text without replacement `0x3F` bytes. The recovery check MUST distinguish actual file bytes from terminal rendering.
- **Scope:** Phase 2B MUST contain exactly the 100 assignment members in `scheduled-disease-01` through `scheduled-disease-10`. A baseline, evidence report, rewrite, manifest, generated output, or review record containing an omitted, duplicated, or out-of-scope slug MUST fail validation.
- **Summary behavior:** A target `## Summary` MUST use **粗體標籤** plus short bullets. A disease axis MUST appear only when one or more locked fact units and existing source references support it. The rewrite MUST preserve qualifiers, thresholds, exceptions and `[^n]` footnote definitions. It MUST NOT add facts beyond the lock or reviewed source.
- **Evidence behavior:** Every locked fact unit MUST have exactly one final disposition: `covered`, `research-needed`, or `manual-review`. `newUnsupportedFacts` MUST equal zero. A note or batch with any unresolved fact MUST NOT be claimed as verified; its derived manual queue MUST list that fact ID.
- **Build behavior:** For each 10-note sub-batch, `scripts/build_concepts.py` MUST write only its selected detail JSON files and `data/concepts-index.json`. Its second run MUST produce no byte or mtime delta. The generated keyPoints MUST equal the verified Summary bullet projection.
- **Review and acceptance:** A sub-batch MUST receive an independent approved review after evidence and build validation. The 100-note tranche MUST pass all sub-batch validators, source-hash and lossless Summary locks, source coverage, footnotes, generated-output checks, and its derived manual queue before acceptance.

## Risks / Trade-offs

- [100-note scope magnifies a source error] → baseline, evidence, validation and reviewer gates remain 10-note scoped; a failed batch blocks only itself.
- [Parallel workers modify shared outputs] → parallelism is confined to disjoint Markdown/evidence inputs; builds, manifests and tranche writes are serialized.
- [Short bullets omit qualification] → fact-unit coverage requires qualifiers, thresholds and exceptions to remain represented or be explicitly queued for review.
- [External literature requires login] → do not insert a claim; record `research-needed` with the missing verification condition.
- [Windows shell corrupts CJK content] → use UTF-8 file writes and byte-level verification rather than a PowerShell pipeline for artifact text.

## Migration Plan

1. Replace the corrupted Phase 2B artifacts with valid UTF-8 and validate their content before touching vault notes.
2. Promote the ten scheduled disease batches while preserving their membership and order; create a lock and evidence report for each.
3. Rewrite and strictly validate each 10-note batch; failed notes remain in a derived manual/research queue without generated publication.
4. Run each accepted batch's scoped build twice, seal its generated observation, then obtain independent review.
5. Run the 100-note tranche validation. If a gate fails, restore only the affected Summary from its hash-guarded lock and retain the evidence record for follow-up.
