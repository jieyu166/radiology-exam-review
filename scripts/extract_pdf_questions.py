#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從官方詳解 PDF（pdftotext -layout 文字）擷取結構化題目。

詳解 PDF 每題結構（已驗證）：
    [縮排][答案字母]          ← 單獨一行、有縮排（^L 換頁後亦可）
    [縮排][題幹 ... ?]
    [縮排](A) ... (B) ... (C) ... (D) ...
    [縮排][參考文獻：作者引用]
    [頂格]A. Correct/Incorrect. ...   ← 逐選項詳解，頂格起
    [頂格]B. ... / C. ... / D. ...

輸出：scripts/_pdf_questions_{year}.json，每題 {answer, stem, options, references, explanation}。

用法：python scripts/extract_pdf_questions.py 2016
"""
from __future__ import annotations
import json, re, sys, subprocess, os, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_text(year: str) -> str:
    cached = os.path.join(REPO, 'scripts', f'_jieda_{year}.txt')
    if os.path.exists(cached):
        return open(cached, encoding='utf-8', errors='ignore').read()
    pdfs = glob.glob(os.path.join(REPO, 'vault', 'references', '交換考', f'*{year}*詳解*.pdf'))
    if not pdfs:
        sys.exit(f'找不到 {year} 詳解 PDF')
    subprocess.run(['pdftotext', '-layout', pdfs[0], cached], check=False)
    return open(cached, encoding='utf-8', errors='ignore').read()


ANS_LINE = re.compile(r'^[ \t\x0c]+([A-E])[ \t]*$')   # 縮排、單獨答案字母
EXPL_LINE = re.compile(r'^([A-E])\.\s')                # 頂格逐選項詳解


def extract(year: str) -> list[dict]:
    raw = get_text(year)
    lines = raw.replace('\x0c', '\n').split('\n')

    # 1) 找所有「答案字母行」當題目分界
    starts = []
    for i, ln in enumerate(lines):
        m = ANS_LINE.match(ln)
        if m:
            starts.append((i, m.group(1)))
    starts.append((len(lines), None))

    out = []
    for k in range(len(starts) - 1):
        i0, ans = starts[k]
        i1 = starts[k + 1][0]
        block = lines[i0 + 1:i1]
        body = '\n'.join(block)
        flat = re.sub(r'[ \t]*\n[ \t]*', ' ', body)   # 軟換行接成空白
        flat = re.sub(r'\s+', ' ', flat).strip()

        # 2) 選項：(A)..(B)..(C)..(D)..[(E)..]
        om = re.search(r'\(A\)\s*(.*?)\s*\(B\)\s*(.*?)\s*\(C\)\s*(.*?)\s*\(D\)\s*(.*?)(?:\(E\)\s*(.*?))?$', flat)
        if not om:
            continue
        a, b, c, dd, ee = om.groups()
        stem = flat[:om.start()].strip()

        # 3) 把參考/詳解從 (D)/(E) 後切出（頂格 'X. Correct/Incorrect'）
        rest = ''
        for j in range(i0 + 1, i1):
            if EXPL_LINE.match(lines[j]):
                rest = '\n'.join(lines[j:i1])
                break
        expl = re.sub(r'[ \t]*\n[ \t]*\n?', ' ', rest).strip()
        # 末選項 D/E 常黏到參考；截到第一個作者引用/期刊樣式前
        def clean_opt(s):
            s = re.split(r'\s{2,}|(?:[A-Z][a-z]+ [A-Z]{1,3},)|Radiographics|Radiology\.|AJR|et al\.|edition|Philadelphia|Lippincott|Saunders|Amirsys|Thieme|doi:|http', s)[0]
            return s.strip().rstrip('.').strip()
        opts = [('A', a), ('B', b), ('C', c), ('D', dd)]
        if ee:
            opts.append(('E', ee))
        opts = [{'letter': L, 'text': clean_opt(t)} for L, t in opts if t and t.strip()]

        out.append({
            'answer': ans,
            'stem': stem,
            'options': opts,
            'explanation': expl[:3000],
        })
    return out


def main():
    year = sys.argv[1] if len(sys.argv) > 1 else '2016'
    qs = extract(year)
    outp = os.path.join(REPO, 'scripts', f'_pdf_questions_{year}.json')
    json.dump(qs, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'擷取 {len(qs)} 題 → {outp}')
    # 預覽前 2 題
    for q in qs[:2]:
        print('---', 'Ans:', q['answer'])
        print('STEM:', q['stem'][:90])
        for o in q['options']:
            print('  ', o['letter'], ':', o['text'][:60])
        print('EXPL:', q['explanation'][:120])


if __name__ == '__main__':
    main()
