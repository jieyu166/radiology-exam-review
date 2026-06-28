#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""移除概念筆記中重抄考題的 `## 題目` 區（實際題卡由 `## 考題` dataview 動態列出）。

依醫師決定（見記憶 concept-no-duplicate-question）：概念不該在 `## 題目` 把已存在的
交換考題整題重抄一次——那會與「實際題卡 ＋ `## 考題` dataview ＋ `> [!note] 考點`」
形成三重複。本腳本只移除 `## 題目` 標題到下一個 `## ` 區塊（必為 `## 考題`）之間的內容,
保留 frontmatter／導讀／Summary／考點／參考來源／`## 考題` dataview。

安全性：概念無 `<!--SR:-->`、無 genHash;`## 題目` 一律在 `## 考題` 前。若 `## 題目` 後
的下一個 `## ` 不是 `## 考題`,則跳過該檔並回報（不亂刪）。

用法：
  python scripts/dedupe_concept_questions.py            # dry-run（只報告，不寫入）
  python scripts/dedupe_concept_questions.py --apply    # 實際寫入
"""
from __future__ import annotations
import glob, sys, pathlib, re

def main() -> None:
    apply = "--apply" in sys.argv
    concepts = sorted(glob.glob("vault/concepts/*.md"))
    changed = 0
    total_removed = 0
    skipped = []
    samples = []
    qnums_total = 0

    for f in concepts:
        text = pathlib.Path(f).read_text(encoding="utf-8")
        lines = text.split("\n")
        # 找 ## 題目
        t = next((i for i, l in enumerate(lines) if l.strip() == "## 題目"), None)
        if t is None:
            continue
        # 找其後第一個 ## 區塊
        k = next((j for j in range(t + 1, len(lines)) if lines[j].startswith("## ")), None)
        if k is None:
            skipped.append(f"{f}（## 題目 後無其他 ## 區塊）")
            continue
        if lines[k].strip() != "## 考題":
            skipped.append(f"{f}（## 題目 後下一節非 ## 考題,而是「{lines[k].strip()}」）")
            continue
        block = lines[t:k]
        removed = len(block)
        qnums = re.findall(r"20\d\d-\d{2,3}", "\n".join(block))
        qnums_total += len(set(qnums))
        new_lines = lines[:t] + lines[k:]
        # 收尾：避免移除後出現 3+ 連續空行（壓成最多 1 空行於該接縫）
        new_text = re.sub(r"\n{3,}", "\n\n", "\n".join(new_lines))
        total_removed += removed
        changed += 1
        if len(samples) < 4:
            samples.append(f"  {pathlib.Path(f).name}: 移除 {removed} 行（題目@{t+1}→考題@{k+1}）"
                           + (f"；含題號 {sorted(set(qnums))}" if qnums else ""))
        if apply:
            pathlib.Path(f).write_text(new_text, encoding="utf-8")

    print(f"{'★已套用 --apply' if apply else '◇ DRY-RUN（未寫入）'}：{changed} 檔可移除 ## 題目 區,共 {total_removed} 行;"
          f"涉及題號約 {qnums_total} 個（保留於 ## 考題 dataview 動態列出）。")
    print("樣本：")
    for s in samples:
        print(s)
    if skipped:
        print(f"⚠ 跳過 {len(skipped)} 檔（結構異常,未動）：")
        for s in skipped:
            print("  -", s)

if __name__ == "__main__":
    main()
