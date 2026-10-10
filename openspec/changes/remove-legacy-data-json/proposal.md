## Why

2026-09-08 起正式網站已完全由 vault Markdown 編譯（`vault-native-review-site` 已於 2026-10-10 驗收 archive），`data/` 下約 1000 個 JSON 與讀寫它們的腳本、JS、測試、specs 對網站已無作用，卻仍是 12 MB 的雙真相來源：題目 `reference` 只存在 `data/20xx.json`、4 張題圖只存在 `data/images/`、Phase 2B 稿件仍寫進 `data/concepts/`，每次改題都要雙寫。現在收尾，讓 vault 成為唯一來源、repo 只剩一條資料流。

## What Changes

- **資料搶救（刪除前）**：把 2007 題的 `reference` 字串寫入對應 vault 題卡 frontmatter 的 `reference` 欄位；為 `2019-521`、`2021-334` 補建 vault 題卡；4 張 `data/images/obsidian/*.png` 上傳 Cloudflare 圖床後改寫 4 張題卡的圖片連結。
- compiler 把 frontmatter `reference` 投影進 question record 與 `indexes/questions.json`；前端題目卡揭曉答案後顯示「參考來源」。
- **BREAKING** 刪除 `data/` 整個目錄（含 `20xx.json`、`concepts/`、`concepts-index.json`、`concepts.json`、`index.json`、`rex-edits-*.json`、`images/`、`2016_subspecialty_review.csv`），並在 `.gitignore` 加入 `data/`。
- **BREAKING** NR Summary Phase 1/2A/2B 稽核鏈整組退役：先將工作區未提交的 Phase 2B 成果（`scripts/nr_summary_audit.py`、測試、86 個 `data/concepts` JSON、`docs/reports/nr-summary-rewrite/phase2b/`）原樣 commit 封存，再刪除 `scripts/nr_summary_audit.py`、`scripts/build_concepts.py`、`scripts/build_phase2b_evidence.py`、`scripts/rewrite_phase2b_summary.py` 與其測試。`docs/reports/nr-summary-rewrite/` 證據檔保留不改。
- **BREAKING** 刪除 legacy 腳本：`json_to_vault.py`、`vault_to_json.py`、`merge_edits.py`、`sheets_to_json.py`、`json_to_sheets.py`、`sheets_schema.py`、`import_obsidian_sr.py`、`test_import_obsidian_sr.py`、`verify_obsidian_image_output.py`、`parse_2016.py`、`tmp_purge_oldimg.py`、`detect_cross_year_dupes.py`、`test_format.js`。
- 混用腳本改為 vault-only：`lint_concepts.py`（題目檢查改讀 vault 題卡 frontmatter，移除 `data/images` 檢查）、`audit_questions.py`、`extract_official_explanations.py`、`extract_subscription_refs.py`、`audit_concept_imaging.py`（題目資料改讀 `vault/questions/**/*.md` frontmatter 與內文）。
- `exam-explanation-pipeline` skill（`.claude/skills/` 與 `.agents/skills/` 兩份）改寫：輸入改為 vault 題卡與 `tmp/official-{year}.json`，輸出改為直接修改 vault 題卡（`??` 後詳解段與 frontmatter `reference`），移除 rex-edits patch 與 `merge_edits.py` 步驤。
- 刪除未被 `index.html` 載入的 JS 死碼：`js/app.js`、`card-mode.js`、`concept-cards.js`、`editor.js`、`exam-mode.js`、`format.js`、`list-mode.js`、`question-store.js`；`js/data-loader.js` 移除 legacy fetch 與 edit 函式，只留學習進度 API；`css/main.css` 移除僅供舊 JS 使用的 83 個 class 區段。
- 守門測試與稽核調整：`audit_vault_native_cutover.py`、`accept_vault_native_migration.py`、`test_legacy_isolation.py` 移除「legacy 還原工具必須存在」條件；`test_study_progress.js` 移除 `loadYear` 與 `data/` fetch mock；保留 `test_content_store.js` 與 `test_deploy_workflow.py` 對「不得 fetch/複製 data/」的斷言。
- 文件同步：`README.md`、`scripts/README.md`、`worktree 操作備忘.md` 移除 data/ 與 Sheets 流程描述；`openspec/specs/concept-lazy-loading`、`sheets-sync` 整份移除，`concept-subspecialty-filter`、`vault-generation`、`nr-summary-phase2b-disease-batch` 移除 data/ 與 legacy JS 引用。

