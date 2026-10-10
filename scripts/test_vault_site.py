#!/usr/bin/env python3
"""Fixture tests for the vault-native publication compiler."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from vault_site.compiler import SCHEMA_VERSION, build_package, discover_sources, validate_package


class VaultSiteCompilerTests(unittest.TestCase):
    @staticmethod
    def _tree_hashes(root: Path) -> dict[str, str]:
        return {
            path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.vault = self.root / "vault"
        (self.vault / "concepts").mkdir(parents=True)
        (self.vault / "questions" / "2024").mkdir(parents=True)

        (self.vault / "concepts" / "brain-abscess.md").write_text(
            "---\nname: Brain abscess\nsubspecialty: [NR]\n---\n# Brain abscess\n\n## Teaching Pearls\nUnknown source section remains here.\n- one list item\n1. ordered item\n| A | B |\n| - | - |\n> [!note] Callout\n[^1] Footnote\nSee [[brain-abscess]] and $x^2$.\n==unknown safe extension==\n\n![[brain-abscess.png]]\n",
            encoding="utf-8",
        )
        (self.vault / "attachments").mkdir()
        (self.vault / "attachments" / "brain-abscess.png").write_bytes(b"fixture-image")
        (self.vault / "concepts" / "_private.md").write_text(
            "---\npublish: true\n---\n# private\n",
            encoding="utf-8",
        )
        (self.vault / "concepts" / "draft.md").write_text(
            "---\npublish: false\n---\n# draft\n",
            encoding="utf-8",
        )
        (self.vault / "questions" / "2024" / "2024-001.md").write_text(
            "---\nid: 2024-001\nyear: [2024]\nsubspecialty: NR\nconcepts: [brain-abscess]\n---\n"
            "#交換 #2024交換 #NR Which is correct?\n"
            "(A) One\n(B) Two\n(C) Three\n(D) Four\n(E) Five\n??\n"
            "**Ans: B**\nExplanation.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_discover_classifies_every_source(self) -> None:
        notes = discover_sources(self.vault)
        self.assertEqual([note.relative_path for note in notes], [
            "concepts/_private.md",
            "concepts/brain-abscess.md",
            "concepts/draft.md",
            "questions/2024/2024-001.md",
        ])
        self.assertEqual({note.excluded_reason for note in notes if note.excluded_reason}, {"underscore_basename", "publish_false"})

    def test_build_emits_raw_assets_records_and_exclusions(self) -> None:
        output = self.root / "dist"
        result = build_package(self.vault, output, strict=True)
        self.assertTrue(result.ok, result.errors)
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schemaVersion"], SCHEMA_VERSION)
        self.assertEqual(len(manifest["entries"]), 2)

        raw = output / "notes/concepts/brain-abscess.md"
        source = self.vault / "concepts/brain-abscess.md"
        self.assertEqual(raw.read_bytes(), source.read_bytes())
        self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(), manifest["entries"][0]["sourceSha256"])
        record = json.loads((output / "records/concept/brain-abscess.json").read_text(encoding="utf-8"))
        self.assertEqual(record["outline"][1]["heading"], "Teaching Pearls")
        self.assertNotIn("definition", record)
        resolved_asset = record["embeds"][0]["resolvedPath"]
        self.assertTrue(resolved_asset.startswith("assets/"))
        self.assertEqual((output / resolved_asset).read_bytes(), b"fixture-image")
        self.assertFalse((output / "notes/concepts/_private.md").exists())
        self.assertFalse((output / "notes/concepts/draft.md").exists())

        question_record = json.loads((output / "records/question/2024-001.json").read_text(encoding="utf-8"))
        required_record_keys = {
            "schemaVersion", "id", "kind", "sourcePath", "sourceSha256", "rawPath",
            "frontmatter", "outline", "links", "embeds", "diagnostics",
        }
        self.assertTrue(required_record_keys.issubset(question_record))
        self.assertEqual(question_record["sr"]["front"]["startLine"], 7)
        self.assertLess(question_record["sr"]["front"]["endLine"], question_record["sr"]["back"]["startLine"])
        self.assertEqual([option["letter"] for option in question_record["sr"]["options"]], list("ABCDE"))
        self.assertEqual(len(question_record["sr"]["options"]), 5)
        self.assertEqual(question_record["sr"]["correctAnswer"], "B")
        self.assertEqual(question_record["sr"]["conceptIds"], ["brain-abscess"])
        for index_path in (
            "indexes/concepts.json", "indexes/questions.json", "indexes/relations.json",
            "indexes/search.json", "build-report.json",
        ):
            self.assertTrue((output / index_path).exists(), index_path)
        self.assertTrue(validate_package(self.vault, output).ok)
        syntax_classes = set(result.report["syntaxClasses"])
        self.assertTrue({"heading", "unordered_list", "ordered_list", "table", "callout", "footnote", "wikilink", "image_embed", "math"}.issubset(syntax_classes))
        self.assertTrue(any(item["code"] == "unknown_safe_markdown" and item["sourcePath"] == "concepts/brain-abscess.md" for item in result.warnings))
        self.assertTrue((output / "notes/concepts/brain-abscess.md").read_text(encoding="utf-8").find("==unknown safe extension==") >= 0)

    def test_invalid_question_contracts_are_hard_errors(self) -> None:
        missing_boundary = self.vault / "questions" / "2024" / "2024-002.md"
        missing_boundary.write_text(
            "---\nid: 2024-002\n---\n(A) One\n(B) Two\n(C) Three\nAns: B\n",
            encoding="utf-8",
        )
        conflicting = self.vault / "questions" / "2024" / "2024-003.md"
        conflicting.write_text(
            "---\nid: 2024-003\ncorrectAnswer: A\n---\n(A) One\n(B) Two\n(C) Three\n??\nAns: B\n",
            encoding="utf-8",
        )
        result = build_package(self.vault, self.root / "invalid-dist", strict=True)
        codes = {error["code"] for error in result.errors}
        self.assertIn("question_sr_boundary", codes)
        self.assertIn("question_conflicting_answer", codes)
        inventory_status = {item["sourcePath"]: item["status"] for item in result.report["inventory"]}
        self.assertEqual(inventory_status["questions/2024/2024-002.md"], "hard_error")

    def test_explicit_answer_states_support_any_and_unresolved(self) -> None:
        multi = self.vault / "questions" / "2024" / "2024-004.md"
        multi.write_text(
            "---\nid: 2024-004\nanswerStatus: confirmed\nanswerMode: any\nacceptedAnswers: [B, D]\ncorrectAnswer: B,D\n---\n"
            "(A) One\n(B) Two\n(C) Three\n(D) Four\n??\n**Ans: BD**\nExplanation.\n",
            encoding="utf-8",
        )
        unresolved = self.vault / "questions" / "2024" / "2024-005.md"
        unresolved.write_text(
            "---\nid: 2024-005\nreviewStatus: needs_review\nanswerStatus: unresolved\nanswerMode: none\nacceptedAnswers: []\n---\n"
            "(A) One\n(B) Two\n(C) Three\n(D) Four\n??\n**Answer status: unresolved**\n",
            encoding="utf-8",
        )
        output = self.root / "answer-states"
        result = build_package(self.vault, output, strict=True)
        self.assertTrue(result.ok, result.errors)

        multi_record = json.loads((output / "records/question/2024-004.json").read_text(encoding="utf-8"))
        self.assertEqual(multi_record["sr"]["acceptedAnswers"], ["B", "D"])
        self.assertEqual(multi_record["sr"]["answerMode"], "any")
        self.assertTrue(multi_record["sr"]["scorable"])

        unresolved_record = json.loads((output / "records/question/2024-005.json").read_text(encoding="utf-8"))
        self.assertEqual(unresolved_record["sr"]["answerStatus"], "unresolved")
        self.assertEqual(unresolved_record["sr"]["answerMode"], "none")
        self.assertEqual(unresolved_record["sr"]["acceptedAnswers"], [])
        self.assertFalse(unresolved_record["sr"]["scorable"])
        question_index = json.loads((output / "indexes/questions.json").read_text(encoding="utf-8"))["entries"]
        index_by_id = {entry["id"]: entry for entry in question_index}
        self.assertFalse(index_by_id["2024-005"]["scorable"])

    def test_corrected_answer_state_validation_matrix(self) -> None:
        body = "(A) One\n(B) Two\n(C) Three\n(D) Four\n??\n**Ans: {ans}**\n"
        cases = {
            "2024-010": ("corrected", "B", "D"),
            "2024-011": ("corrected", None, "D"),
            "2024-012": ("corrected", "BD", "A"),
            "2024-013": ("confirmed", "B", "B"),
        }
        for qid, (status, official, correct) in cases.items():
            front = f"---\nid: {qid}\nanswerStatus: {status}\ncorrectAnswer: {correct}\n"
            if official is not None:
                front += f"officialAnswer: {official}\n"
            (self.vault / "questions" / "2024" / f"{qid}.md").write_text(front + "---\n" + body.format(ans=correct), encoding="utf-8")
        output = self.root / "corrected-dist"
        result = build_package(self.vault, output, strict=False, write=True)
        errors = {}
        for error in result.errors:
            errors.setdefault(error["sourcePath"], set()).add(error["code"])
        self.assertNotIn("questions/2024/2024-010.md", errors)
        self.assertEqual(errors.get("questions/2024/2024-011.md"), {"question_official_answer"})
        self.assertEqual(errors.get("questions/2024/2024-012.md"), {"question_official_answer"})
        self.assertNotIn("questions/2024/2024-013.md", errors)

        published = json.loads((output / "records/question/2024-010.json").read_text(encoding="utf-8"))["sr"]
        self.assertEqual(published["acceptedAnswers"], ["D"])
        self.assertEqual(published["officialAnswer"], "B")
        self.assertEqual(published["answerMode"], "single")
        self.assertTrue(published["scorable"])

        confirmed = json.loads((output / "records/question/2024-013.json").read_text(encoding="utf-8"))["sr"]
        self.assertEqual(confirmed["officialAnswer"], "")
        ignored = [item for item in result.warnings if item["code"] == "official_answer_ignored"]
        self.assertEqual([item["sourcePath"] for item in ignored], ["questions/2024/2024-013.md"])
        plain = json.loads((output / "records/question/2024-001.json").read_text(encoding="utf-8"))["sr"]
        self.assertEqual(plain["officialAnswer"], "")

        unresolved_corrected = self.vault / "questions" / "2024" / "2024-014.md"
        unresolved_corrected.write_text("---\nid: 2024-014\nanswerStatus: corrected\nofficialAnswer: C\n---\n" + "(A) One\n(B) Two\n(C) Three\n??\nno answer line\n", encoding="utf-8")
        strict = build_package(self.vault, self.root / "corrected-strict", strict=True, write=False)
        codes = {error["code"] for error in strict.errors if error["sourcePath"] == "questions/2024/2024-014.md"}
        self.assertIn("question_missing_answer", codes)

    def test_reference_projection_string_absent_and_non_string(self) -> None:
        (self.vault / "questions" / "2024" / "2024-006.md").write_text(
            "---\nid: 2024-006\nreference: Radiology Review Manual P.466\n---\n"
            "(A) One\n(B) Two\n(C) Three\n??\n**Ans: B**\n",
            encoding="utf-8",
        )
        (self.vault / "questions" / "2024" / "2024-007.md").write_text(
            "---\nid: 2024-007\nreference: [AJR, RadioGraphics]\n---\n"
            "(A) One\n(B) Two\n(C) Three\n??\n**Ans: A**\n",
            encoding="utf-8",
        )
        output = self.root / "reference-dist"
        result = build_package(self.vault, output, strict=True)
        self.assertTrue(result.ok, result.errors)

        with_ref = json.loads((output / "records/question/2024-006.json").read_text(encoding="utf-8"))
        self.assertEqual(with_ref["sr"]["reference"], "Radiology Review Manual P.466")
        without_ref = json.loads((output / "records/question/2024-001.json").read_text(encoding="utf-8"))
        self.assertEqual(without_ref["sr"]["reference"], "")
        list_ref = json.loads((output / "records/question/2024-007.json").read_text(encoding="utf-8"))
        self.assertEqual(list_ref["sr"]["reference"], "")

        warnings = [item for item in result.warnings if item["code"] == "reference_not_string"]
        self.assertEqual([item["sourcePath"] for item in warnings], ["questions/2024/2024-007.md"])

        index_by_id = {entry["id"]: entry for entry in json.loads((output / "indexes/questions.json").read_text(encoding="utf-8"))["entries"]}
        self.assertEqual(index_by_id["2024-006"]["reference"], "Radiology Review Manual P.466")
        self.assertEqual(index_by_id["2024-001"]["reference"], "")
        search_text = (output / "indexes/search.json").read_text(encoding="utf-8")
        self.assertNotIn("Radiology Review Manual", search_text)

    def test_frontmatter_wikilink_in_reference_does_not_duplicate_links(self) -> None:
        (self.vault / "questions" / "2024" / "2024-008.md").write_text(
            "---\nid: 2024-008\nconcepts: [brain-abscess]\nreference: \"See [[brain-abscess]] and [[other-concept]]\"\n---\n"
            "Stem [[brain-abscess]]\n(A) One\n(B) Two\n(C) Three\n??\n**Ans: C**\n",
            encoding="utf-8",
        )
        output = self.root / "wikilink-dist"
        result = build_package(self.vault, output, strict=True)
        self.assertTrue(result.ok, result.errors)
        record = json.loads((output / "records/question/2024-008.json").read_text(encoding="utf-8"))
        self.assertEqual(record["links"], [{"target": "brain-abscess", "display": ""}])
        self.assertEqual(record["sr"]["conceptIds"], ["brain-abscess"])
        wikilink_lines = [item["line"] for item in result.report["syntaxInventory"] if item["sourcePath"] == "questions/2024/2024-008.md" and item["syntax"] == "wikilink"]
        self.assertEqual(wikilink_lines, [6])

    def test_missing_and_ambiguous_assets_are_hard_errors(self) -> None:
        (self.vault / "concepts" / "missing.md").write_text(
            "# Missing\n![[not-found.png]]\n",
            encoding="utf-8",
        )
        (self.vault / "attachments" / "one").mkdir()
        (self.vault / "attachments" / "two").mkdir()
        (self.vault / "attachments" / "one" / "same.png").write_bytes(b"one")
        (self.vault / "attachments" / "two" / "same.png").write_bytes(b"two")
        (self.vault / "concepts" / "ambiguous.md").write_text(
            "# Ambiguous\n![[same.png]]\n",
            encoding="utf-8",
        )
        result = build_package(self.vault, self.root / "asset-errors", strict=True)
        codes = {error["code"] for error in result.errors}
        self.assertIn("missing_required_asset", codes)
        self.assertIn("ambiguous_required_asset", codes)

    def test_validator_detects_missing_record_from_existing_package(self) -> None:
        output = self.root / "missing-record"
        self.assertTrue(build_package(self.vault, output, strict=True).ok)
        (output / "records/question/2024-001.json").unlink()
        result = validate_package(self.vault, output)
        self.assertFalse(result.ok)
        self.assertTrue(any(error["code"] == "missing_package_file" and error["sourcePath"] == "questions/2024/2024-001.md" for error in result.errors))

    def test_repeated_build_is_byte_deterministic(self) -> None:
        first = self.root / "first-dist"
        second = self.root / "second-dist"
        self.assertTrue(build_package(self.vault, first, strict=True).ok)
        self.assertTrue(build_package(self.vault, second, strict=True).ok)
        self.assertEqual(self._tree_hashes(first), self._tree_hashes(second))


if __name__ == "__main__":
    unittest.main()
