#!/usr/bin/env python3
"""Tests for the one-time legacy reference migration (``migrate_question_reference.py``)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from migrate_question_reference import insert_reference, migrate, yaml_scalar
from vault_site.compiler import parse_frontmatter

CARD = (
    "---\n"
    "id: {qid}\n"
    "year:\n"
    "  - {year}\n"
    "subspecialty: CH\n"
    "correctAnswer: B\n"
    "concepts: []\n"
    "checked: false\n"
    "genHash: b233a4628c3e\n"
    "{extra}"
    "---\n"
    "#交換 #{year}交換 #CH stem\n"
    "(A) one\n"
    "(B) two\n"
    "??\n"
    "**Ans: B**\n"
)


def _card(qid: str, extra: str = "", eol: str = "\n") -> bytes:
    return CARD.format(qid=qid, year=qid[:4], extra=extra).replace("\n", eol).encode("utf-8")


class MigrateQuestionReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.data = root / "data"
        self.vault = root / "vault"
        self.data.mkdir()
        (self.vault / "questions" / "2020").mkdir(parents=True)
        (self.vault / "questions" / "2019").mkdir(parents=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_data(self, year: str, records: list[dict[str, str]]) -> None:
        (self.data / f"{year}.json").write_text(json.dumps({"year": int(year), "questions": records}), encoding="utf-8")

    def _write_card(self, qid: str, extra: str = "", eol: str = "\n") -> Path:
        path = self.vault / "questions" / qid[:4] / f"{qid}.md"
        path.write_bytes(_card(qid, extra, eol))
        return path

    def test_dry_run_reports_without_writing(self) -> None:
        self._write_data("2020", [{"id": "2020-001", "reference": "Agrawal R, et al. RadioGraphics 2020;40(3):656-666."}])
        path = self._write_card("2020-001")
        before = path.read_bytes()
        summary = migrate(self.data, self.vault, dry_run=True)
        self.assertEqual(summary, {"updated": 1, "alreadyPresent": 0, "conflicts": [], "missingCards": []})
        self.assertEqual(path.read_bytes(), before)

    def test_inserts_single_line_before_closing_fence_and_keeps_body(self) -> None:
        ref = "Agrawal R, et al. RadioGraphics 2020;40(3):656-666."
        self._write_data("2020", [{"id": "2020-001", "reference": ref}])
        path = self._write_card("2020-001")
        before = path.read_bytes().decode("utf-8")
        summary = migrate(self.data, self.vault, dry_run=False)
        self.assertEqual(summary["updated"], 1)
        after = path.read_bytes().decode("utf-8")
        self.assertEqual(after.count("\n"), before.count("\n") + 1)
        before_lines, after_lines = before.split("\n"), after.split("\n")
        fence = before_lines.index("---", 1)
        self.assertEqual(after_lines[fence], f"reference: {ref}")
        self.assertEqual(after_lines[:fence] + after_lines[fence + 1:], before_lines)
        frontmatter, _ = parse_frontmatter(after)
        self.assertEqual(frontmatter["reference"], ref)

    def test_preserves_existing_reference_and_reports_conflict(self) -> None:
        self._write_data(
            "2020",
            [
                {"id": "2020-001", "reference": "Same value"},
                {"id": "2020-100", "reference": "Legacy value"},
            ],
        )
        same = self._write_card("2020-001", extra="reference: Same value\n")
        conflict = self._write_card("2020-100", extra="reference: Vault value\n")
        same_before, conflict_before = same.read_bytes(), conflict.read_bytes()
        summary = migrate(self.data, self.vault, dry_run=False)
        self.assertEqual(summary, {"updated": 0, "alreadyPresent": 1, "conflicts": ["2020-100"], "missingCards": []})
        self.assertEqual(same.read_bytes(), same_before)
        self.assertEqual(conflict.read_bytes(), conflict_before)

    def test_spec_example_table_second_row(self) -> None:
        self._write_data(
            "2020",
            [
                {"id": "2020-001", "reference": "New value"},
                {"id": "2020-002", "reference": "Same value"},
                {"id": "2020-100", "reference": "Legacy value"},
            ],
        )
        self._write_data("2019", [{"id": "2019-521", "reference": "Radiology Review Manual P.466"}])
        self._write_card("2020-001")
        self._write_card("2020-002", extra="reference: Same value\n")
        self._write_card("2020-100", extra="reference: Vault value\n")
        summary = migrate(self.data, self.vault, dry_run=False)
        self.assertEqual(summary, {"updated": 1, "alreadyPresent": 1, "conflicts": ["2020-100"], "missingCards": ["2019-521"]})

    def test_unparseable_frontmatter_is_reported_not_written(self) -> None:
        self._write_data("2020", [{"id": "2020-001", "reference": "x"}])
        path = self.vault / "questions" / "2020" / "2020-001.md"
        path.write_text("no frontmatter here\n", encoding="utf-8")
        summary = migrate(self.data, self.vault, dry_run=False)
        self.assertEqual(summary["missingCards"], ["2020-001"])
        self.assertEqual(path.read_text(encoding="utf-8"), "no frontmatter here\n")

    def test_crlf_card_keeps_crlf(self) -> None:
        self._write_data("2020", [{"id": "2020-001", "reference": "Ref: AJR 2008;190:S18-S22"}])
        path = self._write_card("2020-001", eol="\r\n")
        migrate(self.data, self.vault, dry_run=False)
        after = path.read_bytes()
        self.assertNotIn(b"\n", after.replace(b"\r\n", b""))
        self.assertIn(b'reference: "Ref: AJR 2008;190:S18-S22"\r\n---\r\n', after)

    def test_mixed_eol_card_follows_previous_line_and_keeps_bytes(self) -> None:
        self._write_data("2021", [{"id": "2021-336", "reference": "AJR 2008;190:S18-S22"}])
        (self.vault / "questions" / "2021").mkdir()
        path = self.vault / "questions" / "2021" / "2021-336.md"
        before = (
            b"---\r\nid: 2021-336\r\nyear:\r\n  - 2021\r\ncorrectAnswer: B\r\ngenHash: eba8314dc368\n"
            b"reviewStatus: needs_review\nanswerStatus: unresolved\n---\n#stem\r\n(A) one\r\n??\r\n**Ans: B**\r\n"
        )
        path.write_bytes(before)
        summary = migrate(self.data, self.vault, dry_run=False)
        self.assertEqual(summary["updated"], 1)
        after = path.read_bytes()
        self.assertEqual(after, before.replace(b"answerStatus: unresolved\n---\n", b"answerStatus: unresolved\nreference: AJR 2008;190:S18-S22\n---\n"))

    def test_yaml_scalar_quoting_round_trips_through_compiler(self) -> None:
        cases = {
            "Radiology Review Manual P.466": "Radiology Review Manual P.466",
            "Ref: AJR 2008": '"Ref: AJR 2008"',
            'He said "hi" there': "'He said \"hi\" there'",
            "466": '"466"',
            "- leading dash": '"- leading dash"',
        }
        for value, rendered in cases.items():
            with self.subTest(value=value):
                self.assertEqual(yaml_scalar(value), rendered)
                frontmatter, _ = parse_frontmatter(f"---\nid: x\nreference: {rendered}\n---\nbody\n")
                self.assertEqual(frontmatter["reference"], value)
        with self.assertRaises(ValueError):
            yaml_scalar("both \"double\" and 'single'")

    def test_insert_reference_rejects_missing_fence(self) -> None:
        with self.assertRaises(ValueError):
            insert_reference(b"---\nid: x\n", "ref")


if __name__ == "__main__":
    unittest.main()
