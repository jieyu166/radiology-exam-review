# 放射科交換考題複習

放射科住院醫師交換考題線上複習系統，支援卡片翻牌、列表瀏覽、模擬考試與概念筆記。

**`vault/` 的 Markdown 是題目與概念內容的權威來源。** 醫師與 AI 在 Obsidian 或文字編輯器修改筆記，覆核後由編譯器產生網站發布套件；JSON 僅作為產生的索引與結構化輔助資料，不是日常編輯或回寫來源。

## 功能特色

- **卡片與列表**：逐題複習、顯示答案詳解，依年份、次專科、已覆核狀態等條件篩選
- **模擬考**：抽題、倒數計時、評分與考試紀錄
- **概念筆記**：閱讀 Markdown 內容，透過 wikilink 與題目、概念互相連結
- **來源追溯**：發布資料保留來源路徑與 SHA256，方便比對內容版本
- **學習進度**：瀏覽器本機保存星號、作答與考試紀錄，可匯出／匯入備份
- **響應式設計**：支援手機、平板與桌面

網站是內容閱讀端；題目與概念請回到 vault 編輯。`checked` 表示覆核狀態，使用者可開啟「已確認」篩選；它不是自動阻擋發布的開關。

## 使用與本機預覽

線上網站：[GitHub Pages](https://jieyu166.github.io/radiology-exam-review/)。

需求：Git、Python 3.12（與 CI 相同），以及執行 JavaScript 測試所需的 Node.js。新版網站編譯器使用 Python 標準函式庫，前端為純 HTML／JavaScript／CSS，無 npm 安裝步驟。Obsidian 為選用的筆記編輯工具。

取得專案後，於專案根目錄依序執行；每一步須成功才繼續下一步：

```powershell
python scripts/audit_vault_native_cutover.py --vault vault --report tmp/cutover-audit.json
python scripts/build_vault_site.py --vault vault --output dist --report dist/build-report.json
python scripts/validate_vault_site.py --vault vault --output dist --report tmp/build-report-validate.json
python scripts/build_static_site.py --output dist
python -m http.server 8080 --directory dist
```

開啟 `http://127.0.0.1:8080`。`dist/` 是可重新產生的發布套件，不要直接修改其中的筆記或 JSON。若建置／驗證失敗，先查看報告的來源檔、錯誤代碼與訊息，修正 vault 後重新建置。

## 醫師與 AI 編輯流程

1. 用 Obsidian 開啟專案內的 `vault/`，或直接使用文字編輯器。
2. 題目編輯 `vault/questions/{year}/{id}.md`；概念編輯 `vault/concepts/{slug}.md`。保留既有 frontmatter、題目的 `??` 正反面分隔、選項與答案格式，以及引用來源。題目的參考書目寫在 frontmatter `reference`（純字串），網站揭曉答案後會顯示。
3. 使用 `[[concepts/slug]]`、`[[questions/year/id]]` 等 wikilink 連結待覆核筆記。AI 補充的醫學內容與 Summary 圖仍須醫師覆核；確認後再更新適當的覆核欄位。
4. 不應發布的題目／概念在 frontmatter 明確設定 `publish: false`。編譯器也排除檔名以 `_` 開頭的筆記。其餘位於 questions／concepts 的筆記會進入發布範圍，即使 `checked: false` 亦然。
5. 執行上述建置與驗證，完成下列測試，再用本機網站檢視內容與圖片。
6. 檢查 Git 差異，只提交已確認的來源筆記與必要程式變更。推送至 `main` 後由 GitHub Actions 建置及部署。

本機 Summary 圖稿與圖片覆核另行管理，並非此網站的公開管理功能。編譯器只掃描 `vault/questions/` 與 `vault/concepts/`，不會自動發布 `vault/summary-graphics/` 的草稿；將已核准圖片正式引用到發布筆記前，仍須確認圖文與圖片來源。

### Obsidian 複習

題目沿用 Spaced Repetition 的 `??` 卡片格式及 `#交換` 標籤；概念可含 Dataview 查詢。首次開啟 vault 時，如需這些功能，請自行安裝並啟用 **Spaced Repetition** 與 **Dataview** 社群外掛。網站不執行這些 Obsidian 外掛。

## 測試與發布

與目前 Pages workflow 相同的測試命令：

```powershell
python scripts/test_vault_site.py
node scripts/test_content_store.js
node scripts/test_note_renderer.js
node scripts/test_vault_question_view.js
node scripts/test_study_progress.js
```

[`deploy-pages.yml`](.github/workflows/deploy-pages.yml) 的流程為：

```text
vault Markdown
  → audit_vault_native_cutover
  → build_vault_site
  → validate_vault_site
  → build_static_site
  → Python / JavaScript 測試
  → 上傳 dist Pages artifact
  → GitHub Pages 部署
```

GitHub repository 的 **Settings → Pages → Source** 應使用 **GitHub Actions**。Workflow 在 `main` 的 vault、網站程式或建置相關路徑變更時觸發，也可於 Actions 手動執行；只修改 README 不會自動觸發。建置／驗證／測試失敗時不進入部署，報告另存為 Actions artifact。

## 帳號與跨裝置同步

網站可不登入使用（學習紀錄只在本機）。登入後，作答事件（題號、選項、對錯、耗時、信心、來源版本）會以離線優先的方式上傳到 Cloudflare Worker `rex-api`（`worker/`，D1 資料庫），換裝置登入即取回。

- 帳號為邀請制：管理者在設定面板簽發一次性邀請碼；第一位管理者以 `BOOTSTRAP_INVITE_CODE` 註冊。
- 登入用帳號密碼，session 為 Bearer token（30 天），不使用 cookie。
- 題卡可標記官方答案有誤：frontmatter `answerStatus: corrected` 加 `officialAnswer`，以 `correctAnswer` 為覆核答案計分。
- 後端架構、API 契約、本機開發與正式部署步驟見 [`docs/account-sync.md`](docs/account-sync.md)。

## 資料來源與覆核限制

- 交換考題 PDF（2016–2024）；實際發布題數以本次 `dist/build-report.json` 為準。
- 官方詳解 PDF 為詳解的事實基礎，概念筆記與放射科文章提供補充來源。
- 編譯與測試通過只證明格式、連結與程式行為檢查通過，不代表醫學內容已獲核准。
- 學習紀錄存在目前瀏覽器，沒有跨裝置帳號同步；換裝置前請先匯出。
- 網站僅支援其 Markdown renderer 實作的語法，不等同完整 Obsidian 執行環境；外部圖片仍依賴其網址可用。

## 技術架構與專案結構

編譯器保存 Markdown 內容，另外產生 manifest、索引、來源位置與題目結構資料；前端由 ContentStore 讀取發布套件，再由筆記 renderer 與題目 view 顯示。舊 JSON 資料與瀏覽器內容 patch 不會成為新版內容來源。

```text
radiology-exam-review/
├── vault/
│   ├── questions/{year}/{id}.md   # 題目權威來源
│   └── concepts/{slug}.md        # 概念權威來源
├── index.html                   # 新版網站入口
├── css/main.css
├── js/
│   ├── content-store.js         # 發布套件讀取
│   ├── note-renderer.js         # Markdown / wikilink 顯示
│   ├── vault-question-view.js   # 題目與答案顯示
│   ├── vault-app.js             # 路由、篩選與複習模式
│   └── data-loader.js           # 學習進度、舊 patch 匯出相容功能
├── scripts/
│   ├── vault_site/              # Markdown 編譯器
│   ├── audit_vault_native_cutover.py
│   ├── build_vault_site.py
│   ├── validate_vault_site.py
│   ├── build_static_site.py
│   └── test_*                   # Python / JavaScript 測試
├── .github/workflows/deploy-pages.yml
└── dist/                        # 產生的發布套件（不進 git）
```

## 已退役：legacy JSON 資料流

2026-10-10 起 `data/` 目錄（`20xx.json`、`concepts/*.json`、`rex-edits` patch）與其讀寫工具（Google Sheets 同步、`json_to_vault.py`／`vault_to_json.py`、`merge_edits.py`、`build_concepts.py`、NR Summary 稽核鏈）已全部自 repo 移除；題目 `reference` 已遷入題卡 frontmatter，題圖改放 Cloudflare 圖床。vault Markdown 是唯一來源，任何內容修正直接改 `vault/` 下的 `.md`，push `main` 後由 Actions 重新編譯部署。

`scripts/audit_vault_native_cutover.py` 會在 CI 檢查 `data/` 與退役腳本不得重新出現。歷史資料可在 commit `342a349`（封存 Phase 2B 成果）之前的版本取得。題目層級的輔助工具（`audit_questions.py`、`extract_official_explanations.py`、`lint_concepts.py` 等）現在一律讀 vault 題卡，用法見 [`scripts/README.md`](scripts/README.md)。
