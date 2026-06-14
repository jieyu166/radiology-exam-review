#!/usr/bin/env python3
"""放射來源辨識閘（取代 lit-review 的 DOI/CrossRef 解析）。

交換考詳解的來源不走 PRISMA/EBM，而是放射科常見來源：期刊、線上資源、教科書、
官方詳解。本模組以白名單 regex 校驗 `reference` 字串是否歸因到可辨識來源，並判定
其來源層級 `reference_source`，供 skill 與 audit_questions.py 共用。

用法（CLI 自測）：
  python scripts/verify_reference.py --selftest
  python scripts/verify_reference.py "Radiology 2018; UPJ obstruction"

設計原則：
  - 不連網解析（避免外連負擔與不確定性），純字串白名單比對。
  - 校驗期刊/書名拼寫，擋掉 LLM 編造的不存在來源。
  - 一個 reference 可含多筆來源（以 ; 或換行分隔），任一筆過閘即視為有出處，
    但回傳全部命中的來源層級，最高可信者為主。
"""
from __future__ import annotations

import re
import sys

# ── 來源層級（可信度由高至低）─────────────────────────────────────────────────
# official_pdf : 官方詳解（保底，永遠可標）
# vault_note   : vault 筆記既有 footnote（可回溯實體 PDF）
# journal      : 具名放射期刊 + 年份
# textbook     : 具名教科書（+ 章節）
# online       : radiopaedia / statdx
# llm_suggested: 不屬上述、由 LLM 提出 → 強制人覆核
REFERENCE_SOURCE_RANK = {
    "official_pdf": 5,
    "vault_note": 4,
    "journal": 3,
    "textbook": 3,
    "online": 2,
    "llm_suggested": 1,
}

# ── 期刊白名單（含常見全名與縮寫）──────────────────────────────────────────────
# 需伴隨 4 位數年份，避免單純出現期刊名就過關。
# 區分「distinctive（獨特，不會被當子字串）」與「generic（單字 Radiology，須防偽）」：
#   distinctive 直接比對；generic「Radiology」另以前綴檢查擋掉
#   「Journal of Imaginary Radiology」這類把 Radiology 當尾字的編造期刊。
#
# 收錄重點放射期刊（全名 + 常見縮寫）。註：官方詳解 PDF 內轉錄的引用一律由 skill 標
# reference_source=official_pdf 直接採信（含跨專科期刊如 Urol Clin North Am），
# 故此白名單只需涵蓋放射科常見來源即可，不必窮舉全醫學期刊。
_JOURNAL_DISTINCTIVE = [
    r"RadioGraphics",
    r"AJNR", r"AJR", r"JVIR", r"JMRI", r"BJR", r"JACR",
    r"American Journal of (?:Roentgenology|Neuroradiology)",
    r"Journal of Vascular and Interventional Radiology",
    # 多字期刊（含「Radiology」尾字者均為真實期刊，可直接收）
    r"European (?:Journal of )?Radiology",
    r"Pediatric Radiology", r"Skeletal Radiology", r"Abdominal Radiology",
    r"Emergency Radiology", r"Academic Radiology", r"Investigative Radiology",
    r"Clinical Radiology", r"Korean Journal of Radiology",
    r"Insights into Imaging", r"Neuroradiology",
    r"Cardiovascular and Interventional Radiology",
    r"Journal of (?:Magnetic Resonance Imaging|Computer Assisted Tomography|Ultrasound)",
    r"Magnetic Resonance Imaging", r"Investigative Radiology",
    r"Radiologic Clinics of North America",
    # 常見縮寫形式
    r"Eur(?:opean)?\.?\s?Radiol", r"Radiol Clin North Am", r"Pediatr Radiol",
    r"Skeletal Radiol", r"Abdom (?:Radiol|Imaging)", r"Emerg Radiol",
    r"Acad Radiol", r"Invest Radiol", r"Clin Radiol", r"Korean J Radiol",
    r"Insights Imaging", r"Cardiovasc Intervent Radiol",
    r"J Magn Reson Imaging", r"Magn Reson Imaging", r"J Comput Assist Tomogr",
    r"J Ultrasound Med", r"AJR Am J Roentgenol",
]
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
_DISTINCTIVE_RE = re.compile(r"\b(?:" + "|".join(_JOURNAL_DISTINCTIVE) + r")\b", re.IGNORECASE)


def _journal_hit(text: str) -> bool:
    """是否命中放射期刊（具名期刊 + 同句出現 4 位數年份）。"""
    if not _YEAR_RE.search(text):
        return False
    if _DISTINCTIVE_RE.search(text):
        return True
    # generic Radiology：逐個比對前綴，排除「Xxx Radiology」這類尾字偽冒。
    for m in re.finditer(r"Radiology\b", text):
        start = m.start()
        prefix = text[:start]
        # 前一個 token 不是大寫起首的英文字才算真正的 Radiology 期刊。
        if not re.search(r"[A-Z][a-z]+\s+$", prefix):
            return True
    return False

