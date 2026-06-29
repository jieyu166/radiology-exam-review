#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""稽核概念是否含「一般放射科判讀影像知識」（見記憶 concept-imaging-interpretation-standard）。

啟發式：抽每個概念的實質內容（frontmatter 之後、`### 參考來源`／`## 考題` 之前,
即導讀＋Summary＋各節＋考點），計算「影像關鍵詞涵蓋分數」與「應試詞密度」,
並對照該概念被幾題交換考引用（考題數），輸出依「分數低、考題多」排序的補強清單。

分數為粗略指標、供醫師覆核;不是自動改寫,只標記哪些概念可能只是考題詳解、缺影像特徵。

用法：
  python scripts/audit_concept_imaging.py            # 預設門檻,輸出清單
  python scripts/audit_concept_imaging.py --thr 7    # 自訂影像分數門檻
輸出：vault/概念影像補強清單.md
"""
from __future__ import annotations
import glob, re, json, sys, pathlib, datetime, collections

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONCEPTS = ROOT / "vault" / "concepts"
DATA = ROOT / "data"
OUT = ROOT / "vault" / "概念影像補強清單.md"

# 影像關鍵詞（分組;每組命中即 +1,計「涵蓋廣度」而非次數）
IMG_GROUPS = [
    r"\bCT\b|電腦斷層", r"MRI|\bMR\b|磁振", r"\bUS\b|ultrasound|超音波|Doppler|都卜勒",
    r"X-?ray|radiograph|平片|X 光|攝影", r"angiograph|血管攝影|CTA|MRA|CTV|MRV",
    r"\bT1\b", r"\bT2\b", r"FLAIR|DWI|ADC|GRE|SWI|T2\*", r"perfus|灌注|PET|核醫",
    r"signal|訊號", r"enhanc|強化|顯影", r"attenuat|density|密度|HU\b|高密度|低密度",
    r"echo|回音|echogen|無回音|高回音|低回音",
    r"sign\b|徵象", r"high.?intens|low.?intens|高訊號|低訊號|等訊號",
    r"calcif|鈣化", r"邊界|margin|well.?defined|ill.?defined|circumscrib",
    r"充盈缺損|filling defect|washout|wash-?in|delayed", r"水腫|edema|oedema|出血|hemorrhag|壞死|necros",
    r"DDx|鑑別|differential", r"分型|classif|type\b|stage|分期|grade",
    # 平片/骨骼解剖徵象
    r"骨化|ossif|骨皮質|cortex|骨膜|periost|骨骺|epiphys|髓腔|metaphys|椎體|vertebr",
    # 大小/口徑/管腔變化
    r"萎縮|atroph|肥大|hypertroph|擴張|dilat|狹窄|stenos|strictur|narrow",
    # 結石/管內/充盈
    r"結石|stone|calcul|管內|intraluminal|filling|spur|web\b",
    # 血管影像
    r"aneurysm|動脈瘤|fistula|瘻|側枝|collateral|引流|drainage|管壁|血栓|thromb",
    # 先天/變異/發育
    r"變異|variant|anomal|畸形|發育不全|hypoplas|aplas|agenes|憩室|divertic",
    # 泌尿/腹部徵象
    r"水腎|hydronephro|hydroureter|逆流|reflux|膀胱|bladder|輸尿管|ureter|VCUG|腎\b",
    # 胸部 HRCT 型態學
    r"consolidat|實變|air bronchogram|氣支氣管",
    r"ground.?glass|GGO|毛玻璃|halo|atoll|暈徵",
    r"reticul|網狀|honeycomb|蜂窩|蜂巢|crazy.?paving|鋪石",
    r"nodul|結節|centrilobular|小葉中心|tree.?in.?bud|樹芽|micronodul",
    r"bronchiect|支氣管擴張|interlobular|小葉間隔|perilobular|septal thicken|mosaic|嵌鑲",
]
EXAM_MARKERS = re.compile(r"選項|題目正解|題目所引|正解|何者|不正確|錯誤敘述|為非|為假|為真|皆正確")


def body_of(text: str) -> str:
    # 去 frontmatter
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    t = text[m.end():] if m else text
    # 截到 ### 參考來源 或 ## 考題（取較前者）
    cut = len(t)
    for marker in ("\n### 參考來源", "\n## 考題", "\n### 參考", "\n## 考"):
        i = t.find(marker)
        if i != -1:
            cut = min(cut, i)
    return t[:cut]


def img_score(body: str) -> int:
    return sum(1 for g in IMG_GROUPS if re.search(g, body, re.I))


def qcount_map() -> dict:
    c = collections.Counter()
    for f in glob.glob(str(DATA / "*.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for q in d.get("questions", []):
            for slug in (q.get("concepts") or []):
                c[slug] += 1
    return c


def main() -> None:
    thr = 7
    if "--thr" in sys.argv:
        thr = int(sys.argv[sys.argv.index("--thr") + 1])
    qc = qcount_map()
    rows = []
    dist = collections.Counter()
    for f in sorted(glob.glob(str(CONCEPTS / "*.md"))):
        slug = pathlib.Path(f).stem
        if slug.startswith("_"):  # MOC／索引頁,非醫學概念,排除
            continue
        body = body_of(pathlib.Path(f).read_text(encoding="utf-8"))
        s = img_score(body)
        dist[s] += 1
        rows.append({
            "slug": slug, "img": s, "len": len(body.strip()),
            "exam": len(EXAM_MARKERS.findall(body)), "q": qc.get(slug, 0),
        })

    flagged = [r for r in rows if r["img"] < thr]
    # 優先序：影像分數低 → 考題多 → 內容短
    flagged.sort(key=lambda r: (r["img"], -r["q"], r["len"]))

    today = datetime.date.today().isoformat()
    L = []
    L.append("# 概念影像補強清單（缺一般放射判讀知識者）")
    L.append("")
    L.append(f"> 由 `scripts/audit_concept_imaging.py` 啟發式評分:影像關鍵詞涵蓋 `img`（滿分 {len(IMG_GROUPS)}）、"
             f"被引考題數 `q`、實質內容長度 `len`、應試詞數 `exam`。")
    L.append(f"> 門檻 img<{thr} 視為「可能偏考題詳解、影像特徵不足」,依（分數低→考題多→內容短）排序。**供醫師覆核**。")
    L.append(f"> 重跑：`python scripts/audit_concept_imaging.py`｜更新：{today}｜"
             f"概念總數 {len(rows)}、標記 {len(flagged)}。")
    L.append("")
    L.append(f"分數分布（img:檔數）：{dict(sorted(dist.items()))}")
    L.append("")
    L.append("| 概念 | img | 考題q | len | exam |")
    L.append("|---|---|---|---|---|")
    for r in flagged:
        L.append(f"| [ ] [[{r['slug']}]] | {r['img']} | {r['q']} | {r['len']} | {r['exam']} |")
    L.append("")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"已輸出 {OUT}")
    print(f"概念 {len(rows)}、標記(img<{thr}) {len(flagged)}｜分數分布 {dict(sorted(dist.items()))}")


if __name__ == "__main__":
    main()
