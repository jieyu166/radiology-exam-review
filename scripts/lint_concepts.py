#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""專案慣例 linter（唯讀）：檢查 vault/concepts、data/*.json、卡片、圖片資產是否符合本專案慣例。

用法：python scripts/lint_concepts.py [--quiet]
  ERROR=真正的問題（壞圖、未定義 footnote、殘留 ![[...]]、指向不存在的概念）
  WARN =建議覆核（缺章節、孤兒 footnote、引用院內筆記、孤兒圖）
退出碼：有 ERROR → 1，否則 0。
"""
from __future__ import annotations
import json, re, sys, os, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
sys.stdout.reconfigure(encoding="utf-8")

errors: list[str] = []
warns: list[str] = []
def err(m): errors.append(m)
def warn(m): warns.append(m)

WIKI_EMBED = re.compile(r"!\[\[")                      # Obsidian 嵌入（網站不認）
IMG_MD = re.compile(r"!\[[^\]]*\]\((data/images/[^)]+)\)")
FN_DEF = re.compile(r"(?m)^\[\^([^\]]+)\]:")
FN_REF = re.compile(r"\[\^([^\]]+)\](?!:)")
FM_CONCEPTS = re.compile(r"(?m)^concepts:\s*\[([^\]]+)\]")
DV_SLUG = re.compile(r'contains\(concepts,\s*"([^"]+)"\)')
INTERNAL_NOTE = re.compile(r"院內筆記|整理自.{0,8}筆記|演講筆記")
# 一手來源標記：同一條 footnote 若含這些,代表演講/院內筆記僅為 provenance、已附可查證一手來源
STRONG_REF = re.compile(r"radiopaedia|radiographic|rsna|doi:|ajnr|ajr|statdx|clinicalkey|pubmed|neurolog|lancet|ann neurol|ann intern|am j|chest\.|stroke|front oncol|radiology|10\.\d{4}|NBK|et al\.|guideline|實際查證|已查核|查證 accessed", re.I)

# ---- 收集所有「實際被引用的圖」----
referenced_imgs: set[str] = set()
def collect_imgs(text):
    for m in IMG_MD.findall(text):
        referenced_imgs.add(m.replace("\\", "/"))

# ---- 1) 概念檔檢查 ----
concept_slugs: set[str] = set()
concept_files = [p for p in sorted(glob.glob("vault/concepts/*.md"))
                 if not os.path.basename(p).startswith("_")]   # 跳過 _MOC/_index 等索引檔
for p in concept_files:
    name = os.path.basename(p)[:-3]
    t = open(p, encoding="utf-8").read()
    collect_imgs(t)
    fm = FM_CONCEPTS.search(t)
    slug = fm.group(1).strip() if fm else None
    if slug:
        concept_slugs.add(slug)
        if slug != name:
            err(f"[概念slug≠檔名] {name}.md 的 concepts:[{slug}]")
    else:
        warn(f"[概念缺 concepts 欄] {name}.md")
    if WIKI_EMBED.search(t):
        warn(f"[概念含 ![[...]] 嵌入(網站不認)] {name}.md")
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

# ---- 2) json 題目檢查 ----
for p in sorted(glob.glob("data/20*.json")):
    d = json.load(open(p, encoding="utf-8"))
    y = os.path.basename(p)[:-5]
    for q in d.get("questions", []):
        qid = q.get("id", "?")
        blob = (q.get("questionText","") or "") + " " + (q.get("explanation","") or "") + " " + \
               " ".join(o.get("text","") or "" for o in q.get("options",[]))
        collect_imgs(blob)
        if WIKI_EMBED.search(blob):
            err(f"[json 殘留 ![[...]]] {qid}")
        if not q.get("correctAnswer"):
            warn(f"[題目無 correctAnswer] {qid}")
        for c in (q.get("concepts") or []):
            if c not in concept_slugs:
                err(f"[題目指向不存在概念] {qid} → concepts:[{c}]（無 {c}.md）")

# ---- 3) 卡片檢查（收集圖引用，順便抓殘留 ![[...]]）----
for p in glob.glob("vault/questions/**/*.md", recursive=True):
    t = open(p, encoding="utf-8").read()
    collect_imgs(t)

# ---- 4) 圖片資產：壞圖 + 孤兒圖 ----
for img in sorted(referenced_imgs):
    if not os.path.exists(img):
        err(f"[壞圖(引用但檔案不存在)] {img}")
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
existing = set()
for root, _, files in os.walk("data/images"):
    for f in files:
        if os.path.splitext(f)[1].lower() not in IMG_EXT: continue
        existing.add(os.path.join(root, f).replace("\\", "/"))
orphans = existing - referenced_imgs
for o in sorted(orphans):
    warn(f"[孤兒圖(存在但無人引用)] {o}")

# ---- 報告 ----
print(f"檢查：{len(concept_files)} 概念、{len(referenced_imgs)} 圖引用、{len(existing)} 圖檔")
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
