# -*- coding: utf-8 -*-
import os, re, io, json, glob, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

IMG_RE = re.compile(r'!\[[^\]]*\]\(data/images/obsidian/[^)]*\)')
IMGNAME_RE = re.compile(r'data/images/obsidian/([^)\]\s]+)')

# 1) 掃 json，建立 題目→圖片 對照
mapping = []   # (id, year, [imgs], stem)
for p in sorted(glob.glob('data/20*.json')):
    d = json.load(open(p, encoding='utf-8'))
    for q in d['questions']:
        ex = q.get('explanation') or ''
        imgs = IMGNAME_RE.findall(ex)
        if imgs:
            mapping.append((q['id'], q.get('year',''), imgs, (q.get('questionText','') or '').strip()[:60]))

# 2) 寫對照清單檔
out = io.open('data/images/_舊詳解圖清單.md', 'w', encoding='utf-8', newline='')
out.write('# 舊詳解圖 → 題目對照清單\n\n')
out.write(f'> 這些題的詳解原本嵌有圖（來自舊匯入）。圖已全部刪除、引用已從 json/卡片移除。\n')
out.write(f'> 若需要,請在這些題重新加入自己的圖。共 {len(mapping)} 題。\n\n')
out.write('| 題號 | 圖片數 | 題幹 |\n|---|---|---|\n')
for qid, y, imgs, stem in mapping:
    stem_clean = stem.replace('|','/').replace('\n',' ')
    out.write(f'| {qid} | {len(imgs)} | {stem_clean} |\n')
out.close()
print(f'對照清單：{len(mapping)} 題有舊詳解圖')

# 3) 從 json explanation 移除圖片 markdown
for p in sorted(glob.glob('data/20*.json')):
    d = json.load(open(p, encoding='utf-8')); changed=0
    for q in d['questions']:
        ex = q.get('explanation')
        if ex and IMG_RE.search(ex):
            new = IMG_RE.sub('', ex)
            new = re.sub(r'[ \t]+\n', '\n', new)        # 行尾空白
            new = re.sub(r'\n{3,}', '\n\n', new).strip() # 多重空行
            q['explanation'] = new; changed+=1
    if changed:
        json.dump(d, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=2); open(p,'a',encoding='utf-8').write('\n')
        print(os.path.basename(p),'移除圖片引用題數:',changed)

# 4) 從卡片 .md 移除圖片 markdown（含受保護卡片，避免破圖）
card_changed=0
for p in glob.glob('vault/questions/**/*.md', recursive=True):
    t = io.open(p, encoding='utf-8').read()
    if IMG_RE.search(t):
        new = IMG_RE.sub('', t)
        new = re.sub(r'[ \t]+\n','\n',new); new=re.sub(r'\n{4,}','\n\n\n',new)
        io.open(p,'w',encoding='utf-8',newline='').write(new); card_changed+=1
print('卡片移除圖片引用檔數:',card_changed)

# 5) 刪除所有 data/images/obsidian/ 檔
dirp='data/images/obsidian'
n=len(os.listdir(dirp))
shutil.rmtree(dirp); os.makedirs(dirp, exist_ok=True)
# 放個 .gitkeep 保留資料夾
io.open(os.path.join(dirp,'.gitkeep'),'w').write('')
print(f'已刪除 data/images/obsidian/ 全部 {n} 張圖（保留空資料夾）')
