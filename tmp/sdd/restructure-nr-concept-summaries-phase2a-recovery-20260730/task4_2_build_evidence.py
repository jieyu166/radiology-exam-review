"""Build the Task 4.2 Batch 03 pre-review evidence deterministically.

The default is a read-only dry run.  ``--write-evidence`` may write exactly
``docs/reports/nr-summary-rewrite/phase2a/evidence/batch-03-pattern.json``.
This script performs no network, subprocess, authentication, or source-note
write.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from dataclasses import replace
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(SCRIPT_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_REPO_ROOT))

from scripts import nr_summary_audit as audit


BATCH_ID = "batch-03-pattern"
ASSIGNMENT_PATH = Path(
    "docs/reports/nr-summary-rewrite/phase2-assignment.json"
)
EVIDENCE_PATH = Path(
    "docs/reports/nr-summary-rewrite/phase2a/evidence/batch-03-pattern.json"
)
IMPLEMENTER = "/root/phase2a_task4_2_impl"
REVIEWER = "/root/phase2a_task4_3_review"
APPROVED_PENDING_SCAFFOLD_SHA256 = (
    "2a474f66730af8f541b2fd7024553132b548a3f1d83620fda920022bbf6104c4"
)

RESEARCH_NEEDED_FACT_IDS = (
    "cns-opportunistic-infection-f03",
    "cns-opportunistic-infection-f06",
    "cns-opportunistic-infection-f07",
)

SOURCE_REF_OVERRIDES_BY_FACT_ID = {
    "dural-based-masses-aids-f04": ["1"],
    "dural-based-masses-aids-f05": ["1"],
    "dural-based-masses-aids-f06": ["1"],
}

# Each inner array names the fact ordinals represented by one current Summary
# bullet, in source and bullet order.  The zero-fact legacy-heading migration
# is intentionally absent: its refs are derived directly from its three new
# canonical Summary bullets by the evidence builder.
FACT_ORDINALS_BY_BULLET = {
    "brain-tumor-imaging": [
        [1],
        [2],
        [3, 4, 6],
        [5],
        [7],
    ],
    "cerebral-infarction-fogging": [
        [1],
        [2],
        [3],
        [4],
        [5],
    ],
    "cerebral-microbleeds": [
        [1],
        [2, 3, 4, 5],
        [6, 7],
        [8],
        [9],
        [10, 11],
    ],
    "chemical-shift-artifact": [
        [1, 2],
        [3, 4],
        [5],
        [6, 7],
        [8, 9],
        [10],
        [11, 12],
        [13, 14],
        [15, 16],
        [17],
        [18, 19],
        [20],
        [21, 22],
        [23],
        [24, 25],
        [26, 27, 28],
        [29, 30],
        [31],
        [32, 33, 34],
    ],
    "cns-opportunistic-infection": [
        [1, 2],
        [4, 5],
    ],
    "cranial-nerve-muscle-atrophy": [
        [1],
        [2],
        [3, 4],
        [5, 6],
    ],
    "dural-based-masses-aids": [
        [1, 2],
        [3, 4],
        [5],
        [6],
        [7],
    ],
    "facial-fracture-complications": [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11],
        [12, 13, 14],
    ],
    "gbm-vs-pcnsl": [
        [1],
        [2],
        [3],
    ],
}


def _repo_root() -> Path:
    root = SCRIPT_REPO_ROOT
    if Path.cwd().resolve() != root:
        raise SystemExit(
            f"Refusing cwd {Path.cwd()!s}; run from the script's repo root {root!s}."
        )
    return root


def _fact_to_bullet_index(slug: str) -> dict[str, int]:
    groups = FACT_ORDINALS_BY_BULLET.get(slug)
    if groups is None:
        return {}
    return {
        f"{slug}-f{ordinal:02d}": bullet_index
        for bullet_index, ordinals in enumerate(groups, start=1)
        for ordinal in ordinals
    }


def _medical_body(bullet: str) -> str:
    match = audit.VALID_BULLET_RE.match(bullet)
    if match is None:
        raise ValueError(f"Not a strict Summary bullet: {bullet!r}")
    return audit.FOOTNOTE_REFERENCE_RE.sub("", bullet[match.end() :]).strip()


def _clause_candidates(fact_text: str, medical_body: str) -> list[str]:
    clauses = [
        clause.strip()
        for clause in re.split(r"(?<=[；。])", medical_body)
        if clause.strip()
    ]
    if not clauses:
        return [medical_body]

    scores = []
    for index, clause in enumerate(clauses):
        matcher = difflib.SequenceMatcher(
            None,
            fact_text,
            clause,
            autojunk=False,
        )
        scores.append(
            (
                matcher.find_longest_match().size,
                matcher.ratio(),
                -index,
                index,
            )
        )
    best_index = max(scores)[3]
    candidates = [clauses[best_index]]
    if best_index:
        candidates.append(
            f"{clauses[best_index - 1]} {clauses[best_index]}"
        )
    if best_index + 1 < len(clauses):
        candidates.append(
            f"{clauses[best_index]} {clauses[best_index + 1]}"
        )
    candidates.append(medical_body)
    return list(dict.fromkeys(candidates))


def _derive_anchors(
    context: audit.BatchContext,
) -> dict[str, list[dict[str, object]]]:
    unresolved = set(RESEARCH_NEEDED_FACT_IDS)
    anchors: dict[str, list[dict[str, object]]] = {}
    covered_ids: set[str] = set()

    for locked in context.baseline["notes"]:
        slug = locked["slug"]
        if audit._phase2_is_exact_empty_projection(locked):
            continue
        fact_to_bullet = _fact_to_bullet_index(slug)
        bullet_lines = audit._summary_bullet_lines(
            context.note_records[slug]
        )
        if set(fact_to_bullet) != {
            fact["id"]
            for fact in locked["factUnits"]
            if fact["id"] not in unresolved
        }:
            raise ValueError(
                f"Source-order bullet map does not exactly cover {slug!r}."
            )

        for fact in locked["factUnits"]:
            fact_id = fact["id"]
            if fact_id in unresolved:
                continue
            covered_ids.add(fact_id)
            bullet_index = fact_to_bullet[fact_id]
            bullet = bullet_lines[bullet_index - 1]
            source_refs = SOURCE_REF_OVERRIDES_BY_FACT_ID.get(
                fact_id,
                fact["sourceRefs"],
            )
            if not set(source_refs) <= set(
                audit._ordered_footnote_refs(bullet)
            ):
                raise ValueError(
                    f"Bullet refs do not cover {fact_id!r}."
                )

            anchor = None
            for quote in _clause_candidates(
                fact["text"],
                _medical_body(bullet),
            ):
                candidate = {
                    "bulletIndex": bullet_index,
                    "quote": quote,
                }
                if audit._phase2_coverage_anchor_is_valid(
                    candidate,
                    bullet_lines,
                    source_refs,
                ):
                    anchor = candidate
                    break
            if anchor is None:
                raise ValueError(
                    f"No valid clause-level coverage anchor for {fact_id!r}."
                )
            anchors[fact_id] = [anchor]

    expected_covered_ids = {
        fact["id"]
        for locked in context.baseline["notes"]
        for fact in locked["factUnits"]
    } - unresolved
    if covered_ids != expected_covered_ids or set(anchors) != expected_covered_ids:
        raise ValueError("Derived anchors are not the exact covered fact set.")
    return anchors


def _build_evidence(
    context: audit.BatchContext,
) -> tuple[dict, bytes, list[audit.Finding]]:
    anchors = _derive_anchors(context)
    evidence = audit.build_phase2_rewrite_evidence(
        context,
        implementer=IMPLEMENTER,
        reviewer=REVIEWER,
        research_needed_fact_ids=RESEARCH_NEEDED_FACT_IDS,
        coverage_anchors_by_fact_id=anchors,
        source_ref_overrides_by_fact_id=SOURCE_REF_OVERRIDES_BY_FACT_ID,
    )
    evidence_bytes = (
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    findings = audit.validate_phase2_batch(
        replace(context, evidence=evidence),
        check_source_hashes=False,
        check_generated=False,
    )
    unexpected_codes = {
        finding.code
        for finding in findings
        if finding.code != "phase2-review-sequence"
    }
    if unexpected_codes:
        raise ValueError(
            "Pre-review evidence has non-review findings: "
            + ", ".join(sorted(unexpected_codes))
        )
    return evidence, evidence_bytes, findings


def _pending_scaffold_is_safe_to_replace(context: audit.BatchContext) -> bool:
    evidence = context.evidence
    evidence_path = context.repo_root / context.evidence_path
    return (
        evidence_path.is_file()
        and hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        == APPROVED_PENDING_SCAFFOLD_SHA256
        and isinstance(evidence, dict)
        and evidence.get("batch") == BATCH_ID
        and evidence.get("status") == "baseline"
        and evidence.get("workflow")
        == {
            "sequence": 3,
            "predecessor": "batch-02-disease",
            "implementer": "/root/phase2a_task4_1_impl",
            "reviewer": None,
            "reviewStatus": "not-started",
            "reviewedBaselineSha256": None,
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-evidence",
        action="store_true",
        help=f"write only {EVIDENCE_PATH.as_posix()}",
    )
    args = parser.parse_args()

    root = _repo_root()
    context = audit.load_phase2_batch(
        root,
        ASSIGNMENT_PATH,
        BATCH_ID,
    )
    if (
        context.batch["id"] != BATCH_ID
        or context.evidence_path != EVIDENCE_PATH
    ):
        raise SystemExit("Refusing a non-Batch-03 context or evidence path.")

    evidence, evidence_bytes, findings = _build_evidence(context)
    output = {
        "batch": BATCH_ID,
        "mode": "write" if args.write_evidence else "dry-run",
        "evidencePath": EVIDENCE_PATH.as_posix(),
        "evidenceSha256": hashlib.sha256(evidence_bytes).hexdigest(),
        "noteCount": len(evidence["notes"]),
        "factCount": sum(
            len(entry["facts"]) for entry in evidence["notes"]
        ),
        "coveredCount": sum(
            fact["disposition"] == "covered"
            for entry in evidence["notes"]
            for fact in entry["facts"]
        ),
        "researchNeededFactIds": evidence["manualReviewFactIds"],
        "findingCodes": sorted({finding.code for finding in findings}),
    }

    if args.write_evidence:
        if not _pending_scaffold_is_safe_to_replace(context):
            raise SystemExit(
                "Refusing to replace anything except the approved pending scaffold."
            )
        destination = root / EVIDENCE_PATH
        destination.write_bytes(evidence_bytes)
        output["writtenBytes"] = len(evidence_bytes)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
