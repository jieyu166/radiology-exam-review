#!/usr/bin/env python3
"""One-time migration: copy legacy ``data/<year>.json`` question references into vault frontmatter.

Behaviour contract (openspec change ``remove-legacy-data-json``):

* Only the frontmatter block of a question card is touched. Exactly one
  ``reference: <value>`` line is inserted immediately before the closing ``---``.
  The card body bytes and the card's line-ending style are preserved.
* A card that already carries ``reference`` is never overwritten. Same value →
  ``alreadyPresent``; different value → listed under ``conflicts``.
* A legacy record whose id has no vault card, or whose card has no parseable
  frontmatter block, is listed under ``missingCards`` and the process exits 1.
* stdout prints one JSON object:
  ``{"updated": n, "alreadyPresent": n, "conflicts": [...], "missingCards": [...]}``.

This script is deleted together with ``data/`` once the migration has run.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from vault_site.compiler import FRONTMATTER_END, parse_frontmatter  # noqa: E402

YAML_SPECIAL_START = ('-', '?', ',', '[', ']', '{', '}', '#', '&', '*', '!', '|', '>', "'", '"', '%', '@', '`')


def yaml_scalar(value: str) -> str:
    """Render ``value`` so both the vault compiler and a strict YAML parser read it back verbatim."""
    needs_quote = (
        value != value.strip()
        or not value
        or value.startswith(YAML_SPECIAL_START)
        or ": " in value
        or " #" in value
        or value.endswith(":")
        or value.isdigit()
        or value.lower() in {"true", "false", "null", "~"}
    )
    if '"' in value:
        if "'" in value:
            raise ValueError("reference contains both quote styles; cannot round-trip through the vault compiler")
        return f"'{value}'"
    if needs_quote:
        return f'"{value}"'
    return value


def load_legacy_references(data_root: Path) -> dict[str, str]:
    refs: dict[str, str] = {}
    for path in sorted(data_root.glob("20*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        questions = payload["questions"] if isinstance(payload, dict) else payload
        for question in questions:
            value = question.get("reference")
            if isinstance(value, str) and value.strip():
                refs[str(question["id"])] = value.strip()
    return refs


def card_path(vault_root: Path, question_id: str) -> Path:
    return vault_root / "questions" / question_id[:4] / f"{question_id}.md"


def insert_reference(raw: bytes, value: str) -> bytes:
    """Return ``raw`` with a ``reference`` line inserted before the closing frontmatter fence."""
    text = raw.decode("utf-8")
    frontmatter, body_start = parse_frontmatter(text)
    if not frontmatter or body_start <= 1:
        raise ValueError("no parseable frontmatter block")
    lines = text.splitlines(keepends=True)
    fence_index = body_start - 2
    if fence_index >= len(lines) or lines[fence_index].rstrip("\r\n") != FRONTMATTER_END:
        raise ValueError("closing frontmatter fence not found where expected")
    previous = lines[fence_index - 1]
    eol = "\r\n" if previous.endswith("\r\n") else "\n"
    lines.insert(fence_index, f"reference: {yaml_scalar(value)}{eol}")
    return "".join(lines).encode("utf-8")


def migrate(data_root: Path, vault_root: Path, *, dry_run: bool) -> dict[str, Any]:
    refs = load_legacy_references(data_root)
    summary: dict[str, Any] = {"updated": 0, "alreadyPresent": 0, "conflicts": [], "missingCards": []}
    for question_id in sorted(refs):
        path = card_path(vault_root, question_id)
        if not path.is_file():
            summary["missingCards"].append(question_id)
            continue
        raw = path.read_bytes()
        frontmatter, body_start = parse_frontmatter(raw.decode("utf-8", errors="replace"))
        if not frontmatter or body_start <= 1:
            summary["missingCards"].append(question_id)
            continue
        existing = frontmatter.get("reference")
        if existing is not None:
            if str(existing).strip() == refs[question_id]:
                summary["alreadyPresent"] += 1
            else:
                summary["conflicts"].append(question_id)
            continue
        try:
            updated = insert_reference(raw, refs[question_id])
        except ValueError:
            summary["missingCards"].append(question_id)
            continue
        if not dry_run:
            path.write_bytes(updated)
        summary["updated"] += 1
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Migrate legacy question references into vault frontmatter")
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--vault", type=Path, default=Path("vault"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    summary = migrate(args.data.resolve(), args.vault.resolve(), dry_run=args.dry_run)
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if summary["missingCards"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
