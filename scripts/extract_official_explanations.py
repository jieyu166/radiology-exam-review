#!/usr/bin/env python3
"""官方交換考詳解 PDF 抽取器（流水線「便宜層」：pdftotext 抽取 + 切題 + 對齊）。

官方詳解 PDF（3. Resources/論文s/交換考/{year} 交換考題 詳解.pdf）每題結構：
    <答案字母>          ← 單獨一行，作為切題標記
    <題幹>
    (A) ... (B) ... (C) ... (D) ...   ← 選項
    <參考文獻區>        ← 真正的 reference 來源（期刊/教科書）
    A. Incorrect ...    ← 逐選項詳解
    B. Correct ...

本腳本抽取並解析為結構化候選，再用題幹文字相似度對齊 data/{year}.json 的題號，
輸出 tmp/official-{year}.json。智慧層（skill）據此重構 explanation + 補 reference。

用法：
  python scripts/extract_official_explanations.py 2016
  python scripts/extract_official_explanations.py 2016 --pdf "完整路徑.pdf"

需求：pdftotext（Poppler / Git for Windows 內建）。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

REPO = Path(__file__).parent.parent
DATA_DIR = REPO / "data"
TMP_DIR = REPO / "tmp"

# 官方詳解 PDF 預設搜尋目錄（vault）。可用 --pdf 覆寫。
VAULT_EXAM_DIR = Path(
    r"C:\Users\jai16\OneDrive\00 放射科\0筆記\Radiology\3. Resources\論文s\交換考"
)

_LONE_ANSWER_RE = re.compile(r"^[A-E]$")
_OPTION_RE = re.compile(r"^\(([A-E])\)\s*(.*)")
_PER_OPTION_RE = re.compile(r"^([A-E])[.\)、]\s*(.*)", re.IGNORECASE)
# 逐選項詳解的判定/正誤關鍵字（中英文皆認，因官方詳解由不同人編寫、語言不一）。
_VERDICT_RE = re.compile(r"correct|incorrect|true|false|錯誤|錯|正確|對|不對|是|非", re.IGNORECASE)


def _has_explanation_text(text: str) -> bool:
    """raw 區塊是否含逐選項詳解文字。

    訊號：出現 ≥2 行「行首 X.（非選項宣告 (X)）+ 內容」的逐選項說明行。
    用行首樣式而非關鍵字搜尋，避免題幹「which is TRUE?」的 true/false 誤判。
    """
    count = 0
    for ln in text.splitlines():
        s = ln.strip()
        if _OPTION_RE.match(s):  # 「(A) ...」是選項宣告，不算詳解
            continue
        m = _PER_OPTION_RE.match(s)  # 「A. ...」「B、...」是逐選項說明
        if m and m.group(2).strip():
            count += 1
    return count >= 2


def run_pdftotext(pdf: Path) -> list[str]:
    """以 -layout 抽取 PDF 文字，回傳 strip 後非空行清單（保留切題用的答案字母行）。"""
    try:
        out = subprocess.run(
            ["pdftotext", "-layout", str(pdf), "-"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except FileNotFoundError:
        print("Error: 找不到 pdftotext，請確認 Poppler / Git for Windows 已安裝。", file=sys.stderr)
        sys.exit(1)
    if out.returncode != 0:
        print(f"Error: pdftotext 失敗：{out.stderr}", file=sys.stderr)
        sys.exit(1)
    lines = [ln.strip() for ln in out.stdout.splitlines()]
    return [ln for ln in lines if ln]  # 去空行（含縮排），保留內容行


def split_blocks(lines: list[str]) -> list[list[str]]:
    """以「單獨一行的答案字母」為界，切成題目區塊。

    單獨字母在內文/文獻中偶會誤觸，故事後合併：真正的題目區塊必含選項行 (A)，
    缺 (A) 者視為前一題的續寫並併回，避免過度切分。
    """
    raw: list[list[str]] = []
    cur: list[str] = []
    for ln in lines:
        if _LONE_ANSWER_RE.match(ln):
            if cur:
                raw.append(cur)
            cur = [ln]
        elif cur:  # 忽略第一個答案字母前的封面/雜訊
            cur.append(ln)
    if cur:
        raw.append(cur)

    merged: list[list[str]] = []
    for blk in raw:
        has_option = any(_OPTION_RE.match(ln) for ln in blk[1:])
        if has_option or not merged:
            merged.append(blk)
        else:
            merged[-1].extend(blk)  # 缺 (A)，併回前一題
    return merged


def parse_block(block: list[str]) -> dict:
    """把一個區塊解析為 {answer, question_text, options, citations, per_option, raw}。"""
    answer = block[0]
    body = block[1:]

    # 找第一個選項行 (A)
    opt_start = next((i for i, ln in enumerate(body) if _OPTION_RE.match(ln)), len(body))
    question_text = " ".join(body[:opt_start]).strip()

    # 解析選項，直到出現逐選項詳解（行首 "A. Incorrect/Correct" 等）或文獻
    options: dict[str, str] = {}
    per_option: dict[str, str] = {}
    citations: list[str] = []

    i = opt_start
    cur_opt = None
    # 階段一：蒐集選項（option 標記為 "(X)"）
    while i < len(body):
        m = _OPTION_RE.match(body[i])
        if m:
            cur_opt = m.group(1)
            options[cur_opt] = m.group(2).strip()
            i += 1
        else:
            # 選項可能換行續寫，但一旦碰到逐選項詳解（X. + 正誤判定詞）就停止
            if _PER_OPTION_RE.match(body[i]) and _VERDICT_RE.search(body[i]):
                break
            if cur_opt and not _looks_like_citation(body[i]):
                options[cur_opt] += " " + body[i].strip()
                i += 1
            else:
                break

    # 階段二：文獻區 + 逐選項詳解（混雜，靠 "X. Correct/Incorrect" 樣式區分）
    cur_expl = None
    while i < len(body):
        ln = body[i]
        m = _PER_OPTION_RE.match(ln)
        if m and _VERDICT_RE.search(ln):
            cur_expl = m.group(1).upper()
            per_option[cur_expl] = m.group(2).strip()
        elif cur_expl:
            per_option[cur_expl] += " " + ln.strip()
        else:
            citations.append(ln.strip())
        i += 1

    return {
        "answer": answer,
        "question_text": question_text,
        "options": options,
        "citations": [c for c in citations if c],
        "per_option": per_option,
        "raw": "\n".join(block),
    }


def _looks_like_citation(line: str) -> bool:
    """粗略判斷一行是否為文獻引用（含年份且像書目）。"""
    return bool(re.search(r"\b(19|20)\d{2}\b", line) and
                re.search(r"[A-Z][a-z]+,?\s+[A-Z]{1,3}\b|\bed[s]?\.|\bRadiology\b|\bAm\b|\bJ\b", line))


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", text.lower())


def align(blocks_parsed: list[dict], questions: list[dict], threshold: float = 0.45) -> dict:
    """全域貪婪指派對齊（不依賴題序；JSON 來自 Obsidian 匯入，與 PDF 順序未必一致）。

    算每個 (題, 區塊) 配對相似度，以 quick_ratio 預篩再算精確 ratio，
    依相似度由高到低貪婪配對（兩端皆未用且過門檻才配）。高精度：寧缺勿錯配。
    """
    q_norm = [_norm(q.get("questionText", "")) for q in questions]
    b_norm = [_norm(b["question_text"]) for b in blocks_parsed]

    pairs = []
    for qi, qt in enumerate(q_norm):
        sm = SequenceMatcher(None, qt, "")
        sm.set_seq1(qt)
        for bi, bt in enumerate(b_norm):
            sm.set_seq2(bt)
            if sm.quick_ratio() < threshold:  # 便宜上界，先篩掉
                continue
            r = sm.ratio()
            if r >= threshold:
                pairs.append((r, qi, bi))

    pairs.sort(reverse=True)
    q_assigned: dict[int, int] = {}
    b_used: set[int] = set()
    for r, qi, bi in pairs:
        if qi in q_assigned or bi in b_used:
            continue
        q_assigned[qi] = bi
        b_used.add(bi)

    matches = []
    for qi, q in enumerate(questions):
        if qi in q_assigned:
            b = blocks_parsed[q_assigned[qi]]
            matches.append({
                "qid": q.get("id"),
                "number": q.get("number"),
                "answer_official": b["answer"],
                "answer_json": q.get("correctAnswer"),
                "answer_agree": b["answer"] == q.get("correctAnswer"),
                "similarity": round(SequenceMatcher(None, q_norm[qi],
                                                    b_norm[q_assigned[qi]]).ratio(), 3),
                "citations": b["citations"],
                "per_option": b["per_option"],
                "has_per_option": bool(b["per_option"]),
                "has_explanation": _has_explanation_text(b["raw"]),
                "raw": b["raw"],
            })
        else:
            matches.append({
                "qid": q.get("id"),
                "number": q.get("number"),
                "matched": False,
            })
    return {
        "matched": len(q_assigned),
        "matches": matches,
        "unused_blocks": [blocks_parsed[i]["raw"][:200]
                          for i in range(len(blocks_parsed)) if i not in b_used],
    }


def find_pdf(year: str) -> Path | None:
    """在 vault 交換考目錄找該年份詳解 PDF（排除 old/ 備份）。"""
    if not VAULT_EXAM_DIR.exists():
        return None
    cands = [p for p in VAULT_EXAM_DIR.glob(f"{year}*詳解*.pdf") if "old" not in p.parts]
    return cands[0] if cands else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("year")
    ap.add_argument("--pdf", help="官方詳解 PDF 路徑（覆寫自動搜尋）")
    args = ap.parse_args()

    pdf = Path(args.pdf) if args.pdf else find_pdf(args.year)
    if not pdf or not pdf.exists():
        print(f"Error: 找不到 {args.year} 的官方詳解 PDF（用 --pdf 指定）。", file=sys.stderr)
        sys.exit(1)

    json_path = DATA_DIR / f"{args.year}.json"
    if not json_path.exists():
        print(f"Error: {json_path} 不存在。", file=sys.stderr)
        sys.exit(1)
    questions = json.loads(json_path.read_text(encoding="utf-8")).get("questions", [])

    print(f"PDF      : {pdf.name}")
    lines = run_pdftotext(pdf)
    blocks = split_blocks(lines)
    parsed = [parse_block(b) for b in blocks]
    print(f"PDF 區塊 : {len(parsed)}  /  JSON 題數 : {len(questions)}")

    result = align(parsed, questions)
    result["year"] = args.year
    result["pdf"] = str(pdf)
    result["block_count"] = len(parsed)
    result["json_count"] = len(questions)

    # 答案一致性檢查（對已對齊者）
    agree = sum(1 for m in result["matches"] if m.get("answer_agree"))
    disagree = [m["qid"] for m in result["matches"] if m.get("answer_agree") is False]

    TMP_DIR.mkdir(exist_ok=True)
    out = TMP_DIR / f"official-{args.year}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"對齊成功 : {result['matched']}/{len(questions)}  "
          f"（答案一致 {agree}，不一致 {len(disagree)}）")
    if disagree:
        print(f"  答案不一致題（需查）: {', '.join(disagree[:15])}{' …' if len(disagree) > 15 else ''}")
    if result["unused_blocks"]:
        print(f"  未對齊 PDF 區塊: {len(result['unused_blocks'])}（可能為跨欄雜訊或多餘）")
    print(f"  → {out}")


if __name__ == "__main__":
    main()
