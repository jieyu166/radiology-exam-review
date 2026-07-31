"""Incremental, executable coverage-anchor mapping for Phase 2A Task 3.2.

The production evidence stores the resulting exact anchors.  This helper keeps
the fact-to-bullet assignment reviewable and reproducible while the two
five-note groups are checked.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import nr_summary_audit as audit  # noqa: E402


ASSIGNMENT_PATH = Path("docs/reports/nr-summary-rewrite/phase2-assignment.json")
BATCH_ID = "batch-02-disease"
UNRESOLVED_FACT_IDS = (
    "adrenoleukodystrophy-f30",
    "adrenoleukodystrophy-f33",
)
FIRST_GROUP = (
    "2-hydroxyglutarate-idh-mutant-glioma",
    "adrenoleukodystrophy",
    "aicardi-syndrome",
    "als-imaging",
    "angioinvasive-aspergillosis",
)
SECOND_GROUP = (
    "anti-nmda-encephalitis",
    "arterial-dissection-mri",
    "atypical-teratoid-rhabdoid-tumor",
    "autoimmune-encephalitis",
    "basilar-artery-occlusion",
)


# Values are one-based indexes into the accepted Summary's top-level bullets.
# A fact may require multiple anchors when the rewrite intentionally splits one
# compound baseline fact across several short bullets.
FACT_BULLET_INDEXES: dict[str, tuple[int, ...]] = {}


def _assign(slug: str, indexes: dict[int, tuple[int, ...]]) -> None:
    for fact_number, bullet_indexes in indexes.items():
        FACT_BULLET_INDEXES[f"{slug}-f{fact_number:02d}"] = bullet_indexes


_assign(
    "2-hydroxyglutarate-idh-mutant-glioma",
    {
        1: (1,),
        2: (2,),
        3: (2,),
        4: (3,),
        5: (3,),
        6: (4,),
        7: (5,),
    },
)
_assign(
    "adrenoleukodystrophy",
    {
        1: (1,), 2: (1,), 3: (1,),
        4: (2,), 5: (2,), 6: (2,),
        7: (3,), 8: (3,), 9: (4,),
        10: (5,), 11: (5,), 12: (6,), 13: (7,),
        14: (8,), 15: (9,),
        16: (10,), 17: (10,), 18: (10,),
        19: (11,), 20: (12,), 21: (12,),
        22: (13,), 23: (13,),
        24: (14,), 25: (14,),
        26: (15,), 27: (15,), 28: (15,),
        29: (16,),
        31: (17,), 32: (17,),
        34: (18,), 35: (18,), 36: (19,),
    },
)
_assign(
    "aicardi-syndrome",
    {
        1: (1,), 2: (1,), 3: (2,), 4: (3,),
        5: (4,), 6: (5,), 7: (6,), 8: (7,),
    },
)
_assign("als-imaging", {1: (1,), 2: (1,), 3: (2,), 4: (3,)})
_assign(
    "angioinvasive-aspergillosis",
    {1: (1,), 2: (2,), 3: (2,), 4: (3,), 5: (4,), 6: (5,)},
)
_assign(
    "anti-nmda-encephalitis",
    {1: (1,), 2: (1,), 3: (2,), 4: (3,), 5: (3,), 6: (4,), 7: (4,)},
)
_assign(
    "arterial-dissection-mri",
    {1: (1,), 2: (1,), 3: (2,), 4: (3,), 5: (4,), 6: (4,), 7: (5,)},
)
_assign(
    "atypical-teratoid-rhabdoid-tumor",
    {
        1: (1,), 2: (1,),
        3: (2,), 4: (2,), 5: (2,),
        6: (3,), 7: (3,),
        8: (4,), 9: (4,),
        10: (5,), 11: (5,), 12: (5,),
    },
)
_assign(
    "autoimmune-encephalitis",
    {1: (1,), 2: (2,), 3: (3,), 4: (4,)},
)
_assign(
    "basilar-artery-occlusion",
    {1: (1,), 2: (1,), 3: (2,), 4: (3,), 5: (4,), 6: (5, 6, 7), 7: (8,)},
)


FOOTNOTE_RE = re.compile(r"\[\^[^\]]+\]")
CLAUSE_SPLIT_RE = re.compile(r"(?<=[；。！？])")


def _quote_candidates(bullet: str) -> list[str]:
    body = FOOTNOTE_RE.sub("", bullet).strip()
    candidates = [
        part.strip().rstrip("；。！？")
        for part in CLAUSE_SPLIT_RE.split(body)
        if part.strip()
    ]
    return [candidate for candidate in candidates if len(candidate.replace(" ", "")) >= 8]


def _best_exact_quote(fact_text: str, bullet: str) -> str:
    candidates = _quote_candidates(bullet)
    if not candidates:
        raise ValueError(f"No clause-level quote candidate in bullet: {bullet!r}")

    def score(candidate: str) -> tuple[int, float, int]:
        matcher = difflib.SequenceMatcher(None, fact_text, candidate)
        matched = sum(block.size for block in matcher.get_matching_blocks())
        return matched, matcher.ratio(), -len(candidate)

    return max(candidates, key=score)


def build_anchor_map(
    context: audit.BatchContext,
) -> dict[str, list[dict[str, object]]]:
    locked_by_slug = {
        note["slug"]: note for note in context.baseline["notes"]
    }
    anchors: dict[str, list[dict[str, object]]] = {}
    for slug in context.batch["slugs"]:
        note = context.note_records[slug]
        bullets = audit._summary_bullet_lines(note)
        for fact in locked_by_slug[slug]["factUnits"]:
            fact_id = fact["id"]
            if fact_id in UNRESOLVED_FACT_IDS:
                continue
            indexes = FACT_BULLET_INDEXES[fact_id]
            anchors[fact_id] = [
                {
                    "bulletIndex": bullet_index,
                    "quote": _best_exact_quote(
                        fact["text"], bullets[bullet_index - 1]
                    ),
                }
                for bullet_index in indexes
            ]
    return anchors


def validate_group(
    context: audit.BatchContext,
    anchors: dict[str, list[dict[str, object]]],
    slugs: tuple[str, ...],
) -> dict[str, object]:
    locked_by_slug = {
        note["slug"]: note for note in context.baseline["notes"]
    }
    fact_count = 0
    anchor_count = 0
    max_bullet_length = 0
    bullet_counts: dict[str, int] = {}
    for slug in slugs:
        bullets = audit._summary_bullet_lines(context.note_records[slug])
        bullet_counts[slug] = len(bullets)
        max_bullet_length = max(
            max_bullet_length,
            *(len(line) for line in bullets),
        )
        for fact in locked_by_slug[slug]["factUnits"]:
            fact_id = fact["id"]
            if fact_id in UNRESOLVED_FACT_IDS:
                continue
            fact_count += 1
            anchor_count += len(anchors[fact_id])
            if not audit._phase2_fact_coverage_is_valid(
                anchors[fact_id],
                bullets,
                fact["sourceRefs"],
            ):
                raise ValueError(f"Invalid anchor mapping: {fact_id}")
    return {
        "slugs": list(slugs),
        "coveredFacts": fact_count,
        "anchors": anchor_count,
        "bulletCounts": bullet_counts,
        "maxBulletLength": max_bullet_length,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--group",
        choices=("first", "second", "all"),
        default="all",
    )
    parser.add_argument(
        "--write-evidence",
        action="store_true",
        help="Write production evidence only after both groups validate.",
    )
    parser.add_argument(
        "--mapping-file",
        type=Path,
        help="Use an independently audited exact-anchor JSON mapping.",
    )
    args = parser.parse_args()

    context = audit.load_phase2_batch(
        REPO_ROOT,
        ASSIGNMENT_PATH,
        BATCH_ID,
    )
    anchors = (
        json.loads(args.mapping_file.read_text(encoding="utf-8"))
        if args.mapping_file is not None
        else build_anchor_map(context)
    )
    slugs = (
        FIRST_GROUP
        if args.group == "first"
        else SECOND_GROUP
        if args.group == "second"
        else FIRST_GROUP + SECOND_GROUP
    )
    report = validate_group(context, anchors, slugs)

    # A full builder call is the dry-run gate even while one five-note group is
    # being reviewed.  The evidence is written only with --write-evidence.
    evidence_bytes = audit.build_phase2_rewrite_evidence_bytes(
        context,
        implementer="/root/phase2a_task3_2_impl",
        reviewer="/root/phase2a_task3_3_review",
        research_needed_fact_ids=UNRESOLVED_FACT_IDS,
        coverage_anchors_by_fact_id=anchors,
    )
    parsed = json.loads(evidence_bytes)
    report["productionCoveredFacts"] = sum(
        fact["disposition"] == "covered"
        for note in parsed["notes"]
        for fact in note["facts"]
    )
    report["productionAnchors"] = sum(
        len(fact["coverage"])
        for note in parsed["notes"]
        for fact in note["facts"]
        if fact["disposition"] == "covered"
    )
    if args.write_evidence:
        evidence_path = REPO_ROOT / context.evidence_path
        evidence_path.write_bytes(evidence_bytes)
        report["written"] = context.evidence_path.as_posix()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
