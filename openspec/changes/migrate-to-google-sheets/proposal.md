## Why

題庫以 9 個 JSON 檔直接手改，已發生 commit `a8aa269` 意外覆寫 2016 年度 Q1–Q14 題幹的事故，且跨年度重複題目分散在多個 JSON 中無法同步管理。改以 Google Sheets 作為 source of truth 可提供結構化欄位、內建版本歷史，並透過同步腳本產生前端所需的 JSON，兼顧編輯安全與現有架構相容。

## What Changes

- 新增 `scripts/sheets_schema.py`：定義 Google Sheets 欄位常數與 schema 驗證邏輯（不含 `subspecialty_confidence`，此欄位已廢除）
- 新增 `scripts/json_to_sheets.py`：一次性將現有 `data/*.json` + `data/concepts.json` 匯出至 Google Sheets（去重跨年度題目，每題只存一列）
- 新增 `scripts/sheets_to_json.py`：日常同步腳本，從 Google Sheets 讀取後重新產生 `data/*.json` 與 `data/concepts.json`，包含 schema 驗證與 diff 報告
- 新增 `.env.example`：記錄 `SHEET_ID` 與 `GOOGLE_KEY_PATH` 環境變數範例
- 修改 `.gitignore`：忽略 Google service account 金鑰檔與 `.env`
- 修改 `README.md`：新增「如何編輯題目」章節（打開 Sheet → 編輯 → 執行 sync → commit）
- 修改 `scripts/README.md`：說明兩支腳本的安裝與執行方式
- `js/*` 前端不改，繼續讀取 `data/*.json`

## Non-Goals

- 本 change 不改前端：前端仍讀 `data/*.json`（日後版本規劃前端直接從 Google Sheets 載入，屬後續 change 範疇）
- 不做即時同步或 webhook：每次編輯後手動執行 `sheets_to_json.py`
- 不做 GitHub Actions 自動化（先手動驗證穩定後再評估）
- 不重新命名現有題目 ID（維持 `YYYY-NNN` 格式）
- 不將圖片移至 Google Drive（圖片仍存 git，explanation 中用 markdown 相對路徑引用）

## Capabilities

### New Capabilities

- `sheets-sync`: 在 Google Sheets 與本地 JSON 之間雙向同步題庫資料，包含匯出（json→sheets）與匯入（sheets→json）兩個腳本，以及 schema 驗證與衝突偵測

### Modified Capabilities

（無現有 spec 需更新）

## Impact

- Affected specs: `sheets-sync`（新建）
- Affected code:
  - `scripts/sheets_schema.py`（新增）
  - `scripts/json_to_sheets.py`（新增）
  - `scripts/sheets_to_json.py`（新增）
  - `.env.example`（新增）
  - `.gitignore`（修改）
  - `README.md`（修改）
  - `scripts/README.md`（修改）