# ── 教科書白名單（具名書；章節為加分非必須）──────────────────────────────────
_TEXTBOOK_RE = re.compile(
    r"Osborn'?s\s+Brain"
    r"|Core\s+Radiology"
    r"|(?:The\s+)?Requisites"
    r"|Fundamentals\s+of\s+(?:CT|MRI|Skeletal\s+Radiology|Body\s+CT)"
    r"|BI-?RADS\s*(?:20\d{2})?"
    r"|Brant\s+and\s+Helms"
    r"|Dahnert'?s?",
    re.IGNORECASE,
)

# ── 線上資源白名單 ─────────────────────────────────────────────────────────────
_ONLINE_RE = re.compile(r"radiopaedia(?:\.org)?|statdx", re.IGNORECASE)

# ── 官方詳解（保底來源）────────────────────────────────────────────────────────
_OFFICIAL_RE = re.compile(
    r"官方詳解|交換考\s*20\d{2}.*詳解|official\s+(?:answer|explanation)",
    re.IGNORECASE,
)

# ── vault 筆記出處（Obsidian wikilink 指向筆記/PDF）────────────────────────────
_VAULT_RE = re.compile(r"\[\[[^\]]+\]\]")


def classify_reference(reference: str) -> list[str]:
    """回傳 reference 字串命中的所有來源層級（去重、依可信度排序）。

    空字串或無任何命中 → 回傳 []（代表未過閘）。
    """
    if not reference or not reference.strip():
        return []

    text = reference.strip()
    hits: set[str] = set()

    if _OFFICIAL_RE.search(text):
        hits.add("official_pdf")
    if _VAULT_RE.search(text):
        hits.add("vault_note")
    if _journal_hit(text):
        hits.add("journal")
    if _TEXTBOOK_RE.search(text):
        hits.add("textbook")
    if _ONLINE_RE.search(text):
        hits.add("online")

    return sorted(hits, key=lambda s: REFERENCE_SOURCE_RANK.get(s, 0), reverse=True)


def passes_gate(reference: str) -> bool:
    """reference 是否通過來源辨識閘（至少命中一個白名單來源）。"""
    return len(classify_reference(reference)) > 0


def best_source(reference: str) -> str:
    """回傳最高可信度的來源層級；未過閘回傳 'llm_suggested'。

    'llm_suggested' 代表有寫 reference 但不屬白名單 → 需人覆核。
    完全空字串也回傳 'llm_suggested'（呼叫端應另以 passes_gate 判空）。
    """
    sources = classify_reference(reference)
    return sources[0] if sources else "llm_suggested"


# ── CLI 自測 ───────────────────────────────────────────────────────────────────
_SELFTEST_CASES = [
    # (reference, 應否過閘, 預期最佳來源)
    ("Radiology 2018;287:103-118", True, "journal"),
    ("AJNR 2015", True, "journal"),
    ("European Radiology 2018;28:1234", True, "journal"),
    ("Eur Radiol 2019", True, "journal"),
    ("Skeletal Radiol 2015;44:1", True, "journal"),
    ("Pediatric Radiology 2020", True, "journal"),
    ("AJR Am J Roentgenol 2012;199:W1", True, "journal"),
    ("radiopaedia: UPJ obstruction", True, "online"),
    ("StatDx - Adrenal adenoma", True, "online"),
    ("Osborn's Brain, ch.5", True, "textbook"),
    ("Core Radiology", True, "textbook"),
    ("The Requisites (Neuroradiology)", True, "textbook"),
    ("BI-RADS 2013", True, "textbook"),
    ("交換考 2016 官方詳解 p.12", True, "official_pdf"),
    ("見 [[2011 AJNR Neuroradiology of Cholesteatomas]]", True, "vault_note"),
    # 反例：應被擋
    ("", False, "llm_suggested"),
    ("   ", False, "llm_suggested"),
    ("Journal of Imaginary Radiology 2020", False, "llm_suggested"),
    ("某教科書第三章", False, "llm_suggested"),
    ("Radiology", False, "llm_suggested"),  # 無年份不過關
]


def _run_selftest() -> int:
    failed = 0
    for ref, want_pass, want_src in _SELFTEST_CASES:
        got_pass = passes_gate(ref)
        got_src = best_source(ref)
        ok = (got_pass == want_pass) and (got_src == want_src)
        if not ok:
            failed += 1
        mark = "OK " if ok else "FAIL"
        print(f"[{mark}] ref={ref!r:55} pass={got_pass}(want {want_pass}) src={got_src}(want {want_src})")
    print(f"\n{len(_SELFTEST_CASES) - failed}/{len(_SELFTEST_CASES)} 通過")
    return 1 if failed else 0


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] == "--selftest":
        sys.exit(_run_selftest())
    ref = " ".join(args)
    sources = classify_reference(ref)
    print(f"reference : {ref!r}")
    print(f"過閘      : {passes_gate(ref)}")
    print(f"來源層級  : {sources or ['(無，llm_suggested)']}")
    print(f"最佳來源  : {best_source(ref)}")


if __name__ == "__main__":
    main()
