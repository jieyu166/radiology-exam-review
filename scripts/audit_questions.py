#!/usr/bin/env python3
"""題目品質稽核器（移植 lit-review 的 PRISMA 清單稽核，改為放射考題 5 項清單）。

對 vault/questions/{year}/ 的每張題卡跑品質清單，輸出 tmp/audit-{year}.json 報告：哪些題缺哪項。
題卡由 scripts/vault_questions.py 讀取（重用 vault_site compiler 解析）。
可離線重複執行，量化「機器先審」前後的品質提升，亦供 skill 決定要修補哪些題。

品質清單（每項 True/False/None）：
  1. answer          — 有合法 correctAnswer (A–E)
  2. per_option_expl — explanation 逐選項解釋（偵測 (A)/(B) 或行首 A:/A. 樣式）
  3. subspecialty    — 已分類（非 Unknown / 空）
  4. reference       — 非空且通過放射來源辨識閘（verify_reference）
  5. image           — 圖片已連結（題卡 body 偵測到 ![](...) 或帶圖片副檔名的 ![[...]] 嵌入）；
                       無法離線判定是否需圖時記為 None(NA)，不扣分

audit_score = 通過項數；applicable = 非 NA 項數。score < applicable 即列入缺項。

用法：
  python scripts/audit_questions.py 2016
  python scripts/audit_questions.py 2016 2017 2018
  python scripts/audit_questions.py --all
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# 同目錄匯入來源辨識閘與題卡讀取器
sys.path.insert(0, str(Path(__file__).parent))
import verify_reference  # noqa: E402
from vault_questions import QuestionCard, iter_question_cards  # noqa: E402

VAULT_DIR = Path(__file__).parent.parent / "vault"
TMP_DIR = Path(__file__).parent.parent / "tmp"

VALID_ANSWERS = {"A", "B", "C", "D", "E"}

# explanation 逐選項樣式：含 (A)/（A）… 或 多行行首（可帶 - * 項目符號/粗體）A:/A./A、/A（ 等
_PER_OPTION_PAREN = re.compile(r"[(（][A-E][)）]")
_PER_OPTION_LINE = re.compile(r"(?m)^\s*[-*]?\s*\*{0,2}[A-E]\*{0,2}[\s:：.\)）、（(]")


def _has_per_option(explanation: str) -> bool:
    """explanation 是否逐選項解釋（至少出現 2 個選項標記）。"""
    if not explanation:
        return False
    paren = len(_PER_OPTION_PAREN.findall(explanation))
    line = len(_PER_OPTION_LINE.findall(explanation))
    return paren >= 2 or line >= 2


_IMG_MD = re.compile(r"!\[[^\]]*\]\([^)]+\)")
_IMG_EMBED = re.compile(r"!\[\[[^\]|]+\.(?:png|jpg|jpeg|gif|webp|svg)(?:\|[^\]]*)?\]\]", re.IGNORECASE)


def count_image_embeds(text: str) -> int:
    """題卡 body 中的圖片嵌入數：markdown 圖 ![](...) 與帶圖片副檔名的 Obsidian ![[...]]。

    ![[concept-slug]]（概念轉錄）不算圖片。
    """
    if not text:
        return 0
    return len(_IMG_MD.findall(text)) + len(_IMG_EMBED.findall(text))


def audit_question(card: QuestionCard) -> dict:
    """回傳單張題卡稽核結果 dict（含各項布林、score、applicable、missing）。"""
    checks: dict[str, bool | None] = {}

    # 1. answer（多重答案為逗號串接，逐字母皆須 A–E）
    letters = [x for x in card.correct_answer.split(",") if x]
    checks["answer"] = bool(letters) and all(x in VALID_ANSWERS for x in letters)

    # 2. per_option_expl
    checks["per_option_expl"] = _has_per_option(card.explanation)

    # 3. subspecialty
    sub = (card.subspecialty or "").strip()
    checks["subspecialty"] = bool(sub) and sub != "Unknown"

    # 4. reference
    checks["reference"] = verify_reference.passes_gate(card.reference)

    # 5. image（NA：無法離線判定是否需圖）；images = 題卡 body 偵測到的圖片嵌入數
    body = "\n".join([card.stem, *card.options.values(), card.explanation])
    checks["image"] = True if count_image_embeds(body) else None  # None = NA，待 skill 用官方 PDF 判定

    applicable = [k for k, v in checks.items() if v is not None]
    passed = [k for k in applicable if checks[k]]
    missing = [k for k in applicable if not checks[k]]

    return {
        "id": card.id,
        "subspecialty": card.subspecialty,
        "checks": checks,
        "audit_score": len(passed),
        "applicable": len(applicable),
        "missing": missing,
        "needs_image_review": checks["image"] is None,
    }


def _load_official_coverage(year: str) -> dict[str, bool]:
    """讀 tmp/official-{year}.json（若有），回傳 {qid: 是否有可用官方逐選項詳解}。

    用於把題目分成 Phase A（有官方詳解→重構）與 Phase B（無→最後再生成）。
    """
    path = TMP_DIR / f"official-{year}.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    coverage = {}
    for m in data.get("matches", []):
        qid = m.get("qid")
        if not qid:
            continue
        # 有對齊且 raw 含逐選項詳解文字才算「有官方詳解可重構」（Phase A）。
        # 僅有題幹+選項+引用、無詳解文字者歸 Phase B（最後再生成）。
        coverage[qid] = bool(m.get("similarity") is not None and m.get("has_explanation"))
    return coverage


def _cards_by_year() -> dict[str, list[QuestionCard]]:
    """讀整個 vault 一次，依題卡所在資料夾（vault/questions/{year}/）分組。"""
    grouped: dict[str, list[QuestionCard]] = {}
    for card in iter_question_cards(VAULT_DIR):
        grouped.setdefault(card.path.parent.name, []).append(card)
    return grouped


def audit_year(year: str, cards: list[QuestionCard] | None = None) -> dict:
    """稽核單一年份，回傳彙總 dict 並寫出 tmp/audit-{year}.json。"""
    if cards is None:
        cards = _cards_by_year().get(year, [])
    if not cards:
        print(f"  Warning: {VAULT_DIR / 'questions' / year} 無題卡，跳過")
        return {}

    coverage = _load_official_coverage(year)
    results = []
    for card in cards:
        r = audit_question(card)
        r["has_official"] = coverage.get(card.id, None)  # None=未跑抽取
        results.append(r)

    n = len(results)
    perfect = sum(1 for r in results if r["audit_score"] == r["applicable"])
    by_check = {c: sum(1 for r in results if r["checks"].get(c) is True)
                for c in ("answer", "per_option_expl", "subspecialty", "reference", "image")}
    needs_image = sum(1 for r in results if r["needs_image_review"])

    # Phase A（有官方詳解→重構，先做）vs Phase B（無→最後生成）
    has_official = sum(1 for r in results if r["has_official"] is True)
    no_official = sum(1 for r in results if r["has_official"] is False)
    coverage_known = any(r["has_official"] is not None for r in results)

    summary = {
        "year": year,
        "total": n,
        "perfect": perfect,
        "perfect_pct": round(perfect / n * 100, 1) if n else 0,
        "passed_by_check": by_check,
        "needs_image_review": needs_image,
        "phase_a_has_official": has_official,
        "phase_b_no_official": no_official,
        "questions": results,
    }

    TMP_DIR.mkdir(exist_ok=True)
    out = TMP_DIR / f"audit-{year}.json"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # 主控台摘要
    print(f"\n[{year}] 共 {n} 題，全通過 {perfect} ({summary['perfect_pct']}%)")
    print(f"  各項通過數: answer={by_check['answer']}  逐選項={by_check['per_option_expl']}  "
          f"分類={by_check['subspecialty']}  reference={by_check['reference']}  "
          f"已連圖={by_check['image']}（待判定圖片 {needs_image}）")
    if coverage_known:
        print(f"  官方詳解覆蓋: Phase A 有官方 {has_official}　/　Phase B 無官方(待最後生成) {no_official}")
    else:
        print("  （未跑 extract_official_explanations.py，無 Phase A/B 分類）")
    print(f"  → 報告: {out}")
    return summary


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("用法: python scripts/audit_questions.py <year> [year ...] | --all")
        sys.exit(1)

    grouped = _cards_by_year()
    if args == ["--all"]:
        years = sorted(y for y in grouped if y.startswith("20"))
    else:
        years = args

    print("  （image 檢查：題卡 body 偵測 ![](...) 與圖片副檔名 ![[...]] 嵌入；無嵌入記 NA）")
    grand_total = grand_perfect = 0
    for year in years:
        s = audit_year(year, grouped.get(year, []))
        if s:
            grand_total += s["total"]
            grand_perfect += s["perfect"]

    if len(years) > 1:
        pct = round(grand_perfect / grand_total * 100, 1) if grand_total else 0
        print(f"\n=== 全部 {len(years)} 年：{grand_total} 題，全通過 {grand_perfect} ({pct}%) ===")


if __name__ == "__main__":
    main()
