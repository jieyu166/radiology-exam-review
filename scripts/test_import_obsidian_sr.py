#!/usr/bin/env python3
"""Smoke tests for scripts/import_obsidian_sr.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("import_obsidian_sr.py")
spec = importlib.util.spec_from_file_location("import_obsidian_sr", SCRIPT_PATH)
assert spec and spec.loader
importer = importlib.util.module_from_spec(spec)
sys.modules["import_obsidian_sr"] = importer
spec.loader.exec_module(importer)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_smoke() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        vault = root / "Radiology"
        target = root / "radiology-exam-review"
        target.mkdir()
        write_bytes(vault / "attachments" / "figure.png", b"fake-png")
        write_bytes(vault / "assets" / "brain.svg", b"<svg></svg>")
        write_bytes(vault / "dup-a" / "ambig.png", b"a")
        write_bytes(vault / "dup-b" / "ambig.png", b"b")

        multi_year = vault / "2. Areas" / "NR" / "sellar.md"
        write(
            multi_year,
            """---
subspecialty: \u591a\u79d1\u5225
---

#2018\u4ea4\u63db #2020\u4ea4\u63db #NR\u8003 Which finding is true? ![[assets/brain.svg|Brain SVG]]
```
A. Alpha
B. Beta
C. Gamma
D. Delta
```
??
Ans: D.
Delta is correct.
![[figure.png]]
![[missing.png]]
![[ambig.png]]
![[note.md]]
<!--SR:!2026-01-01,1,250-->
""",
        )

        numeric = vault / "abd.md"
        write(
            numeric,
            """---
subspecialty: ABD
---

> 1. #2019\u4ea4\u63db #\u8a18 Which sequence is best?
> 1. First
> 2. Second
> 3. Third
> 4. Fourth
> ??
> Ans: B
> Numeric options are normalized.
""",
        )

        bullet = vault / "unknown.md"
        write(
            bullet,
            """#2021\u4ea4\u63db Pick the false statement.
- choice one
- choice two
- choice three
??
Ans: C
No YAML should become Unknown.
""",
        )

        before = {path: sha256(path) for path in vault.rglob("*") if path.is_file()}

        dry_report = target / "dry-report.json"
        dry_code = importer.main(["--vault", str(vault), "--target", str(target), "--dry-run", "--report", str(dry_report)])
        assert_true(dry_code == 0, "dry-run should succeed")
        assert_true(not (target / "data" / "index.json").exists(), "dry-run must not write index")
        dry_report_data = load(dry_report)
        assert_true(len(dry_report_data["pendingImageCopies"]) == 2, "dry-run should report pending image copies")
        assert_true(len(dry_report_data["missingImageEmbeds"]) == 1, "dry-run should report missing image embeds")
        assert_true(len(dry_report_data["ambiguousImageEmbeds"]) == 1, "dry-run should report ambiguous image embeds")
        assert_true(len(dry_report_data["unsupportedEmbeds"]) == 1, "dry-run should report unsupported embeds")

        real_report = target / "real-report.json"
        code = importer.main(["--vault", str(vault), "--target", str(target), "--report", str(real_report)])
        assert_true(code == 0, "real import should succeed")
        code = importer.main(["--vault", str(vault), "--target", str(target)])
        assert_true(code == 0, "second keep-mode import should succeed without duplicating")

        after = {path: sha256(path) for path in vault.rglob("*") if path.is_file()}
        assert_true(before == after, "source vault hashes must remain unchanged")

        data_2018 = load(target / "data" / "2018.json")
        assert_true(data_2018["totalQuestions"] == 1, "keep mode should not duplicate existing imported questions")
        first = data_2018["questions"][0]
        assert_true(first["years"] == [2018, 2020], "multi-year tags should be preserved")
        assert_true(first["subspecialty"] == "NR", "#NR exam tag should override YAML")
        assert_true(first["subspecialty_confidence"] == "manual", "manual specialty confidence expected")
        assert_true(first["correctAnswer"] == "D", "answer should parse from Ans line")
        assert_true(len(first["options"]) == 4 and first["options"][0]["letter"] == "A", "fenced letter options should parse")
        assert_true("source" not in first and "sourceLine" not in first, "question JSON should match public schema")
        assert_true("![Brain SVG](data/images/obsidian/brain-" in first["questionText"], "exact path image embed should convert in question text")
        assert_true("![figure](data/images/obsidian/figure-" in first["explanation"], "basename image embed should convert in explanation")
        assert_true("![[missing.png]]" in first["explanation"], "missing embeds should remain unchanged")
        assert_true("![[ambig.png]]" in first["explanation"], "ambiguous embeds should remain unchanged")
        assert_true("![[note.md]]" in first["explanation"], "unsupported embeds should remain unchanged")
        assert_true(first["images"] == [], "inline converted images should not be duplicated into images array")
        for link in importer.OBSIDIAN_EMBED_RE.findall(first["questionText"] + first["explanation"]):
            assert_true(link in {"missing.png", "ambig.png", "note.md"}, "only unresolved embeds should remain")
        real_report_data = load(real_report)
        assert_true(len(real_report_data["copiedImages"]) == 2, "real import should copy converted images")
        for copied in real_report_data["copiedImages"]:
            assert_true((target / copied["target"]).exists(), "copied image target should exist")

        data_2019 = load(target / "data" / "2019.json")
        assert_true(data_2019["questions"][0]["questionText"] == "Which sequence is best?", "leading numbering and tags should be removed")
        assert_true(data_2019["questions"][0]["options"][1]["letter"] == "B", "numeric options should map to A-E")
        assert_true(data_2019["questions"][0]["subspecialty"] == "ABD", "YAML subspecialty should be used")

        data_2021 = load(target / "data" / "2021.json")
        assert_true(data_2021["questions"][0]["options"][2]["letter"] == "C", "bullet options should map to A-E")
        assert_true(data_2021["questions"][0]["subspecialty"] == "Unknown", "missing YAML should become Unknown")

        index = load(target / "data" / "index.json")
        assert_true([entry["year"] for entry in index["years"]] == [2021, 2019, 2018], "index years should sort descending")


if __name__ == "__main__":
    run_smoke()
    print("import_obsidian_sr smoke tests passed")
