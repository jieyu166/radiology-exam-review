#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_concepts.py — 由 vault/concepts/*.md 產生網站用的概念資料。

輸出（皆 UTF-8、排序穩定、可重複執行）：
  data/concepts-index.json          清單頁用的輕量索引（slug/name/nameZh/subspecialty/checked）
  data/concepts/<slug>.json         每概念一檔的完整內容（網站 schema）

對映（Note v5 章節 → 網站欄位）：
  導讀粗體段          → definition
  ## Summary          → keyPoints（各 bullet）
  ## 放射科醫師影像判讀重點 → imagingFindings
  鑑別/DDx 段          → differentialDiagnosis[]
  ## 臨床重點          → management
  ### 參考來源 內 DOI/連結 → externalLinks[{label,url}]

用法：python scripts/build_concepts.py [--quiet]
退出碼：成功 0；有無法解析 slug 的檔僅警告、不致命。
"""
from __future__ import annotations
import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

SRC_DIR = "vault/concepts"
OUT_DIR = "data/concepts"
INDEX_PATH = "data/concepts-index.json"

# audit: slug 會被當檔名與前端 fetch 路徑使用，僅允許安全字元，杜絕路徑穿越/注入。
SAFE_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CJK = re.compile(r"[一-鿿]")
FOOTNOTE_REF = re.compile(r"\[\^[^\]]+\]")          # [^1] 引用標記（顯示時移除）
MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
BARE_URL = re.compile(r"https?://[^\s)\]）]+")
PLAIN_DOI = re.compile(r"\b(10\.\d{4,}/[^\s)\]）,；。]+)")


def _strip_footnotes(text: str) -> str:
    return FOOTNOTE_REF.sub("", text).rstrip()


def parse_frontmatter(raw: str):
    """回傳 (fm_dict, body)。fm 僅解析本工具需要的欄位，同時接受 inline 與 YAML list。"""
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    if end == -1:
        return {}, raw
    fm_text = raw[3:end]
    body = raw[end + 4:]
    lines = fm_text.splitlines()

    fm = {"concepts": None, "name": None, "subspecialty": [], "aliases": []}
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()

        def collect_list(start_idx):
            """收集接續的 `  - item` 行，回傳 (items, next_idx)。"""
            items, j = [], start_idx
            while j < len(lines) and re.match(r"^\s*-\s+", lines[j]):
                items.append(re.sub(r"^\s*-\s+", "", lines[j]).strip().strip('"\''))
                j += 1
            return items, j

        if key == "concepts":
            if val.startswith("["):
                inner = val.strip("[]")
                fm["concepts"] = inner.split(",")[0].strip().strip('"\'') if inner else None
                i += 1
            else:
                items, i = collect_list(i + 1)
                fm["concepts"] = items[0] if items else None
        elif key == "subspecialty":
            if val.startswith("["):
                fm["subspecialty"] = [s.strip().strip('"\'') for s in val.strip("[]").split(",") if s.strip()]
                i += 1
            elif val:
                fm["subspecialty"] = [val.strip('"\'')]
                i += 1
            else:
                items, i = collect_list(i + 1)
                fm["subspecialty"] = items
        elif key == "aliases":
            if val.startswith("["):
                fm["aliases"] = [s.strip().strip('"\'') for s in val.strip("[]").split(",") if s.strip()]
                i += 1
            elif val:
                fm["aliases"] = [val.strip('"\'')]
                i += 1
            else:
                items, i = collect_list(i + 1)
                fm["aliases"] = items
        elif key == "name":
            fm["name"] = val.strip('"\'')
            i += 1
        else:
            i += 1
    return fm, body


def split_sections(body: str):
    """把 body 依 ## / ### 標題切段。回傳 (lead, sections)。
    lead = 第一個標題前的內容（含導讀粗體）；sections = [(header_text, level, content_str)]。
    """
    lines = body.splitlines()
    lead_lines, sections = [], []
    cur_header, cur_level, cur_buf = None, 0, []
    for line in lines:
        hm = re.match(r"^(#{2,3})\s+(.*)$", line)
        if hm:
            if cur_header is not None:
                sections.append((cur_header, cur_level, "\n".join(cur_buf).strip()))
            cur_header = hm.group(2).strip()
            cur_level = len(hm.group(1))
            cur_buf = []
        else:
            if cur_header is None:
                lead_lines.append(line)
            else:
                cur_buf.append(line)
    if cur_header is not None:
        sections.append((cur_header, cur_level, "\n".join(cur_buf).strip()))
    return "\n".join(lead_lines).strip(), sections


def find_section(sections, *keywords):
    """回傳第一個 header 含任一 keyword 的段落內容，並『包含其巢狀較深標題的子段落』
    （直到遇到同層或更高層標題為止），以免內容放在 ### 子標題下被漏抓。找不到回空字串。"""
    for i, (header, level, content) in enumerate(sections):
        if any(k in header for k in keywords):
            parts = [content] if content.strip() else []
            j = i + 1
            while j < len(sections) and sections[j][1] > level:
                chdr, _clvl, ccontent = sections[j]
                block = ("**%s**" % chdr) if chdr else ""
                if ccontent.strip():
                    block = (block + "\n" + ccontent) if block else ccontent
                if block.strip():
                    parts.append(block)
                j += 1
            return "\n\n".join(parts)
    return ""