## Capabilities

### New Capabilities

- `question-reference`: vault 題卡 frontmatter `reference` 欄位為題目參考來源的唯一儲存位置；compiler 投影到 question record 與 index，前端於揭曉答案後顯示。

### Modified Capabilities

- `vault-generation`: 移除「從 `data/{year}.json` 產生 vault」與 Phase 2B 寫入 `data/concepts` 的需求；vault 不再由任何 JSON 生成。
- `concept-lazy-loading`: 整份移除（概念清單已由 `vault-native-review-web` 的 `indexes/concepts.json` 懶載入涵蓋）。
- `sheets-sync`: 整份移除（Google Sheets 與 JSON 互轉流程退役）。
- `nr-summary-phase2b-disease-batch`: 移除「寫入 `data/concepts` 與 `concepts-index.json`」需求；Phase 2B 成果以 vault Summary 與 `docs/reports` 證據檔為最終型態。
- `concept-subspecialty-filter`: 移除對 legacy JS（`concept-cards.js`）與 `data/concepts-index.json` 的引用，改以 `indexes/concepts.json` 的 `subspecialty` 欄位描述。
- `vault-native-publication`: question record 與 `indexes/questions.json` 新增 `reference` 欄位。
- `vault-native-review-web`: 題目卡揭曉後顯示參考來源。

## Impact

- Affected specs: question-reference（新）、vault-generation、concept-lazy-loading（移除）、sheets-sync（移除）、nr-summary-phase2b-disease-batch、concept-subspecialty-filter、vault-native-publication、vault-native-review-web
- Affected code:
  - New: scripts/migrate_question_reference.py（一次性，執行後隨 data/ 一併刪除）、vault/questions/2019/2019-521.md、vault/questions/2021/2021-334.md、scripts/test_question_reference.py
  - Modified: scripts/vault_site/compiler.py、js/vault-question-view.js、js/data-loader.js、css/main.css、scripts/lint_concepts.py、scripts/audit_questions.py、scripts/extract_official_explanations.py、scripts/extract_subscription_refs.py、scripts/audit_concept_imaging.py、scripts/audit_vault_native_cutover.py、scripts/accept_vault_native_migration.py、scripts/test_legacy_isolation.py、scripts/test_study_progress.js、scripts/test_vault_site.py、scripts/test_vault_question_view.js、.claude/skills/exam-explanation-pipeline/SKILL.md、.agents/skills/exam-explanation-pipeline/SKILL.md、.gitignore、README.md、scripts/README.md、worktree 操作備忘.md、vault/questions/2017/2017-089.md、vault/questions/2017/2017-090.md、vault/questions/2023/2023-129.md、vault/questions/2023/2023-132.md、約 2007 張 vault 題卡 frontmatter
  - Removed: data/（整個目錄）、scripts/nr_summary_audit.py、scripts/test_nr_summary_audit.py、scripts/build_concepts.py、scripts/test_build_concepts.py、scripts/build_phase2b_evidence.py、scripts/rewrite_phase2b_summary.py、scripts/json_to_vault.py、scripts/vault_to_json.py、scripts/merge_edits.py、scripts/sheets_to_json.py、scripts/json_to_sheets.py、scripts/sheets_schema.py、scripts/import_obsidian_sr.py、scripts/test_import_obsidian_sr.py、scripts/verify_obsidian_image_output.py、scripts/parse_2016.py、scripts/tmp_purge_oldimg.py、scripts/detect_cross_year_dupes.py、scripts/test_format.js、js/app.js、js/card-mode.js、js/concept-cards.js、js/editor.js、js/exam-mode.js、js/format.js、js/list-mode.js、js/question-store.js、openspec/specs/concept-lazy-loading/spec.md、openspec/specs/sheets-sync/spec.md
