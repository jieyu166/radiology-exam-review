"""
一次性匯出腳本：將 data/*.json + data/concepts.json 寫入 Google Sheets。

用法：
  python scripts/json_to_sheets.py

環境變數（參考 .env.example）：
  SHEET_ID         Google Spreadsheet ID
  GOOGLE_KEY_PATH  service account 金鑰路徑（預設 ~/.config/radiology-sheets-key.json）
"""

import json
import sys
from pathlib import Path

# 載入環境變數（若 .env 存在）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
CONFLICTS_PATH = ROOT / "scripts" / "conflicts.json"
YEARS = list(range(2016, 2025))

from sheets_schema import (
    QUESTIONS_COLUMNS,
    CONCEPTS_COLUMNS,
    EXPLANATION_MAX_CHARS,
    get_sheets_service,
)


# ── 資料收集 ───────────────────────────────────────────────────────────────────

def load_questions() -> tuple[dict, list[str]]:
    """
    讀取所有年度 JSON，回傳 (questions_dict, conflict_ids)。

    questions_dict: { question_id -> row_dict }
    conflict_ids:   有內容衝突的 question_id 清單
    """
    raw: dict[str, list[dict]] = {}  # question_id -> [all versions]

    for year in YEARS:
        path = DATA_DIR / f"{year}.json"
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for q in data.get("questions", []):
            qid = q.get("id", "")
            if not qid:
                continue
            raw.setdefault(qid, []).append(q)

    # 先全面偵測重複（內容不同），若有則中止
    conflicts = []
    for qid, versions in raw.items():
        if len(versions) > 1:
            # 比較關鍵欄位：questionText、options、correctAnswer
            first = versions[0]
            for v in versions[1:]:
                if (v.get("questionText") != first.get("questionText") or
                        v.get("correctAnswer") != first.get("correctAnswer") or
                        v.get("options") != first.get("options")):
                    conflicts.append(qid)
                    break

    if conflicts:
        for qid in sorted(conflicts):
            print(f"DUPLICATE: {qid}", file=sys.stderr)
        print(
            f"\n{len(conflicts)} question(s) have conflicting content across year files.\n"
            "Fix conflicts before exporting. Aborting.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 合併（相同內容的跨年度重複：合併 years）
    merged: dict[str, dict] = {}
    for qid, versions in raw.items():
        base = versions[0].copy()
        all_years = set()
        for v in versions:
            all_years.update(v.get("years", [v.get("year", 0)]))
        base["_all_years"] = sorted(all_years)
        merged[qid] = base

    return merged, []


def build_question_row(q: dict) -> list:
    """q dict → QUESTIONS_COLUMNS 對應的值清單。"""
    options = {o["letter"]: o.get("text", "") for o in q.get("options", [])}
    all_years = q.get("_all_years", [q.get("year", "")])
    primary_year = int(q.get("id", "0-").split("-")[0]) if "-" in q.get("id", "") else q.get("year", "")

    explanation = q.get("explanation", "") or ""
    if len(explanation) > EXPLANATION_MAX_CHARS:
        print(f"WARNING: {q['id']} explanation truncated ({len(explanation)} chars)", file=sys.stderr)
        explanation = explanation[:EXPLANATION_MAX_CHARS] + "[TRUNCATED]"

    return [
        q.get("id", ""),
        primary_year,
        q.get("number", ""),
        ",".join(str(y) for y in all_years),
        q.get("subspecialty", "Unknown"),
        q.get("questionText", ""),
        options.get("A", ""),
        options.get("B", ""),
        options.get("C", ""),
        options.get("D", ""),
        options.get("E", ""),
        q.get("correctAnswer", ""),
        q.get("reference", ""),
        q.get("reference_source", ""),
        explanation,
        ",".join(q.get("concepts", [])),
        "TRUE" if q.get("checked") else "FALSE",
    ]


def _to_str(v) -> str:
    """將可能是 list 的欄位轉成換行分隔字串。"""
    if isinstance(v, list):
        return "\n".join(str(i) for i in v)
    return v or ""


def load_concepts() -> list[list]:
    """讀取 concepts.json，回傳 CONCEPTS_COLUMNS 對應的 rows。"""
    path = DATA_DIR / "concepts.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    concepts = data.get("concepts", {})
    rows = []
    for cid, c in concepts.items():
        rows.append([
            cid,
            c.get("name", ""),
            c.get("nameZh", ""),
            c.get("subspecialty", ""),
            _to_str(c.get("definition", "")),
            _to_str(c.get("imagingFindings", "")),
            _to_str(c.get("differentialDiagnosis", "")),
            _to_str(c.get("externalLinks", "")),
            _to_str(c.get("keyPoints", "")),
            _to_str(c.get("management", "")),
            "TRUE" if c.get("checked") else "FALSE",
        ])
    return rows


# ── Google Sheets 操作 ─────────────────────────────────────────────────────────

def ensure_sheets(service, spreadsheet_id: str, sheet_names: list[str]) -> dict[str, int]:
    """確保試算表中存在指定的 sheets，回傳 {name: sheetId}。"""
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    existing = {s["properties"]["title"]: s["properties"]["sheetId"]
                for s in meta.get("sheets", [])}

    requests = []
    for name in sheet_names:
        if name not in existing:
            requests.append({"addSheet": {"properties": {"title": name}}})

    if requests:
        resp = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests},
        ).execute()
        for reply in resp.get("replies", []):
            props = reply.get("addSheet", {}).get("properties", {})
            if props:
                existing[props["title"]] = props["sheetId"]

    return existing


