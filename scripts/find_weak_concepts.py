#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_weak_concepts.py — 找出「弱來源」概念檔，供 /radiology-topic-research 五來源補強。

定義：參考來源段（「### 參考來源」之後）只含「官方20xx詳解／題目所引」這類弱引用，
且【完全沒有】Tier1／全文已讀／實際查證／DOI／PMC／Radiopaedia 等任何一手查證標記。
補強完成（掛上 Tier1/DOI 等）後會自動從清單消失，故本腳本本身即為進度追蹤器。

用法：
  python scripts/find_weak_concepts.py            # 印出剩餘數量與清單（依 git 新增日期，新→舊）
  python scripts/find_weak_concepts.py --count     # 只印數量
  python scripts/find_weak_concepts.py -n 20       # 只印前 20 個
"""
import glob, re, os, sys, subprocess

WEAK = re.compile(r'官方\s*20\d\d\s*詳解|題目所引')
# 任一存在即視為「已有一手/查證來源」，不列入弱來源
TIER = re.compile(r'Tier ?1|Tier ?2|全文已讀|實際查證|開放全文|PMC\d|accessed 20|doi|10\.1148|10\.2214|radiopaedia|STATdx|ClinicalKey', re.I)

def weak_files():
    out = []
    for f in glob.glob('vault/concepts/*.md'):
        t = open(f, encoding='utf-8').read()
        idx = t.find('參考來源')
        ref = t[idx:] if idx >= 0 else t
        if WEAK.search(ref) and not TIER.search(ref):
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
    files = weak_files()
    if '--count' in sys.argv:
        print(len(files)); return
    limit = None
    if '-n' in sys.argv:
        limit = int(sys.argv[sys.argv.index('-n') + 1])
    rows = sorted(((add_date(f), os.path.basename(f)) for f in files), reverse=True)
    print(f'弱來源概念檔剩餘：{len(rows)}')
    for d, n in (rows[:limit] if limit else rows):
        print(d, n)

if __name__ == '__main__':
    main()
