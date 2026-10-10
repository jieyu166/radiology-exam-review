## Context

正式網站自 commit 2089da9 起由 `scripts/vault_site/compiler.py` 將 `vault/` 編譯為 `dist/`，GitHub Actions 部署。`data/` 目錄（約 1000 個 JSON、12 MB）與其讀寫腳本已不在正式路徑，但仍是三類資料的唯一副本：

1. 2007 題的 `reference` 字串（來源書目），只存在 `data/20xx.json`，vault 題卡 frontmatter 沒有此欄位。
2. 2 題（`2019-521`、`2021-334`）只在 `data/` 有紀錄，vault 無題卡。
3. 4 張題圖 `data/images/obsidian/*.png`，被 `2017-089`、`2017-090`、`2023-129`、`2023-132` 四張題卡以相對路徑嵌入；`vault/images/` 在 `.gitignore` 內，`dist/` 不含 `data/`，這 4 張在線上已是破圖。

另有一條與網站無關但深度耦合 `data/concepts/` 的工具鏈：`scripts/nr_summary_audit.py`（約 9000 行）以 code-owned SHA-256 seal 綁定 `data/concepts/*.json` 的內容來驗證 NR Summary Phase 1/2A/2B 改寫；工作區有 1784 行未提交的 Phase 2B 修改與 86 個未提交的 `data/concepts` JSON。使用者已決定整組退役。

`exam-explanation-pipeline` skill（`.claude/skills/` 與 `.agents/skills/` 各一份）以 `data/20xx.json` 為輸入、以 rex-edits patch 為輸出，使用者已決定改寫為直接修改 vault。

約束：vault 題卡是醫師手寫內容，任何批次改寫只允許新增 frontmatter 欄位與替換圖片連結，不得改動內文；`docs/reports/` 內的封存證據檔（含 data/ 路徑與 hash）不得改寫。

## Goals / Non-Goals

**Goals:**

- `data/` 從 repo 消失後，網站、CI、所有保留腳本與測試仍全部通過。
- `reference`、2 張缺卡、4 張圖片在刪除前完整遷入 vault 或 Cloudflare 圖床，網站可見。
- NR Summary 稽核鏈的最後狀態（Phase 2B）原樣封存於 git 歷史與 `docs/reports/`，之後移除程式碼。
- 詳解流水線 skill 改以 vault 為唯一讀寫對象。
- 文件與 specs 不再出現 `data/` 資料流。

**Non-Goals:**

- 不改寫 git 歷史、不做 filter-repo；`.git` 大小不變。
- 不重做 NR Summary 稽核的 vault-only 版本；Summary 品質日後由 compiler warning 與 `find_weak_concepts.py`／`find_shallow_concepts.py` 把關。
- 不新增前端功能（FSRS、作答事件流等 mcq-bank 借鏡另開 change）。
- 不處理 `vault/醫師待辦清單.md` 等醫師筆記內提到 data/ 的文字。
- 不整理 `.git` loose objects（另行 `git gc`）。

## Decisions

### 先搶救再刪除：reference 遷入 frontmatter、缺卡補建、圖片上 Cloudflare

- `reference` 寫成題卡 frontmatter 的 `reference` 純字串欄位（與 `data/` 原值逐字相同，不拆解、不正規化）。替代方案「寫進內文 footnote」被否決：內文是醫師手寫區，且 footnote 會進 SR back 面影響閱讀。
- 遷移腳本 `scripts/migrate_question_reference.py` 一次性執行，只在 frontmatter 區塊末尾（`---` 前）插入一行，內文 byte 不變；題卡已有 `reference` 時以 vault 為準不覆寫，並回報差異。腳本在任務完成後隨 `data/` 一併刪除，避免留下讀 `data/` 的程式。
- 2 張缺卡依現有題卡格式手寫建立（frontmatter + `#交換 #YYYY交換 #Sub` 題幹 + 選項 + `??` + `**Ans: X**` + 詳解），來源為 `data/2019.json`、`data/2021.json` 對應紀錄；`2021-334` 的圖 `2021-334-1.png` 若在 `data/images/` 找不到，則題卡標 `reviewStatus: needs_review` 並在詳解註明缺圖。
- 4 張 PNG 依既有 img-hosting 技能上傳 Cloudflare 取得 URL，題卡中 `data/images/obsidian/...` 替換為該 URL；替代方案「放進 `vault/images/`」被否決，因該目錄被 gitignore，CI 看不到。

