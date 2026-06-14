"""
Google Sheets 欄位定義、schema 驗證、service account 認證。
"""
import os
import sys
from pathlib import Path

# ── questions sheet 欄位（有序，對應 Sheet 的欄位順序）──────────────────────────
QUESTIONS_COLUMNS = [
    "question_id",
    "primary_year",
    "number",
    "years",
    "subspecialty",
    "question_text",
    "option_A",
    "option_B",
    "option_C",
    "option_D",
    "option_E",
    "correct_answer",
    "reference",
    "reference_source",
    "explanation",
    "concepts",
    "checked",
]

# reference_source 允許值（詳解流水線標註來源層級；空字串代表未標）。
VALID_REFERENCE_SOURCES = {
    "official_pdf", "vault_note", "journal", "textbook", "online", "llm_suggested", "",
}

# ── concepts sheet 欄位 ─────────────────────────────────────────────────────────
CONCEPTS_COLUMNS = [
    "concept_id",
    "name",
    "name_zh",
    "subspecialty",
    "definition",
    "imaging_findings",
    "differential_diagnosis",
    "external_links",
    "key_points",
    "management",
    "checked",
]

# ── 允許的 subspecialty 值 ─────────────────────────────────────────────────────
VALID_SUBSPECIALTIES = {
    "ABD", "CV", "CH", "Breast", "H&N", "MSK",
    "NR", "PED", "US", "IR", "Physics", "Unknown",
}

VALID_CORRECT_ANSWERS = {"A", "B", "C", "D", "E"}

EXPLANATION_MAX_CHARS = 49_000


def validate_question_row(row: dict) -> list[str]:
    """
    驗證 question row dict。回傳錯誤字串清單，無錯誤則回傳空清單。
    row 的 key 對應 QUESTIONS_COLUMNS。
    """
    errors = []

    correct = row.get("correct_answer", "")
    if correct not in VALID_CORRECT_ANSWERS:
        errors.append(f"invalid correct_answer: {correct!r}")

    subspecialty = row.get("subspecialty", "")
    if subspecialty not in VALID_SUBSPECIALTIES:
        errors.append(f"invalid subspecialty: {subspecialty!r}")

    if not str(row.get("question_text", "")).strip():
        errors.append("question_text is empty")

    for opt in ("option_A", "option_B", "option_C"):
        if not str(row.get(opt, "")).strip():
            errors.append(f"{opt} is empty")

    return errors


def get_sheets_service():
    """
    建立並回傳 (service, sheet_id) tuple。

    讀取環境變數：
      SHEET_ID         — 必填
      GOOGLE_KEY_PATH  — 選填，預設 ~/.config/radiology-sheets-key.json

    任一前置條件不符則輸出錯誤至 stderr 並 sys.exit(1)。
    """
    sheet_id = os.environ.get("SHEET_ID", "").strip()
    if not sheet_id:
        print("Error: SHEET_ID environment variable not set", file=sys.stderr)
        sys.exit(1)

    default_key = Path.home() / ".config" / "radiology-sheets-key.json"
    key_path = Path(os.environ.get("GOOGLE_KEY_PATH", str(default_key))).expanduser()

    if not key_path.exists():
        print(f"Error: Google key file not found: {key_path}", file=sys.stderr)
        sys.exit(1)

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_file(
            str(key_path),
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
    except Exception as exc:
        print(f"Error: failed to build Sheets service: {exc}", file=sys.stderr)
        sys.exit(1)

    return service, sheet_id
