# 放射科交換考題複習

放射科住院醫師交換考題線上複習系統，支援卡片翻牌、列表瀏覽、模擬考試三種模式。

## 功能特色

- **卡片模式**：逐題翻牌複習（題目 → 答案 → 詳解），支援觸控滑動與鍵盤導航
- **列表模式**：所有題目以可展開的 accordion 呈現，快速瀏覽
- **模擬考模式**：隨機抽題、倒數計時、自動評分與錯題分析
- **概念卡片**：疾病/概念知識卡片，與考題雙向連結
- **編輯介面**：醫師可直接在網頁上修改題目內容、標記已確認
- **內容審核**：每題有 `checked` 欄位，預設只顯示已確認內容
- **響應式設計**：手機、平板、桌面皆可使用

## 使用方式

### 線上使用

前往 GitHub Pages：`https://jieyu166.github.io/radiology-exam-review/`

### 本機使用

```bash
# 啟動本地伺服器
python -m http.server 8080
# 開啟瀏覽器前往 http://localhost:8080
```

### 編輯流程（Google Sheets 工作流程）

題目資料以 Google Sheets 為 source of truth，日常編輯流程：

1. 開啟 Google Sheets 試算表（`questions` sheet）
2. 直接編輯題目內容（題幹、選項、正確答案、詳解、subspecialty、概念等）
3. 編輯完成後，在本機執行同步腳本：
   ```bash
   python scripts/sheets_to_json.py
   ```
4. 確認變更符合預期：
   ```bash
   git diff data/
   ```
5. 提交並發布：
   ```bash
   git add data/
   git commit -m "sync: update questions from Google Sheets"
   git push
   ```

首次設定請參考 [`scripts/README.md`](scripts/README.md)，需要設定 Google service account 金鑰。

## 資料來源

- 交換考題 PDF（2016–2024）
- 已匯入：**2016–2024 共 1,230 題**（各年 15–239 題）
- 官方詳解 PDF（vault `3. Resources/論文s/交換考/`）為詳解的事實基礎

## 詳解流水線（機器先審、人覆核）

為大量未審核題目逐批製作逐選項詳解、補放射來源 reference、補分類，再由醫師覆核。
移植 robust-lit-review 的品質工程骨架，查核閘改為放射科來源（期刊/radiopaedia/statdx/教科書/官方詳解）。

```bash
# 1) 便宜層：抽官方詳解 + 稽核基準（每年份一次）
python scripts/extract_official_explanations.py 2016   # → tmp/official-2016.json
python scripts/audit_questions.py 2016                 # → tmp/audit-2016.json

# 2) 智慧層：在 Claude Code 內呼叫 skill「exam-explanation-pipeline」逐批產出 patch
#    → data/rex-edits-pipeline-2016-YYYY-MM-DD.json（不設 checked，留待覆核）

# 3) 覆核：合併 → 網頁 editor 確認 → 設 checked → commit
python scripts/merge_edits.py data/rex-edits-pipeline-2016-*.json

# 來源辨識閘可獨立自測
python scripts/verify_reference.py --selftest
```

## Obsidian SR Vault（vault/）

把交換考題整理成獨立的 Obsidian Spaced-Repetition vault（與網站分離），以卡片翻牌複習、以
concept 筆記組織知識。資料源為 `data/{year}.json`，單一真實來源仍是 JSON、vault 由其產生。

```bash
# 由 data/2016.json 產生 vault（一題一檔 SR 卡片 + 概念筆記 + SR 外掛設定）
python scripts/json_to_vault.py 2016
# 補詳解後重生（保留既有 SR 排程 <!--SR:--> 行）
python scripts/json_to_vault.py 2016 --force
```

- **題目卡片** `vault/questions/{year}/{id}.md`：YAML frontmatter + `#交換 #{year}交換 #{科}` tag +
  題幹選項 + `??` + 答案與逐選項詳解 + `[[concept-id]]` 概念連結。
- **概念筆記** `vault/concepts/{id}.md`：概念說明（取自 `data/concepts.json`）+ Dataview 動態匯整相關題。
- **詳解不足**的題（逐選項未通過）背面會標 `> [!todo] 待補詳解`，交給 `exam-explanation-pipeline`
  skill 補後，更新回 JSON 再 `--force` 重生。
- **冪等**：預設不覆寫既有檔（保護編輯與 SR 排程）；`--force` 覆寫時保留 `<!--SR:` 排程行。

> **前提**：首次用 Obsidian 開 `vault/` 後，需手動啟用社群外掛 **Spaced Repetition**（flashcard tag
> 已設為 `#交換`）與 **Dataview**。腳本只寫設定、不安裝外掛。

## 技術架構

- 純 HTML / JavaScript / CSS（無框架）
- 靜態網站，部署於 GitHub Pages
- 資料以 JSON 格式儲存
- PDF 解析使用 Python + PyMuPDF

## 專案結構

```
radiology-exam-review/
├── index.html              # SPA 入口
├── css/main.css            # 樣式
├── js/                     # JavaScript 模組
│   ├── app.js              # 路由
│   ├── data-loader.js      # 資料載入
│   ├── question-store.js   # 題目篩選
│   ├── card-mode.js        # 卡片模式
│   ├── list-mode.js        # 列表模式
│   ├── exam-mode.js        # 模擬考
│   ├── concept-cards.js    # 概念卡片
│   └── editor.js           # 編輯介面
├── data/
│   ├── index.json          # 年份索引
│   ├── 2016.json           # 2016 考題
│   ├── concepts.json       # 概念資料
│   └── images/2016/        # 考題圖片
└── scripts/
    ├── parse_2016.py                      # 早期 PDF 解析
    ├── import_obsidian_sr.py              # 從 Obsidian SR 匯入題目
    ├── sheets_to_json.py / json_to_sheets.py  # Google Sheets 雙向同步
    ├── merge_edits.py                     # 合併 rex-edits patch
    ├── extract_official_explanations.py   # 詳解流水線：抽官方詳解+對齊
    ├── audit_questions.py                 # 詳解流水線：5 項品質稽核
    └── verify_reference.py                # 詳解流水線：放射來源辨識閘
```
