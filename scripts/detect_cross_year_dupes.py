#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨年重複/相似題偵測（report-only，不改任何資料）。

在開始處理某新年份前，把該年題目與「所有更早年份」已處理題比對，輸出三類清單：
  EXACT  完全重複（questionText + 全選項皆同）→ 應合併 years（情境 1，零重工）
  NEAR   高相似（題幹幾乎相同、僅差 1–2 個選項）→ 重用既有概念、只查改動選項（情境 2）
  NEW    全新題 → 正常逐題查證

用法：
  python scripts/detect_cross_year_dupes.py 2017                 # 比對 2017 vs <2017
  python scripts/detect_cross_year_dupes.py 2017 --threshold 0.9 # 調題幹相似度門檻
  python scripts/detect_cross_year_dupes.py 2017 --json          # 輸出 JSON 供後續程式用
"""
from __future__ import annotations
import argparse, json, re, sys, glob, os
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding="utf-8")
DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def norm(s: str) -> str:
    """正規化：去 markdown/標點/空白、轉小寫，利於比對。"""
    s = (s or "").lower()
    s = re.sub(r"\*+|`+|_+", "", s)              # markdown 強調
    s = re.sub(r"[^0-9a-z一-鿿]+", "", s)  # 只留字母數字漢字
    return s


def opts(q) -> list[str]:
    return [norm(o.get("text", "")) for o in (q.get("options") or [])]


def load(year: int) -> list[dict]:
    p = os.path.join(DATA, f"{year}.json")
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding="utf-8")).get("questions", [])


def opt_diff(a: list[str], b: list[str]) -> int:
    """兩組選項的差異數（以集合對稱差的一半近似改動選項數）。"""
    sa, sb = set(a), set(b)
    return max(len(sa - sb), len(sb - sa))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("year", type=int)
    ap.add_argument("--threshold", type=float, default=0.88, help="題幹相似度門檻（NEAR）")
    ap.add_argument("--json", action="store_true", help="輸出 JSON")
    args = ap.parse_args()

    target = load(args.year)
    # 比對基準：所有更早年份
    prior = [(y, q) for y in range(2016, args.year) for q in load(y)]
    prior_norm = [(y, q, norm(q.get("questionText", "")), opts(q)) for y, q in prior]

    exact, near, new = [], [], []
    for q in target:
        qid = q.get("id")
        qt = norm(q.get("questionText", ""))
        qo = opts(q)
        best = None  # (ratio, year, id, optdiff)
        for y, pq, pqt, po in prior_norm:
            if not qt or not pqt:
                continue
            r = SequenceMatcher(None, qt, pqt).ratio()
            if best is None or r > best[0]:
                best = (r, y, pq.get("id"), opt_diff(qo, po))
        if best and best[0] >= 0.985 and best[3] == 0:
            exact.append((qid, best[2], q.get("years")))
        elif best and best[0] >= args.threshold and best[3] <= 2:
            near.append((qid, best[2], round(best[0], 3), best[3]))
        else:
            new.append(qid)

    if args.json:
        print(json.dumps({"year": args.year, "exact": exact, "near": near, "new": new},
                         ensure_ascii=False, indent=2))
        return

    print(f"=== 跨年去重報告：{args.year}（比對 <{args.year}，共 {len(prior)} 題基準）===")
    print(f"\n[EXACT 完全重複] {len(exact)} 題 → 應合併 years、零重工")
    for qid, src, yrs in exact:
        print(f"  {qid}  ≡  {src}   (該題 years={yrs})")
    print(f"\n[NEAR 高相似（差 1–2 選項）] {len(near)} 題 → 重用概念、只查改動選項")
    for qid, src, ratio, od in near:
        print(f"  {qid}  ~  {src}   題幹相似 {ratio}，選項差 {od}")
    print(f"\n[NEW 全新] {len(new)} 題 → 正常逐題查證")
    print("  " + ", ".join(new[:40]) + (" ..." if len(new) > 40 else ""))
    print(f"\n小計：EXACT {len(exact)}、NEAR {len(near)}、NEW {len(new)}，共 {len(target)} 題")


if __name__ == "__main__":
    main()
