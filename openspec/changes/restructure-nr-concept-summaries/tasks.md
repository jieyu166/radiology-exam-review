## 1. Audit tooling 與測試

- [x] 1.1 實作「Deterministic audit tooling does not generate medical prose」與「Observable behavior」：新增 scripts/nr_summary_audit.py 與 scripts/test_nr_summary_audit.py，提供 Public Python interfaces（parse_note、parse_note_text、extract_summary_sections、validate_summary、validate_inventory、validate_inventory_against_notes、validate_evidence）、穩定 Finding codes 與 CLI Failure modes；Task 1 的 validate_evidence／validate-batch 僅為可呼叫 placeholder，不驗證 evidence content，完整 evidence semantics 由 Task 3 實作且不更改 signature；以 python scripts/test_nr_summary_audit.py 輸出 NR_SUMMARY_AUDIT_OK、python -m py_compile 成功及 Acceptance criteria 所列命令驗證。

## 2. NR inventory 與分類

- [x] 2.1 滿足「NR concept inventory is complete and explicitly classified」與「Manual classification uses a closed enum and complete inventory」：建立 docs/reports/nr-summary-rewrite/inventory.json 的 JSON data shapes，明確分類 216 篇 notes、固定 10 篇 batch-00、其餘 206 篇 unassigned，並遵守 Scope boundaries；以 inventory --check 驗證 216／0 duplicate／0 unclassified／10／206。

## 3. Pilot baseline evidence

- [x] 3.1 滿足「Batch evidence provides lossless and source-mapped coverage」與「Fact coverage is an explicit batch evidence contract」：在任何 Summary edit 前建立 docs/reports/nr-summary-rewrite/batch-00.json，保存 10 篇 lossless originalSummary、originalSha256、穩定 fact units、sourceRefs 與 unresolved disposition；以 validate-batch --allow-pending 驗證 10 notes、0 missing sources，且每個 fact 均為 pending、research-needed 或 manual-review。

## 4. Pilot Summary 語意重組

- [x] 4.1 滿足「NR Summary bullets follow a type-specific labeled format」與「Summary rewriting preserves sourced medical facts」：只改寫固定 10 篇 pilot 的 Summary，以 type-specific bold-label top-level bullets 保存全部 qualifier、polarity、number、version、negation、exception 與 footnote，且不修改正文、題目、frontmatter、圖片、Dataview；逐篇以 validate-note 與 batch fact coverage review 驗證。
- [x] 4.2 滿足「Literature research is exception-driven and auditable」與「Source research is exception-driven」：僅對 unmapped、conflicted、time-sensitive 或 weak-source-dependent facts 啟用 radiology-topic-research，新增內容必須同步新增 article/chapter footnote；需要登入時將 note 保持 research-needed 並等待使用者自行登入，以 batch evidence 的 sourceStatus、sourceRefs 與 manual-review 狀態驗證。

## 5. Build、lint baseline 與網站輸出

- [x] 5.1 滿足「Generated keyPoints preserve source Summary bullets」與「Generated keyPoints must match source Summary bullets」：執行 scripts/build_concepts.py，僅保留 10 篇 pilot 對應的 deterministic JSON 差異，讓 validate-batch 比對 keyPoints 與 source top-level bullets；任何 mismatch 必須產生 generated-keypoints-mismatch 並阻止 verified。
- [x] 5.2 滿足「Phase 1 validation permits only the fixed non-NR lint baseline」與「Lint acceptance compares against a fixed baseline」：執行 smoke tests、validate-batch、build 與 scripts/lint_concepts.py --quiet，確認 NR pilot notes 零 error，project lint 僅保留 ceap-classification.md 的 [^*] 與 question 2022-264 的 ![[...]] 兩項既有 errors／124 warnings；新增 error、第三項 error 或 pilot error 均使 Phase 1 失敗。

## 6. Pilot baseline hash 獨立錨定

- [x] 6.1 補強「Batch evidence provides lossless and source-mapped coverage」與「Fact coverage is an explicit batch evidence contract」：將固定 10 篇 pilot 的受審 pre-edit `originalSha256` 置於 inventory.json／batch-00.json 之外的獨立 trust material，且 validation 不得從任一 mutable evidence file 推導 expected value；先以回歸測試重現同時把兩份 JSON 的同一 pilot hash 改為相同任意合法 64-hex 仍通過的缺陷，再使該案例產生穩定 trusted-baseline mismatch finding 並 nonzero exit，同時以 `python scripts/test_nr_summary_audit.py`、真實 `inventory --check`（216／10／206）與 `validate-batch` 通過驗證，保持 root `needs-review`、四項 manual queue、Phase 2 disabled 及非 pilot outputs 不變。
