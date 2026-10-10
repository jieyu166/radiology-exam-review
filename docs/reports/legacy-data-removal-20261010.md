# Legacy `data/` JSON 資料流移除報告

- 日期：2026-10-10
- Change：`remove-legacy-data-json`（16 任務）
- 結論：**`data/` 與所有讀寫它的程式已自 repo 移除，vault Markdown 為唯一來源；全量驗收 `accept_vault_native_migration.py` 回報 passed: true。**

## 三段獨立 commit

| 段 | commit | 內容 |
|---|---|---|
| 封存 | `342a349` | 原樣提交 Phase 2B 稽核鏈最終成果（nr_summary_audit.py 等 4 支、86 個 data/concepts JSON、docs/reports phase2b 證據），供日後重現 seal |
| 搶救 | `3f34d16`、`2bb2894` | 2005 題 `reference` 遷入題卡 frontmatter；補建 2019-521、2021-334；4 張題圖改 Cloudflare 圖床；compiler／前端投影並顯示參考來源（已部署並線上驗證） |
| 刪除 | 本次 | `git rm -r data/`（1003 檔）、退役 19 支腳本與測試、8 支 JS 死碼、CSS 564 行；混用腳本改讀 vault；守門稽核反轉；skill 與文件改寫 |

## 搶救結果

| 項目 | 數字 |
|---|---|
| 遷入 frontmatter 的 reference | 2005 題（每檔恰 +1 行，body bytes 不變） |
| 已有 reference 的衝突 | 0 |
| 補建題卡 | 2019-521（CH）、2021-334（MSK，缺圖，標 `reviewStatus: needs_review`） |
| 上傳 Cloudflare 的題圖 | 4 張（2017-089、2017-090、2023-129、2023-132），HTTP 200 |
| 遷移前後 dist 逐題比對 | 3000 筆 record 的 sr／outline／diagnostics 完全一致（行號位移已校正） |

compiler 連帶修正：links／embeds／wikilink 概念與 syntax inventory 只掃 frontmatter 之後的 body，避免含 `[[wikilink]]` 的 reference 造成重複連結（211 張題卡受影響）。

## 刪除清單

- `data/` 整個目錄：`2016–2024.json`、`concepts/*.json`（980）、`concepts-index.json`、`concepts.json`、`index.json`、`rex-edits-*.json`、`images/`、`2016_subspecialty_review.csv`。`.gitignore` 新增 `data/`。
- 腳本：`nr_summary_audit.py`、`test_nr_summary_audit.py`、`build_concepts.py`、`test_build_concepts.py`、`build_phase2b_evidence.py`、`rewrite_phase2b_summary.py`、`json_to_vault.py`、`vault_to_json.py`、`merge_edits.py`、`sheets_to_json.py`、`json_to_sheets.py`、`sheets_schema.py`、`import_obsidian_sr.py`、`test_import_obsidian_sr.py`、`verify_obsidian_image_output.py`、`parse_2016.py`、`tmp_purge_oldimg.py`、`detect_cross_year_dupes.py`、`test_format.js`、一次性 `migrate_question_reference.py` 與其測試。
- JS：`app.js`、`card-mode.js`、`concept-cards.js`、`editor.js`、`exam-mode.js`、`format.js`、`list-mode.js`、`question-store.js`；`data-loader.js` 346 → 168 行，只留學習進度 API，無任何 fetch。
- CSS：`main.css` 1217 → 655 行；判準為 class 在 index.html 與 5 支保留 JS 皆未出現；對照表 `tmp/css-class-audit.json`。
- Specs：`concept-lazy-loading`、`sheets-sync` 整份移除（archive 時套用）。

## 改寫

- 新增 `scripts/vault_questions.py`（`iter_question_cards`，重用 compiler 解析），`lint_concepts.py`、`audit_questions.py`、`extract_official_explanations.py`、`extract_subscription_refs.py`、`audit_concept_imaging.py` 全部改讀題卡，CLI 與輸出 schema 不變。
- `audit_vault_native_cutover.py`：`legacyRecoveryToolsPresent` 改為 `legacyToolsAbsent` ＋ `legacyResidue`，`data/` 或任一退役腳本／JS 存在即 exit 1，CI 每次部署都會跑。
- `exam-explanation-pipeline` skill（兩份統一）：輸入 vault 題卡與 `tmp/official-{year}.json`，輸出直接改題卡詳解段與 frontmatter `reference`。
- `README.md`、`scripts/README.md`、`worktree 操作備忘.md`、`scripts/requirements.txt` 同步。

## 驗收

| 檢查 | 結果 |
|---|---|
| `accept_vault_native_migration.py` | passed: true，無 blocker |
| `test_vault_site.py`（9）、`test_vault_questions.py`（9）、`test_legacy_isolation.py`（5）、`test_deploy_workflow.py`（3） | 全過 |
| 4 支 node smoke tests | 全過 |
| `audit_vault_native_cutover.py` | `legacyToolsAbsent: true`、`legacyResidue: []` |
| `git ls-files data/` | 0 |
| `grep "data/"` scripts／js／index.html／.github | 僅剩守門測試的負向斷言與一行註解 |

## 留待後續

1. `index.html` 仍含舊殼層 class（toast-container、result-*、exam-grid*、edit-panel 等），對應約 20 條 CSS 因此保留；若清 index.html 殼層可再刪一輪。
2. compiler `_question_projection` 會把 body wikilink 就地 append 進 `note.frontmatter["concepts"]`（既有行為，vault_questions.py 已迴避）；建議改為複製列表。
3. `vault/全文待查清單.md`、`vault/概念影像補強清單.md` 是 2026-06 舊產物，檔頭仍寫 `data/*.json`；重跑對應腳本即可更新，本 change 未動醫師筆記。
4. `scripts/verify_reference.py` 白名單與既有題卡 reference（Dahnert、Primer 等）有張力，skill 已規定既有值只追加不刪。
5. 下一個 change：學習功能強化與使用者帳號（見 memory `learning-features-direction`）。
