#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_shallow_concepts.py — 找出「淺層」概念檔（品質未達標，需 /radiology-topic-research 深補）。

弱來源偵測器（find_weak_concepts.py）只檢查「有沒有掛到任一 tier 標記」，
但實務發現很多檔只掛了 Radiopaedia + 官方詳解就過關，深度不足（見 brain-metastasis-mri 反例）。
本偵測器定義「淺層」＝參考來源段【沒有任何一手期刊/STATdx/ClinicalKey/PMC 強來源】，
即來源實質只有 Radiopaedia（rID / 10.53347）與/或 官方詳解／題目所引。

強來源（任一存在即「非淺層」）：
  STATdx、ClinicalKey、RadioGraphics、AJR、Radiology(期刊)、PMC 全文、
  或任一非 Radiopaedia(10.53347) 的期刊 DOI。

用法：
  python scripts/find_shallow_concepts.py            # 數量 + 清單（依 git 新增日期新→舊）
  python scripts/find_shallow_concepts.py --count
  python scripts/find_shallow_concepts.py -n 20
  python scripts/find_shallow_concepts.py --breast    # 只列 subspecialty 含 Breast/BR 的淺層檔
"""
import glob, re, os, sys, subprocess

WEAK = re.compile(r'官方\s*20\d\d\s*詳解|題目所引')
RADIOP = re.compile(r'radiopaedia|rID[- ]?\d|10\.53347', re.I)
# 強來源：真正一手期刊/資料庫
STATDX = re.compile(r'STATdx|ClinicalKey|RadioGraphics|\bAJR\b|Radiology 1|Radiology 2|Radiol\.', re.I)
PMC = re.compile(r'PMC\d')
# 任一非 radiopaedia 的期刊 DOI（10.53347 為 Radiopaedia，需排除）
DOI = re.compile(r'10\.(?!53347)\d{3,}\S+')
# 權威一手法規/規範來源（法規、對比劑、輻防題之正確 Tier-1，非影像期刊但同屬強來源）
REG = re.compile(r'FDA|DailyMed|仿單|ACR Manual|ACR Appropriateness|核安會|全國法規資料庫|游離輻射防護|erss\.nusc|law\.moj|原能會|\bICRP\b|\bNCRP\b|\bIAEA\b', re.I)

def analyze(f):
    t = open(f, encoding='utf-8').read()
    idx = t.find('參考來源')
    ref = t[idx:] if idx >= 0 else t
    strong = bool(STATDX.search(ref) or PMC.search(ref) or DOI.search(ref) or REG.search(ref))
    has_weak = bool(WEAK.search(ref))
    has_radiop = bool(RADIOP.search(ref))
    # 淺層：沒有強來源，且參考來源實質只靠 radiopaedia / 官方詳解
    shallow = (not strong) and (has_weak or has_radiop)
    return shallow, strong

def subspec(f):
    t = open(f, encoding='utf-8').read()
    m = re.search(r'subspecialty:\s*(.+)', t)
    head = t[:t.find('---', 3)] if '---' in t else t
    return head

def is_breast(f):
    head = subspec(f)
    return bool(re.search(r'subspecialty:[^\n]*\b(Breast|BR)\b', head) or
                re.search(r'-\s*(Breast|BR)\b', head))

def shallow_files():
    out = []
    for f in glob.glob('vault/concepts/*.md'):
        shallow, _ = analyze(f)
        if shallow:
            out.append(f.replace('\\', '/'))
    return out

def add_date(f):
    try:
        return subprocess.check_output(
            ['git', 'log', '--diff-filter=A', '--format=%ad', '--date=short', '-1', '--', f],
            text=True).strip() or '?'
    except Exception:
        return '?'

def main():
    files = shallow_files()
    if '--breast' in sys.argv:
        files = [f for f in files if is_breast(f)]
    if '--count' in sys.argv:
        print(len(files)); return
    limit = None
    if '-n' in sys.argv:
        limit = int(sys.argv[sys.argv.index('-n') + 1])
    rows = sorted(((add_date(f), os.path.basename(f)) for f in files), reverse=True)
    print(f'淺層概念檔剩餘：{len(rows)}')
    for d, n in (rows[:limit] if limit else rows):
        print(d, n)

if __name__ == '__main__':
    main()
