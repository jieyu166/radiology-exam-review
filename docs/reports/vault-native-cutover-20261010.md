# Vault-native 複習網站遷移驗收（cutover report）

- 日期：2026-10-10
- Change：`vault-native-review-site`（任務 4.4）
- 驗收指令：`python scripts/accept_vault_native_migration.py`
- 機器可讀報告：`tmp/vault-native-migration-acceptance.json`（schema `vault-native-migration-acceptance/v1`，tmp/ 不進 git；重跑指令即可重建）
- 驗收基準 commit：`5289557`
- 結論：**通過，無 blocker**

## 1. 真實 vault 盤點與發佈完整性

| 項目 | 結果 |
|---|---|
| 掃描 note 數 | 4127 |
| eligible | 4126 |
| excluded（underscore / `publish: false`） | 1 |
| published | 4126 |
| manifest entries | 4126 |
| inventory 完整（eligible ＝ manifest/raw/record） | ✅ |
| manifest `sourceSha256` 與 raw 輸出一致 | ✅ |
| 雙次 build 樹狀 SHA-256 完全相同（determinism） | ✅ |
| hard error | 0 |
| warning（degraded rendering，已寫入 build report） | 6807，分佈於 3321 篇 |

## 2. 失敗部署保留（failed-deploy retention）

以含無效 SR 題目的 fixture vault 做 strict build：

- 產生 3 個 hard error，build 中止。
- 既有 `dist/` 內容（模擬前一次 Pages artifact）未被覆寫。
- 未產生新的 `manifest.json`，但 `build-report.json` 仍寫出。

結果：✅

## 3. 答案狀態標註（4.5 後續）

| 項目 | 結果 |
|---|---|
| `reviewStatus: needs_review` 篇數 | 49（符合預期） |
| `answerStatus: unresolved` 篇數 | 19，皆為 `answerMode: none`、`acceptedAnswers: []` |
| 2017-010 多重答案 | `confirmed` / `any` / `[B, D]` ✅ |
| 錯誤隊列缺標註 | 0 |

## 4. Cutover 邊界稽核（`audit_vault_native_cutover.py`）

- 來源完整性：clean（驗收過程未改寫任何 vault note）。
- 正式路徑（index.html 載入的 JS）無任何 legacy `data/*.json` 引用。
- `deploy-pages.yml` 無 legacy 指令（build_concepts / vault_to_json / json_to_vault）。
- Legacy 匯入／還原工具仍存在於 repo（本 change 範圍內刻意保留；移除另開 change）。

## 5. 測試套件

| 套件 | 結果 |
|---|---|
| compiler fixture suite（`test_vault_site.py`） | ✅ |
| deployment workflow contract（`test_deploy_workflow.py`） | ✅ |
| legacy isolation（`test_legacy_isolation.py`） | ✅ |
| content store browser smoke | ✅ |
| note renderer browser smoke | ✅ |
| question view browser smoke | ✅ |
| study progress and legacy patch export | ✅ |

## 6. 正式環境

- GitHub Pages：`https://jieyu166.github.io/radiology-exam-review/`，build type ＝ workflow，狀態 built。
- `deploy-pages.yml` 最近三次執行（2026-09-25、2026-10-09 ×2）皆 success。
- Legacy Pages（直接服務 repo 根目錄 + `data/*.json`）已自 2026-09-08 commit `2089da9` 起由 Actions artifact 取代。

## 7. 殘留事項（本 change 不處理）

1. `data/` 下約 1000 個 legacy JSON 與 `build_concepts.py`、`json_to_vault.py`、`vault_to_json.py`、Sheets 互轉等工具仍在 repo；對網站已無作用。
2. `js/data-loader.js` 的 legacy fetch 函式與未載入的 `app.js`、`concept-cards.js`、`question-store.js`、`card-mode.js`、`list-mode.js`、`exam-mode.js`、`editor.js` 為死碼。
3. `openspec/specs/concept-lazy-loading`、`sheets-sync` 與 `scripts/README.md` 仍描述 JSON 流程。

以上由後續 change「移除 legacy data/ JSON 流程」處理。
