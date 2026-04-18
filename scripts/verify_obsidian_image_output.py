#!/usr/bin/env python3
"""Verify imported Obsidian image links point to repository files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


IMAGE_LINK_RE = re.compile(r"!\[[^\]]*\]\((data/images/obsidian/[^)]+)\)")
OBSIDIAN_EMBED_RE = re.compile(r"!\[\[[^\]]+\]\]")


def iter_question_texts(data_dir: Path):
    for path in sorted(data_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "questions" not in data:
            continue
        for question in data["questions"]:
            yield path, question.get("questionText", "")
            yield path, question.get("reference", "")
            yield path, question.get("explanation", "")
            for option in question.get("options", []):
                yield path, option.get("text", "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path)
    args = parser.parse_args()

    target = args.target.resolve()
    data_dir = target / "data"
    json_files = sorted(data_dir.glob("*.json"))
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))

    links: list[str] = []
    unresolved: list[str] = []
    for _, text in iter_question_texts(data_dir):
        links.extend(IMAGE_LINK_RE.findall(text or ""))
        unresolved.extend(OBSIDIAN_EMBED_RE.findall(text or ""))

    missing = [link for link in links if not (target / link).exists()]
    image_dir = data_dir / "images" / "obsidian"
    image_files = sorted(image_dir.glob("*")) if image_dir.exists() else []

    print(f"json_files {len(json_files)}")
    print(f"inline_links {len(links)}")
    print(f"missing_link_files {len(missing)}")
    print(f"remaining_obsidian_embeds {len(unresolved)}")
    print(f"image_files {len(image_files)}")
    if missing:
        print("First missing links:")
        for link in missing[:10]:
            print(f"  {link}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
