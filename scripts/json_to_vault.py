#!/usr/bin/env python3
"""把 data/{year}.json 轉成 Obsidian Spaced-Repetition vault。

產出：
  vault/questions/{year}/{id}.md   一題一檔（SR 卡片）
  vault/concepts/{concept-id}.md   一概念一檔（Dataview 匯整相關題）
  vault/.obsidian/...              SR 外掛 flashcard tag 設為 #交換

單一內容真實來源為 data/{year}.json；本腳本只負責產生 vault。冪等：預設不覆寫既有檔
（保護使用者編輯與 SR 排程）；--force 覆寫但保留檔內 <!--SR: 排程註解行。

用法：
  python scripts/json_to_vault.py 2016
  python scripts/json_to_vault.py 2016 --force
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
DATA_DIR = REPO / "data"
VAULT_DIR = REPO / "vault"

# 重用稽核器的「逐選項詳解」判定，避免重造
sys.path.insert(0, str(Path(__file__).parent))
import audit_questions  # noqa: E402

FLASHCARD_TAG = "#交換"


# ── 題目卡片 ───────────────────────────────────────────────────────────────────

def render_card(q: dict) -> str:
    """把一題渲染成 SR 卡片 markdown。"""
    concepts = q.get("concepts") or []
    sub = q.get("subspecialty") or "Unknown"
    year = q.get("year", "")

    frontmatter = [
        "---",
        f"id: {q.get('id', '')}",
        f"year: {year}",
        f"subspecialty: {sub}",
        f"correctAnswer: {q.get('correctAnswer', '')}",
        f"concepts: [{', '.join(concepts)}]",
        f"checked: {str(bool(q.get('checked'))).lower()}",
        "---",
    ]
    tag_line = f"{FLASHCARD_TAG} #{year}交換 #{sub}"

    # 正面：題幹 + 選項
    front = [q.get("questionText", "").strip()]
    for opt in q.get("options", []):
        front.append(f"({opt['letter']}) {opt.get('text', '').strip()}")

    # 背面：答案 + 詳解（不足則 callout 佔位，保留既有殘缺詳解）
    explanation = (q.get("explanation") or "").strip()
    sufficient = bool(explanation) and audit_questions._has_per_option(explanation)
    back = [f"**Ans: {q.get('correctAnswer', '')}**"]
    if sufficient:
        back.append(explanation)
    else:
        callout = "> [!todo] 待補詳解"
        if explanation:
            callout += "\n" + "\n".join(f"> {ln}" for ln in explanation.splitlines())
        back.append(callout)

    body = "\n".join(front) + "\n??\n" + "\n".join(back)
    if concepts:
        body += "\n\n概念：" + " ".join(f"[[{c}]]" for c in concepts)

    return "\n".join(frontmatter) + "\n" + tag_line + "\n\n" + body + "\n"


# ── 概念筆記 ───────────────────────────────────────────────────────────────────

_DESC_FIELDS = [
    ("definition", "定義"),
    ("imagingFindings", "影像特徵"),
    ("differentialDiagnosis", "鑑別診斷"),
    ("keyPoints", "重點"),
    ("management", "處置"),
]


def render_concept(cid: str, cdata: dict) -> str:
    """渲染概念筆記；cdata 為 concepts.json 中的條目（缺則 {}）。"""
    name = (cdata.get("name") or cid).strip()
    sub = cdata.get("subspecialty", "")

    frontmatter = ["---", f"concept: {cid}", f"name: {name}", f"subspecialty: {sub}", "---"]
    lines = [f"# {name}", ""]

    has_desc = False
    for key, label in _DESC_FIELDS:
        val = cdata.get(key)
        if not val:
            continue
        lines.append(f"## {label}")
        if isinstance(val, list):
            # list 欄位（如 differentialDiagnosis / keyPoints）→ 逐項 bullet，
            # 避免被 str() 渲染成 Python repr（['...', '...']）
            lines.extend(f"- {str(item).strip()}" for item in val if str(item).strip())
        elif str(val).strip():
            lines.append(str(val).strip())
        lines.append("")
        has_desc = True
    if not has_desc:
        lines.append("（概念說明待補）")
        lines.append("")

    lines.append("## 相關交換考題")
    lines.append("```dataview")
    lines.append(f'list from {FLASHCARD_TAG} where contains(concepts, "{cid}")')
    lines.append("```")

    return "\n".join(frontmatter) + "\n" + "\n".join(lines) + "\n"


# ── 寫檔（冪等 + SR 排程保留）──────────────────────────────────────────────────

def write_file(path: Path, content: str, force: bool) -> str:
    """寫入檔案。回傳 'write' / 'skip'。--force 覆寫時保留 <!--SR: 行。"""
    if path.exists() and not force:
        return "skip"
    if path.exists() and force:
        old = path.read_text(encoding="utf-8")
        sr_lines = [ln for ln in old.splitlines() if ln.lstrip().startswith("<!--SR:")]
        if sr_lines:
            content = content.rstrip("\n") + "\n" + "\n".join(sr_lines) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return "write"


# ── SR 外掛設定 ────────────────────────────────────────────────────────────────

def write_obsidian_config(force: bool) -> None:
    """寫最小 .obsidian 設定：SR flashcard tag = #交換，並標記啟用 SR/Dataview。

    僅寫設定，不安裝外掛（外掛檔需使用者自行安裝）。既有設定預設不覆寫。
    """
    sr_dir = VAULT_DIR / ".obsidian" / "plugins" / "obsidian-spaced-repetition"
    sr_data = sr_dir / "data.json"
    if not sr_data.exists() or force:
        sr_dir.mkdir(parents=True, exist_ok=True)
        sr_data.write_text(
            json.dumps({"flashcardTags": [FLASHCARD_TAG]}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    community = VAULT_DIR / ".obsidian" / "community-plugins.json"
    if not community.exists() or force:
        community.parent.mkdir(parents=True, exist_ok=True)
        community.write_text(
            json.dumps(["obsidian-spaced-repetition", "dataview"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


# ── 主流程 ─────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("year")
    ap.add_argument("--force", action="store_true", help="覆寫既有檔（保留 <!--SR: 行）")
    args = ap.parse_args()

    json_path = DATA_DIR / f"{args.year}.json"
    if not json_path.exists():
        print(f"Error: {json_path} 不存在。", file=sys.stderr)
        sys.exit(1)
    questions = json.loads(json_path.read_text(encoding="utf-8")).get("questions", [])

    concepts_all = {}
    cpath = DATA_DIR / "concepts.json"
    if cpath.exists():
        concepts_all = json.loads(cpath.read_text(encoding="utf-8")).get("concepts", {})

    # 1) 題目卡片
    q_written = q_skipped = 0
    referenced: set[str] = set()
    for q in questions:
        out = VAULT_DIR / "questions" / str(args.year) / f"{q['id']}.md"
        if write_file(out, render_card(q), args.force) == "write":
            q_written += 1
        else:
            q_skipped += 1
        referenced.update(q.get("concepts") or [])

    # 2) 概念筆記（只為被引用到的 concept）
    c_written = c_skipped = 0
    for cid in sorted(referenced):
        out = VAULT_DIR / "concepts" / f"{cid}.md"
        if write_file(out, render_concept(cid, concepts_all.get(cid, {})), args.force) == "write":
            c_written += 1
        else:
            c_skipped += 1

    # 3) SR 外掛設定
    write_obsidian_config(args.force)

    print(f"[{args.year}] 題目卡片：寫入 {q_written}、略過 {q_skipped}（共 {len(questions)}）")
    print(f"        概念筆記：寫入 {c_written}、略過 {c_skipped}（被引用 {len(referenced)}）")
    print(f"        SR flashcard tag = {FLASHCARD_TAG} → {VAULT_DIR / '.obsidian'}")


if __name__ == "__main__":
    main()
