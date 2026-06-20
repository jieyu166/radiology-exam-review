#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""上傳圖片到 R2 圖床（img-hosting worker），回傳公開 URL 或 markdown。

圖片改走 R2、不再進 git：用本工具上傳後，把回傳的 URL（或 markdown）貼進
data/{year}.json 的 questionText/explanation，網站 js/format.js 已允許該 host。

設定來源（依序，先有先用）：
  1. 環境變數 WORKER_URL / API_KEY
  2. IMG_HOSTING_ENV 指向的 .env 檔
  3. 預設 img-hosting skill 的 .env（見 DEFAULT_ENV）
※ API_KEY 只在執行時讀取使用,不寫進本 repo。

用法：
  python scripts/r2_upload.py 圖.png [圖2.png ...]      # 每行印 URL
  python scripts/r2_upload.py --md 圖.png               # 印 ![stem](url)
  python scripts/r2_upload.py --html 圖.png --alt "說明" # 印 <img ...>
"""
from __future__ import annotations
import sys, os, json, urllib.request, urllib.error, pathlib

DEFAULT_ENV = r"C:\Users\jai16\Downloads\img-hosting\img-hosting\.env"

def load_cfg() -> tuple[str, str]:
    url = os.environ.get("WORKER_URL"); api = os.environ.get("API_KEY")
    envf = os.environ.get("IMG_HOSTING_ENV") or DEFAULT_ENV
    if (not url or not api) and os.path.exists(envf):
        for line in open(envf, encoding="utf-8"):
            line = line.strip()
            if line.startswith("WORKER_URL=") and not url: url = line.split("=", 1)[1].strip().strip('"')
            if line.startswith("API_KEY=")    and not api: api = line.split("=", 1)[1].strip().strip('"')
    if not url or not api:
        sys.exit("缺 WORKER_URL / API_KEY（設環境變數或讓 IMG_HOSTING_ENV 指向 img-hosting 的 .env）")
    return url.rstrip("/"), api

def upload(path: str, url: str, api: str) -> dict:
    data = pathlib.Path(path).read_bytes()
    req = urllib.request.Request(
        url + "/3/image", data=data, method="POST",
        headers={
            "Authorization": "Bearer " + api,
            "Content-Type": "application/octet-stream",
            "User-Agent": "curl/8.0 img-hosting-uploader",  # 預設 Python-urllib UA 會被 Cloudflare 擋成 bot
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            j = json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:400]
        raise SystemExit(f"上傳失敗 HTTP {e.code}: {body}")
    if not j.get("success"):
        raise RuntimeError(f"上傳失敗: {j}")
    return j["data"]

def main() -> None:
    args = sys.argv[1:]
    fmt = "url"; alt = None; files = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--md": fmt = "md"
        elif a == "--html": fmt = "html"
        elif a == "--json": fmt = "json"
        elif a == "--alt": i += 1; alt = args[i]
        else: files.append(a)
        i += 1
    if not files: sys.exit(__doc__)
    url, api = load_cfg()
    for f in files:
        d = upload(f, url, api)
        link = d["link"]; a = alt or pathlib.Path(f).stem
        if fmt == "md":     print(f"![{a}]({link})")
        elif fmt == "html": print(f'<img src="{link}" alt="{a}" loading="lazy" />')
        elif fmt == "json": print(json.dumps(d, ensure_ascii=False))
        else:               print(link)
        # deletehash 印到 stderr 方便日後刪除（不污染 stdout 的可貼用輸出）
        print(f"  (deletehash={d.get('deletehash')})", file=sys.stderr)

if __name__ == "__main__":
    main()
