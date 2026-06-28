#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""掃描 exam-review 全部 reference，抽出「全文需訂閱／館藏」的來源，供醫師找全文。

來源範圍：
  1. data/*.json 每題的 `reference` 欄
  2. vault/concepts/*.md 的 footnote（`[^n]: ...`）

做法：把每條 reference 依分隔符拆成citation 片段 → 過濾掉免費可得者
（Radiopaedia、實際查證網頁、NBK/StatPearls 等）→ 其餘依訊號分到
期刊／教科書／指引平台三類 → 正規化去重、附引用位置 → 輸出 markdown 清單。

注意：分類為「盡力而為」啟發式（regex 比對來源名），供醫師覆核，非精確解析。

用法：python scripts/extract_subscription_refs.py
輸出：vault/全文待查清單.md
"""
from __future__ import annotations
import json, glob, re, collections, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONCEPTS = ROOT / "vault" / "concepts"
OUT = ROOT / "vault" / "全文待查清單.md"

# 免費可得 → 排除（不需找全文）
FREE = re.compile(
    r"radiopaedia|實際查證|已查核|已查證|introductiontoradiology|nde-?ed|statpearls|"
    r"\bNBK\d|ncbi\.nlm|wikipedia|youtube|stroke\.org\.tw",
    re.I,
)

# 訂閱／館藏訊號
JOURNALS = (r"RadioGraphics|Radiology\b|\bAJR\b|\bAJNR\b|\bJVIR\b|\bStroke\b|Neurology|"
            r"Andrology|Lancet|Ann Neurol|Ann Intern|\bChest\b|Eur Radiol|Korean J Radiol|"
            r"Insights Imaging|J Nucl Med|Radiol Clin|Semin |Front Oncol|Radiographics")
TEXTBOOKS = (r"Dahnert|Radiology Review Manual|Requisites|Primer of Diagnostic|Osborn|"
             r"Core Radiology|Grainger|Bushberg|Essential Physics|Fundamentals|Pediatric Imaging|"
             r"Diagnostic Ultrasound|Brant and Helms|Webb |Atlas|Caffey|Felson")
PLATGUIDE = r"ICRP|STATdx|StatDx|ClinicalKey|BI-?RADS|ESUR|ACR (Manual|Appropriateness|BI)|Fleischner|TI-?RADS|LI-?RADS|guideline"
# DOI——排除 Radiopaedia 自家 DOI 前綴 10.53347（免費、非付費期刊）
DOI = r"10\.(?!53347/)\d{4,9}/\S+"

SUB = re.compile("|".join([JOURNALS, TEXTBOOKS, PLATGUIDE, DOI]), re.I)
RE_JOURNAL = re.compile(JOURNALS, re.I)
RE_TEXT = re.compile(TEXTBOOKS, re.I)
RE_PLAT = re.compile(PLATGUIDE, re.I)
RE_DOI = re.compile(DOI)
# 強訂閱訊號（足以蓋過「免費」標記）：只用「明確付費期刊縮寫／DOI／教科書／指引平台」，
# 不用模糊英文字（Stroke/Radiology/Neurology 等可能是病名或 Radiopaedia 內文）以免誤殺免費條目
STRONG = re.compile("|".join([DOI, TEXTBOOKS, PLATGUIDE,
                              r"RadioGraphics|\bAJR\b|\bAJNR\b|\bJVIR\b"]), re.I)
# 已可取得 → 不需找（排除）
READ_OK = re.compile(r"全文已讀|本機 ?PDF|gitignore|開放取用|開放取得|\bPMC\b|open[\- ]?access", re.I)
# 非「可找全文的單篇文章」段落（排除）
SKIPSEG = re.compile(r"provenance|演講筆記|整理自|院內筆記", re.I)


def split_segments(text: str) -> list[str]:
    """只拆全形 `；。` 與換行——保住 Vancouver citation（其內用英文 . ; : 分隔）完整。"""
    text = re.sub(r"^\[\^\d+\]:\s*", "", text.strip())
    parts = re.split(r"[；。\n]", text)
    out = []
    for p in parts:
        p = p.strip(" *-．.。，,、:：\t　①②③④⑤⑥⑦⑧⑨⑩")
        if len(p) >= 8:
            out.append(p)
    return out


def included(seg: str) -> bool:
    if not SUB.search(seg):
        return False
    if SKIPSEG.search(seg):
        return False
    if READ_OK.search(seg) and "未讀" not in seg:   # 已讀/開放/有本機 PDF → 已可取得
        return False
    if FREE.search(seg) and not STRONG.search(seg):  # 純免費來源（無訂閱目標）
        return False
    return True


def norm_key(seg: str) -> str:
    """正規化去重鍵：去掉 accessed 日期、括號註、頁碼、版次尾巴。"""
    k = re.sub(r"（[^）]*）|\([^)]*\)", "", seg)
    k = re.sub(r"accessed[^,，;；]*", "", k, flags=re.I)
    k = re.sub(r"實際查證[^,，;；]*", "", k)
    k = re.sub(r"\s+", " ", k).strip()
    return k.lower()[:90]


_JN = (r"RadioGraphics|Radiology|AJR Am J Roentgenol|\bAJR\b|\bAJNR\b|\bJVIR\b|Int J Stroke|"
       r"J Stroke Cerebrovasc|\bStroke\b|Neuro Oncol|Neurology|Andrology|Lancet|Eur Radiol|"
       r"Korean J Radiol|J Nucl Med|Insights Imaging|J Am Coll Cardiol|Circulation|Chest")


def journal_key(seg: str) -> str:
    """期刊去重鍵：優先用 期刊+年卷(+首頁) signature（可合併『有DOI/無DOI』的同篇）；否則 DOI；再否則 norm。"""
    jn = re.search(_JN, seg, re.I)
    sig = re.search(r"(?:19|20)\d{2}\s*;?\s*\d+", seg)   # 年;卷
    page = re.search(r":\s*(\d+)", seg)
    if jn and sig:
        k = re.sub(r"\s+", "", jn.group(0).lower()).replace("radiographics", "rg")
        k += re.sub(r"\D", "", sig.group(0))
        if page:
            k += "p" + page.group(1)
        return "j:" + k
    m = RE_DOI.search(seg)
    if m:
        return "doi:" + re.sub(r"[^0-9a-zA-Z./_-]+$", "", m.group(0).lower())
    return norm_key(seg)


def textbook_key(seg: str) -> str:
    """教科書去重鍵：收斂到『書名＋版次』，丟掉章節/頁/引文（同一本書只列一次）。"""
    m = RE_TEXT.search(seg)
    if not m:
        return norm_key(seg)
    tail = seg[m.start():m.start() + 60]
    tail = re.split(r"[：:，,（(「『]|\bpp?\.|\bCh\b|\bp\.?\s*\d|第|——", tail)[0]
    return "b:" + re.sub(r"\s+", " ", tail).strip().lower()


def bucket(seg: str) -> str:
    if RE_DOI.search(seg) or RE_JOURNAL.search(seg):
        return "journal"
    if RE_TEXT.search(seg):
        return "textbook"
    if RE_PLAT.search(seg):
        return "platguide"
    return "other"


def collect():
    # source key -> {rep: 原文代表, locs: set, bucket}
    store: dict[str, dict] = {}

    def add(seg: str, loc: str):
        if not included(seg):
            return
        b = bucket(seg)
        k = journal_key(seg) if b == "journal" else textbook_key(seg) if b == "textbook" else norm_key(seg)
        if not k:
            return
        e = store.setdefault(k, {"rep": seg.strip(), "locs": set(), "bucket": b})
        # 取較長的原文當代表（資訊較全）
        if len(seg.strip()) > len(e["rep"]):
            e["rep"] = seg.strip()
        e["locs"].add(loc)

    for f in sorted(glob.glob(str(DATA / "*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for q in d.get("questions", []):
            r = (q.get("reference") or "").strip()
            if not r:
                continue
            for seg in split_segments(r):
                add(seg, q.get("id", "?"))

    for f in sorted(glob.glob(str(CONCEPTS / "*.md"))):
        slug = pathlib.Path(f).stem
        for ln in open(f, encoding="utf-8"):
            if re.match(r"^\[\^\d+\]:", ln):
                for seg in split_segments(ln):
                    add(seg, slug)
    return store


def fmt_locs(locs: set) -> str:
    ls = sorted(locs)
    shown = ls[:8]
    s = "、".join(shown)
    if len(ls) > 8:
        s += f" 等 {len(ls)} 處"
    return s


SENTINEL = "<!-- ===== 醫師回填區：以下內容重跑腳本時保留 ===== -->"


def load_existing(path: pathlib.Path):
    """重跑時保留使用者編輯：①條目內的勾選與 [[...pdf]]；②檔尾『醫師回填區』整段。"""
    inline: dict[str, tuple] = {}
    tail = None
    if not path.exists():
        return inline, tail
    txt = path.read_text(encoding="utf-8")
    if SENTINEL in txt:
        tail = txt[txt.index(SENTINEL):].rstrip() + "\n"
    for ln in txt.splitlines():
        m = re.match(r"^- \[([ xX])\] \*\*(.+?)\*\*(.*)$", ln)
        if not m:
            continue
        pdfs = re.findall(r"\[\[[^\]]*?\.pdf[^\]]*?\]\]", m.group(3), re.I)
        if m.group(1).lower() == "x" or pdfs:
            inline[norm_key(m.group(2))] = (m.group(1).lower() == "x", pdfs)
    return inline, tail


def main():
    store = collect()
    inline, tail = load_existing(OUT)
    buckets = {"journal": [], "textbook": [], "platguide": [], "other": []}
    for k, e in store.items():
        buckets[e["bucket"]].append(e)
    for b in buckets.values():
        b.sort(key=lambda e: (-len(e["locs"]), e["rep"].lower()))

    today = datetime.date.today().isoformat()
    total = sum(len(v) for v in buckets.values())
    kept = 0
    L = []
    L.append("# 全文待查清單（需訂閱／館藏，供醫師找全文）")
    L.append("")
    L.append("> 自動掃描 `data/*.json` 的 reference 欄與 `vault/concepts/*.md` 的 footnote 抽出。")
    L.append("> **免費可得／已讀／有本機 PDF 的來源已排除**（Radiopaedia、實際查證網頁、NBK、PMC 開放、本機 PDF 等）。")
    L.append("> 分類為啟發式比對、**供醫師覆核**；同一來源已去重並附引用位置。")
    L.append("> **回填方式**：找到全文後在該條目後貼 `[[檔名.pdf]]` 並把 `[ ]` 改成 `[x]`；"
             "或統一貼到檔尾「醫師回填區」。重跑腳本會**保留**這些編輯。我會據 `[[...pdf]]` 讀取整合。")
    L.append(f"> 重跑：`python scripts/extract_subscription_refs.py`｜更新：{today}｜相異來源 {total} 筆。")
    L.append("")
    L.append("> **奇美館藏全文授權年限（2026-06-21 實查）**：可取得＝**AJR(1965–)、AJNR(1980–)、"
             "Stroke/Int J Stroke/J Stroke Cerebrovasc Dis**；**RadioGraphics 與 Radiology 僅 2022–present**"
             "——本清單的 RG/Radiology 多為 2000–2021，**讀不到全文**，需另尋（PMC/作者版/換刊）。")
    L.append("> 取得方式：`pubs.rsna.org` 有 Cloudflare、自動化讀取不穩；**最可靠＝醫師手動經圖書館開→下載 PDF→ 給我整合**。"
             "查授權：lib.chimei.org.tw 電子期刊搜刊名看年限。詳見記憶 `chimei-library-proxy`。")
    L.append("")
    sections = [
        ("journal", "## 期刊文章（含 DOI，多在 RSNA/Elsevier/Wiley 等付費平台）"),
        ("textbook", "## 教科書（需館藏／訂閱電子書）"),
        ("platguide", "## 指引與平台（ICRP／STATdx／ClinicalKey／BI-RADS／ESUR／ACR 等）"),
        ("other", "## 其他（需人工判斷）"),
    ]
    for key, title in sections:
        items = buckets[key]
        if not items:
            continue
        L.append(f"{title}（{len(items)} 筆）")
        L.append("")
        for e in items:
            box, pdfs = inline.get(norm_key(e["rep"]), (False, []))
            if box or pdfs:
                kept += 1
            mark = "x" if box else " "
            suffix = ("　" + " ".join(pdfs)) if pdfs else ""
            L.append(f"- [{mark}] **{e['rep']}**　— 引用於 {fmt_locs(e['locs'])}{suffix}")
        L.append("")
    L.append("---")
    L.append("")
    if tail:
        L.append(tail.rstrip())
    else:
        L.append(SENTINEL)
        L.append("## 已找到的全文（醫師回填 [[檔名.pdf]]）")
        L.append("")
        L.append("> 在此自由貼上找到的全文 PDF wikilink，例如 `[[2015 RG Mosaic Attenuation.pdf]]`。")
    L.append("")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"已輸出 {OUT}")
    print("各類筆數：", {k: len(v) for k, v in buckets.items()}, "｜總計", total,
          f"｜保留既有回填 {kept} 筆")


if __name__ == "__main__":
    main()
