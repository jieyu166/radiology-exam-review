#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""專案慣例 linter（唯讀）：檢查 vault/concepts 與 vault/questions 題卡是否符合本專案慣例。

用法：python scripts/lint_concepts.py [--quiet]
  ERROR=真正的問題（未定義 footnote、殘留 ![[...]]、題卡指向不存在的概念）
  WARN =建議覆核（缺章節、孤兒 footnote、引用院內筆記、題卡無 correctAnswer）
退出碼：有 ERROR → 1，否則 0。

題卡來源：scripts/vault_questions.py 的 iter_question_cards（重用 vault_site compiler 解析）。
"""
from __future__ import annotations
import re, sys, os, glob
from pathlib import Path

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(REPO, "scripts"))
from vault_questions import iter_question_cards  # noqa: E402
from vault_site.compiler import parse_frontmatter  # noqa: E402  與網站共用 frontmatter 解析（支援行內與多行清單）

errors: list[str] = []
warns: list[str] = []
def err(m): errors.append(m)
def warn(m): warns.append(m)

WIKI_EMBED = re.compile(r"!\[\[([^\]|#]+)")              # Obsidian 嵌入
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")  # 網站 compiler 支援的圖片嵌入
FN_DEF = re.compile(r"(?m)^\[\^([^\]]+)\]:")
FN_REF = re.compile(r"\[\^([^\]]+)\](?!:)")
DV_SLUG = re.compile(r'contains\(concepts,\s*"([^"]+)"\)')
INTERNAL_NOTE = re.compile(r"院內筆記|整理自.{0,8}筆記|演講筆記")
# 一手來源標記：同一條 footnote 若含這些,代表演講/院內筆記僅為 provenance、已附可查證一手來源
STRONG_REF = re.compile(r"radiopaedia|radiographic|rsna|doi:|ajnr|ajr|statdx|clinicalkey|pubmed|neurolog|lancet|ann neurol|ann intern|am j|chest\.|stroke|front oncol|radiology|10\.\d{4}|NBK|et al\.|guideline|實際查證|已查核|查證 accessed", re.I)
VALID_ANSWERS = set("ABCDE")

# ---- 1) 概念檔檢查 ----
concept_slugs: set[str] = set()
concept_files = [p for p in sorted(glob.glob("vault/concepts/*.md"))
                 if not os.path.basename(p).startswith("_")]   # 跳過 _MOC/_index 等索引檔
for p in concept_files:
    name = os.path.basename(p)[:-3]
    t = open(p, encoding="utf-8").read()
    fmd, _ = parse_frontmatter(t)
    cs = fmd.get("concepts")
    if isinstance(cs, str):
        cs = [cs]
    slug = str(cs[0]).strip() if cs else None
    if slug:
        concept_slugs.add(slug)
        if slug != name:
            err(f"[概念slug≠檔名] {name}.md 的 concepts:[{slug}]")
    else:
        warn(f"[概念缺 concepts 欄] {name}.md")
    bad_embeds = [e for e in WIKI_EMBED.findall(t) if not e.strip().lower().endswith(IMAGE_EXT)]
    if bad_embeds:
        warn(f"[概念含非圖片 ![[...]] 嵌入(網站不認)] {name}.md：{bad_embeds[0]}")
    if "### 參考來源" not in t:
        warn(f"[概念缺 ### 參考來源] {name}.md")
    dv = DV_SLUG.search(t)
    if "## 考題" not in t or not dv:
        warn(f"[概念缺 ## 考題 dataview] {name}.md")
    elif slug and dv.group(1) != slug:
        err(f"[dataview slug 不符] {name}.md dataview=\"{dv.group(1)}\" ≠ {slug}")
    # footnote 定義 vs 引用
    defs = set(FN_DEF.findall(t)); refs = set(FN_REF.findall(t))
    for r in refs - defs:
        err(f"[footnote 未定義] {name}.md 用了 [^{r}] 但無定義")
    for d in defs - refs:
        warn(f"[footnote 未被引用] {name}.md 定義 [^{d}] 但沒用到")
    if "### 參考來源" in t and INTERNAL_NOTE.search(t):
        # provenance 容忍：逐條 footnote 檢查——提及院內/演講筆記「但同條無一手來源」才算違規
        ref_sec = t.split("### 參考來源", 1)[-1]
        for e in re.split(r"(?m)^(?=\[\^)", ref_sec):
            if INTERNAL_NOTE.search(e) and not STRONG_REF.search(e):
                fnm = re.match(r"\[\^([^\]]+)\]", e.strip())
                warn(f"[院內/演講筆記為唯一來源] {name}.md [^{fnm.group(1) if fnm else '?'}]（需併附一手來源）")

# ---- 2) 題卡檢查（vault/questions）----
card_count = 0
for card in iter_question_cards(Path("vault")):
    card_count += 1
    letters = [x for x in card.correct_answer.split(",") if x]
    valid_answer = bool(letters) and all(x in VALID_ANSWERS for x in letters)
    if not valid_answer and "送分" not in card.explanation:
        warn(f"[題目無 correctAnswer] {card.id}")
    for c in card.concepts:
        if c not in concept_slugs:
            err(f"[題目指向不存在概念] {card.id} → concepts:[{c}]（無 {c}.md）")

# ---- 報告 ----
print(f"檢查：{len(concept_files)} 概念、{card_count} 題卡")
print(f"\n=== ERROR ({len(errors)}) ===")
for m in errors: print("  ✗", m)
print(f"\n=== WARN ({len(warns)}) ===")
if "--quiet" in sys.argv:
    from collections import Counter
    cat = Counter(re.match(r"\[([^\]]+)\]", w).group(1) for w in warns if re.match(r"\[", w))
    for k, n in cat.most_common(): print(f"  ⚠ {k}: {n}")
else:
    for m in warns: print("  ⚠", m)
print(f"\n小結：{len(errors)} errors, {len(warns)} warnings")
sys.exit(1 if errors else 0)