### compiler 與前端投影 reference

- compiler 在 question record 的 `sr` 投影與 `indexes/questions.json` 各題目項目新增 `reference` 字串欄位（frontmatter 無此欄位時為空字串）。
- 題目卡 view 在揭曉答案後、答案徽章之後渲染 `vault-question-reference` 區塊顯示「參考來源：…」；空字串不渲染。文字以 `_esc` 轉義，不解析 Markdown。
- `indexes/search.json` 不納入 reference（避免搜尋被書目噪音淹沒）。

### NR Summary 稽核鏈整組退役，先封存再刪

- 第一步以單一 commit 原樣提交工作區現有的 Phase 2B 成果：`scripts/nr_summary_audit.py`、`scripts/test_nr_summary_audit.py`、`scripts/build_concepts.py`、`scripts/test_build_concepts.py`、86 個 `data/concepts/*.json`、`data/concepts-index.json`、`docs/reports/nr-summary-rewrite/phase2b/`、`openspec/changes/archive/2026-08-02-restructure-nr-concept-summaries-phase2b/`、`openspec/specs/nr-summary-phase2b-disease-batch/`。此 commit 不改任何內容，目的是讓 seal 與其綁定的資料在歷史中可重現。
- 第二步刪除 `nr_summary_audit.py`、`build_concepts.py`、`build_phase2b_evidence.py`、`rewrite_phase2b_summary.py` 及四者測試。`docs/reports/nr-summary-rewrite/` 全部保留。
- 替代方案「改寫為 vault-only 並重封 seal」被否決：100 多處 `data/concepts` 引用、70 多個測試要改，而稽核鏈的任務（100 篇 NR Summary 改寫）已完成。

### 混用腳本改讀 vault 題卡

- 共用一個新模組 `scripts/vault_questions.py`，提供 `iter_question_cards(vault_root)`，回傳 `QuestionCard` 含 `id`、`year`、`subspecialty`、`correct_answer`、`concepts`、`reference`、`stem`（`??` 前、去掉 tag 行的題幹）、`options`（A–E 文字）、`explanation`（`??` 後原文）、`path`。解析規則與 compiler 的 SR 切分一致，直接重用 compiler 內的 frontmatter／SR 邊界函式而非複製。
- `lint_concepts.py`：題目段改用 `iter_question_cards` 檢查 `concepts` 是否存在於 `vault/concepts/`、`correctAnswer` 是否為 A–E；刪除 `data/images` 壞圖／孤兒圖檢查。
- `audit_questions.py`、`extract_official_explanations.py`、`extract_subscription_refs.py`、`audit_concept_imaging.py`：所有 `data/{year}.json` 讀取改為 `iter_question_cards`，欄位對應 answer→`correct_answer`、questionText→`stem`、explanation→`explanation`、reference→`reference`、每概念考題數→依 `concepts` 統計。輸出格式不變。

### 詳解流水線 skill 改為直接修改 vault

- 兩份 `exam-explanation-pipeline/SKILL.md` 內容統一為同一版本。輸入：`tmp/official-{year}.json`（由改寫後的 `extract_official_explanations.py` 產生）與 vault 題卡。輸出：直接編輯題卡 `??` 之後的詳解段，以及 frontmatter `reference`；`checked` 保持 false 交醫師覆核。
- 移除 rex-edits patch、`merge_edits.py`、`git add data/` 所有步驧；`verify_reference.passes_gate()` 閘門保留。
- 進度檔 `tmp/pipeline-progress.json` 機制保留。

