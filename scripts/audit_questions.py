#!/usr/bin/env python3
"""題目品質稽核器（移植 lit-review 的 PRISMA 清單稽核，改為放射考題 5 項清單）。

對 data/{year}.json 逐題跑品質清單，輸出 tmp/audit-{year}.json 報告：哪些題缺哪項。
可離線重複執行，量化「機器先審」前後的品質提升，亦供 skill 決定要修補哪些題。

品質清單（每項 True/False/None）：
  1. answer          — 有合法 correctAnswer (A–E)
  2. per_option_expl — explanation 逐選項解釋（偵測 (A)/(B) 或行首 A:/A. 樣式）
  3. subspecialty    — 已分類（非 Unknown / 空）
  4. reference       — 非空且通過放射來源辨識閘（verify_reference）
  5. image           — 圖片已連結；無法離線判定是否需圖時記為 None(NA)，不扣分

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

# 同目錄匯入來源辨識閘
sys.path.insert(0, str(Path(__file__).parent))
import verify_reference  # noqa: E402

DATA_DIR = Path(__file__).parent.parent / "data"
TMP_DIR = Path(__file__).parent.parent / "tmp"

VALID_ANSWERS = {"A", "B", "C", "D", "E"}

# explanation 逐選項樣式：含 (A)…(B)… 或 多行行首 A:/A./A、 等
_PER_OPTION_PAREN = re.compile(r"\([A-E]\)")
_PER_OPTION_LINE = re.compile(r"(?m)^\s*[A-E][\s:：.\)、]")


def _has_per_option(explanation: str) -> bool:
    """explanation 是否逐選項解釋（至少出現 2 個選項標記）。"""
    if not explanation:
        return False
    paren = len(_PER_OPTION_PAREN.findall(explanation))
    line = len(_PER_OPTION_LINE.findall(explanation))
    return paren >= 2 or line >= 2


def _has_image_markup(text: str) -> bool:
    """字串是否含圖片標記（markdown 圖或 Obsidian 圖片 embed）。"""
    if not text:
        return False
    return bool(re.search(r"!\[[^\]]*\]\([^)]+\)", text) or
                re.search(r"\[\[[^\]]+\.(?:png|jpg|jpeg|gif)", text, re.IGNORECASE))


def audit_question(q: dict) -> dict:
    """回傳單題稽核結果 dict（含各項布林、score、applicable、missing）。"""
    checks: dict[str, bool | None] = {}

    # 1. answer
    checks["answer"] = q.get("correctAnswer", "") in VALID_ANSWERS

    # 2. per_option_expl
    checks["per_option_expl"] = _has_per_option(q.get("explanation", ""))

    # 3. subspecialty
    sub = (q.get("subspecialty") or "").strip()
    checks["subspecialty"] = bool(sub) and sub != "Unknown"

    # 4. reference
    checks["reference"] = verify_reference.passes_gate(q.get("reference", ""))

    # 5. image（NA：無法離線判定是否需圖）
    has_img = bool(q.get("images")) or _has_image_markup(q.get("questionText", "")) \
        or _has_image_markup(q.get("explanation", ""))
    checks["image"] = True if has_img else None  # None = NA，待 skill 用官方 PDF 判定

    applicable = [k for k, v in checks.items() if v is not None]
    passed = [k for k in applicable if checks[k]]
    missing = [k for k in applicable if not checks[k]]

    return {
        "id": q.get("id"),
        "subspecialty": q.get("subspecialty"),
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


def audit_year(year: str) -> dict:
    """稽核單一年份，回傳彙總 dict 並寫出 tmp/audit-{year}.json。"""
    json_path = DATA_DIR / f"{year}.json"
    if not json_path.exists():
        print(f"  Warning: {json_path} 不存在，跳過")
        return {}

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    questions = data.get("questions", [])

    coverage = _load_official_coverage(year)
    results = []
    for q in questions:
        r = audit_question(q)
        r["has_official"] = coverage.get(q.get("id"), None)  # None=未跑抽取
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

    if args == ["--all"]:
        years = sorted(p.stem for p in DATA_DIR.glob("20*.json"))
    else:
        years = args

    grand_total = grand_perfect = 0
    for year in years:
        s = audit_year(year)
        if s:
            grand_total += s["total"]
            grand_perfect += s["perfect"]

    if len(years) > 1:
        pct = round(grand_perfect / grand_total * 100, 1) if grand_total else 0
        print(f"\n=== 全部 {len(years)} 年：{grand_total} 題，全通過 {grand_perfect} ({pct}%) ===")


if __name__ == "__main__":
    main()
