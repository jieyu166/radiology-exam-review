# Scripts

所有腳本都以 `vault/` 的 Markdown 為唯一輸入；repo 內沒有任何 JSON 資料來源（legacy `data/` 已於 2026-10-10 退役）。
產出一律寫到 `tmp/`（已 gitignore）或 `dist/`（已 gitignore）。

## 安裝依賴

建置與測試只需要 Python 3.12 標準函式庫與 Node.js。PDF 詳解抽取工具另需系統指令 `pdftotext`（poppler）。

```bash
pip install -r scripts/requirements.txt   # 目前無必要第三方套件
```

---

## 發布流程（GitHub Actions 同一順序）

| 腳本 | 用途 |
|---|---|
| `audit_vault_native_cutover.py --vault vault --report tmp/cutover-audit.json` | 唯讀稽核：vault 來源雜湊不變、`index.html` 與 workflow 無 legacy 引用、`data/` 與退役腳本不存在（`legacyToolsAbsent`）。任一不符 exit 1。 |
| `build_vault_site.py --vault vault --output dist --report dist/build-report.json` | 以 `vault_site/compiler.py` 把 vault 編譯成 `dist/`（manifest、indexes、records、notes 原文、assets）。 |
| `validate_vault_site.py --vault vault --output dist --report tmp/build-report-validate.json` | 重新編譯並與 `dist/` 比對完整性與雜湊。 |
| `build_static_site.py --output dist` | 複製 `index.html`、`css/`、`js/` 進 `dist/`。 |
| `accept_vault_native_migration.py` | 遷移驗收總閘：真實 vault 盤點、雙次 build 確定性、失敗部署保留、全部測試；報告寫到 `tmp/vault-native-migration-acceptance.json`。 |

## 題目工具（讀 `vault/questions/**/*.md`）

共用解析模組 `vault_questions.py`：`iter_question_cards(vault_root)` 以 compiler 相同規則回傳每張題卡的 `id / year / subspecialty / correct_answer / concepts / reference / stem / options / explanation / path`。

| 腳本 | 用途 |
|---|---|
| `lint_concepts.py [--quiet]` | 專案慣例 linter：概念檔結構、題卡 `concepts` 是否存在、`correctAnswer` 是否合法。 |
| `audit_questions.py {year}` | 題目品質五項清單稽核，輸出 `tmp/audit-{year}.json`。 |
| `extract_official_explanations.py {year} [--pdf PATH]` | 以 `pdftotext` 抽官方詳解 PDF、切題並對齊題卡題幹，輸出 `tmp/official-{year}.json`。 |
| `extract_subscription_refs.py` | 彙整題卡 `reference` 與概念 footnote 中需訂閱／館藏的來源。 |
| `verify_reference.py --selftest` | 放射來源白名單閘（`passes_gate()`），供詳解流水線使用。 |
| `extract_pdf_questions.py {year}` | 從官方詳解 PDF 文字擷取結構化題目（回填新年份時用）。 |

詳解流水線（`/exam-explanation-pipeline` skill）直接編輯題卡的詳解段與 frontmatter `reference`，不再產生 patch。

## 概念工具（讀 `vault/concepts/*.md`）

| 腳本 | 用途 |
|---|---|
| `find_weak_concepts.py [-n N]` | 找出弱來源概念，供五來源補強。 |
| `find_shallow_concepts.py [-n N]` | 找出淺層概念，供深補。 |
| `audit_concept_imaging.py [--thr N]` | 稽核概念是否含一般放射科判讀影像知識；考題數依題卡 `concepts` 統計。 |
| `dedupe_concept_questions.py` | 移除概念檔中重抄的 `## 題目` 區。 |

## 圖片

圖片不進 git。`r2_upload.py` 與 `image_asset_manager.py --port 8765`（本機目錄工具）都透過 img-hosting CLI 上傳 Cloudflare 圖床，把回傳的 URL 貼進筆記。

## 測試

```bash
python scripts/test_vault_site.py          # compiler fixture
python scripts/test_vault_questions.py     # 題卡解析模組
python scripts/test_deploy_workflow.py     # workflow 契約
python scripts/test_legacy_isolation.py    # legacy 隔離與 cutover audit
node scripts/test_content_store.js
node scripts/test_note_renderer.js
node scripts/test_vault_question_view.js
node scripts/test_study_progress.js
```
