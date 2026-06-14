# Scripts

## 安裝依賴

```bash
pip install -r scripts/requirements.txt
```

依賴套件：`pymupdf`、`google-auth`、`google-auth-httplib2`、`google-api-python-client`。

---

## Google Sheets 同步

### 環境設定

1. 複製 `.env.example` 為 `.env`，填入實際值：
   ```
   SHEET_ID=<your-spreadsheet-id>
   GOOGLE_KEY_PATH=~/.config/radiology-sheets-key.json
   ```
2. 下載 Google service account JSON 金鑰至 `GOOGLE_KEY_PATH` 指定路徑。
3. 在 Google Sheet 上將服務帳戶 email 加為「編輯者」。

### json_to_sheets.py — 一次性初始匯出

將 `data/*.json` + `data/concepts.json` 全部寫入 Google Sheets（清空後重寫）。
**首次設定時執行一次，日後改用 `sheets_to_json.py` 同步。**

```bash
python scripts/json_to_sheets.py
```

執行後會建立 `questions`、`concepts`、`_metadata` 三個 sheet，並將 `question_id` 欄設為 warning-only Protected Range。

### sheets_to_json.py — 日常同步

從 Google Sheets 讀取題目，寫回 `data/*.json` 與 `data/concepts.json`。

```bash
# 預覽變更（不寫入）
python scripts/sheets_to_json.py --dry-run

# 實際同步
python scripts/sheets_to_json.py
```

同步完成後建議執行 `git diff data/` 確認變更，再 `git commit` 發布。

驗證失敗的列（例如答案不在 A-E 或 subspecialty 無效）會輸出至 stderr 並略過，原始 JSON 不受影響。

---

## Obsidian SR Import

Use `import_obsidian_sr.py` to scan the Radiology Obsidian vault for spaced-repetition exchange-question notes and export compatible JSON into this project.

The importer treats the vault as read-only. It records hashes before and after the run and exits with an error if any source Markdown file changes.

```bash
python scripts/import_obsidian_sr.py --dry-run --report tmp/obsidian-sr-import-report.json
python scripts/import_obsidian_sr.py --merge-mode keep
```

Useful options:

- `--vault <path>`: Obsidian vault root. Defaults to the sibling `0筆記/Radiology` vault.
- `--target <path>`: `radiology-exam-review` root. Defaults to this project.
- `--dry-run`: parse and print/report counts without writing `data/{year}.json` or `data/index.json`.
- `--merge-mode keep|replace|update`: default `keep`; controls behavior when an imported deterministic id already exists.
- `--report <path>`: write a JSON report with scanned files, imported/skipped counts, skip reasons, fallback specialty decisions, and written files.

Question blocks are detected from SR structure: `#YYYY交換`, a `??` separator, and an `Ans:` line. Multiple year tags are exported as `years`; the canonical `year` is the earliest year. `#NR考` overrides YAML subspecialty, otherwise valid YAML `subspecialty` is used. Missing or broad YAML values are exported as `Unknown` with `subspecialty_confidence: "auto"` and are listed in the report.