### 守門測試改為 legacy 工具不得存在

- `audit_vault_native_cutover.py` 的 `legacyRecoveryToolsPresent` 欄位改名為 `legacyToolsAbsent`，語意反轉：`scripts/` 不得存在 `LEGACY_PRODUCTION_NAMES` 名單中的檔案與 `json_to_vault.py`、`vault_to_json.py`、`merge_edits.py`，且 repo 根不得存在 `data/` 目錄；任一存在即 exit 1。`accept_vault_native_migration.py`、`test_legacy_isolation.py` 同步改用新欄位。
- `test_content_store.js` 與 `test_deploy_workflow.py` 既有「不得 fetch／複製 `data/`」斷言保留。
- `.gitignore` 加入 `data/`，防止舊腳本殘留在他處重新產生後被誤 commit。

### JS 與 CSS 死碼移除

- 刪除 `index.html` 未載入的 8 支 JS。`data-loader.js` 只保留 `vault-app.js` 實際呼叫的進度 API：`getProgress`、`markSeen`、`recordAnswer`、`addExamRecord`、`exportProgress`、`importProgress`、`clearProgress`、`exportAllEdits`／`exportLegacyEdits`；`toggleStar`／`isStarred` 一併保留（進度 schema 含 `starred`，匯入匯出需向下相容）。移除 `loadIndex`、`loadYear`、`loadConcepts`、`loadConceptsIndex`、`loadConcept`、`loadAllAvailableYears`、`getLoadedQuestions`、`saveConceptEdit`、`saveQuestionEdit`、`discardAllEdits`、`countPendingEdits`、`_getLocalEdits`、`_mergeEdits`。
- `css/main.css` 刪除只被舊 JS 使用的區段（卡片模式、徽章、列表／Accordion、舊模擬考結果、編輯面板、舊概念卡、toast、燈箱）；保留導覽、篩選、按鈕、Responsive 與 `Vault-native` 區段。以「class 名稱在 `index.html` 與 5 支保留 JS 中都未出現」為刪除判準，逐一 grep 確認。

## Implementation Contract

**Behavior**

- 題目卡揭曉答案後，若題卡 frontmatter 有非空 `reference`，畫面顯示「參考來源：<原文>」；無則不顯示任何參考來源元素。
- 執行 build_vault_site 產出的 `dist/indexes/questions.json` 每筆含 `reference` 字串鍵；`dist/records/question/<id>.json` 的 `sr.reference` 同值。
- 執行 audit_vault_native_cutover 在 `data/` 或任何 legacy 腳本存在時 exit 1 並於報告 `legacyToolsAbsent: false` 列出殘留路徑；全部移除後 exit 0。
- lint_concepts、audit_questions、extract_official_explanations、extract_subscription_refs、audit_concept_imaging 五支腳本在 `data/` 不存在時正常執行，輸出 schema 與現況一致。
- 題卡 `2017-089`、`2017-090`、`2023-129`、`2023-132` 的圖片在線上網站可載入（HTTP 200）。
- `2019-521`、`2021-334` 出現在 `dist/indexes/questions.json`。

**Interface / data shape**

- vault 題卡 frontmatter 新增可選鍵 `reference: <string>`。
- `scripts/vault_questions.py`：`iter_question_cards(vault_root: Path) -> Iterator[QuestionCard]`；`QuestionCard` dataclass 欄位 `id, year: list[int], subspecialty: str, correct_answer: str, concepts: list[str], reference: str, stem: str, options: dict[str, str], explanation: str, path: Path`。
- cutover audit 報告 JSON：移除 `legacyRecoveryToolsPresent`，新增 `legacyToolsAbsent: bool` 與 `legacyResidue: list[str]`。
- 遷移腳本參數 `--data data --vault vault [--dry-run]`：stdout 印 JSON `{"updated": n, "alreadyPresent": n, "conflicts": [...], "missingCards": [...]}`；`conflicts` 為 vault 已有且與 data 不同的題號。