def clear_and_write(service, spreadsheet_id: str, sheet_name: str, rows: list[list]):
    """清空指定 sheet 並寫入 rows（含 header）。"""
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1:ZZ",
    ).execute()
    if rows:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="RAW",
            body={"values": rows},
        ).execute()


def add_question_id_protection(service, spreadsheet_id: str, questions_sheet_id: int):
    """將 questions sheet 的 A 欄（question_id）設為 warning-only protected range。"""
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{
            "addProtectedRange": {
                "protectedRange": {
                    "range": {
                        "sheetId": questions_sheet_id,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1,
                    },
                    "description": "question_id — do not edit manually",
                    "warningOnly": True,
                }
            }
        }]},
    ).execute()


# ── 主流程 ─────────────────────────────────────────────────────────────────────

def main():
    print("Loading questions from JSON files...")
    questions, _ = load_questions()
    print(f"  {len(questions)} unique questions loaded")

    concept_rows = load_concepts()
    print(f"  {len(concept_rows)} concepts loaded")

    service, sheet_id = get_sheets_service()
    print(f"Connected to spreadsheet: {sheet_id}")

    sheet_names = ["questions", "concepts", "_metadata"]
    sheet_ids = ensure_sheets(service, sheet_id, sheet_names)

    # questions sheet
    print("Writing questions sheet...")
    q_rows = [QUESTIONS_COLUMNS] + [build_question_row(q) for q in questions.values()]
    clear_and_write(service, sheet_id, "questions", q_rows)
    print(f"  {len(q_rows) - 1} rows written")

    # concepts sheet
    print("Writing concepts sheet...")
    c_rows = [CONCEPTS_COLUMNS] + concept_rows
    clear_and_write(service, sheet_id, "concepts", c_rows)
    print(f"  {len(c_rows) - 1} rows written")

    # _metadata sheet
    import datetime
    meta_rows = [
        ["key", "value"],
        ["exported_at", datetime.datetime.utcnow().isoformat() + "Z"],
        ["question_count", len(questions)],
        ["concept_count", len(concept_rows)],
    ]
    clear_and_write(service, sheet_id, "_metadata", meta_rows)

    # question_id protected range
    print("Setting question_id column as protected range...")
    add_question_id_protection(service, sheet_id, sheet_ids["questions"])

    print("\nDone. Open your spreadsheet to verify:")
    print(f"  https://docs.google.com/spreadsheets/d/{sheet_id}/edit")


if __name__ == "__main__":
    main()
