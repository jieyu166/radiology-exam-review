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

        multi_year = vault / "2. Areas" / "NR" / "sellar.md"
        write(
            multi_year,
            """---
subspecialty: \u591a\u79d1\u5225
---

#2018\u4ea4\u63db #2020\u4ea4\u63db #NR\u8003 Which finding is true?
```
A. Alpha
B. Beta
C. Gamma
D. Delta
```
??
Ans: D.
Delta is correct.
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

        before = {path: sha256(path) for path in vault.rglob("*.md")}

        dry_code = importer.main(["--vault", str(vault), "--target", str(target), "--dry-run"])
        assert_true(dry_code == 0, "dry-run should succeed")
        assert_true(not (target / "data" / "index.json").exists(), "dry-run must not write index")

        code = importer.main(["--vault", str(vault), "--target", str(target)])
        assert_true(code == 0, "real import should succeed")
        code = importer.main(["--vault", str(vault), "--target", str(target)])
        assert_true(code == 0, "second keep-mode import should succeed without duplicating")

        after = {path: sha256(path) for path in vault.rglob("*.md")}
        assert_true(before == after, "source markdown hashes must remain unchanged")

        data_2018 = load(target / "data" / "2018.json")
        assert_true(data_2018["totalQuestions"] == 1, "keep mode should not duplicate existing imported questions")
        first = data_2018["questions"][0]
        assert_true(first["years"] == [2018, 2020], "multi-year tags should be preserved")
        assert_true(first["subspecialty"] == "NR", "#NR exam tag should override YAML")
        assert_true(first["subspecialty_confidence"] == "manual", "manual specialty confidence expected")
        assert_true(first["correctAnswer"] == "D", "answer should parse from Ans line")
        assert_true(len(first["options"]) == 4 and first["options"][0]["letter"] == "A", "fenced letter options should parse")
        assert_true("source" not in first and "sourceLine" not in first, "question JSON should match public schema")

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
