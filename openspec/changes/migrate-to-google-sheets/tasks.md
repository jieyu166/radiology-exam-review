## 1. 準備與環境設定

- [x] 1.1 在 `.gitignore` 新增忽略規則：`*.json` 服務帳戶金鑰檔（`*-key.json`）、`.env`、`scripts/conflicts.json`
- [x] 1.2 建立 `.env.example`，包含 `SHEET_ID=<your-spreadsheet-id>` 與 `GOOGLE_KEY_PATH=~/.config/radiology-sheets-key.json` 兩個佔位符，加上說明如何取得 Google service account 金鑰
- [x] 1.3 在 `scripts/` 下新增 `requirements.txt`（或更新現有 requirements），加入 `google-auth>=2.0`、`google-auth-httplib2`、`google-api-python-client>=2.0`

## 2. Schema 定義模組（sheets-sync — schema definition module）

- [x] 2.1 建立 `scripts/sheets_schema.py`，依「每題一列的 questions sheet 設計」決定，定義 `QUESTIONS_COLUMNS` 有序清單（question_id, primary_year, number, years, subspecialty, question_text, option_A, option_B, option_C, option_D, option_E — 依「選項 inline 而非另開 options sheet」決定，correct_answer, reference, explanation, concepts — 依「concepts 用逗號分隔字串」決定，checked）與 `CONCEPTS_COLUMNS` 有序清單；`subspecialty_confidence` 已廢除不列入；圖片依「圖片仍留 git，不搬 Google Drive」決定維持 markdown 路徑，不加圖片欄位
- [x] 2.2 在 `sheets_schema.py` 定義 `VALID_SUBSPECIALTIES` 集合（ABD, CV, CH, Breast, H&N, MSK, NR, PED, US, IR, Physics, Unknown）
- [x] 2.3 在 `sheets_schema.py` 實作 `validate_question_row(row: dict) -> list[str]`：檢查 `correct_answer` 在 {A,B,C,D,E}、`subspecialty` 在允許清單、`question_text` 非空、`option_A/B/C` 非空，回傳錯誤字串清單（schema definition module 完成）

## 3. 認證模組（sheets-sync — authentication via service account；service account 認證）

- [x] 3.1 在 `scripts/sheets_schema.py`（或獨立的 `scripts/sheets_auth.py`）實作 `get_sheets_service()` 函式：依「service account 認證」決定讀取 `SHEET_ID` 環境變數（缺少時輸出 `Error: SHEET_ID environment variable not set` 並以 code 1 退出）；讀取 `GOOGLE_KEY_PATH` 環境變數（預設 `~/.config/radiology-sheets-key.json`）；金鑰檔不存在時輸出錯誤訊息並以 code 1 退出；成功時回傳 `(service, sheet_id)` tuple（authentication via service account 完成）

## 4. JSON 匯出腳本（sheets-sync — JSON to Sheets export）

- [x] 4.1 建立 `scripts/json_to_sheets.py`：讀取 9 個年度 JSON 檔，彙整所有題目至 dict（key = question_id）；依「question_id 唯一性強制與欄位鎖定」決定，若彙整時發現重複 question_id（內容不同）則輸出 `DUPLICATE: <id>` 至 stderr 並以 code 1 中止，不呼叫任何 API（question_id uniqueness and protected range 完成）
- [x] 4.2 在 `json_to_sheets.py` 實作 `years` 欄位合併邏輯：對每個 question_id，將所有出現年份合併為逗號分隔字串（JSON to Sheets export — cross-year duplicates 完成）
- [x] 4.3 在 `json_to_sheets.py` 實作 explanation 長度檢查：超過 49,000 字元時截斷為 49,000 字並附加 `[TRUNCATED]`，輸出 stderr 警告（explanation exceeds cell character limit 完成）
- [x] 4.4 在 `json_to_sheets.py` 呼叫 `get_sheets_service()`，使用 `batchUpdate` API 建立/清空 `questions`、`concepts`、`_metadata` 三個 sheet 並寫入全部資料（JSON to Sheets export — normal export 完成）
- [x] 4.5 在 `json_to_sheets.py` 寫入完成後呼叫 `addProtectedRange` API，將 `questions` sheet 的 A 欄（question_id）設為 `warningOnly: true` 的 Protected Range（question_id column protected after export 完成）

## 5. Sheets 同步腳本（sheets-sync — Sheets to JSON sync）

- [x] 5.1 建立 `scripts/sheets_to_json.py`（Sheets to JSON sync）：呼叫 `get_sheets_service()`，讀取 `questions` sheet 全部資料列
- [x] 5.2 在 `sheets_to_json.py` 對每列呼叫 `validate_question_row()`；驗證失敗的列輸出 `SKIP: <question_id> — <error>` 至 stderr 並略過，不寫入任何 JSON 檔（sync with validation error 完成）
- [x] 5.3 在 `sheets_to_json.py` 實作 `years` 展開邏輯：解析 `years` 欄逗號分隔整數，將每道題寫入所有對應年度的題目清單（cross-year expansion 完成）
- [x] 5.4 在 `sheets_to_json.py` 實作原子寫入：每個 JSON 先寫入 `<path>.tmp`，成功後 rename 為正式路徑；若寫入失敗則刪除 `.tmp` 並以 code 1 退出，原始檔案保持不變（atomic write on partial failure 完成）
- [x] 5.5 在 `sheets_to_json.py` 實作 diff 報告：與 `git show HEAD:data/<year>.json` 輸出比較，印出每個檔案的新增/刪除行數摘要（normal sync from clean Sheet 完成）

## 6. 文件更新

- [x] 6.1 更新 `scripts/README.md`：新增「安裝依賴」段（`pip install -r scripts/requirements.txt`）、`json_to_sheets.py` 使用說明（設定 SHEET_ID、GOOGLE_KEY_PATH，一次性執行）、`sheets_to_json.py` 使用說明（日常同步、--dry-run 模式）
- [x] 6.2 更新 `README.md`：在「如何編輯題目」章節說明 Google Sheets 工作流程（打開 Sheet → 編輯 → 執行 `python scripts/sheets_to_json.py` → `git diff data/` → commit）

## 7. 驗證

- [x] 7.1 執行 `python scripts/json_to_sheets.py`，確認 Sheet `questions` 的列數 ≈ 去重後題目總數（~1,141 列），`concepts` 有 3 列，`scripts/conflicts.json` 有衝突清單（如有）
- [ ] 7.2 執行 `python scripts/sheets_to_json.py`，確認輸出 `git diff data/` 幾乎為空（僅格式化差異），9 個年度 JSON + concepts.json 均正確產生
- [ ] 7.3 用瀏覽器開 `index.html`，隨機選 5 題不同年度，確認題幹、選項、詳解與概念連結顯示正常
- [ ] 7.4 在 Sheet 手動改一題 `checked` 欄為 `TRUE`，執行 sync，確認對應年度 JSON 的該題 `checked` 變為 `true`
