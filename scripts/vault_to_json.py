#!/usr/bin/env python3
"""反向同步：把 vault 題卡 .md 中「醫師手動設定的結構性欄位」回寫 data/{year}.json。

設計原則（與 json_to_vault.py 的 genHash 防呆相輔）：
- **題卡 .md 是醫師審閱/標記的所在**；本腳本把 .md frontmatter 的結構性欄位（預設 `checked`，
  可選 `subspecialty` / `correctAnswer` / `concepts`）回寫 json，讓網頁編輯器 / Google Sheets 同步。
- **不回寫自由文字**（explanation、題幹加粗、`#記` 等複習標籤）——那些以 .md 為準（受 genHash 保護），
  避免脆弱的反向解析。
- 預設 dry-run 只報告差異；加 --write 才實際寫入 json。

用法：
  python scripts/vault_to_json.py 2016                 # 只報告 .md 與 json 的欄位差異
  python scripts/vault_to_json.py 2016 --write         # 回寫 checked 至 json
  python scripts/vault_to_json.py 2016 --write --fields checked,subspecialty
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
DATA_DIR = REPO / "data"
VAULT_DIR = REPO / "vault"

_FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def _parse_frontmatter(text: str) -> dict:
    """極簡 YAML frontmatter 解析（僅支援 scalar 與 [a, b] 行內陣列，足夠題卡所需）。"""
    m = _FM_RE.search(text)
    if not m:
        return {}
    fm: dict = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line or line.startswith(" "):
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            fm[key] = [x.strip() for x in val[1:-1].split(",") if x.strip()]
        elif val.lower() in ("true", "false"):
            fm[key] = (val.lower() == "true")
        elif val:
            fm[key] = val
    return fm


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("year")
    ap.add_argument("--write", action="store_true", help="實際回寫 json（預設只報告）")
    ap.add_argument("--fields", default="checked",
                    help="要回寫的欄位（逗號分隔；預設 checked）。可選 checked,subspecialty,correctAnswer,concepts")
    args = ap.parse_args()
    fields = [f.strip() for f in args.fields.split(",") if f.strip()]

    json_path = DATA_DIR / f"{args.year}.json"
    if not json_path.exists():
        print(f"Error: {json_path} 不存在。", file=sys.stderr)
        sys.exit(1)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    jq = {q.get("id"): q for q in data.get("questions", [])}

    qdir = VAULT_DIR / "questions" / str(args.year)
    changes: list[tuple[str, str, object, object]] = []
    for md in sorted(qdir.glob("*.md")):
        fm = _parse_frontmatter(md.read_text(encoding="utf-8"))
        qid = fm.get("id")
        if qid not in jq:
            continue
        for fld in fields:
            if fld not in fm:
                continue
            new = fm[fld]
            old = jq[qid].get(fld)
            # 正規化 checked 為 bool
            if fld == "checked":
                old = bool(old)
                new = bool(new)
            if new != old:
                changes.append((qid, fld, old, new))
                if args.write:
                    jq[qid][fld] = new

    for qid, fld, old, new in changes:
        print(f"  {qid}: {fld}  {old!r} -> {new!r}")
    print(f"[{args.year}] 欄位差異 {len(changes)} 筆"
          + ("（已回寫 json）" if args.write else "（dry-run，加 --write 才寫入）"))

    if args.write and changes:
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