def lead_paragraph(lead: str) -> str:
    """取導讀：跳過 # 標題、> callout、[[..]] 導覽、表格、圖片，
    優先回傳以 ** 開頭的粗體心法段，否則第一段散文。"""
    paras = re.split(r"\n\s*\n", lead)

    def is_prose(p):
        s = p.strip()
        if not s:
            return False
        first = s.splitlines()[0].strip()
        if first.startswith(("#", ">", "|", "![", "<!--")):
            return False
        if first.startswith("[[") and first.endswith("]]"):
            return False
        return True

    prose = [" ".join(p.split()) for p in paras if is_prose(p)]
    for p in prose:
        if p.startswith("**"):
            return _strip_footnotes(p).strip()
    return _strip_footnotes(prose[0]).strip() if prose else ""


def bullets(content: str):
    """取 `- ` 開頭的 bullet（去除 footnote 標記）。"""
    res = []
    for line in content.splitlines():
        m = re.match(r"^\s*-\s+(.*)$", line)
        if m:
            t = _strip_footnotes(m.group(1)).strip()
            if t:
                res.append(t)
    return res


def numbered_or_bullets(content: str) -> str:
    """臨床重點：保留原文（數字/bullet 清單），僅去 footnote。"""
    return _strip_footnotes(content).strip()


def extract_ddx(sections):
    """從『鑑別/DDx』段落抓 bullet；若為表格則取每列第一欄。"""
    content = find_section(sections, "鑑別", "DDx", "DDX", "Differential")
    if not content:
        return []
    b = bullets(content)
    if b:
        return b
    rows = []
    for line in content.splitlines():
        if line.strip().startswith("|") and "---" not in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0] and cells[0] not in ("線索", "要點", "特徵", "項目"):
                rows.append(_strip_footnotes(cells[0]))
    return rows


def _norm_doi_key(doi):
    """以 DOI 字串正規化為去重鍵（大小寫、doi.org 前綴無關）。"""
    d = doi.lower()
    if "doi.org/" in d:
        d = d.split("doi.org/")[-1]
    return d.rstrip(".)")


