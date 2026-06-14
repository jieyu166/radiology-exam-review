## Context

目前放射科交換考題複習 Web App 以 9 個 JSON 檔（`data/2016.json`⋯`data/2024.json`）加上 `data/concepts.json` 儲存共約 1,230 道題目及 3 個概念。資料由開發者或協作醫師直接修改 JSON 或透過 `merge_edits.py` 腳本合併 patch 檔。

已知問題：
- commit `a8aa269 Render markdown and Obsidian images` 在預期只修改圖片路徑的過程中，意外用舊版 JSON 覆寫了 2016 年度 Q1–Q14 的題幹與選項（Q1–Q5 已透過後續 commit 修回，Q6–Q14 仍需人工驗證）
- 89 道跨年度題目分散存於多個年度 JSON 中，若只改其中一份就會造成不一致
- 無欄位驗證：`correctAnswer` 填錯字、`concepts` 打錯 ID 等問題只有在前端執行時才會發現

設計約束：
- 前端 `js/data-loader.js` 讀取 `data/*.json`，**不能更動前端**
- 圖片儲存於 `data/images/`（git），`explanation` 欄位以 markdown 相對路徑引用
- Google Sheets API 需要 OAuth 或 service account 認證

## Goals / Non-Goals

**Goals:**

- Google Sheets 作為題庫唯一 source of truth，題目的新增/修改/刪除均在 Sheet 上進行
- `json_to_sheets.py`：一次性將現有 JSON 去重匯出至 Sheet
- `sheets_to_json.py`：日常 sync，從 Sheet 產生 `data/*.json` 與 `data/concepts.json`，驗證欄位、產生 diff 報告
- `sheets_schema.py`：集中定義欄位常數與驗證規則，供兩支腳本共用
- 圖片仍留 git，不移動

**Non-Goals:**

- 本 change 前端不改（繼續讀 JSON）；前端直讀 Google Sheets 屬後續 change
- 不做即時 sync 或 webhook；sync 由人工手動觸發
- 不做 GitHub Actions 自動化（後續評估）
- 不重新命名題目 ID（維持 `YYYY-NNN`）
- 不把圖片搬到 Google Drive

## Decisions

### 每題一列的 questions sheet 設計

**決定**：questions sheet 中每道題目只存一列，以 `question_id`（`YYYY-NNN` 格式）為主鍵；跨年度出現的題目用 `years` 欄（逗號分隔，如 `2018,2019,2022`）記錄所有年份，sync 腳本展開時寫入各年度 JSON。`subspecialty_confidence` 欄位廢除不保留（用途不明確，auto/manual 區別對日後直讀 Sheet 無意義）。

**選項 A（選用）**：每題一列 + `years` 欄展開
**選項 B（放棄）**：每年一列，跨年度題目重複多列

放棄 B 的原因：B 會導致同一道題的詳解、答案可能在不同列各自編輯而分歧，重現今日 JSON 的問題。

### 選項 inline 而非另開 options sheet

**決定**：選項 A/B/C/D 各為 questions sheet 的一個欄位（`option_A`⋯`option_D`，加 `option_E` 備用）。

**選項 A（選用）**：inline 欄位
**選項 B（放棄）**：另開 options sheet，以 question_id + letter 為複合主鍵

放棄 B 的原因：放射科考題固定 4 個選項，用 join 反而增加編輯複雜度，且 Google Sheets 使用者通常不熟悉關聯式操作。

### concepts 用逗號分隔字串

**決定**：`questions.concepts` 欄位存逗號分隔的 concept ID（如 `upj-obstruction,calcium-score`）。concepts 定義存在獨立 concepts sheet。

**選項 A（選用）**：逗號分隔字串
**選項 B（放棄）**：question_concepts bridge sheet

放棄 B 的原因：Google Sheets 不是關聯式資料庫，bridge sheet 的維護成本高且對醫師編輯不友善；逗號分隔字串對 split/join 處理簡單，且 concept 數量預期不超過 10 個/題。

### 圖片仍留 git，不搬 Google Drive

**決定**：`explanation` 欄位維持現有 markdown 格式，圖片以 `![alt](data/images/obsidian/xxx.png)` 相對路徑引用。

**理由**：目前 245 張圖片已在 git；搬到 Google Drive 需要另一套 URL 管理邏輯，且 Drive 的公開分享 URL 不穩定。

### Service account 認證

**決定**：使用 Google service account JSON 金鑰，金鑰路徑存在 `.env` 的 `GOOGLE_KEY_PATH`；`.env` 與金鑰不進 git。

**理由**：Service account 不需要互動式 OAuth 流程，適合腳本自動化。開發者自行下載金鑰並設定環境變數。

## Risks / Trade-offs

- **[Risk] Explanation 欄位超過 Google Sheets 單格字元上限（50,000 字）** → Mitigation：`sheets_schema.py` 在寫入前檢查長度，超限時截斷並警告，不中斷整體 sync
- **[Risk] Google Sheets API 每日讀寫 quota（每分鐘 60 次寫入）** → Mitigation：`json_to_sheets.py` 使用 batch update（`batchUpdate` API），全部題目一次 call 完成
- **[Risk] 跨年度去重時發現 JSON 內容不一致** → Mitigation：`json_to_sheets.py` 以 `primary_year` 版本為準，並輸出衝突清單至 `scripts/conflicts.json` 供人工確認
- **[Risk] Service account 金鑰洩漏** → Mitigation：`.gitignore` 明確排除 `*.json`（服務帳戶金鑰）與 `.env`；`.env.example` 只放佔位符

## Migration Plan

1. **事前**：在 Google Cloud Console 建立專案、啟用 Sheets API、建立 service account 並下載 JSON 金鑰；建立空的 Google Sheet 並將 service account 加為編輯者
2. **匯出**：執行 `python scripts/json_to_sheets.py`，確認 Sheet 列數 ≈ 去重後題目總數，檢查 `scripts/conflicts.json`
3. **驗證**：執行 `python scripts/sheets_to_json.py --dry-run`，輸出與原始 JSON 的 diff，人工確認無意外差異
4. **上線**：執行 `python scripts/sheets_to_json.py`，`git diff` 確認僅有格式化差異，commit
5. **Rollback**：`git checkout HEAD -- data/` 可立即還原到上一個 JSON 版本；Google Sheet 保有版本歷史

### question_id 唯一性強制與欄位鎖定

**決定**：`question_id` 欄設為 Protected Range（僅 Sheet owner 可修改），且 `json_to_sheets.py` 寫入前必須驗證所有 question_id 無重複；若發現重複則中止寫入並輸出錯誤清單。

**理由**：question_id 是跨年度連結的唯一識別鍵，一旦手誤修改會造成 sync 後多個年度 JSON 產生孤兒資料。Protected Range 提供 UI 防護；寫入前驗證提供程式防護。

**實作**：`json_to_sheets.py` 彙整 dict 後，若 dict key（question_id）與來源 JSON 的 id 不一致（表示有重複），以 code 1 中止並列出衝突；寫入完成後呼叫 Sheets API `addProtectedRange` 將 A 欄（question_id）設為 WARNING 層級保護。
