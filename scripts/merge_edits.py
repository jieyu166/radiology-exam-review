#!/usr/bin/env python3
"""合併醫師匯出的 patch JSON 到 data/2016.json 和 data/concepts.json。

用法：
  python scripts/merge_edits.py <patch.json>
  python scripts/merge_edits.py data/rex-edits-2026-04-13.json

patch.json 格式（由網頁「匯出 JSON」產出）：
{
  "rex_edits_year_2016": {
    "2016-001": { "subspecialty": "ABD", "explanation": "...", "checked": true, ... },
    "2016-005": { ... }
  },
  "rex_edits_concepts": {
    "upj-obstruction": { "name": "...", ... }
  }
}
"""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def merge_year(year: str, patches: dict) -> int:
    """合併題目 patch 到 {year}.json，回傳更新題數。"""
    json_path = DATA_DIR / f"{year}.json"
    if not json_path.exists():
        print(f"  Warning: {json_path} 不存在，跳過")
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    questions = data.get("questions", [])
    q_map = {q["id"]: q for q in questions}

    for qid, patch in patches.items():
        if qid in q_map:
            q_map[qid].update(patch)
            updated += 1
        else:
            print(f"  Warning: {qid} 不在 {year}.json 中，跳過")

    data["questions"] = list(q_map.values())
    data["totalQuestions"] = len(data["questions"])

    with open(json_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return updated


def merge_concepts(patches: dict) -> int:
    """合併概念 patch 到 concepts.json，回傳更新概念數。"""
    json_path = DATA_DIR / "concepts.json"
    if not json_path.exists():
        print(f"  Warning: {json_path} 不存在，建立新檔")
        data = {"concepts": {}}
    else:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    concepts = data.get("concepts", {})
    updated = 0

    for cid, patch in patches.items():
        if cid in concepts:
            concepts[cid].update(patch)
        else:
            concepts[cid] = patch
        updated += 1

    data["concepts"] = concepts

    with open(json_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return updated


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/merge_edits.py <patch.json>")
        sys.exit(1)

    patch_path = Path(sys.argv[1])
    if not patch_path.exists():
        print(f"ERROR: 找不到 {patch_path}")
        sys.exit(1)

    with open(patch_path, "r", encoding="utf-8") as f:
        patches = json.load(f)

    print(f"Patch 檔案: {patch_path}")
    total_q = 0
    total_c = 0

    for key, value in patches.items():
        if key.startswith("rex_edits_year_"):
            year = key.replace("rex_edits_year_", "")
            n = merge_year(year, value)
            total_q += n
            print(f"  {year}.json: 更新 {n} 題")
        elif key == "rex_edits_concepts":
            n = merge_concepts(value)
            total_c += n
            print(f"  concepts.json: 更新 {n} 個概念")
        else:
            print(f"  跳過未知 key: {key}")

    print(f"\n完成！更新 {total_q} 題 + {total_c} 個概念")


if __name__ == "__main__":
    main()
