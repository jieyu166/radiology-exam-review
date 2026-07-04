## Why

舊放射 vault 太複雜、讀書時間有限，難以逐題複習交換考題。先前的網站／Google Sheets／稽核流水線方向過於龐大。改以獨立、乾淨的 Obsidian vault 整理交換考題：以 spaced repetition（SR）卡片複習、以 concept 筆記組織知識，先做 2016。

## What Changes

- 在 radiology-exam-review repo 內新增一個獨立 Obsidian vault（子資料夾 vault/，含自己的 .obsidian/ 設定），與既有網站程式碼分離。
- 新增轉檔腳本，將既有 data/2016.json 的 197 題轉為一題一檔的 SR 卡片 markdown：YAML frontmatter（id/year/subspecialty/correctAnswer/concepts/checked）+ tag 行（#交換 #2016交換 #{subspecialty}）+ 題幹選項 + `??` 分隔 + 答案與逐選項詳解 + 內文 [[concept-id]] 概念連結。
- 為被引用到的 concept 產出一概念一檔的概念筆記（概念說明 + Dataview 動態匯整相關題），題目→概念用 [[ ]] 連結產生反向匯整。
- 轉檔腳本冪等：預設不覆寫已存在卡片以保護使用者編輯與 SR 排程；覆寫模式下永遠保留檔內 SR 排程註解行。
- 詳解不足的題（由既有 audit 判定）交給既有 exam-explanation-pipeline skill 補詳解（官方詳解優先、不足才生成），更新回 data/2016.json 後重生受影響卡片。
- 單一內容真實來源仍為 data/2016.json；vault 由其產生。

## Non-Goals

- 不做網站整合、不動既有 js/、index.html、Google Sheets 同步腳本。
- 本變更只處理 2016；其他年份之後比照辦理。
- 不修改既有 data 內容（除 Step 2 補詳解流程更新個別題目欄位外）。
- 不代為安裝 Obsidian 社群外掛（Spaced Repetition、Dataview）；腳本僅寫入外掛設定。

## Capabilities

### New Capabilities

- `vault-generation`: 將 data/{year}.json 與 data/concepts.json 轉為 Obsidian SR vault（題目卡片 + 概念筆記），含 SR 卡片格式、概念反向連結匯整、冪等重生與 SR 排程保留，以及詳解不足題重生流程。

### Modified Capabilities

(none)

## Impact

- Affected specs: 新增能力 vault-generation
- Affected code:
  - New: scripts/json_to_vault.py, vault/.obsidian/, vault/questions/2016/, vault/concepts/
  - Modified: data/2016.json, README.md
  - Removed: 無
- 既有資產（僅讀取、不修改）：data/concepts.json、scripts/verify_reference.py、scripts/audit_questions.py、.claude 內 exam-explanation-pipeline skill
- 前置需求：使用者需在 Obsidian 安裝並啟用 Spaced Repetition 與 Dataview 社群外掛