def extract_links(sections):
    """從『參考來源』抓 markdown 連結、裸 URL 與純文字 DOI；以 DOI 去重、限筆數。"""
    content = find_section(sections, "參考來源", "參考文獻", "References")
    if not content:
        return []
    seen, links = set(), []

    def add(url, label):
        key = _norm_doi_key(url) if ("doi.org/" in url.lower() or "10." in url) else url.lower()
        if key in seen:
            return
        seen.add(key)
        links.append({"label": _strip_footnotes(label).strip() or url, "url": url})

    for label, url in MD_LINK.findall(content):
        add(url, label)
    for url in BARE_URL.findall(content):
        add(url.rstrip(".,)）"), url.rstrip(".,)）"))
    # 純文字 DOI（多數 Radiopaedia/官方引用為此形式）→ 建 doi.org 連結
    for doi in PLAIN_DOI.findall(content):
        doi = doi.rstrip(".,)）")
        add("https://doi.org/" + doi, doi)
    return links[:12]


def pick_name_zh(aliases):
    for a in aliases:
        if CJK.search(a):
            return a
    return ""


def build_concept(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    fm, body = parse_frontmatter(raw)
    filename_slug = os.path.basename(path)[:-3]

    slug = filename_slug
    if not SAFE_SLUG.match(slug):
        return None, f"跳過（不安全 slug）：{path}"
    if fm.get("concepts") and fm["concepts"] != slug:
        # 檔名為準，但記錄不一致
        pass

    lead, sections = split_sections(body)
    imaging = find_section(sections, "放射科醫師", "影像判讀", "判讀骨架", "影像診斷", "影像表現", "影像特徵", "技術要點")
    summary = find_section(sections, "Summary")
    clinical = find_section(sections, "臨床重點", "應用重點", "實務重點", "臨床/考試")

    obj = {
        "slug": slug,
        "name": fm.get("name") or slug,
        "nameZh": pick_name_zh(fm.get("aliases") or []),
        "subspecialty": (fm.get("subspecialty") or [""])[0],
        "definition": lead_paragraph(lead),
        "imagingFindings": _strip_footnotes(imaging).strip(),
        "differentialDiagnosis": extract_ddx(sections),
        "externalLinks": extract_links(sections),
        "keyPoints": bullets(summary),
        "management": numbered_or_bullets(clinical),
        "checked": False,
    }
    return obj, None


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")


def main():
    quiet = "--quiet" in sys.argv
    files = sorted(p for p in glob.glob(os.path.join(SRC_DIR, "*.md"))
                   if not os.path.basename(p).startswith("_"))
    os.makedirs(OUT_DIR, exist_ok=True)

    index, skipped = [], []
    n_no_imaging = n_no_links = 0
    written_slugs = set()

    for path in files:
        obj, warn = build_concept(path)
        if obj is None:
            skipped.append(warn)
            continue
        write_json(os.path.join(OUT_DIR, obj["slug"] + ".json"), obj)
        written_slugs.add(obj["slug"])
        index.append({
            "slug": obj["slug"],
            "name": obj["name"],
            "nameZh": obj["nameZh"],
            "subspecialty": obj["subspecialty"],
            "checked": obj["checked"],
        })
        if not obj["imagingFindings"]:
            n_no_imaging += 1
        if not obj["externalLinks"]:
            n_no_links += 1

    index.sort(key=lambda e: e["slug"])
    write_json(INDEX_PATH, {"concepts": index})

    # 移除已不存在於 vault 的舊產物（保持 idempotent、無孤兒）
    removed = 0
    for stale in glob.glob(os.path.join(OUT_DIR, "*.json")):
        slug = os.path.basename(stale)[:-5]
        if slug not in written_slugs:
            os.remove(stale)
            removed += 1

    if not quiet:
        print(f"概念總數：{len(index)}")
        print(f"缺影像判讀重點：{n_no_imaging}    缺參考來源連結：{n_no_links}")
        print(f"移除孤兒檔：{removed}    跳過：{len(skipped)}")
        for s in skipped:
            print("  ⚠", s)
        print(f"輸出：{INDEX_PATH} + {OUT_DIR}/*.json")


if __name__ == "__main__":
    main()
