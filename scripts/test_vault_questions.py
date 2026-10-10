#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fixture tests for scripts/vault_questions.py (vault/questions card reader)."""
from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from vault_questions import QuestionCard, iter_question_cards


def _card(stem: str, options: list[str], answer: str, *, frontmatter: str, back: str = "Explanation.") -> str:
    lines = ["---", frontmatter.strip(), "---", f"#交換 #2024交換 #NR {stem}"]
    lines += [f"({letter}) {text}" for letter, text in zip("ABCDE", options)]
    lines += ["??", f"**Ans: {answer}**", back, ""]
    return "\n".join(lines)


class VaultQuestionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = Path(self.tmp.name) / "vault"
        self.questions = self.vault / "questions" / "2024"
        self.questions.mkdir(parents=True)
        (self.vault / "concepts").mkdir()
        (self.vault / "concepts" / "brain-abscess.md").write_text(
            "---\nconcepts: [brain-abscess]\n---\n# Brain abscess\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write(self, name: str, text: str) -> None:
        (self.questions / name).write_text(text, encoding="utf-8")

    def _cards(self) -> tuple[dict[str, QuestionCard], str]:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            cards = {card.id: card for card in iter_question_cards(self.vault)}
        return cards, stderr.getvalue()

    def test_full_card_with_reference_concepts_and_five_options(self) -> None:
        self._write("2024-001.md", _card(
            "Which is **correct**?",
            ["One", "Two", "Three", "Four", "Five"],
            "B",
            frontmatter=(
                "id: 2024-001\nyear:\n  - 2024\nsubspecialty: NR\ncorrectAnswer: B\n"
                "concepts:\n  - brain-abscess\n  - second-concept\nchecked: false\n"
                'reference: "Osborn AG. Diagnostic Imaging: Brain. 3rd ed."'
            ),
            back="Per-option detail.\n概念：[[brain-abscess]]",
        ))
        cards, warnings = self._cards()
        self.assertEqual(warnings, "")
        card = cards["2024-001"]
        self.assertEqual(card.year, [2024])
        self.assertEqual(card.subspecialty, "NR")
        self.assertEqual(card.correct_answer, "B")
        self.assertEqual(card.concepts, ["brain-abscess", "second-concept"])
        self.assertEqual(card.reference, "Osborn AG. Diagnostic Imaging: Brain. 3rd ed.")
        self.assertEqual(card.stem, "Which is **correct**?")
        self.assertEqual(card.options, {"A": "One", "B": "Two", "C": "Three", "D": "Four", "E": "Five"})
        self.assertTrue(card.explanation.startswith("**Ans: B**"))
        self.assertIn("Per-option detail.", card.explanation)
        self.assertIn("概念：[[brain-abscess]]", card.explanation)
        self.assertEqual(card.path, self.questions / "2024-001.md")

    def test_card_without_reference_and_four_options(self) -> None:
        self._write("2024-002.md", _card(
            "下列何者為**非**？",
            ["Alpha", "Beta", "Gamma", "Delta"],
            "D",
            frontmatter="id: 2024-002\nyear:\n  - 2024\nsubspecialty: Breast\ncorrectAnswer: D\nconcepts: []\nchecked: false",
            back="(benign origin)",
        ))
        cards, _ = self._cards()
        card = cards["2024-002"]
        self.assertEqual(card.reference, "")
        self.assertEqual(card.concepts, [])
        self.assertEqual(card.subspecialty, "Breast")
        self.assertEqual(card.stem, "下列何者為**非**？")
        self.assertEqual(list(card.options), ["A", "B", "C", "D"])
        self.assertEqual(card.options["D"], "Delta")
        self.assertEqual(card.correct_answer, "D")
        self.assertEqual(card.explanation, "**Ans: D**\n(benign origin)")

    def test_multi_answer_joins_accepted_answers(self) -> None:
        self._write("2024-003.md", _card(
            "Pick the not-true ones.",
            ["One", "Two", "Three", "Four"],
            "BD",
            frontmatter=(
                "id: 2024-003\nyear:\n  - 2024\nsubspecialty: Breast\ncorrectAnswer: B,D\nconcepts: []\n"
                "answerStatus: confirmed\nanswerMode: any\nacceptedAnswers: [B, D]"
            ),
        ))
        cards, warnings = self._cards()
        self.assertEqual(warnings, "")
        self.assertEqual(cards["2024-003"].correct_answer, "B,D")

    def test_unresolved_card_has_empty_correct_answer(self) -> None:
        self._write("2024-004.md", _card(
            "Unresolved stem.",
            ["One", "Two", "Three", "Four"],
            "C",
            frontmatter=(
                "id: 2024-004\nyear:\n  - 2024\nsubspecialty: NR\ncorrectAnswer: C\nconcepts: []\n"
                "answerStatus: unresolved\nanswerMode: none\nacceptedAnswers: []"
            ),
        ))
        cards, _ = self._cards()
        self.assertEqual(cards["2024-004"].correct_answer, "")

    def test_multiline_option_and_stem_are_joined(self) -> None:
        self._write("2024-005.md", (
            "---\nid: 2024-005\nyear:\n  - 2024\nsubspecialty: NR\ncorrectAnswer: A\nconcepts: []\n---\n"
            "#交換 #2024交換 #NR First stem line\nsecond stem line\n"
            "(A) Option A first line\ncontinued A\n(B) Option B\n(C) Option C\n??\n**Ans: A**\nWhy.\n"
        ))
        cards, _ = self._cards()
        card = cards["2024-005"]
        self.assertEqual(card.stem, "First stem line\nsecond stem line")
        self.assertEqual(card.options["A"], "Option A first line\ncontinued A")
        self.assertEqual(card.options["C"], "Option C")

    def test_missing_boundary_is_skipped_with_warning(self) -> None:
        self._write("2024-006.md", (
            "---\nid: 2024-006\nyear:\n  - 2024\nsubspecialty: NR\ncorrectAnswer: A\nconcepts: []\n---\n"
            "#交換 #2024交換 #NR No boundary here\n(A) One\n(B) Two\n(C) Three\n**Ans: A**\n"
        ))
        self._write("2024-007.md", _card(
            "Good card.", ["One", "Two", "Three"], "A",
            frontmatter="id: 2024-007\nyear:\n  - 2024\nsubspecialty: NR\ncorrectAnswer: A\nconcepts: []",
        ))
        cards, warnings = self._cards()
        self.assertEqual(sorted(cards), ["2024-007"])
        self.assertIn("questions/2024/2024-006.md", warnings)
        self.assertIn("question_sr_boundary", warnings)
        self.assertEqual(len(warnings.strip().splitlines()), 1)

    def test_underscore_and_publish_false_are_excluded_silently(self) -> None:
        self._write("_draft.md", _card(
            "Underscore draft.", ["One", "Two", "Three"], "A",
            frontmatter="id: 2024-900\nyear:\n  - 2024\nsubspecialty: NR\ncorrectAnswer: A\nconcepts: []",
        ))
        self._write("2024-901.md", _card(
            "Unpublished.", ["One", "Two", "Three"], "A",
            frontmatter="id: 2024-901\nyear:\n  - 2024\nsubspecialty: NR\ncorrectAnswer: A\nconcepts: []\npublish: false",
        ))
        self._write("2024-902.md", _card(
            "Published.", ["One", "Two", "Three"], "A",
            frontmatter="id: 2024-902\nyear:\n  - 2024\nsubspecialty: NR\ncorrectAnswer: A\nconcepts: []",
        ))
        cards, warnings = self._cards()
        self.assertEqual(sorted(cards), ["2024-902"])
        self.assertEqual(warnings, "")

    def test_body_wikilinks_do_not_leak_into_concepts(self) -> None:
        self._write("2024-008.md", _card(
            "Stem with body links.", ["One", "Two", "Three"], "A",
            frontmatter="id: 2024-008\nyear:\n  - 2024\nsubspecialty: MSK\ncorrectAnswer: A\nconcepts: []",
            back="See [[Synovial joints (MRI online)#PVNS]] and [[brain-abscess]].",
        ))
        cards, _ = self._cards()
        self.assertEqual(cards["2024-008"].concepts, [])

    def test_concept_notes_are_never_yielded(self) -> None:
        cards, warnings = self._cards()
        self.assertEqual(cards, {})
        self.assertEqual(warnings, "")


if __name__ == "__main__":
    unittest.main()
