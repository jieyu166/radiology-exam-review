"""
日常同步腳本：從 Google Sheets 讀取題目並寫回 data/*.json。

用法：
  python scripts/sheets_to_json.py [--dry-run]

環境變數（參考 .env.example）：
  SHEET_ID         Google Spreadsheet ID
  GOOGLE_KEY_PATH  service account 金鑰路徑（預設 ~/.config/radiology-sheets-key.json）

選項：
  --dry-run  只印出 diff 報告，不寫入任何檔案
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"

from sheets_schema import (
    QUESTIONS_COLUMNS,
    CONCEPTS_COLUMNS,
    validate_question_row,
    get_sheets_service,
)

YEARS = list(range(2016, 2025))


# ── 讀取 Sheets ────────────────────────────────────────────────────────────────

def read_sheet(service, spreadsheet_id: str, sheet_name: str) -> list[list[str]]:
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1:ZZ",
    ).execute()
    return result.get("values", [])


def rows_to_dicts(rows: list[list[str]], columns: list[str]) -> list[dict]:
    """將 sheet rows（含 header）轉換為 dict 清單。"""
    if not rows:
        return []
    header = rows[0]
    result = []
    for row in rows[1:]:
        # 補齊短列
        padded = row + [""] * (len(header) - len(row))
        result.append(dict(zip(header, padded)))
    return result


# ── 題目轉換 ───────────────────────────────────────────────────────────────────

def parse_years(years_str: str) -> list[int]:
    """解析逗號分隔年份字串，回傳整數清單。"""
    result = []
    for part in years_str.split(","):
        part = part.strip()
        if part.isdigit():
            result.append(int(part))
    return result


def row_to_question(row: dict) -> dict:
    """將 sheet row dict 轉換為 JSON 題目格式。"""
    options = []
    for letter in ("A", "B", "C", "D", "E"):
        text = row.get(f"option_{letter}", "").strip()
        if text:
            options.append({"letter": letter, "text": text})

    concepts_str = row.get("concepts", "").strip()
    concepts = [c.strip() for c in concepts_str.split(",") if c.strip()] if concepts_str else []

    years_str = row.get("years", "").strip()
    years = parse_years(years_str) if years_str else []

    qid = row.get("question_id", "")
    primary_year_str = row.get("primary_year", "")
    try:
        primary_year = int(primary_year_str)
    except (ValueError, TypeError):
        primary_year = int(qid.split("-")[0]) if "-" in qid else 0

    number_str = row.get("number", "")
    try:
        number = int(number_str)
    except (ValueError, TypeError):
        number = 0

    return {
        "id": qid,
        "year": primary_year,
        "number": number,
        "years": years,
        "subspecialty": row.get("subspecialty", "Unknown"),
        "questionText": row.get("question_text", ""),
        "options": options,
        "correctAnswer": row.get("correct_answer", ""),
        "reference": row.get("reference", ""),
        "reference_source": row.get("reference_source", ""),
        "explanation": row.get("explanation", ""),
        "concepts": concepts,
        "checked": row.get("checked", "").upper() == "TRUE",
    }


# ── 建置年度 dict ──────────────────────────────────────────────────────────────

def build_year_data(questions: list[dict]) -> dict[int, list[dict]]:
    """將題目清單依 years 欄展開，每個年度一份清單。"""
    year_map: dict[int, list[dict]] = {y: [] for y in YEARS}
    for q in questions:
        for y in q.get("years", [q.get("year", 0)]):
            if y in year_map:
                year_map[y].append(q)
    for y in year_map:
        year_map[y].sort(key=lambda q: q.get("number", 0))
    return year_map


# ── 原子寫入 ───────────────────────────────────────────────────────────────────

def atomic_write_json(path: Path, data: dict):
    """將 data 寫入 path，先寫 .tmp 再 rename（原子操作）。"""
    tmp = path.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(path)
    except Exception as exc:
        if tmp.exists():
            tmp.unlink()
        raise RuntimeError(f"Failed to write {path}: {exc}") from exc


# ── Diff 報告 ──────────────────────────────────────────────────────────────────

def diff_summary(path: Path, new_content: str) -> str:
    """與 HEAD 版本比較，回傳 +N/-N 摘要字串。"""
    rel = path.relative_to(ROOT).as_posix()
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(ROOT),
        )
        if result.returncode != 0:
            return "(new file)"
        old_lines = set(result.stdout.splitlines())
        new_lines = set(new_content.splitlines())
        added = len(new_lines - old_lines)
        removed = len(old_lines - new_lines)
        if added == 0 and removed == 0:
            return "(no change)"
        return f"+{added}/-{removed} lines"
    except Exception:
        return "(diff unavailable)"


# ── 主流程 ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sync Google Sheets → data/*.json")
    parser.add_argument("--dry-run", action="store_true", help="只印 diff，不寫入檔案")
    args = parser.parse_args()

    service, sheet_id = get_sheets_service()
    print(f"Connected to spreadsheet: {sheet_id}")

    # 讀取 questions sheet
    print("Reading questions sheet...")
    q_rows = read_sheet(service, sheet_id, "questions")
    q_dicts = rows_to_dicts(q_rows, QUESTIONS_COLUMNS)
    print(f"  {len(q_dicts)} rows read")

    # 驗證並過濾
    valid_questions = []
    skip_count = 0
    for row in q_dicts:
        qid = row.get("question_id", "(no id)")
        errors = validate_question_row(row)
        if errors:
            for e in errors:
                print(f"SKIP: {qid} — {e}", file=sys.stderr)
            skip_count += 1
            continue
        valid_questions.append(row_to_question(row))

    if skip_count:
        print(f"  {skip_count} row(s) skipped due to validation errors", file=sys.stderr)
    print(f"  {len(valid_questions)} valid questions")

    # 讀取 concepts sheet
    print("Reading concepts sheet...")
    c_rows = read_sheet(service, sheet_id, "concepts")
    c_dicts = rows_to_dicts(c_rows, CONCEPTS_COLUMNS)
    print(f"  {len(c_dicts)} concepts read")

    # 展開年度
    year_data = build_year_data(valid_questions)

    # 寫入年度 JSON
    errors_writing = []
    for year in YEARS:
        questions_for_year = year_data[year]
        if not questions_for_year:
            continue

        path = DATA_DIR / f"{year}.json"
        output = {"year": year, "questions": questions_for_year}
        content = json.dumps(output, ensure_ascii=False, indent=2)
        summary = diff_summary(path, content)
        print(f"  {year}.json  {len(questions_for_year)} questions  {summary}")

        if not args.dry_run:
            try:
                atomic_write_json(path, output)
            except RuntimeError as exc:
                print(str(exc), file=sys.stderr)
                errors_writing.append(year)

    # 寫入 concepts.json
    concepts_dict: dict[str, dict] = {}
    for c in c_dicts:
        cid = c.get("concept_id", "")
        if not cid:
            continue
        concepts_dict[cid] = {
            "name": c.get("name", ""),
            "nameZh": c.get("name_zh", ""),
            "subspecialty": c.get("subspecialty", ""),
            "definition": c.get("definition", ""),
            "imagingFindings": c.get("imaging_findings", ""),
            "differentialDiagnosis": c.get("differential_diagnosis", ""),
            "externalLinks": c.get("external_links", ""),
            "keyPoints": c.get("key_points", ""),
            "management": c.get("management", ""),
            "checked": c.get("checked", "").upper() == "TRUE",
        }

    concepts_path = DATA_DIR / "concepts.json"
    concepts_output = {"concepts": concepts_dict}
    concepts_content = json.dumps(concepts_output, ensure_ascii=False, indent=2)
    concepts_summary = diff_summary(concepts_path, concepts_content)
    print(f"  concepts.json  {len(concepts_dict)} concepts  {concepts_summary}")

    if not args.dry_run:
        try:
            atomic_write_json(concepts_path, concepts_output)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            errors_writing.append("concepts")

    if errors_writing:
        print(f"\nFailed to write: {errors_writing}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("\nDry run complete. No files written.")
    else:
        print(f"\nDone. Run `git diff data/` to review changes.")


if __name__ == "__main__":
    main()