**Failure modes**

- 遷移腳本遇到 frontmatter 無法解析的題卡：跳過並列入 `missingCards`，不寫入；非零 exit。
- compiler 遇到 `reference` 非字串（如 list）：發 warning `reference_not_string` 並投影為空字串，不 hard error。
- `iter_question_cards` 遇到缺 `??` 邊界的題卡：略過該卡並以 stderr 警告，與 compiler 的 missing boundary 行為一致。

**Acceptance criteria**

- test_vault_site：新增 fixture「有 reference」「無 reference」「reference 為 list」三案通過。
- test_vault_question_view：新增「揭曉後顯示參考來源」「空 reference 不渲染」兩案通過。
- 新增 test_question_reference：遷移腳本 dry-run／實跑／衝突三案於 temp 目錄通過。
- test_legacy_isolation、test_deploy_workflow、test_content_store、test_study_progress、test_note_renderer 全部通過。
- accept_vault_native_migration 回報 `passed: true`。
- `git ls-files data/` 為空；grep `data/` 於 scripts、js、index.html、.github、兩份 README 僅剩守門測試中的負向斷言字串。
- 推送 main 後 deploy-pages workflow 成功，線上任一有 reference 的題目揭曉後可見參考來源。

**Scope boundaries**

- In：上述 Decisions 全部；vault 題卡只動 frontmatter 與 4 個圖片連結。
- Out：題卡內文、概念卡、`docs/reports/`、git 歷史、新學習功能、`vault/` 內醫師筆記文字。

## Risks / Trade-offs

- [批次改 2007 張題卡 frontmatter 誤傷內文] → 腳本只在 frontmatter 結尾 `---` 前插入一行；以 git diff --stat 確認每檔恰 +1 行，並以 compiler 重建後 `sourceSha256` 以外欄位（stem、options、back）與改前 `dist/` 逐題比對相同。
- [OneDrive 同步時批次寫檔造成衝突副本] → 先暫停 OneDrive 同步或在非 OneDrive 的 worktree 執行，完成後 commit 再恢復。
- [Phase 2B 工作區修改屬於另一個 session] → 封存 commit 前以 git status 列出並確認無新變動；只 add 明確列出的路徑，不用 add -A。
- [刪除 nr_summary_audit 後無人把關 Summary 結構] → compiler 既有 warning 與 `find_weak_concepts.py`／`find_shallow_concepts.py` 繼續可用；Phase 2B 證據封存於 `docs/reports/`。
- [reference 文字含 `<`、`&`] → 前端一律 `_esc`。
- [刪 CSS 誤刪保留 JS 的 class] → 刪除前後各跑一次 browser smoke tests，並以 grep 清單為唯一判準。

## Migration Plan

1. 封存 commit：原樣提交 Phase 2B 工作區成果（不改內容）。推 main（不觸發部署，因路徑不在 workflow 過濾內）。
2. 搶救 commit：圖片上傳 Cloudflare 並改 4 張題卡；補建 2 張缺卡；執行遷移腳本；compiler／前端加 reference；跑全部測試；推 main 觸發部署，線上確認參考來源與圖片。
3. 刪除 commit：移除 `data/`、刪 legacy 腳本與 JS／CSS 死碼、改混用腳本、改守門稽核、改 skill 與文件、刪兩份 spec；跑全部測試與 accept_vault_native_migration；推 main 部署。
4. 回滾：三個 commit 各自獨立，任一出問題 git revert 該 commit 即可；步驧 3 回滾後 `data/` 內容與步驧 1 封存時一致。

## Open Questions

- 無。三項關鍵決策（稽核鏈退役、reference 遷入 frontmatter、skill 改寫為直接改 vault）已於 2026-10-10 由使用者確認。
