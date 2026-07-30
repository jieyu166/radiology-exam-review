"""Smoke tests for the NR Summary audit interfaces.

Run directly with ``python scripts/test_nr_summary_audit.py``; no test runner
or third-party dependency is required.
"""

import hashlib
import io
import json
import os
import re
import shutil
import tempfile
from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import nr_summary_audit as audit


NR_DEMO_TEXT = """---
concepts: [demo]
subspecialty: [NR]
---
## Summary
- **Label**: Demo fact.[^1]

## References
[^1]: Example.
"""
NR_DEMO_SUMMARY = "## Summary\n- **Label**: Demo fact.[^1]\n\n"
NR_REWRITE_TEXT = """---
concepts: [demo]
subspecialty: [NR]
---
## Summary
- **Label**: Rewritten fact.[^1]

## References
[^1]: Example.
"""
NR_REWRITE_SUMMARY = "## Summary\n- **Label**: Rewritten fact.[^1]\n\n"

PILOT_SLUGS = (
    "acute-stroke-management",
    "artery-of-adamkiewicz",
    "aspects-score",
    "basal-ganglia-t1-shortening",
    "bilateral-subcortical-dwi-hyperintensity-ddx",
    "cerebral-amyloid-angiopathy",
    "clippers",
    "cpa-masses",
    "craniopharyngioma",
    "dementia-neuroimaging-overview",
)
PILOT_TYPES = {
    "acute-stroke-management": "anatomy-measurement-management",
    "artery-of-adamkiewicz": "anatomy-measurement-management",
    "aspects-score": "anatomy-measurement-management",
    "basal-ganglia-t1-shortening": "pattern-ddx",
    "bilateral-subcortical-dwi-hyperintensity-ddx": "pattern-ddx",
    "cerebral-amyloid-angiopathy": "disease",
    "clippers": "disease",
    "cpa-masses": "pattern-ddx",
    "craniopharyngioma": "disease",
    "dementia-neuroimaging-overview": "pattern-ddx",
}


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def baseline_evidence_sha256(entry: dict) -> str:
    return canonical_sha256(
        {
            "originalSummary": entry["originalSummary"],
            "factUnits": [
                {
                    "id": fact["id"],
                    "text": fact["text"],
                    "sourceRefs": fact["sourceRefs"],
                }
                for fact in entry["factUnits"]
            ],
        }
    )


def coverage_evidence_sha256(entry: dict) -> str:
    return canonical_sha256(
        {
            "rewrittenSummary": entry["rewrittenSummary"],
            "factDispositions": [
                {"id": fact["id"], "disposition": fact["disposition"]}
                for fact in entry["factUnits"]
            ],
            "summaryBulletEvidence": entry["summaryBulletEvidence"],
        }
    )


def summary_bullet_evidence(slug: str, fact_id: str) -> list[dict]:
    bullet = "- **Label**: Demo fact.[^1]"
    return [
        {
            "id": f"{slug}-s01",
            "sha256": hashlib.sha256(bullet.encode("utf-8")).hexdigest(),
            "factIds": [fact_id],
            "sourceRefs": ["1"],
        }
    ]


def seal_entry(entry: dict) -> None:
    entry["baselineEvidenceSha256"] = baseline_evidence_sha256(entry)
    entry["coverageEvidenceSha256"] = coverage_evidence_sha256(entry)


def make_entry_final(entry: dict) -> None:
    fact = entry["factUnits"][0]
    entry["rewrittenSummary"] = entry["originalSummary"]
    entry["summaryBulletEvidence"] = summary_bullet_evidence(entry["slug"], fact["id"])
    fact["disposition"] = "covered"
    entry["status"] = "verified"
    entry["validation"].update(
        {
            "pendingFactCount": 0,
            "structure": "pass",
            "footnotes": "pass",
            "factCoverage": "pass",
        }
    )
    seal_entry(entry)


def make_nr_note(slug: str) -> audit.NoteRecord:
    return audit.parse_note_text(Path(f"vault/concepts/{slug}.md"), NR_DEMO_TEXT)


def make_inventory_entry(
    note: audit.NoteRecord,
    *,
    note_type: str = "disease",
    batch: str = "batch-00",
) -> dict:
    return {
        "slug": note.slug,
        "path": note.path.as_posix(),
        "type": note_type,
        "batch": batch,
        "status": "pending",
        "sourceStatus": "existing-sufficient",
        "originalSha256": note.sha256,
        "summaryHeadings": ["Summary"],
    }


def make_pilot_inventory() -> tuple[dict, dict[str, audit.NoteRecord]]:
    notes = {slug: make_nr_note(slug) for slug in PILOT_SLUGS}
    inventory = {
        "schemaVersion": 1,
        "scope": "NR",
        "generatedFrom": "vault/concepts",
        "notes": [make_inventory_entry(notes[slug]) for slug in PILOT_SLUGS],
    }
    return inventory, notes


def batch_report_fixture(*, source_refs: list[str] | None = None) -> dict:
    note = make_nr_note("demo")
    report = {
        "schemaVersion": 1,
        "batch": "batch-00",
        "scope": "NR",
        "status": "baseline",
        "notes": [
            {
                "slug": "demo",
                "type": "disease",
                "originalSha256": note.sha256,
                "originalSummary": NR_DEMO_SUMMARY,
                "factUnits": [
                    {
                        "id": "demo-f01",
                        "text": "Demo fact.",
                        "sourceRefs": ["1"] if source_refs is None else source_refs,
                        "disposition": "pending",
                    }
                ],
                "sourceStatus": "existing-sufficient",
                "status": "pending",
                "rewrittenSummary": "",
                "summaryBulletEvidence": [],
                "validation": {
                    "hashMatches": True,
                    "losslessSummaryMatches": True,
                    "allSourceRefsDefined": True,
                    "factCount": 1,
                    "pendingFactCount": 1,
                    "researchNeededFactIds": [],
                    "manualReviewFactIds": [],
                    "newUnsupportedFacts": 0,
                },
            }
        ],
    }
    seal_entry(report["notes"][0])
    return report


def write_valid_batch_cli_fixture(root: Path) -> tuple[Path, dict, dict]:
    """Write a complete ten-note batch fixture and return its mutable JSON objects."""
    summary_snapshot = NR_DEMO_SUMMARY
    source_hash = hashlib.sha256(NR_DEMO_TEXT.encode("utf-8")).hexdigest()
    concepts = root / "vault" / "concepts"
    generated_concepts = root / "data" / "concepts"
    report_dir = root / "docs" / "reports" / "nr-summary-rewrite"
    concepts.mkdir(parents=True)
    generated_concepts.mkdir(parents=True)
    report_dir.mkdir(parents=True)

    inventory_notes = []
    evidence_notes = []
    generated_index_notes = []
    for slug in PILOT_SLUGS:
        note_path = concepts / f"{slug}.md"
        note_path.write_text(NR_DEMO_TEXT, encoding="utf-8", newline="")
        generated_detail = {
            "slug": slug,
            "name": slug,
            "nameZh": "",
            "subspecialty": "NR",
            "checked": False,
            "keyPoints": ["**Label**: Demo fact."],
        }
        (generated_concepts / f"{slug}.json").write_text(
            json.dumps(generated_detail),
            encoding="utf-8",
        )
        generated_index_notes.append(
            {
                field: generated_detail[field]
                for field in ("slug", "name", "nameZh", "subspecialty", "checked")
            }
        )
        inventory_notes.append(
            {
                "slug": slug,
                "path": f"vault/concepts/{slug}.md",
                "batch": "batch-00",
                "originalSha256": source_hash,
            }
        )
        entry = {
                "slug": slug,
                "type": PILOT_TYPES[slug],
                "originalSha256": source_hash,
                "originalSummary": summary_snapshot,
                "factUnits": [
                    {
                        "id": f"{slug}-f01",
                        "text": "Demo fact.",
                        "sourceRefs": ["1"],
                        "disposition": "pending",
                    }
                ],
                "sourceStatus": "existing-sufficient",
                "status": "pending",
                "rewrittenSummary": "",
                "summaryBulletEvidence": [],
                "validation": {
                    "hashMatches": True,
                    "losslessSummaryMatches": True,
                    "allSourceRefsDefined": True,
                    "factCount": 1,
                    "pendingFactCount": 1,
                    "researchNeededFactIds": [],
                    "manualReviewFactIds": [],
                    "newUnsupportedFacts": 0,
                },
            }
        seal_entry(entry)
        evidence_notes.append(entry)

    inventory = {"notes": inventory_notes}
    report = {
        "schemaVersion": 1,
        "batch": "batch-00",
        "scope": "NR",
        "status": "baseline",
        "notes": evidence_notes,
    }
    (report_dir / "inventory.json").write_text(json.dumps(inventory), encoding="utf-8")
    (root / "data" / "concepts-index.json").write_text(
        json.dumps({"concepts": generated_index_notes}),
        encoding="utf-8",
    )
    batch_path = report_dir / "batch-00.json"
    batch_path.write_text(json.dumps(report), encoding="utf-8")
    return batch_path, inventory, report


def run_validate_batch_cli(
    batch_path: Path,
    *,
    allow_pending: bool,
    check_source_hashes: bool = False,
    use_fixture_trust: bool = True,
) -> tuple[int, str]:
    argv = ["validate-batch", str(batch_path)]
    if allow_pending:
        argv.append("--allow-pending")
    if check_source_hashes:
        argv.append("--check-source-hashes")
    output = io.StringIO()
    original_trust = audit.TRUSTED_PILOT_ORIGINAL_SHA256
    original_trusted_anchor = audit._trusted_evidence_anchor_findings
    original_phase1_gate = audit._phase1_verification_findings
    original_inventory_validator = audit.validate_inventory_against_notes
    if use_fixture_trust:
        inventory = json.loads(
            batch_path.with_name("inventory.json").read_text(encoding="utf-8")
        )
        audit.TRUSTED_PILOT_ORIGINAL_SHA256 = {
            entry["slug"]: entry["originalSha256"]
            for entry in inventory["notes"]
            if entry.get("slug") in PILOT_SLUGS
        }
        audit._trusted_evidence_anchor_findings = lambda report, notes, path: []
        audit._phase1_verification_findings = lambda report, notes, path: []
        audit.validate_inventory_against_notes = (
            lambda inventory, notes, **kwargs: []
        )
    try:
        with redirect_stdout(output), redirect_stderr(output):
            exit_code = audit.main(argv)
    except SystemExit as error:
        exit_code = error.code
    finally:
        audit.TRUSTED_PILOT_ORIGINAL_SHA256 = original_trust
        audit._trusted_evidence_anchor_findings = original_trusted_anchor
        audit._phase1_verification_findings = original_phase1_gate
        audit.validate_inventory_against_notes = original_inventory_validator
    return exit_code, output.getvalue()


def load_real_batch_and_notes() -> tuple[dict, dict[str, audit.NoteRecord]]:
    root = Path(__file__).resolve().parents[1]
    report = json.loads(
        (
            root / "docs" / "reports" / "nr-summary-rewrite" / "batch-00.json"
        ).read_text(encoding="utf-8")
    )
    notes = {
        slug: audit.parse_note(root / "vault" / "concepts" / f"{slug}.md")
        for slug in PILOT_SLUGS
    }
    return report, notes


def validate_inventory_with_fixture_trust(
    inventory: dict,
    notes: dict[str, audit.NoteRecord],
    trusted_pilot_hashes: dict[str, str],
    *,
    repo_root: Path | None = None,
) -> list[audit.Finding]:
    """Test-only trust injection; production public defaults remain immutable."""
    original_trust = audit.TRUSTED_PILOT_ORIGINAL_SHA256
    audit.TRUSTED_PILOT_ORIGINAL_SHA256 = trusted_pilot_hashes
    try:
        return audit.validate_inventory_against_notes(
            inventory,
            notes,
            repo_root=repo_root,
        )
    finally:
        audit.TRUSTED_PILOT_ORIGINAL_SHA256 = original_trust


def write_real_shadow_checkout(
    root: Path,
    shadow: Path,
    inventory: dict,
    report: dict,
    *,
    written_inventory: dict | None = None,
) -> tuple[Path, dict[str, audit.NoteRecord]]:
    for entry in inventory["notes"]:
        source = root / entry["path"]
        target = shadow / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    shutil.copytree(root / "data", shadow / "data")
    report_dir = shadow / "docs" / "reports" / "nr-summary-rewrite"
    report_dir.mkdir(parents=True)
    (report_dir / "inventory.json").write_text(
        json.dumps(inventory if written_inventory is None else written_inventory),
        encoding="utf-8",
    )
    batch_path = report_dir / "batch-00.json"
    batch_path.write_text(json.dumps(report), encoding="utf-8")
    notes = {
        slug: audit.parse_note(shadow / "vault" / "concepts" / f"{slug}.md")
        for slug in PILOT_SLUGS
    }
    return batch_path, notes


def promote_manual_queue_to_verified(report: dict) -> None:
    for entry in report["notes"]:
        manual_facts = [
            fact
            for fact in entry["factUnits"]
            if fact["disposition"] == "manual-review"
        ]
        if not manual_facts:
            continue
        for fact in manual_facts:
            fact["disposition"] = "covered"
        entry["sourceStatus"] = "existing-sufficient"
        entry["status"] = "verified"
        entry["validation"]["manualReviewFactIds"] = []
        entry["validation"]["factCoverage"] = "pass"
        seal_entry(entry)
    report["status"] = "verified"
    verification = report["phase1Verification"]
    verification["status"] = "verified"
    verification["factCoverage"] = {
        "total": 225,
        "covered": 225,
        "manualReview": 0,
        "researchNeeded": 0,
        "pending": 0,
    }
    verification["manualQueue"] = []
    verification["reviewGate"] = {
        "status": "verified",
        "verifiedNotes": 10,
        "manualReviewNotes": 0,
        "phase2Started": True,
    }


def reseal_report(report: dict) -> None:
    for entry in report["notes"]:
        seal_entry(entry)


def set_fact_state(
    report: dict,
    *,
    disposition: str,
    note_status: str,
    source_status: str,
) -> None:
    entry = report["notes"][0]
    fact = entry["factUnits"][0]
    fact["disposition"] = disposition
    entry["status"] = note_status
    entry["sourceStatus"] = source_status
    validation = entry["validation"]
    validation["pendingFactCount"] = int(disposition == "pending")
    validation["researchNeededFactIds"] = (
        [fact["id"]] if disposition == "research-needed" else []
    )
    validation["manualReviewFactIds"] = (
        [fact["id"]] if disposition == "manual-review" else []
    )
    seal_entry(entry)


def phase2_inventory_fixture() -> dict:
    notes = []
    for slug, note_type in sorted(audit.NOTE_TYPE_OVERRIDES.items()):
        notes.append(
            {
                "slug": slug,
                "path": f"vault/concepts/{slug}.md",
                "type": note_type,
                "batch": "batch-00" if slug in audit.PILOT_SLUGS else "unassigned",
                "status": "pending",
                "sourceStatus": "existing-sufficient",
                "originalSha256": hashlib.sha256(slug.encode("utf-8")).hexdigest(),
                "summaryHeadings": ["Summary"],
            }
        )
    return {
        "schemaVersion": 1,
        "scope": "NR",
        "generatedFrom": "vault/concepts",
        "notes": notes,
    }


def write_phase2_api_fixture(root: Path, batch_id: str = "batch-01-anatomy") -> tuple[Path, str]:
    report_root = root / "docs" / "reports" / "nr-summary-rewrite"
    baseline_root = report_root / "phase2a" / "baselines"
    evidence_root = report_root / "phase2a" / "evidence"
    generated_root = root / "data" / "concepts"
    concept_root = root / "vault" / "concepts"
    for directory in (baseline_root, evidence_root, generated_root, concept_root):
        directory.mkdir(parents=True, exist_ok=True)

    inventory = phase2_inventory_fixture()
    active_slugs = list(audit.ACTIVE_PHASE2A_BATCHES[batch_id]["slugs"])
    inventory_by_slug = {entry["slug"]: entry for entry in inventory["notes"]}
    for slug in active_slugs:
        note_path = concept_root / f"{slug}.md"
        note_path.write_text(NR_DEMO_TEXT, encoding="utf-8", newline="")
        inventory_by_slug[slug]["originalSha256"] = hashlib.sha256(
            NR_DEMO_TEXT.encode("utf-8")
        ).hexdigest()
    assignment = audit.build_phase2_assignment(inventory)
    inventory = audit.synchronize_phase2_inventory(inventory, assignment)
    assignment_path = report_root / "phase2-assignment.json"
    inventory_path = report_root / "inventory.json"
    assignment_path.write_text(json.dumps(assignment), encoding="utf-8")
    inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

    batch = next(item for item in assignment["batches"] if item["id"] == batch_id)
    baseline = {
        "schemaVersion": 1,
        "kind": "phase2-baseline-lock",
        "batch": batch_id,
        "scope": "NR",
        "assignmentSha256": canonical_sha256(assignment),
        "notes": [
            {
                "slug": slug,
                "path": inventory_by_slug[slug]["path"],
                "type": batch["type"],
                "originalSha256": inventory_by_slug[slug]["originalSha256"],
                "summaryHeadings": ["Summary"],
                "originalSummary": NR_DEMO_SUMMARY,
                "factUnits": [
                    {
                        "id": f"{slug}-f01",
                        "text": "Label: Demo fact.",
                        "sourceStatement": "- **Label**: Demo fact.[^1]",
                        "sourceRefs": ["1"],
                    }
                ],
            }
            for slug in active_slugs
        ],
    }
    baseline_digest = canonical_sha256(baseline)
    baseline_path = baseline_root / f"{batch_id}.json"
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

    evidence = {
        "schemaVersion": 1,
        "kind": "phase2-batch-evidence",
        "batch": batch_id,
        "scope": "NR",
        "baselineLock": {
            "path": f"docs/reports/nr-summary-rewrite/phase2a/baselines/{batch_id}.json",
            "sha256": baseline_digest,
        },
        "status": "verified",
        "workflow": {
            "sequence": 1,
            "predecessor": None,
            "implementer": "/root/fixture_implementer",
            "reviewer": "/root/fixture_reviewer",
            "reviewStatus": "approved",
            "reviewedBaselineSha256": baseline_digest,
        },
        "notes": [
            {
                "slug": slug,
                "sourceStatus": "existing-sufficient",
                "status": "verified",
                "rewrittenSummary": NR_DEMO_SUMMARY,
                "facts": [
                    {
                        "id": f"{slug}-f01",
                        "sourceRefs": ["1"],
                        "disposition": "covered",
                    }
                ],
                "sourceDefinitions": {
                    "1": {
                        "kind": "existing-footnote",
                        "locator": "1",
                        "citation": "Example.",
                    }
                },
                "newUnsupportedFacts": 0,
                "validation": {
                    "hashMatches": True,
                    "losslessSummaryMatches": True,
                    "allSourceRefsDefined": True,
                    "structure": {"errors": 0, "codes": []},
                    "footnotes": {"errors": 0, "codes": []},
                    "factCoverage": {
                        "total": 1,
                        "covered": 1,
                        "researchNeeded": 0,
                        "manualReview": 0,
                    },
                },
                "summaryBulletEvidence": ["**Label**: Demo fact."],
                "coverageEvidenceSha256": "0" * 64,
            }
            for slug in active_slugs
        ],
        "manualReviewFactIds": [],
        "generatedManifest": (
            f"docs/reports/nr-summary-rewrite/phase2a/generated/{batch_id}.json"
        ),
    }
    for entry in evidence["notes"]:
        entry["coverageEvidenceSha256"] = audit.phase2_coverage_evidence_sha256(
            baseline_digest, entry
        )
    (evidence_root / f"{batch_id}.json").write_text(
        json.dumps(evidence), encoding="utf-8"
    )

    index_entries = []
    for slug in active_slugs:
        detail = {
            "slug": slug,
            "name": slug,
            "nameZh": "",
            "subspecialty": "NR",
            "checked": False,
            "keyPoints": ["**Label**: Demo fact."],
        }
        (generated_root / f"{slug}.json").write_text(
            json.dumps(detail), encoding="utf-8"
        )
        index_entries.append(
            {
                key: detail[key]
                for key in ("slug", "name", "nameZh", "subspecialty", "checked")
            }
        )
    (root / "data" / "concepts-index.json").write_text(
        json.dumps({"concepts": index_entries}), encoding="utf-8"
    )
    return assignment_path.relative_to(root), baseline_digest


def phase2_manifest_observations(
    root: Path,
    batch_id: str = "batch-01-anatomy",
    *,
    nonselected_before: dict[str, str] | None = None,
) -> dict:
    selected = set(audit.ACTIVE_PHASE2A_BATCHES[batch_id]["slugs"])
    current_nonselected = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((root / "data" / "concepts").glob("*.json"))
        if path.stem not in selected
    }
    return {
        "nonselected_before": (
            current_nonselected
            if nonselected_before is None
            else nonselected_before
        ),
        "nonselected_after": current_nonselected,
        "first_run": {"changedPaths": [], "mtimeChangedPaths": []},
        "second_run": {"changedPaths": [], "mtimeChangedPaths": []},
    }


def write_phase2_approved_chain_fixture(root: Path) -> tuple[Path, dict[str, str]]:
    batch_ids = list(audit.ACTIVE_PHASE2A_BATCHES)
    for batch_id in batch_ids:
        assignment_path, _ = write_phase2_api_fixture(root, batch_id)

    report_root = root / "docs" / "reports" / "nr-summary-rewrite"
    inventory_path = report_root / "inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory_by_slug = {entry["slug"]: entry for entry in inventory["notes"]}
    source_digest = hashlib.sha256(NR_DEMO_TEXT.encode("utf-8")).hexdigest()
    for contract in audit.ACTIVE_PHASE2A_BATCHES.values():
        for slug in contract["slugs"]:
            inventory_by_slug[slug]["originalSha256"] = source_digest
    assignment = audit.build_phase2_assignment(inventory)
    inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
    (root / assignment_path).write_text(json.dumps(assignment), encoding="utf-8")

    assignment_digest = canonical_sha256(assignment)
    baseline_digests = {}
    for index, batch_id in enumerate(batch_ids):
        baseline_path = (
            report_root / "phase2a" / "baselines" / f"{batch_id}.json"
        )
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        baseline["assignmentSha256"] = assignment_digest
        for entry in baseline["notes"]:
            entry["originalSha256"] = source_digest
        baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
        baseline_digest = canonical_sha256(baseline)
        baseline_digests[batch_id] = baseline_digest

        evidence_path = (
            report_root / "phase2a" / "evidence" / f"{batch_id}.json"
        )
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["baselineLock"]["sha256"] = baseline_digest
        evidence["workflow"].update(
            {
                "sequence": index + 1,
                "predecessor": batch_ids[index - 1] if index else None,
                "reviewStatus": "approved",
                "reviewedBaselineSha256": baseline_digest,
            }
        )
        for entry in evidence["notes"]:
            entry["coverageEvidenceSha256"] = (
                audit.phase2_coverage_evidence_sha256(
                    baseline_digest, entry
                )
            )
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    detail_paths = sorted((root / "data" / "concepts").glob("*.json"))
    index_entries = []
    for detail_path in detail_paths:
        detail = json.loads(detail_path.read_text(encoding="utf-8"))
        index_entries.append(
            {
                key: detail[key]
                for key in audit.GENERATED_INDEX_FIELDS
            }
        )
    (root / "data" / "concepts-index.json").write_text(
        json.dumps({"concepts": sorted(index_entries, key=lambda item: item["slug"])}),
        encoding="utf-8",
    )
    return assignment_path, baseline_digests


def write_phase2_generated_manifest_fixture(
    root: Path, batch_id: str, workflow: dict
) -> None:
    manifest_path = (
        root
        / "docs"
        / "reports"
        / "nr-summary-rewrite"
        / "phase2a"
        / "generated"
        / f"{batch_id}.json"
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(workflow["manifest"]), encoding="utf-8")


def write_phase2_current_index(root: Path) -> None:
    entries = []
    for detail_path in sorted((root / "data" / "concepts").glob("*.json")):
        detail = json.loads(detail_path.read_text(encoding="utf-8"))
        entries.append(
            {
                key: detail[key]
                for key in audit.GENERATED_INDEX_FIELDS
            }
        )
    (root / "data" / "concepts-index.json").write_text(
        json.dumps({"concepts": sorted(entries, key=lambda item: item["slug"])}),
        encoding="utf-8",
    )


def rewrite_phase2_fixture_note(root: Path, batch_id: str, slug: str) -> None:
    (root / "vault" / "concepts" / f"{slug}.md").write_text(
        NR_REWRITE_TEXT,
        encoding="utf-8",
        newline="",
    )
    evidence_path = (
        root
        / "docs"
        / "reports"
        / "nr-summary-rewrite"
        / "phase2a"
        / "evidence"
        / f"{batch_id}.json"
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    entry = next(item for item in evidence["notes"] if item["slug"] == slug)
    entry["rewrittenSummary"] = NR_REWRITE_SUMMARY
    entry["summaryBulletEvidence"] = ["**Label**: Rewritten fact."]
    entry["coverageEvidenceSha256"] = audit.phase2_coverage_evidence_sha256(
        evidence["baselineLock"]["sha256"], entry
    )
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")


def prepare_phase2_later_update_fixture(
    root: Path,
) -> tuple[Path, dict[str, str], dict, dict, dict]:
    assignment_path, baseline_digests = write_phase2_approved_chain_fixture(root)
    original_baseline_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
    original_observation_trust = (
        audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256
    )
    audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = baseline_digests
    try:
        batch_1_workflow = audit.run_phase2_generated_observation_workflow(
            root, "batch-01-anatomy"
        )
        write_phase2_generated_manifest_fixture(
            root, "batch-01-anatomy", batch_1_workflow
        )
        audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = {
            "batch-01-anatomy": batch_1_workflow["observationSha256"]
        }
        batch_2_workflow = audit.run_phase2_generated_observation_workflow(
            root, "batch-02-disease"
        )
        write_phase2_generated_manifest_fixture(
            root, "batch-02-disease", batch_2_workflow
        )
        audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = {
            "batch-01-anatomy": batch_1_workflow["observationSha256"],
            "batch-02-disease": batch_2_workflow["observationSha256"],
        }
        rewrite_phase2_fixture_note(
            root,
            "batch-03-pattern",
            "brain-tumor-imaging",
        )
        batch_3_workflow = audit.run_phase2_generated_observation_workflow(
            root, "batch-03-pattern"
        )
        write_phase2_generated_manifest_fixture(
            root, "batch-03-pattern", batch_3_workflow
        )
    finally:
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_baseline_trust
        audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
            original_observation_trust
        )
    return (
        assignment_path,
        baseline_digests,
        batch_1_workflow,
        batch_2_workflow,
        batch_3_workflow,
    )


def test_phase2_assignment_is_complete_deterministic_and_validated() -> None:
    inventory = phase2_inventory_fixture()

    first = audit.build_phase2_assignment(inventory)
    second = audit.build_phase2_assignment(deepcopy(inventory))
    active = [batch for batch in first["batches"] if batch["state"] == "active"]
    scheduled = [batch for batch in first["batches"] if batch["state"] == "scheduled"]

    assert first == second
    assert canonical_sha256(first) == canonical_sha256(second)
    synchronized = audit.synchronize_phase2_inventory(inventory, first)
    assert audit.validate_phase2_assignment(first, synchronized) == []
    assert [batch["id"] for batch in active] == [
        "batch-01-anatomy",
        "batch-02-disease",
        "batch-03-pattern",
    ]
    assert sum(len(batch["slugs"]) for batch in active) == 30
    assert sum(len(batch["slugs"]) for batch in scheduled) == 176
    assert all(
        len(batch["slugs"]) == 10
        or batch is [
            candidate for candidate in scheduled if candidate["type"] == batch["type"]
        ][-1]
        for batch in scheduled
    )


def test_phase2_assignment_rejects_inventory_batch_status_sync_mismatch() -> None:
    inventory = phase2_inventory_fixture()
    assignment = audit.build_phase2_assignment(inventory)
    assignment_by_slug = {
        slug: batch["id"]
        for batch in assignment["batches"]
        for slug in batch["slugs"]
    }
    for entry in inventory["notes"]:
        if entry["slug"] in audit.PILOT_SLUGS:
            continue
        entry["batch"] = assignment_by_slug[entry["slug"]]
        entry["status"] = "scheduled-not-started"

    mismatched = next(
        entry for entry in inventory["notes"] if entry["slug"] not in audit.PILOT_SLUGS
    )
    mismatched["batch"] = "unassigned"
    mismatched["status"] = "pending"

    codes = {
        finding.code
        for finding in audit.validate_phase2_assignment(assignment, inventory)
    }

    assert "phase2-assignment-inventory-mismatch" in codes


def test_phase2_inventory_synchronization_preserves_pilots_and_immutable_content() -> None:
    inventory = phase2_inventory_fixture()
    assignment = audit.build_phase2_assignment(inventory)
    original_by_slug = {
        entry["slug"]: deepcopy(entry) for entry in inventory["notes"]
    }
    pilot_before = [
        deepcopy(entry)
        for entry in inventory["notes"]
        if entry["slug"] in audit.PILOT_SLUGS
    ]
    synchronize = getattr(
        audit,
        "synchronize_phase2_inventory",
        lambda _inventory, _assignment: {},
    )

    synchronized = synchronize(inventory, assignment)

    assert len(synchronized["notes"]) == 216
    pilot_after = [
        entry
        for entry in synchronized["notes"]
        if entry["slug"] in audit.PILOT_SLUGS
    ]
    assert canonical_sha256(pilot_after) == canonical_sha256(pilot_before)
    assignment_by_slug = {
        slug: batch["id"]
        for batch in assignment["batches"]
        for slug in batch["slugs"]
    }
    for entry in synchronized["notes"]:
        original = original_by_slug[entry["slug"]]
        if entry["slug"] in audit.PILOT_SLUGS:
            assert entry == original
            continue
        assert entry["batch"] == assignment_by_slug[entry["slug"]]
        assert entry["status"] == "scheduled-not-started"
        assert {
            key: value
            for key, value in entry.items()
            if key not in {"batch", "status"}
        } == {
            key: value
            for key, value in original.items()
            if key not in {"batch", "status"}
        }


def test_phase2_assignment_regeneration_emits_canonical_identical_bytes() -> None:
    inventory = phase2_inventory_fixture()
    build_bytes = getattr(
        audit,
        "build_phase2_assignment_bytes",
        lambda _inventory: b"",
    )

    first = build_bytes(inventory)
    second = build_bytes(deepcopy(inventory))

    assert first == second
    assert first.endswith(b"\n")
    assert json.loads(first) == audit.build_phase2_assignment(inventory)


def test_phase2_assignment_counts_are_exact_for_synchronized_production() -> None:
    inventory = phase2_inventory_fixture()
    assignment = audit.build_phase2_assignment(inventory)
    synchronize = getattr(
        audit,
        "synchronize_phase2_inventory",
        lambda _inventory, _assignment: {},
    )
    count_assignment = getattr(
        audit,
        "phase2_assignment_counts",
        lambda _assignment, _inventory: {},
    )

    synchronized = synchronize(inventory, assignment)

    assert count_assignment(assignment, synchronized) == {
        "total": 216,
        "pilot": 10,
        "nonPilot": 206,
        "active": 30,
        "scheduled": 176,
    }


def test_phase2_synchronized_inventory_satisfies_closed_inventory_schema() -> None:
    source_inventory = phase2_inventory_fixture()
    assignment = audit.build_phase2_assignment(source_inventory)
    synchronized = audit.synchronize_phase2_inventory(source_inventory, assignment)

    assert audit.validate_inventory(synchronized) == []


def test_phase2_assignment_reports_stable_inventory_membership_order_and_path_codes() -> None:
    inventory = phase2_inventory_fixture()
    assignment = audit.build_phase2_assignment(inventory)
    inventory = audit.synchronize_phase2_inventory(inventory, assignment)

    changed_inventory = deepcopy(inventory)
    changed_entry = next(
        entry for entry in changed_inventory["notes"] if entry["batch"] != "batch-00"
    )
    changed_entry["originalSha256"] = "f" * 64
    assert "phase2-assignment-inventory-mismatch" in {
        finding.code
        for finding in audit.validate_phase2_assignment(assignment, changed_inventory)
    }

    substituted = deepcopy(assignment)
    active = next(
        batch for batch in substituted["batches"] if batch["id"] == "batch-03-pattern"
    )
    replacement = next(
        batch["slugs"][0]
        for batch in substituted["batches"]
        if batch["state"] == "scheduled" and batch["type"] == "pattern-ddx"
    )
    active["slugs"][0] = replacement
    assert "phase2-assignment-membership" in {
        finding.code
        for finding in audit.validate_phase2_assignment(substituted, inventory)
    }

    reordered = deepcopy(assignment)
    scheduled = next(batch for batch in reordered["batches"] if batch["state"] == "scheduled")
    scheduled["slugs"] = list(reversed(scheduled["slugs"]))
    assert "phase2-assignment-nondeterministic" in {
        finding.code for finding in audit.validate_phase2_assignment(reordered, inventory)
    }

    unsafe_inventory = deepcopy(inventory)
    unsafe_entry = next(
        entry for entry in unsafe_inventory["notes"] if entry["batch"] != "batch-00"
    )
    unsafe_entry["path"] = "../outside.md"
    assert "phase2-path-invalid" in {
        finding.code
        for finding in audit.validate_phase2_assignment(assignment, unsafe_inventory)
    }


def test_phase2_checked_assignment_rejects_duplicate_missing_and_type_drift() -> None:
    source_inventory = phase2_inventory_fixture()
    assignment = audit.build_phase2_assignment(source_inventory)
    inventory = audit.synchronize_phase2_inventory(source_inventory, assignment)

    duplicate_and_missing = deepcopy(assignment)
    scheduled = next(
        batch
        for batch in duplicate_and_missing["batches"]
        if batch["state"] == "scheduled"
    )
    scheduled["slugs"][1] = scheduled["slugs"][0]
    assert "phase2-assignment-membership" in {
        finding.code
        for finding in audit.validate_phase2_assignment(
            duplicate_and_missing, inventory
        )
    }

    mixed_type = deepcopy(assignment)
    anatomy = next(
        batch
        for batch in mixed_type["batches"]
        if batch["state"] == "scheduled"
        and batch["type"] == "anatomy-measurement-management"
    )
    disease = next(
        batch
        for batch in mixed_type["batches"]
        if batch["state"] == "scheduled" and batch["type"] == "disease"
    )
    anatomy["slugs"][0], disease["slugs"][0] = (
        disease["slugs"][0],
        anatomy["slugs"][0],
    )
    mixed_type_codes = {
        finding.code
        for finding in audit.validate_phase2_assignment(mixed_type, inventory)
    }
    assert {
        "phase2-assignment-membership",
        "phase2-assignment-nondeterministic",
    } <= mixed_type_codes

    type_drift = deepcopy(inventory)
    active_slugs = {
        slug
        for contract in audit.ACTIVE_PHASE2A_BATCHES.values()
        for slug in contract["slugs"]
    }
    drifted = next(
        entry
        for entry in type_drift["notes"]
        if entry["slug"] not in audit.PILOT_SLUGS
        and entry["slug"] not in active_slugs
        and entry["type"] == "disease"
    )
    drifted["type"] = "pattern-ddx"
    assert "phase2-assignment-inventory-mismatch" in {
        finding.code
        for finding in audit.validate_phase2_assignment(assignment, type_drift)
    }


def test_phase2_assignment_rejects_mutable_pilot_nonpilot_batch_swap() -> None:
    inventory = phase2_inventory_fixture()
    assignment = audit.build_phase2_assignment(inventory)
    inventory = audit.synchronize_phase2_inventory(inventory, assignment)
    pilot = next(
        entry for entry in inventory["notes"] if entry["slug"] in audit.PILOT_SLUGS
    )
    active_slugs = {
        slug
        for contract in audit.ACTIVE_PHASE2A_BATCHES.values()
        for slug in contract["slugs"]
    }
    scheduled = next(
        entry
        for entry in inventory["notes"]
        if entry["slug"] not in audit.PILOT_SLUGS
        and entry["slug"] not in active_slugs
    )
    pilot["batch"], scheduled["batch"] = scheduled["batch"], pilot["batch"]

    assignment = audit.build_phase2_assignment(inventory)
    codes = {
        finding.code
        for finding in audit.validate_phase2_assignment(assignment, inventory)
    }

    assert "phase2-assignment-membership" in codes
    assigned_slugs = {
        slug for batch in assignment["batches"] for slug in batch["slugs"]
    }
    assert scheduled["slug"] in assigned_slugs
    assert pilot["slug"] not in assigned_slugs


def test_phase2_assignment_rejects_duplicate_pilot_and_217_rows() -> None:
    inventory = phase2_inventory_fixture()
    valid_assignment = audit.build_phase2_assignment(inventory)
    inventory = audit.synchronize_phase2_inventory(inventory, valid_assignment)
    duplicate = deepcopy(
        next(
            entry
            for entry in inventory["notes"]
            if entry["slug"] in audit.PILOT_SLUGS
        )
    )
    inventory["notes"].append(duplicate)

    try:
        audit.build_phase2_assignment(inventory)
    except ValueError:
        generation_failed = True
    else:
        generation_failed = False
    codes = {
        finding.code
        for finding in audit.validate_phase2_assignment(
            valid_assignment, inventory
        )
    }

    assert generation_failed
    assert "phase2-assignment-membership" in codes


def test_phase2_batch_context_is_immutable_root_relative_and_relocation_stable() -> None:
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        canonical = base / "canonical"
        shadow = base / "relocated" / "checkout"
        canonical.mkdir(parents=True)
        assignment_path, baseline_digest = write_phase2_api_fixture(canonical)
        shutil.copytree(canonical, shadow)
        original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
            "batch-01-anatomy": baseline_digest
        }
        try:
            canonical_context = audit.load_phase2_batch(
                canonical, assignment_path, "batch-01-anatomy"
            )
            shadow_context = audit.load_phase2_batch(
                shadow, assignment_path, "batch-01-anatomy"
            )
            canonical_findings = audit.validate_baseline_lock(canonical_context)
            shadow_findings = audit.validate_baseline_lock(shadow_context)
            canonical_manifest = audit.build_phase2_generated_manifest(
                canonical,
                "batch-01-anatomy",
                **phase2_manifest_observations(canonical),
            )
            shadow_manifest = audit.build_phase2_generated_manifest(
                shadow,
                "batch-01-anatomy",
                **phase2_manifest_observations(shadow),
            )
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust

    assert canonical_findings == shadow_findings == []
    assert canonical_manifest == shadow_manifest
    assert canonical_context.assignment_path.as_posix() == (
        "docs/reports/nr-summary-rewrite/phase2-assignment.json"
    )
    assert canonical_context.baseline_path.as_posix().startswith(
        "docs/reports/nr-summary-rewrite/phase2a/baselines/"
    )
    try:
        canonical_context.batch = {}
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("BatchContext must be an immutable dataclass")


def test_phase2_trust_and_explicit_root_path_attacks_have_stable_failures() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assignment_path, baseline_digest = write_phase2_api_fixture(root)
        original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
            "batch-01-anatomy": baseline_digest
        }
        try:
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            baseline_file = root / context.baseline_path
            baseline = json.loads(baseline_file.read_text(encoding="utf-8"))
            baseline["notes"][0]["originalSha256"] = "f" * 64
            baseline_file.write_text(json.dumps(baseline), encoding="utf-8")
            mutated = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            codes = {
                finding.code for finding in audit.validate_baseline_lock(mutated)
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust

        assert "phase2-trusted-batch-lock-mismatch" in codes
        try:
            audit.load_phase2_batch(
                root, (root / assignment_path).resolve(), "batch-01-anatomy"
            )
        except audit.Phase2LoadError as error:
            assert error.code == "phase2-path-invalid"
            assert not Path(error.path).is_absolute()
        else:
            raise AssertionError("Absolute assignment paths must be rejected")


def test_phase2_explicit_root_assignment_cli_matches_relocated_checkout() -> None:
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        roots = (base / "canonical", base / "shadow")
        outputs = []
        for root in roots:
            report_root = root / "docs" / "reports" / "nr-summary-rewrite"
            report_root.mkdir(parents=True)
            inventory = phase2_inventory_fixture()
            assignment = audit.build_phase2_assignment(inventory)
            inventory = audit.synchronize_phase2_inventory(inventory, assignment)
            (report_root / "inventory.json").write_text(
                json.dumps(inventory), encoding="utf-8"
            )
            (report_root / "phase2-assignment.json").write_text(
                json.dumps(assignment), encoding="utf-8"
            )
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                exit_code = audit.main(
                    [
                        "validate-assignment",
                        "--repo-root",
                        str(root),
                        "--inventory",
                        "docs/reports/nr-summary-rewrite/inventory.json",
                        "--assignment",
                        "docs/reports/nr-summary-rewrite/phase2-assignment.json",
                    ]
                )
            outputs.append((exit_code, output.getvalue()))

    assert outputs[0] == outputs[1]
    assert outputs[0][0] == 0
    assert "NR total: 216" in outputs[0][1]
    assert "Phase 1 pilots: 10" in outputs[0][1]
    assert "Phase 2 non-pilots: 206" in outputs[0][1]
    assert "Phase 2A active: 30" in outputs[0][1]
    assert "Scheduled: 176" in outputs[0][1]


def test_phase2_baseline_batch_cli_and_generated_keypoints_gate() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assignment_path, baseline_digest = write_phase2_api_fixture(root)
        original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        original_observation_trust = (
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256
        )
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
            "batch-01-anatomy": baseline_digest
        }
        try:
            workflow = audit.run_phase2_generated_observation_workflow(
                root, "batch-01-anatomy"
            )
            manifest_path = (
                root
                / "docs"
                / "reports"
                / "nr-summary-rewrite"
                / "phase2a"
                / "generated"
                / "batch-01-anatomy.json"
            )
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps(workflow["manifest"]), encoding="utf-8"
            )
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = {
                "batch-01-anatomy": workflow["observationSha256"]
            }
            common = [
                "--repo-root",
                str(root),
                "--assignment",
                assignment_path.as_posix(),
                "--batch",
                "batch-01-anatomy",
            ]
            baseline_output = io.StringIO()
            with redirect_stdout(baseline_output), redirect_stderr(baseline_output):
                baseline_exit = audit.main(["validate-baseline", *common])
            batch_output = io.StringIO()
            with redirect_stdout(batch_output), redirect_stderr(batch_output):
                batch_exit = audit.main(
                    [
                        "validate-batch",
                        *common,
                        "--check-source-hashes",
                        "--check-generated",
                    ]
                )

            selected_slug = audit.ACTIVE_PHASE2A_BATCHES["batch-01-anatomy"][
                "slugs"
            ][0]
            detail_path = root / "data" / "concepts" / f"{selected_slug}.json"
            detail = json.loads(detail_path.read_text(encoding="utf-8"))
            detail["keyPoints"] = ["wrong"]
            detail_path.write_text(json.dumps(detail), encoding="utf-8")
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            attack_codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context, check_source_hashes=True, check_generated=True
                )
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
                original_observation_trust
            )

    assert baseline_exit == batch_exit == 0
    assert baseline_output.getvalue() == batch_output.getvalue() == "[]\n"
    assert "generated-keypoints-mismatch" in attack_codes
    assert "generated-manifest-mismatch" in attack_codes


def test_phase2_batch_separates_pre_edit_source_gate_from_rewrite_validation() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assignment_path, baseline_digest = write_phase2_api_fixture(root)
        slug = audit.ACTIVE_PHASE2A_BATCHES["batch-01-anatomy"]["slugs"][0]
        (root / "vault" / "concepts" / f"{slug}.md").write_text(
            NR_REWRITE_TEXT, encoding="utf-8", newline=""
        )
        evidence_path = (
            root
            / "docs"
            / "reports"
            / "nr-summary-rewrite"
            / "phase2a"
            / "evidence"
            / "batch-01-anatomy.json"
        )
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["notes"][0]["rewrittenSummary"] = NR_REWRITE_SUMMARY
        evidence["notes"][0]["summaryBulletEvidence"] = [
            "**Label**: Rewritten fact."
        ]
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
            "batch-01-anatomy": baseline_digest
        }
        try:
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            rewrite_codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context, check_source_hashes=False, check_generated=False
                )
            }
            pre_edit_codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context, check_source_hashes=True, check_generated=False
                )
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust

    assert "phase2-source-hash-mismatch" not in rewrite_codes
    assert "phase2-lossless-summary-mismatch" not in rewrite_codes
    assert "evidence-rewritten-summary-mismatch" not in rewrite_codes
    assert {
        "phase2-source-hash-mismatch",
        "phase2-lossless-summary-mismatch",
    } <= pre_edit_codes


def test_phase2_evidence_rejects_shrunken_membership_and_forged_workflow() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assignment_path, baseline_digest = write_phase2_api_fixture(root)
        evidence_path = (
            root
            / "docs"
            / "reports"
            / "nr-summary-rewrite"
            / "phase2a"
            / "evidence"
            / "batch-01-anatomy.json"
        )
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["notes"] = evidence["notes"][:1]
        evidence["workflow"].update(
            {
                "sequence": 99,
                "predecessor": "forged-predecessor",
                "implementer": "",
                "reviewer": "",
                "reviewStatus": "approved",
                "reviewedBaselineSha256": "f" * 64,
            }
        )
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
            "batch-01-anatomy": baseline_digest
        }
        try:
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context, check_source_hashes=False, check_generated=False
                )
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust

    assert {
        "phase2-evidence-schema",
        "phase2-review-sequence",
        "phase2-reviewer-conflict",
    } <= codes


def test_phase2_reviewer_identity_requires_canonical_traceable_run_ids() -> None:
    invalid_pairs = (
        ("task-3", "/root/task-3"),
        ("task_3", "/root/task_3"),
        ("/root/task_3", " /root/task_3 "),
        ("/root/task_3", "/root/task_3\t"),
        ("/root/TASK_3", "/root/task_4"),
        ("/root/task_3\x00", "/root/task_4"),
        ("/root/", "/root/task_4"),
        ("/root//task_3", "/root/task_4"),
        ("/root/./task_3", "/root/task_4"),
        ("/root/../task_3", "/root/task_4"),
        ("/root/task-3", "/root/task_4"),
        (r"\root\task_3", "/root/task_4"),
        ("//root/task_3", "/root/task_4"),
        ("/root/task_3/", "/root/task_4"),
    )
    for implementer, reviewer in invalid_pairs:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assignment_path, baseline_digest = write_phase2_api_fixture(root)
            evidence_path = (
                root
                / "docs"
                / "reports"
                / "nr-summary-rewrite"
                / "phase2a"
                / "evidence"
                / "batch-01-anatomy.json"
            )
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["workflow"]["implementer"] = implementer
            evidence["workflow"]["reviewer"] = reviewer
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
                "batch-01-anatomy": baseline_digest
            }
            try:
                context = audit.load_phase2_batch(
                    root, assignment_path, "batch-01-anatomy"
                )
                codes = {
                    finding.code
                    for finding in audit.validate_phase2_batch(
                        context,
                        check_source_hashes=False,
                        check_generated=False,
                    )
                }
            finally:
                audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust
        assert "phase2-reviewer-conflict" in codes, (
            implementer,
            reviewer,
        )

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assignment_path, baseline_digest = write_phase2_api_fixture(root)
        evidence_path = (
            root
            / "docs"
            / "reports"
            / "nr-summary-rewrite"
            / "phase2a"
            / "evidence"
            / "batch-01-anatomy.json"
        )
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["workflow"]["implementer"] = "/root/phase2a/task_3"
        evidence["workflow"]["reviewer"] = "/root/phase2a/reviewer_3"
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
            "batch-01-anatomy": baseline_digest
        }
        try:
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            valid_codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context,
                    check_source_hashes=False,
                    check_generated=False,
                )
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust

    assert "phase2-reviewer-conflict" not in valid_codes


def test_phase2_verified_review_requires_approval_and_predecessor_evidence() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assignment_path, baseline_digest = write_phase2_api_fixture(root)
        evidence_path = (
            root
            / "docs"
            / "reports"
            / "nr-summary-rewrite"
            / "phase2a"
            / "evidence"
            / "batch-01-anatomy.json"
        )
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["workflow"]["reviewStatus"] = "not-started"
        evidence["workflow"]["reviewedBaselineSha256"] = None
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
            "batch-01-anatomy": baseline_digest
        }
        try:
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            unapproved_codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context, check_source_hashes=False, check_generated=False
                )
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assignment_path, baseline_digest = write_phase2_api_fixture(
            root, "batch-02-disease"
        )
        evidence_path = (
            root
            / "docs"
            / "reports"
            / "nr-summary-rewrite"
            / "phase2a"
            / "evidence"
            / "batch-02-disease.json"
        )
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["workflow"].update(
            {
                "sequence": 2,
                "predecessor": "batch-01-anatomy",
                "reviewStatus": "approved",
                "reviewedBaselineSha256": baseline_digest,
            }
        )
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
            "batch-02-disease": baseline_digest
        }
        try:
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-02-disease"
            )
            missing_predecessor_codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context, check_source_hashes=False, check_generated=False
                )
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust

    assert "phase2-review-sequence" in unapproved_codes
    assert "phase2-review-sequence" in missing_predecessor_codes


def test_phase2_evidence_derives_current_footnotes_and_source_definitions() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assignment_path, baseline_digest = write_phase2_api_fixture(root)
        slug = audit.ACTIVE_PHASE2A_BATCHES["batch-01-anatomy"]["slugs"][0]
        note_path = root / "vault" / "concepts" / f"{slug}.md"
        note_path.write_text(
            NR_DEMO_TEXT.replace("[^1]: Example.\n", ""),
            encoding="utf-8",
            newline="",
        )
        original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
            "batch-01-anatomy": baseline_digest
        }
        try:
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context, check_source_hashes=False, check_generated=False
                )
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust

    assert "footnote-undefined" in codes
    assert "evidence-source-definition" in codes
    assert "phase2-evidence-schema" in codes


def test_phase2_manifest_rejects_coordinated_nonselected_and_second_run_attacks() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assignment_path, baseline_digest = write_phase2_api_fixture(root)
        unrelated_slug = "unrelated-detail"
        unrelated = {
            "slug": unrelated_slug,
            "name": "Unrelated",
            "nameZh": "",
            "subspecialty": "NR",
            "checked": False,
            "keyPoints": ["before"],
        }
        unrelated_path = root / "data" / "concepts" / f"{unrelated_slug}.json"
        unrelated_path.write_text(json.dumps(unrelated), encoding="utf-8")
        index_path = root / "data" / "concepts-index.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index["concepts"].append(
            {
                key: unrelated[key]
                for key in ("slug", "name", "nameZh", "subspecialty", "checked")
            }
        )
        index["concepts"].sort(key=lambda entry: entry["slug"])
        index_path.write_text(json.dumps(index), encoding="utf-8")
        manifest_path = (
            root
            / "docs"
            / "reports"
            / "nr-summary-rewrite"
            / "phase2a"
            / "generated"
            / "batch-01-anatomy.json"
        )
        manifest_path.parent.mkdir(parents=True)
        initial_manifest = audit.build_phase2_generated_manifest(
            root,
            "batch-01-anatomy",
            **phase2_manifest_observations(root),
        )
        manifest_path.write_text(json.dumps(initial_manifest), encoding="utf-8")

        unrelated["keyPoints"] = ["coordinated mutation"]
        unrelated_path.write_text(json.dumps(unrelated), encoding="utf-8")
        forged_manifest = audit.build_phase2_generated_manifest(
            root,
            "batch-01-anatomy",
            **phase2_manifest_observations(
                root,
                nonselected_before=initial_manifest["nonselectedAfter"],
            ),
        )
        forged_manifest["secondRun"] = {
            "changedPaths": ["data/concepts/ajcc-8th-head-neck-n-staging.json"],
            "mtimeChangedPaths": [],
        }
        manifest_path.write_text(json.dumps(forged_manifest), encoding="utf-8")
        original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
            "batch-01-anatomy": baseline_digest
        }
        try:
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context, check_source_hashes=False, check_generated=True
                )
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust

    assert "generated-unrelated-write" in codes
    assert "generated-non-idempotent" in codes


def test_phase2_public_manifest_builder_is_read_only_with_empty_registry() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        write_phase2_api_fixture(root)
        before = {
            path.relative_to(root).as_posix(): (
                path.read_bytes(),
                path.stat().st_mtime_ns,
            )
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }
        original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {}
        try:
            audit.build_phase2_generated_manifest(
                root,
                "batch-01-anatomy",
                **phase2_manifest_observations(root),
            )
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust
        after = {
            path.relative_to(root).as_posix(): (
                path.read_bytes(),
                path.stat().st_mtime_ns,
            )
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    assert after == before


def test_phase2_manifest_builder_requires_explicit_build_observations() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        write_phase2_api_fixture(root)
        before = {
            path.relative_to(root).as_posix(): (
                path.read_bytes(),
                path.stat().st_mtime_ns,
            )
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }
        try:
            audit.build_phase2_generated_manifest(
                root, "batch-01-anatomy"
            )
        except audit.Phase2LoadError as error:
            failure_code = error.code
        else:
            failure_code = None
        stale_observations = phase2_manifest_observations(root)
        stale_observations["nonselected_after"] = {
            "data/concepts/ghost.json": "0" * 64
        }
        try:
            audit.build_phase2_generated_manifest(
                root,
                "batch-01-anatomy",
                **stale_observations,
            )
        except audit.Phase2LoadError as error:
            stale_failure_code = error.code
        else:
            stale_failure_code = None
        after = {
            path.relative_to(root).as_posix(): (
                path.read_bytes(),
                path.stat().st_mtime_ns,
            )
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    assert failure_code == "generated-observation-missing"
    assert stale_failure_code == "generated-observation-invalid"
    assert after == before


def test_phase2_statuses_are_closed_and_exactly_derived_from_dispositions() -> None:
    mutations = (
        ("status", "totally-invalid"),
        ("status", "manual-review"),
        ("sourceStatus", "totally-invalid"),
        ("sourceStatus", "conflict"),
        ("root-status", "totally-invalid"),
    )
    for field, value in mutations:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assignment_path, baseline_digest = write_phase2_api_fixture(root)
            evidence_path = (
                root
                / "docs"
                / "reports"
                / "nr-summary-rewrite"
                / "phase2a"
                / "evidence"
                / "batch-01-anatomy.json"
            )
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            entry = evidence["notes"][0]
            fact = entry["facts"][0]
            fact["disposition"] = "research-needed"
            fact_id = fact["id"]
            entry["status"] = "research-needed"
            entry["sourceStatus"] = "research-needed"
            entry["validation"]["factCoverage"] = {
                "total": 1,
                "covered": 0,
                "researchNeeded": 1,
                "manualReview": 0,
            }
            evidence["manualReviewFactIds"] = [fact_id]
            evidence["status"] = "needs-review"
            if field == "root-status":
                evidence["status"] = value
            else:
                entry[field] = value
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
                "batch-01-anatomy": baseline_digest
            }
            try:
                context = audit.load_phase2_batch(
                    root, assignment_path, "batch-01-anatomy"
                )
                codes = {
                    finding.code
                    for finding in audit.validate_phase2_batch(
                        context,
                        check_source_hashes=False,
                        check_generated=False,
                    )
                }
            finally:
                audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust

        assert "phase2-evidence-schema" in codes, (field, value, codes)


def test_phase2_self_attested_no_build_manifest_is_untrusted() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assignment_path, baseline_digest = write_phase2_api_fixture(root)
        manifest = audit.build_phase2_generated_manifest(
            root,
            "batch-01-anatomy",
            **phase2_manifest_observations(root),
        )
        manifest_path = (
            root
            / "docs"
            / "reports"
            / "nr-summary-rewrite"
            / "phase2a"
            / "generated"
            / "batch-01-anatomy.json"
        )
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        original_baseline_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
            "batch-01-anatomy": baseline_digest
        }
        try:
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context,
                    check_source_hashes=False,
                    check_generated=True,
                )
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_baseline_trust

    assert "generated-observation-untrusted" in codes


def test_phase2_gated_two_run_workflow_produces_trusted_observation() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assignment_path, baseline_digest = write_phase2_api_fixture(root)
        original_baseline_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        original_observation_trust = getattr(
            audit, "TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256", None
        )
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
            "batch-01-anatomy": baseline_digest
        }
        try:
            result = audit.run_phase2_generated_observation_workflow(
                root, "batch-01-anatomy"
            )
            manifest = result["manifest"]
            manifest_path = (
                root
                / "docs"
                / "reports"
                / "nr-summary-rewrite"
                / "phase2a"
                / "generated"
                / "batch-01-anatomy.json"
            )
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = {
                "batch-01-anatomy": result["observationSha256"]
            }
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            findings = audit.validate_phase2_batch(
                context,
                check_source_hashes=False,
                check_generated=True,
            )
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_baseline_trust
            if (
                original_observation_trust is None
                and hasattr(audit, "TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256")
            ):
                delattr(audit, "TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256")
            elif original_observation_trust is not None:
                audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
                    original_observation_trust
                )

    assert manifest["firstRun"]["changedPaths"]
    assert manifest["secondRun"] == {
        "changedPaths": [],
        "mtimeChangedPaths": [],
    }
    assert findings == []


def test_phase2_later_trusted_batch_update_preserves_earlier_historical_scope() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (
            assignment_path,
            baseline_digests,
            batch_1_workflow,
            batch_2_workflow,
            batch_3_workflow,
        ) = prepare_phase2_later_update_fixture(root)
        original_baseline_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        original_observation_trust = (
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256
        )
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = baseline_digests
        audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = {
            "batch-01-anatomy": batch_1_workflow["observationSha256"],
            "batch-02-disease": batch_2_workflow["observationSha256"],
            "batch-03-pattern": batch_3_workflow["observationSha256"],
        }
        try:
            batch_3_context = audit.load_phase2_batch(
                root, assignment_path, "batch-03-pattern"
            )
            later_findings = audit.validate_phase2_batch(
                batch_3_context,
                check_source_hashes=False,
                check_generated=True,
            )
            batch_1_context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            earlier_codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    batch_1_context,
                    check_source_hashes=False,
                    check_generated=True,
                )
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_baseline_trust
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
                original_observation_trust
            )

    assert later_findings == []
    assert "generated-manifest-mismatch" not in earlier_codes


def test_phase2_batch3_update_requires_batch2_generated_observation_seal() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (
            assignment_path,
            baseline_digests,
            batch_1_workflow,
            batch_2_workflow,
            batch_3_workflow,
        ) = prepare_phase2_later_update_fixture(root)
        original_baseline_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        original_observation_trust = (
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256
        )
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = baseline_digests
        try:
            failure_codes = []
            direct_batch_3_failure_codes = []
            for batch_2_seal in (None, "f" * 64):
                observation_trust = {
                    "batch-01-anatomy": batch_1_workflow[
                        "observationSha256"
                    ],
                    "batch-03-pattern": batch_3_workflow[
                        "observationSha256"
                    ],
                }
                if batch_2_seal is not None:
                    assert (
                        batch_2_seal
                        != batch_2_workflow["observationSha256"]
                    )
                    observation_trust["batch-02-disease"] = batch_2_seal
                audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
                    observation_trust
                )
                context = audit.load_phase2_batch(
                    root, assignment_path, "batch-01-anatomy"
                )
                failure_codes.append(
                    {
                        finding.code
                        for finding in audit.validate_phase2_batch(
                            context,
                            check_source_hashes=False,
                            check_generated=True,
                        )
                    }
                )
                batch_3_context = audit.load_phase2_batch(
                    root, assignment_path, "batch-03-pattern"
                )
                direct_batch_3_failure_codes.append(
                    {
                        finding.code
                        for finding in audit.validate_phase2_batch(
                            batch_3_context,
                            check_source_hashes=False,
                            check_generated=True,
                        )
                    }
                )
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_baseline_trust
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
                original_observation_trust
            )

    assert all(
        "generated-manifest-mismatch" in codes
        for codes in failure_codes
    )
    assert all(
        "generated-manifest-mismatch" in codes
        for codes in direct_batch_3_failure_codes
    )


def test_phase2_later_update_without_independent_trust_fails_earlier_batch() -> None:
    cases = (
        ("reviewer", "phase2-reviewer-conflict"),
        ("evidence", "phase2-evidence-schema"),
        ("generated", "generated-observation-untrusted"),
    )
    for invalid_gate, expected_later_code in cases:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (
                assignment_path,
                baseline_digests,
                batch_1_workflow,
                batch_2_workflow,
                batch_3_workflow,
            ) = prepare_phase2_later_update_fixture(root)
            evidence_path = (
                root
                / "docs"
                / "reports"
                / "nr-summary-rewrite"
                / "phase2a"
                / "evidence"
                / "batch-03-pattern.json"
            )
            if invalid_gate in {"reviewer", "evidence"}:
                evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
                if invalid_gate == "reviewer":
                    evidence["workflow"]["reviewer"] = evidence["workflow"][
                        "implementer"
                    ]
                else:
                    evidence["status"] = "needs-review"
                evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

            observation_trust = {
                "batch-01-anatomy": batch_1_workflow["observationSha256"],
                "batch-02-disease": batch_2_workflow["observationSha256"],
                "batch-03-pattern": batch_3_workflow["observationSha256"],
            }
            if invalid_gate == "generated":
                observation_trust.pop("batch-03-pattern")
            original_baseline_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
            original_observation_trust = (
                audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256
            )
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = baseline_digests
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = observation_trust
            try:
                batch_3_context = audit.load_phase2_batch(
                    root, assignment_path, "batch-03-pattern"
                )
                later_codes = {
                    finding.code
                    for finding in audit.validate_phase2_batch(
                        batch_3_context,
                        check_source_hashes=False,
                        check_generated=True,
                    )
                }
                batch_1_context = audit.load_phase2_batch(
                    root, assignment_path, "batch-01-anatomy"
                )
                earlier_codes = {
                    finding.code
                    for finding in audit.validate_phase2_batch(
                        batch_1_context,
                        check_source_hashes=False,
                        check_generated=True,
                    )
                }
            finally:
                audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_baseline_trust
                audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
                    original_observation_trust
                )

        assert expected_later_code in later_codes, invalid_gate
        assert "generated-manifest-mismatch" in earlier_codes, invalid_gate


def test_phase2_unassigned_current_detail_drift_still_fails_earlier_batch() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (
            assignment_path,
            baseline_digests,
            batch_1_workflow,
            batch_2_workflow,
            batch_3_workflow,
        ) = prepare_phase2_later_update_fixture(root)
        rogue_detail = {
            "slug": "rogue-detail",
            "name": "Rogue",
            "nameZh": "",
            "subspecialty": "NR",
            "checked": False,
            "keyPoints": ["rogue"],
        }
        (root / "data" / "concepts" / "rogue-detail.json").write_text(
            json.dumps(rogue_detail),
            encoding="utf-8",
        )
        write_phase2_current_index(root)
        original_baseline_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        original_observation_trust = (
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256
        )
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = baseline_digests
        audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = {
            "batch-01-anatomy": batch_1_workflow["observationSha256"],
            "batch-02-disease": batch_2_workflow["observationSha256"],
            "batch-03-pattern": batch_3_workflow["observationSha256"],
        }
        try:
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context,
                    check_source_hashes=False,
                    check_generated=True,
                )
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_baseline_trust
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
                original_observation_trust
            )

    assert "generated-manifest-mismatch" in codes


def test_phase2_earlier_selected_detail_drift_still_fails() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (
            assignment_path,
            baseline_digests,
            batch_1_workflow,
            batch_2_workflow,
            batch_3_workflow,
        ) = prepare_phase2_later_update_fixture(root)
        slug = audit.ACTIVE_PHASE2A_BATCHES["batch-01-anatomy"]["slugs"][0]
        detail_path = root / "data" / "concepts" / f"{slug}.json"
        detail = json.loads(detail_path.read_text(encoding="utf-8"))
        detail["forgedField"] = True
        detail_path.write_text(json.dumps(detail), encoding="utf-8")
        original_baseline_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        original_observation_trust = (
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256
        )
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = baseline_digests
        audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = {
            "batch-01-anatomy": batch_1_workflow["observationSha256"],
            "batch-02-disease": batch_2_workflow["observationSha256"],
            "batch-03-pattern": batch_3_workflow["observationSha256"],
        }
        try:
            context = audit.load_phase2_batch(
                root, assignment_path, "batch-01-anatomy"
            )
            codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context,
                    check_source_hashes=False,
                    check_generated=True,
                )
            }
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_baseline_trust
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
                original_observation_trust
            )

    assert "generated-keypoints-mismatch" not in codes
    assert "generated-manifest-mismatch" in codes


def test_phase2_forged_or_incoherent_current_index_fails_after_later_update() -> None:
    for mutation in ("coherent-forged-bytes", "incoherent-content"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (
                assignment_path,
                baseline_digests,
                batch_1_workflow,
                batch_2_workflow,
                batch_3_workflow,
            ) = prepare_phase2_later_update_fixture(root)
            index_path = root / "data" / "concepts-index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            if mutation == "incoherent-content":
                index["concepts"][0]["name"] = "forged-name"
            index_path.write_text(json.dumps(index), encoding="utf-8")
            original_baseline_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
            original_observation_trust = (
                audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256
            )
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = baseline_digests
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = {
                "batch-01-anatomy": batch_1_workflow["observationSha256"],
                "batch-02-disease": batch_2_workflow["observationSha256"],
                "batch-03-pattern": batch_3_workflow["observationSha256"],
            }
            try:
                context = audit.load_phase2_batch(
                    root, assignment_path, "batch-01-anatomy"
                )
                codes = {
                    finding.code
                    for finding in audit.validate_phase2_batch(
                        context,
                        check_source_hashes=False,
                        check_generated=True,
                    )
                }
            finally:
                audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_baseline_trust
                audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
                    original_observation_trust
                )

        assert "generated-manifest-mismatch" in codes, mutation


def test_phase2_authorized_later_update_is_relocation_stable() -> None:
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        roots = (base / "canonical", base / "relocated" / "checkout")
        fixtures = []
        for root in roots:
            root.mkdir(parents=True)
            fixtures.append(prepare_phase2_later_update_fixture(root))
        (
            canonical_assignment,
            canonical_baselines,
            canonical_batch_1,
            canonical_batch_2,
            canonical_batch_3,
        ) = fixtures[0]
        (
            relocated_assignment,
            relocated_baselines,
            relocated_batch_1,
            relocated_batch_2,
            relocated_batch_3,
        ) = fixtures[1]
        assert canonical_assignment == relocated_assignment
        assert canonical_baselines == relocated_baselines
        assert (
            canonical_batch_1["observationSha256"]
            == relocated_batch_1["observationSha256"]
        )
        assert (
            canonical_batch_2["observationSha256"]
            == relocated_batch_2["observationSha256"]
        )
        assert (
            canonical_batch_3["observationSha256"]
            == relocated_batch_3["observationSha256"]
        )

        original_baseline_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        original_observation_trust = (
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256
        )
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = canonical_baselines
        audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = {
            "batch-01-anatomy": canonical_batch_1["observationSha256"],
            "batch-02-disease": canonical_batch_2["observationSha256"],
            "batch-03-pattern": canonical_batch_3["observationSha256"],
        }
        try:
            finding_codes = []
            cli_results = []
            for root, assignment_path in zip(
                roots,
                (canonical_assignment, relocated_assignment),
            ):
                context = audit.load_phase2_batch(
                    root, assignment_path, "batch-01-anatomy"
                )
                finding_codes.append(
                    [
                        finding.code
                        for finding in audit.validate_phase2_batch(
                            context,
                            check_source_hashes=False,
                            check_generated=True,
                        )
                    ]
                )
                output = io.StringIO()
                with redirect_stdout(output), redirect_stderr(output):
                    exit_code = audit.main(
                        [
                            "validate-batch",
                            "--repo-root",
                            str(root),
                            "--assignment",
                            assignment_path.as_posix(),
                            "--batch",
                            "batch-01-anatomy",
                            "--check-generated",
                        ]
                    )
                cli_results.append((exit_code, output.getvalue()))
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_baseline_trust
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
                original_observation_trust
            )

    assert finding_codes == [[], []]
    assert cli_results[0] == cli_results[1]
    assert cli_results[0][0] == 0


def test_phase2_two_run_workflow_fails_before_write_when_trust_gate_fails() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        write_phase2_api_fixture(root)
        before = {
            path.relative_to(root).as_posix(): (
                path.read_bytes(),
                path.stat().st_mtime_ns,
            )
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }
        original_baseline_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {}
        try:
            audit.run_phase2_generated_observation_workflow(
                root, "batch-01-anatomy"
            )
        except audit.Phase2LoadError as error:
            failure_code = error.code
        else:
            failure_code = None
        finally:
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_baseline_trust
        after = {
            path.relative_to(root).as_posix(): (
                path.read_bytes(),
                path.stat().st_mtime_ns,
            )
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    assert failure_code == "phase2-trusted-batch-lock-mismatch"
    assert after == before


def test_phase2_later_workflow_requires_generated_predecessor_before_write() -> None:
    for predecessor_state in ("missing", "wrong-seal"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assignment_path, baseline_digests = (
                write_phase2_approved_chain_fixture(root)
            )
            original_baseline_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
            original_observation_trust = (
                audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256
            )
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = baseline_digests
            try:
                if predecessor_state == "missing":
                    audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = {}
                else:
                    predecessor_workflow = (
                        audit.run_phase2_generated_observation_workflow(
                            root, "batch-01-anatomy"
                        )
                    )
                    write_phase2_generated_manifest_fixture(
                        root,
                        "batch-01-anatomy",
                        predecessor_workflow,
                    )
                    assert predecessor_workflow["observationSha256"] != "f" * 64
                    audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = {
                        "batch-01-anatomy": "f" * 64
                    }

                batch_id = "batch-02-disease"
                rewrite_phase2_fixture_note(
                    root,
                    batch_id,
                    audit.ACTIVE_PHASE2A_BATCHES[batch_id]["slugs"][0],
                )
                context = audit.load_phase2_batch(
                    root, assignment_path, batch_id
                )
                before = audit._phase2_generated_snapshot(context)
                try:
                    audit.run_phase2_generated_observation_workflow(
                        root, batch_id
                    )
                except audit.Phase2LoadError as error:
                    failure_code = error.code
                else:
                    failure_code = None
                after = audit._phase2_generated_snapshot(context)
            finally:
                audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = (
                    original_baseline_trust
                )
                audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
                    original_observation_trust
                )

        assert failure_code == "phase2-review-sequence", predecessor_state
        assert audit._phase2_snapshot_delta(before, after) == {
            "changedPaths": [],
            "mtimeChangedPaths": [],
        }, predecessor_state


def test_phase2_assignment_path_attack_cli_is_relocation_stable() -> None:
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        outputs = []
        for root in (base / "canonical", base / "relocated" / "shadow"):
            root.mkdir(parents=True)
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                exit_code = audit.main(
                    [
                        "validate-assignment",
                        "--repo-root",
                        str(root),
                        "--inventory",
                        "../inventory.json",
                        "--assignment",
                        "docs/phase2-assignment.json",
                    ]
                )
            outputs.append((exit_code, output.getvalue()))

    assert outputs[0] == outputs[1]
    assert outputs[0][0] == 1
    assert '"code": "phase2-path-invalid"' in outputs[0][1]
    assert str(base) not in outputs[0][1]


def test_evidence_rejects_unmapped_or_unresolved_fact_units() -> None:
    nr_demo = make_nr_note("demo")
    report = batch_report_fixture()
    report["notes"][0]["factUnits"] = [
        {
            "id": "demo-f01",
            "text": "DWI high signal",
            "sourceRefs": [],
            "disposition": "covered",
        }
    ]
    findings = audit.validate_evidence(report, {"demo": nr_demo})
    codes = {finding.code for finding in findings}
    assert "fact-source-missing" in codes


def test_evidence_rejects_source_ref_not_defined_in_note() -> None:
    nr_demo = make_nr_note("demo")
    report = batch_report_fixture(source_refs=["missing"])
    findings = audit.validate_evidence(report, {"demo": nr_demo})
    assert "fact-source-undefined" in {finding.code for finding in findings}


def test_evidence_rejects_invalid_root_membership_hash_and_snapshot() -> None:
    nr_demo = make_nr_note("demo")
    report = batch_report_fixture()
    report["schemaVersion"] = 2
    report["batch"] = "batch-01"
    report["scope"] = "ABD"
    report["status"] = "verified"
    report["notes"][0]["originalSha256"] = "0" * 64
    report["notes"][0]["originalSummary"] = "changed"
    findings = audit.validate_evidence(report, {"demo": nr_demo})
    codes = {finding.code for finding in findings}
    assert {
        "evidence-schema-version",
        "evidence-batch",
        "evidence-scope",
        "evidence-status",
        "evidence-batch-membership",
        "evidence-hash-mismatch",
        "evidence-summary-mismatch",
    } <= codes


def test_evidence_rejects_malformed_note_and_fact_schema_without_raising() -> None:
    nr_demo = make_nr_note("demo")
    report = batch_report_fixture()
    report["notes"].extend(
        [
            None,
            {"slug": "broken"},
            {
                "slug": "demo",
                "type": "disease",
                "originalSha256": nr_demo.sha256,
                "originalSummary": nr_demo.original_summary,
                "factUnits": [None],
                "sourceStatus": "existing-sufficient",
                "status": "pending",
                "rewrittenSummary": "",
                "validation": {},
            },
        ]
    )
    findings = audit.validate_evidence(report, {"demo": nr_demo})
    codes = {finding.code for finding in findings}
    assert {"evidence-note-schema", "fact-schema", "evidence-duplicate-slug"} <= codes


def test_evidence_rejects_invalid_fact_identity_text_disposition_and_refs() -> None:
    nr_demo = make_nr_note("demo")
    report = batch_report_fixture()
    report["notes"][0]["factUnits"] = [
        {
            "id": "wrong-f01",
            "text": "",
            "sourceRefs": "1",
            "disposition": "unknown",
        },
        {
            "id": "wrong-f01",
            "text": "Second fact.",
            "sourceRefs": ["1"],
            "disposition": "pending",
        },
    ]
    findings = audit.validate_evidence(report, {"demo": nr_demo})
    codes = {finding.code for finding in findings}
    assert {
        "fact-id",
        "fact-id-duplicate",
        "fact-text",
        "fact-source-refs",
        "fact-disposition",
    } <= codes


def test_evidence_requires_research_status_for_explicitly_unresolved_fact() -> None:
    nr_demo = make_nr_note("demo")
    report = batch_report_fixture()
    report["notes"][0]["factUnits"][0]["sourceRefs"] = []
    report["notes"][0]["factUnits"][0]["disposition"] = "research-needed"
    findings = audit.validate_evidence(report, {"demo": nr_demo})
    assert "evidence-source-status" in {finding.code for finding in findings}


def test_evidence_enum_fields_reject_unhashable_json_values_without_raising() -> None:
    nr_demo = make_nr_note("demo")
    mutations = (
        ("type", [], "evidence-note-type"),
        ("sourceStatus", {}, "evidence-source-status"),
        ("status", [], "evidence-note-status"),
        ("disposition", {}, "fact-disposition"),
    )
    for field, invalid_value, expected_code in mutations:
        report = batch_report_fixture()
        if field == "disposition":
            report["notes"][0]["factUnits"][0][field] = invalid_value
        else:
            report["notes"][0][field] = invalid_value
        try:
            findings = audit.validate_evidence(report, {"demo": nr_demo})
        except TypeError as error:
            raise AssertionError(f"{field} raised TypeError for JSON value") from error
        assert expected_code in {finding.code for finding in findings}, field


def test_evidence_accepts_fact_derived_baseline_status_combinations() -> None:
    nr_demo = make_nr_note("demo")
    combinations = (
        ("pending", "pending", "existing-sufficient"),
        ("covered", "pending", "existing-sufficient"),
        ("research-needed", "research-needed", "research-needed"),
        ("research-needed", "research-needed", "conflict"),
        ("manual-review", "manual-review", "research-needed"),
        ("manual-review", "manual-review", "conflict"),
    )
    for disposition, note_status, source_status in combinations:
        report = batch_report_fixture()
        set_fact_state(
            report,
            disposition=disposition,
            note_status=note_status,
            source_status=source_status,
        )
        findings = audit.validate_evidence(report, {"demo": nr_demo})
        status_codes = {
            finding.code
            for finding in findings
            if finding.code in {"evidence-note-status", "evidence-source-status"}
        }
        assert status_codes == set(), (disposition, note_status, source_status, status_codes)


def test_evidence_rejects_statuses_that_contradict_fact_dispositions() -> None:
    nr_demo = make_nr_note("demo")
    contradictions = (
        ("pending", "research-needed", "research-needed", {"evidence-note-status", "evidence-source-status"}),
        ("pending", "pending", "conflict", {"evidence-source-status"}),
        ("research-needed", "manual-review", "research-needed", {"evidence-note-status"}),
        ("manual-review", "research-needed", "research-needed", {"evidence-note-status"}),
        ("manual-review", "manual-review", "existing-sufficient", {"evidence-source-status"}),
    )
    for disposition, note_status, source_status, expected_codes in contradictions:
        report = batch_report_fixture()
        set_fact_state(
            report,
            disposition=disposition,
            note_status=note_status,
            source_status=source_status,
        )
        codes = {
            finding.code
            for finding in audit.validate_evidence(report, {"demo": nr_demo})
        }
        assert expected_codes <= codes, (disposition, note_status, source_status, codes)


def test_evidence_rejects_stale_validation_metadata_and_nonsequential_ids() -> None:
    nr_demo = make_nr_note("demo")
    report = batch_report_fixture()
    report["notes"][0]["factUnits"][0]["id"] = "demo-f02"
    report["notes"][0]["validation"]["factCount"] = 2
    findings = audit.validate_evidence(report, {"demo": nr_demo})
    codes = {finding.code for finding in findings}
    assert {"fact-id-sequence", "evidence-validation"} <= codes


def test_validate_batch_cli_requires_allow_pending_for_baseline() -> None:
    with tempfile.TemporaryDirectory() as directory:
        batch_path, _, _ = write_valid_batch_cli_fixture(Path(directory))
        allowed_exit, allowed_output = run_validate_batch_cli(batch_path, allow_pending=True)
        blocked_exit, blocked_output = run_validate_batch_cli(batch_path, allow_pending=False)

    assert allowed_exit == 0
    assert "Batch notes: 10" in allowed_output
    assert "Missing sources: 0" in allowed_output
    assert blocked_exit == 1
    assert "fact-pending" in blocked_output


def test_validate_batch_cli_supports_explicit_pre_edit_hash_gate() -> None:
    with tempfile.TemporaryDirectory() as directory:
        batch_path, _, _ = write_valid_batch_cli_fixture(Path(directory))
        exit_code, output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
            check_source_hashes=True,
        )

    assert exit_code == 0
    assert "Batch notes: 10" in output
    assert "Missing sources: 0" in output


def test_validate_batch_cli_accepts_final_rewrites_and_explicit_manual_review() -> None:
    with tempfile.TemporaryDirectory() as directory:
        batch_path, _, report = write_valid_batch_cli_fixture(Path(directory))
        report["status"] = "verified"
        for entry in report["notes"]:
            make_entry_final(entry)
        batch_path.write_text(json.dumps(report), encoding="utf-8")
        verified_exit, verified_output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
        )

        report["status"] = "needs-review"
        first = report["notes"][0]
        first_fact = first["factUnits"][0]
        first_fact["disposition"] = "manual-review"
        first["sourceStatus"] = "conflict"
        first["status"] = "manual-review"
        first["validation"]["manualReviewFactIds"] = [first_fact["id"]]
        first["validation"]["factCoverage"] = "fail"
        seal_entry(first)
        batch_path.write_text(json.dumps(report), encoding="utf-8")
        review_exit, review_output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
        )

    assert verified_exit == 0, verified_output
    assert review_exit == 0, review_output


def test_validate_batch_cli_rejects_generated_keypoints_mismatch() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        batch_path, _, report = write_valid_batch_cli_fixture(root)
        report["status"] = "verified"
        for entry in report["notes"]:
            make_entry_final(entry)
        batch_path.write_text(json.dumps(report), encoding="utf-8")

        generated_path = root / "data" / "concepts" / f"{PILOT_SLUGS[0]}.json"
        generated_path.write_text(
            json.dumps({"keyPoints": ["wrong generated bullet"]}),
            encoding="utf-8",
        )
        exit_code, output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
        )

    assert exit_code == 1
    assert '"code": "generated-keypoints-mismatch"' in output


def test_validate_batch_cli_rejects_all_generated_keypoints_shape_failures() -> None:
    mutations = (
        ("missing", lambda path: path.unlink()),
        ("malformed", lambda path: path.write_text("{", encoding="utf-8")),
        ("non-object", lambda path: path.write_text("[]", encoding="utf-8")),
        (
            "absent-keyPoints",
            lambda path: path.write_text(json.dumps({"slug": path.stem}), encoding="utf-8"),
        ),
        (
            "wrong-type-keyPoints",
            lambda path: path.write_text(
                json.dumps({"keyPoints": "**Label**: Demo fact."}),
                encoding="utf-8",
            ),
        ),
    )
    for mutation, mutate in mutations:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            batch_path, _, report = write_valid_batch_cli_fixture(root)
            report["status"] = "verified"
            for entry in report["notes"]:
                make_entry_final(entry)
            batch_path.write_text(json.dumps(report), encoding="utf-8")
            generated_path = (
                root / "data" / "concepts" / f"{PILOT_SLUGS[0]}.json"
            )
            mutate(generated_path)

            exit_code, output = run_validate_batch_cli(
                batch_path,
                allow_pending=False,
            )

        assert exit_code == 1, mutation
        assert '"code": "generated-keypoints-mismatch"' in output, mutation


def test_generated_keypoints_preserve_all_variants_and_subheading_order() -> None:
    note = audit.parse_note_text(
        Path("vault/concepts/dementia-neuroimaging-overview.md"),
        """---
subspecialty: [NR]
---
## Summary — first variant
- **First**: One.[^1]

### Nested classification
- **Nested**: Two.[^2]

## Summary — later variant
- **Later**: Three.[^3]

[^1]: One.
[^2]: Two.
[^3]: Three.
""",
    )

    assert audit._generated_keypoints(note) == [
        "**First**: One.",
        "**Nested**: Two.",
        "**Later**: Three.",
    ]


def test_generated_data_root_is_bound_to_source_checkout_not_shadow_tree() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        batch_path, _, report = write_valid_batch_cli_fixture(root)
        report["status"] = "verified"
        for entry in report["notes"]:
            make_entry_final(entry)
        batch_path.write_text(json.dumps(report), encoding="utf-8")

        shadow = root / "docs" / "data" / "concepts"
        shadow.mkdir(parents=True)
        for slug in PILOT_SLUGS:
            (shadow / f"{slug}.json").write_text(
                json.dumps({"keyPoints": ["shadow tree"]}),
                encoding="utf-8",
            )

        exit_code, output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
        )

    assert exit_code == 0, output


def test_validate_batch_cli_rejects_dangling_generated_index_entry() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        batch_path, _, report = write_valid_batch_cli_fixture(root)
        report["status"] = "verified"
        for entry in report["notes"]:
            make_entry_final(entry)
        batch_path.write_text(json.dumps(report), encoding="utf-8")
        index_path = root / "data" / "concepts-index.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index["concepts"].append(
            {
                "slug": "dangling",
                "name": "Dangling",
                "nameZh": "",
                "subspecialty": "NR",
                "checked": False,
            }
        )
        index_path.write_text(json.dumps(index), encoding="utf-8")

        exit_code, output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
        )

    assert exit_code == 1
    assert '"code": "generated-index-dangling"' in output


def test_validate_batch_cli_rejects_nonpilot_index_metadata_drift() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        batch_path, _, report = write_valid_batch_cli_fixture(root)
        report["status"] = "verified"
        for entry in report["notes"]:
            make_entry_final(entry)
        batch_path.write_text(json.dumps(report), encoding="utf-8")

        detail = {
            "slug": "nonpilot",
            "name": "Detail name",
            "nameZh": "細節",
            "subspecialty": "CH",
            "checked": False,
            "keyPoints": [],
        }
        (root / "data" / "concepts" / "nonpilot.json").write_text(
            json.dumps(detail),
            encoding="utf-8",
        )
        index_path = root / "data" / "concepts-index.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index["concepts"].append(
            {
                "slug": "nonpilot",
                "name": "Drifted name",
                "nameZh": "細節",
                "subspecialty": "CH",
                "checked": False,
            }
        )
        index_path.write_text(json.dumps(index), encoding="utf-8")

        exit_code, output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
        )

    assert exit_code == 1
    assert '"code": "generated-index-metadata-mismatch"' in output


def test_generated_manifest_rejects_nonpilot_drift_and_missing_output() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        detail_root = root / "data" / "concepts"
        detail_root.mkdir(parents=True)
        details = {}
        for slug in ("clippers", "nonpilot"):
            detail = {
                "slug": slug,
                "name": slug,
                "nameZh": "",
                "subspecialty": "NR",
                "checked": False,
                "keyPoints": [],
            }
            path = detail_root / f"{slug}.json"
            path.write_text(
                json.dumps(detail, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            details[slug] = path
        index_entries = [
            {
                field: json.loads(path.read_text(encoding="utf-8"))[field]
                for field in audit.GENERATED_INDEX_FIELDS
            }
            for path in details.values()
        ]
        (root / "data" / "concepts-index.json").write_text(
            json.dumps({"concepts": index_entries}, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        reviewed_manifest = audit.build_generated_output_manifest(root)
        assert audit.validate_generated_manifest(reviewed_manifest, root) == []

        nonpilot = json.loads(details["nonpilot"].read_text(encoding="utf-8"))
        nonpilot["keyPoints"] = ["Unreviewed nonpilot drift."]
        details["nonpilot"].write_text(
            json.dumps(nonpilot, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        drift_codes = {
            finding.code
            for finding in audit.validate_generated_manifest(reviewed_manifest, root)
        }
        assert "generated-manifest-mismatch" in drift_codes

        details["nonpilot"].unlink()
        missing_codes = {
            finding.code
            for finding in audit.validate_generated_manifest(reviewed_manifest, root)
        }
        assert "generated-manifest-mismatch" in missing_codes


def test_lint_baseline_parser_accepts_exact_baseline_and_rejects_third_error() -> None:
    exact_output = """檢查：1123 概念、4 圖引用、4 圖檔

=== ERROR (2) ===
  ✗ [footnote 未定義] ceap-classification.md 用了 [^*] 但無定義
  ✗ [json 殘留 ![[...]]] 2022-264

=== WARN (124) ===
  ⚠ 題目無 correctAnswer: 65
  ⚠ 概念缺 ## 考題 dataview: 37
  ⚠ footnote 未被引用: 22

小結：2 errors, 124 warnings
"""
    assert audit.validate_lint_baseline(exact_output, 1) == []

    third_error_output = exact_output.replace(
        "=== ERROR (2) ===",
        "=== ERROR (3) ===",
    ).replace(
        "  ✗ [json 殘留 ![[...]]] 2022-264",
        "  ✗ [json 殘留 ![[...]]] 2022-264\n"
        "  ✗ [footnote 未定義] clippers.md 用了 [^third] 但無定義",
    ).replace(
        "小結：2 errors, 124 warnings",
        "小結：3 errors, 124 warnings",
    )
    findings = audit.validate_lint_baseline(third_error_output, 1)
    assert {finding.code for finding in findings} == {"lint-baseline-mismatch"}


def test_validate_batch_cli_rejects_rewritten_summary_drift() -> None:
    with tempfile.TemporaryDirectory() as directory:
        batch_path, _, report = write_valid_batch_cli_fixture(Path(directory))
        report["status"] = "verified"
        for entry in report["notes"]:
            make_entry_final(entry)
        report["notes"][0]["rewrittenSummary"] = "## Summary\n- **Label**: Drift.[^1]\n"
        batch_path.write_text(json.dumps(report), encoding="utf-8")
        exit_code, output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
        )

    assert exit_code == 1
    assert "evidence-rewritten-summary-mismatch" in output


def test_validate_batch_cli_rejects_final_integrity_mutations() -> None:
    mutations = (
        ("original-hash", "evidence-inventory-hash-mismatch"),
        ("original-summary", "evidence-baseline-digest-mismatch"),
        ("fact-text", "evidence-baseline-digest-mismatch"),
        ("source-refs", "evidence-baseline-digest-mismatch"),
        ("disposition", "evidence-coverage-digest-mismatch"),
    )
    for mutation, expected_code in mutations:
        with tempfile.TemporaryDirectory() as directory:
            batch_path, _, report = write_valid_batch_cli_fixture(Path(directory))
            report["status"] = "verified"
            for entry in report["notes"]:
                make_entry_final(entry)
            first = report["notes"][0]
            if mutation == "original-hash":
                first["originalSha256"] = "0" * 64
            elif mutation == "original-summary":
                first["originalSummary"] += "\nMutated original snapshot."
            elif mutation == "fact-text":
                first["factUnits"][0]["text"] = "Mutated fact text."
            elif mutation == "source-refs":
                first["factUnits"][0]["sourceRefs"] = ["1", "2"]
            elif mutation == "disposition":
                first["factUnits"][0]["disposition"] = "manual-review"
            batch_path.write_text(json.dumps(report), encoding="utf-8")
            exit_code, output = run_validate_batch_cli(
                batch_path,
                allow_pending=False,
            )
        assert exit_code == 1, (mutation, output)
        assert expected_code in output, (mutation, output)


def test_validate_batch_cli_rejects_new_summary_bullet_even_when_snapshot_is_updated() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        batch_path, _, report = write_valid_batch_cli_fixture(root)
        report["status"] = "verified"
        for entry in report["notes"]:
            make_entry_final(entry)

        first = report["notes"][0]
        added_bullet = "- **New**: Unsupported new fact.[^1]\n"
        rewritten = first["rewrittenSummary"] + added_bullet
        first["rewrittenSummary"] = rewritten
        seal_entry(first)
        note_path = root / "vault" / "concepts" / f"{first['slug']}.md"
        note_path.write_text(
            NR_DEMO_TEXT.replace(
                "## References\n",
                f"{added_bullet}\n## References\n",
            ),
            encoding="utf-8",
            newline="",
        )
        batch_path.write_text(json.dumps(report), encoding="utf-8")
        exit_code, output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
        )

    assert exit_code == 1
    assert "summary-bullet-unsupported" in output
    assert "evidence-validation" in output


def test_trusted_baseline_anchor_rejects_coordinated_batch_reseal() -> None:
    report, notes = load_real_batch_and_notes()
    entry = report["notes"][0]
    entry["originalSummary"] += "\nCoordinated baseline mutation."
    entry["factUnits"][0]["text"] = "Coordinated fact-text mutation."
    entry["factUnits"][0]["sourceRefs"] = ["1", "3"]
    reseal_report(report)

    findings = audit.validate_evidence(report, notes)

    assert "evidence-trusted-baseline-mismatch" in {
        finding.code for finding in findings
    }


def test_trusted_summary_anchor_rejects_coordinated_existing_bullet_reseal() -> None:
    report, notes = load_real_batch_and_notes()
    entry = report["notes"][0]
    note = notes[entry["slug"]]
    original_bullet = audit._summary_bullet_lines(note)[0]
    changed_bullet = original_bullet.replace("**", "**Mutated ", 1)
    changed_text = note.path.read_text(encoding="utf-8").replace(
        original_bullet,
        changed_bullet,
        1,
    )
    changed_note = audit.parse_note_text(note.path, changed_text)
    notes[entry["slug"]] = changed_note
    entry["rewrittenSummary"] = changed_note.original_summary
    entry["summaryBulletEvidence"][0]["sha256"] = hashlib.sha256(
        changed_bullet.encode("utf-8")
    ).hexdigest()
    reseal_report(report)

    findings = audit.validate_evidence(report, notes)

    codes = {finding.code for finding in findings}
    assert "evidence-trusted-summary-bullet-mismatch" in codes
    assert "evidence-trusted-final-mismatch" in codes


def test_trusted_final_anchor_rejects_coordinated_manual_queue_reseal() -> None:
    report, notes = load_real_batch_and_notes()
    changed_fact_ids = []
    changed_note_slugs = []
    for entry in report["notes"]:
        manual_facts = [
            fact
            for fact in entry["factUnits"]
            if fact["disposition"] == "manual-review"
        ]
        if not manual_facts:
            continue
        changed_note_slugs.append(entry["slug"])
        changed_fact_ids.extend(fact["id"] for fact in manual_facts)
        for fact in manual_facts:
            fact["disposition"] = "covered"
        entry["sourceStatus"] = "existing-sufficient"
        entry["status"] = "verified"
        entry["validation"]["manualReviewFactIds"] = []
        entry["validation"]["factCoverage"] = "pass"
        seal_entry(entry)

    report["status"] = "verified"
    for verification_name in ("phase1Verification", "fixRound1Verification"):
        verification = report.get(verification_name)
        if not isinstance(verification, dict):
            continue
        verification["factCoverage"] = {
            "total": 225,
            "covered": 225,
            "manualReview": 0,
            "researchNeeded": 0,
            "pending": 0,
        }
        verification["manualQueue"] = []
        review_gate = verification.get("reviewGate")
        if isinstance(review_gate, dict):
            review_gate["status"] = "verified"
            review_gate["verifiedNotes"] = 10
            review_gate["manualReviewNotes"] = 0

    assert sorted(changed_fact_ids) == sorted(audit.EXPECTED_MANUAL_REVIEW_FACT_IDS)
    assert sorted(changed_note_slugs) == [
        "acute-stroke-management",
        "bilateral-subcortical-dwi-hyperintensity-ddx",
    ]
    findings = audit.validate_evidence(report, notes)
    codes = {finding.code for finding in findings}
    assert "evidence-manual-queue-mismatch" in codes
    assert "evidence-trusted-final-mismatch" in codes


def test_plain_summary_prose_reseal_is_structurally_and_cryptographically_rejected() -> None:
    report, notes = load_real_batch_and_notes()
    entry = next(item for item in report["notes"] if item["slug"] == "clippers")
    note = notes[entry["slug"]]
    original_bullet = audit._summary_bullet_lines(note)[0]
    unsupported_claim = "Uncited medical claim: treatment always cures disease."
    changed_text = note.path.read_text(encoding="utf-8").replace(
        original_bullet,
        f"{original_bullet}\n{unsupported_claim}",
        1,
    )
    changed_note = audit.parse_note_text(note.path, changed_text)
    notes[entry["slug"]] = changed_note
    entry["rewrittenSummary"] = changed_note.original_summary
    seal_entry(entry)

    findings = audit.validate_evidence(report, notes)
    codes = {finding.code for finding in findings}
    assert "summary-content-line" in codes
    assert "evidence-trusted-final-mismatch" in codes


def test_validate_batch_loader_rejects_redirected_duplicate_and_unsafe_paths() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        batch_path, inventory, _ = write_valid_batch_cli_fixture(root)
        inventory_path = batch_path.with_name("inventory.json")
        original = json.loads(json.dumps(inventory))
        first_slug, second_slug = PILOT_SLUGS[:2]
        path_mutations = (
            "vault/concepts/elsewhere.md",
            f"vault/concepts/{second_slug}.md",
            f"vault/concepts/../concepts/{first_slug}.md",
            str((root / "vault" / "concepts" / f"{first_slug}.md").resolve()),
        )
        for invalid_path in path_mutations:
            mutated = json.loads(json.dumps(original))
            mutated["notes"][0]["path"] = invalid_path
            inventory_path.write_text(json.dumps(mutated), encoding="utf-8")
            notes, findings = audit._load_batch_notes(batch_path)
            assert notes == {}
            assert "evidence-inventory-path" in {
                finding.code for finding in findings
            }, invalid_path

        duplicated = json.loads(json.dumps(original))
        duplicated["notes"].append(dict(duplicated["notes"][0]))
        inventory_path.write_text(json.dumps(duplicated), encoding="utf-8")
        notes, findings = audit._load_batch_notes(batch_path)
        assert notes == {}
        assert "evidence-inventory-membership" in {
            finding.code for finding in findings
        }


def test_validate_batch_cli_allow_pending_retains_mutation_findings() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)

        schema_path, _, schema_report = write_valid_batch_cli_fixture(root / "schema")
        schema_report["schemaVersion"] = 2
        schema_path.write_text(json.dumps(schema_report), encoding="utf-8")
        exit_code, output = run_validate_batch_cli(schema_path, allow_pending=True)
        assert exit_code == 1
        assert "evidence-schema-version" in output

        hash_path, _, hash_report = write_valid_batch_cli_fixture(root / "hash")
        hash_report["notes"][0]["originalSha256"] = "0" * 64
        hash_path.write_text(json.dumps(hash_report), encoding="utf-8")
        exit_code, output = run_validate_batch_cli(hash_path, allow_pending=True)
        assert exit_code == 1
        assert "evidence-hash-mismatch" in output

        source_path, _, source_report = write_valid_batch_cli_fixture(root / "source")
        source_entry = source_report["notes"][0]
        source_entry["factUnits"][0]["sourceRefs"] = []
        source_entry["factUnits"][0]["disposition"] = "covered"
        source_entry["validation"]["pendingFactCount"] = 0
        source_path.write_text(json.dumps(source_report), encoding="utf-8")
        exit_code, output = run_validate_batch_cli(source_path, allow_pending=True)
        assert exit_code == 1
        assert "fact-source-missing" in output


def test_real_batch_keeps_acute_stroke_legacy_claims_on_source_one() -> None:
    batch_path = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "reports"
        / "nr-summary-rewrite"
        / "batch-00.json"
    )
    report = json.loads(batch_path.read_text(encoding="utf-8"))
    entry = next(
        note for note in report["notes"] if note["slug"] == "acute-stroke-management"
    )
    facts = {fact["id"]: fact for fact in entry["factUnits"]}
    expected_ids = {
        "acute-stroke-management-f08",
        "acute-stroke-management-f09",
        "acute-stroke-management-f17",
        "acute-stroke-management-f18",
    }
    assert len(facts) == 18
    for fact_id in expected_ids:
        assert facts[fact_id]["sourceRefs"] == ["1"]
    assert facts["acute-stroke-management-f09"]["disposition"] == "manual-review"
    for fact_id in expected_ids - {"acute-stroke-management-f09"}:
        assert facts[fact_id]["disposition"] == "covered"


def test_fix_round1_content_and_evidence_regressions() -> None:
    root = Path(__file__).resolve().parents[1]
    batch = json.loads(
        (
            root / "docs" / "reports" / "nr-summary-rewrite" / "batch-00.json"
        ).read_text(encoding="utf-8")
    )
    bilateral_entry = next(
        entry
        for entry in batch["notes"]
        if entry["slug"] == "bilateral-subcortical-dwi-hyperintensity-ddx"
    )
    bilateral_facts = {fact["id"]: fact for fact in bilateral_entry["factUnits"]}
    assert bilateral_facts[
        "bilateral-subcortical-dwi-hyperintensity-ddx-f04"
    ]["disposition"] == "covered"
    assert "10" in bilateral_facts[
        "bilateral-subcortical-dwi-hyperintensity-ddx-f04"
    ]["sourceRefs"]
    assert bilateral_facts[
        "bilateral-subcortical-dwi-hyperintensity-ddx-f08"
    ]["disposition"] == "manual-review"
    assert bilateral_entry["validation"]["manualReviewFactIds"] == [
        "bilateral-subcortical-dwi-hyperintensity-ddx-f08",
        "bilateral-subcortical-dwi-hyperintensity-ddx-f09",
        "bilateral-subcortical-dwi-hyperintensity-ddx-f12",
    ]

    bilateral_note = (
        root / "vault" / "concepts" / "bilateral-subcortical-dwi-hyperintensity-ddx.md"
    ).read_text(encoding="utf-8")
    assert "Cabal-Herrera AM" in bilateral_note
    assert "10.3390/ijms21124391" in bilateral_note
    assert "PMID 32575683" in bilateral_note
    assert "PMC7352421" in bilateral_note
    assert "10.1002/mds.28055" not in bilateral_note
    alexander_footnote = next(
        line for line in bilateral_note.splitlines() if line.startswith("[^8]:")
    )
    assert "diffusion restriction" not in alexander_footnote

    caa_note = (
        root / "vault" / "concepts" / "cerebral-amyloid-angiopathy.md"
    ).read_text(encoding="utf-8")
    caa_entry = next(
        entry
        for entry in batch["notes"]
        if entry["slug"] == "cerebral-amyloid-angiopathy"
    )
    caa_f38 = next(
        fact
        for fact in caa_entry["factUnits"]
        if fact["id"] == "cerebral-amyloid-angiopathy-f38"
    )
    assert caa_f38["disposition"] == "covered"
    assert caa_f38["sourceRefs"] == ["4"]
    assert (
        "possible CAA 為僅 1 個 **strictly lobar hemorrhagic lesion**"
        in caa_note
    )

    adamkiewicz_note = (
        root / "vault" / "concepts" / "artery-of-adamkiewicz.md"
    ).read_text(encoding="utf-8")
    assert "原題／舊來源的記憶範圍為左側約 **77%、T9–T12**" in adamkiewicz_note
    assert "單一高峰集中 T9–T11" in adamkiewicz_note
    assert "完整報告範圍可自 **T3 至 L4**" in adamkiewicz_note


def test_validate_batch_cli_handles_invalid_json_without_raising() -> None:
    with tempfile.TemporaryDirectory() as directory:
        batch_path = Path(directory) / "batch-00.json"
        batch_path.write_text("{", encoding="utf-8")
        output = io.StringIO()
        try:
            with redirect_stdout(output), redirect_stderr(output):
                exit_code = audit.main(
                    ["validate-batch", str(batch_path), "--allow-pending"]
                )
        except SystemExit as error:
            exit_code = error.code
    assert exit_code == 1
    assert "evidence-json-invalid" in output.getvalue()


def test_parse_note_hashes_exact_source_bytes() -> None:
    payload = NR_DEMO_TEXT.replace("\n", "\r\n").encode("utf-8")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "demo.md"
        path.write_bytes(payload)
        note = audit.parse_note(path)
    assert note.sha256 == hashlib.sha256(payload).hexdigest()


def test_note_preserves_lossless_summary_snapshot() -> None:
    text = (
        "---\nconcepts: [demo]\nsubspecialty: [NR]\n---\n"
        "## Summary — first\n"
        "- **Label**: First fact.[^1]\n"
        "\n"
        "## Body\n"
        "Body text.\n"
        "\n"
        "## Summary — second\n"
        "- **Label**: Second fact.[^1]\n"
        "\n"
        "## References\n"
        "[^1]: Example.\n"
    )
    note = audit.parse_note_text(Path("demo.md"), text)
    expected = (
        "## Summary — first\n"
        "- **Label**: First fact.[^1]\n"
        "\n"
        "## Summary — second\n"
        "- **Label**: Second fact.[^1]\n"
        "\n"
    )
    assert getattr(note, "original_summary", None) == expected


def test_summary_variants_are_extracted() -> None:
    text = """---
concepts: [demo]
name: Demo
subspecialty: [NR]
---
# demo

## Summary — 影像
- **影像**：DWI 高訊號。[^1]

## Summary — 陷阱
- **陷阱**：不能只靠單一序列。[^1]

### 參考來源
[^1]: Example source. DOI 10.1000/example.
"""
    note = audit.parse_note_text(Path("demo.md"), text)
    assert [section.heading for section in note.summaries] == [
        "Summary — 影像",
        "Summary — 陷阱",
    ]


def test_non_nr_note_is_not_in_scope() -> None:
    text = """---
concepts: [demo]
subspecialty: [ABD]
---
## Summary
- **影像**：Example.[^1]
[^1]: Example.
"""
    note = audit.parse_note_text(Path("demo.md"), text)
    assert note.in_scope is False


def test_validator_rejects_unlabeled_and_undefined_footnote() -> None:
    text = """---
concepts: [demo]
subspecialty: [NR]
---
## Summary
- 沒有粗體標籤。[^missing]
"""
    findings = audit.validate_summary(audit.parse_note_text(Path("demo.md"), text))
    codes = {finding.code for finding in findings}
    assert "summary-bullet-label" in codes
    assert "footnote-undefined" in codes


def test_validator_rejects_callout_table_and_nested_bullet() -> None:
    text = """---
concepts: [demo]
subspecialty: [NR]
---
## Summary
- **影像**：Example.[^1]
  - nested
> [!note] callout
| A | B |
|---|---|
[^1]: Example.
"""
    findings = audit.validate_summary(audit.parse_note_text(Path("demo.md"), text))
    codes = {finding.code for finding in findings}
    assert {"summary-nested-bullet", "summary-callout", "summary-table"} <= codes


def test_validator_rejects_every_other_nonblank_summary_content_line() -> None:
    invalid_lines = (
        "Uncited medical prose.",
        "> ordinary quote",
        "```python",
        "claim | without | table fences",
        "[^1]: Footnote definitions belong outside Summary.",
    )
    for invalid_line in invalid_lines:
        text = (
            "---\nconcepts: [demo]\nsubspecialty: [NR]\n---\n"
            "## Summary\n"
            "### Allowed subsection\n"
            "- **Label**: Supported fact.[^1]\n"
            f"{invalid_line}\n"
            "\n## References\n[^1]: Example.\n"
        )
        codes = {
            finding.code
            for finding in audit.validate_summary(
                audit.parse_note_text(Path("demo.md"), text)
            )
        }
        assert "summary-content-line" in codes, invalid_line


def test_validator_accepts_level_three_subheadings_and_labeled_bullets_only() -> None:
    text = (
        "---\nconcepts: [demo]\nsubspecialty: [NR]\n---\n"
        "## Summary — first\n"
        "### Allowed subsection\n"
        "- **Label**: Supported fact.[^1]\n"
        "\n## References\n[^1]: Example.\n"
    )
    findings = audit.validate_summary(audit.parse_note_text(Path("demo.md"), text))
    assert findings == []


def test_summary_heading_rejects_unapproved_suffix() -> None:
    text = """---
concepts: [demo]
subspecialty: [NR]
---
## Summary notes
- **Label**: This must not be parsed as a Summary.[^1]
[^1]: Example.
"""
    note = audit.parse_note_text(Path("demo.md"), text)
    assert note.summaries == ()
    assert "summary-missing" in {finding.code for finding in audit.validate_summary(note)}


def test_validator_rejects_missing_empty_and_alternate_table_summaries() -> None:
    missing = audit.parse_note_text(
        Path("missing.md"),
        "---\nconcepts: [demo]\nsubspecialty: [NR]\n---\n# No Summary\n",
    )
    empty = audit.parse_note_text(
        Path("empty.md"),
        "---\nconcepts: [demo]\nsubspecialty: [NR]\n---\n## Summary\n-\n",
    )
    table = audit.parse_note_text(
        Path("table.md"),
        "---\nconcepts: [demo]\nsubspecialty: [NR]\n---\n## Summary\n"
        "- **Label**: Supported fact.[^1]\nA | B\n--- | ---\n[^1]: Example.\n",
    )
    assert "summary-missing" in {finding.code for finding in audit.validate_summary(missing)}
    assert "summary-empty-bullet" in {finding.code for finding in audit.validate_summary(empty)}
    assert "summary-table" in {finding.code for finding in audit.validate_summary(table)}


def test_note_line_numbers_include_frontmatter() -> None:
    text = """---
concepts: [demo]
subspecialty: [NR]
---
# demo

## Summary

- **Label**: Supported fact.[^1]
  - nested
[^1]: Example.
"""
    note = audit.parse_note_text(Path("demo.md"), text)
    assert note.summaries[0].start_line == 7
    nested = next(finding for finding in audit.validate_summary(note) if finding.code == "summary-nested-bullet")
    assert nested.message.endswith("line 10.")


def test_cli_prints_findings_and_uses_error_exit_code() -> None:
    with tempfile.TemporaryDirectory() as directory:
        note_path = Path(directory) / "invalid.md"
        note_path.write_text(
            "---\nconcepts: [demo]\nsubspecialty: [NR]\n---\n# No Summary\n", encoding="utf-8"
        )
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = audit.main(["validate-note", str(note_path)])

    findings = json.loads(output.getvalue())
    assert exit_code == 1
    assert findings[0]["code"] == "summary-missing"


def test_inventory_requires_allowed_type_and_status() -> None:
    note = make_nr_note("demo")
    entry = make_inventory_entry(note, note_type="unknown", batch="unassigned")
    findings = audit.validate_inventory(
        {
            "schemaVersion": 1,
            "scope": "NR",
            "generatedFrom": "vault/concepts",
            "notes": [entry],
        }
    )
    assert "inventory-type" in {finding.code for finding in findings}


def test_inventory_requires_root_contract() -> None:
    inventory = {
        "schemaVersion": 1,
        "notes": [],
    }
    codes = {finding.code for finding in audit.validate_inventory(inventory)}
    assert {"inventory-scope", "inventory-generated-from"} <= codes


def test_inventory_malformed_roots_return_stable_findings_without_raising() -> None:
    for malformed_root in ([], "not-an-object", None, 7):
        findings = audit.validate_inventory(malformed_root)
        assert {finding.code for finding in findings} == {"inventory-root"}
        against_notes = audit.validate_inventory_against_notes(malformed_root, {})
        assert {finding.code for finding in against_notes} == {"inventory-root"}


def test_inventory_rejects_duplicate_slug_and_missing_nr_note() -> None:
    nr_demo = make_nr_note("demo")
    nr_other = make_nr_note("other")
    entry = make_inventory_entry(nr_demo)
    inventory_with_duplicate_demo = {
        "schemaVersion": 1,
        "scope": "NR",
        "generatedFrom": "vault/concepts",
        "notes": [entry, dict(entry)],
    }
    findings = audit.validate_inventory_against_notes(
        inventory_with_duplicate_demo,
        {"demo": nr_demo, "other": nr_other},
    )
    codes = {finding.code for finding in findings}
    assert "inventory-duplicate-slug" in codes
    assert "inventory-scope-mismatch" in codes


def test_inventory_schema_accepts_closed_enum_values_but_enforces_phase1_count() -> None:
    note = make_nr_note("demo")
    entry = make_inventory_entry(note, batch="unassigned")
    inventory = {
        "schemaVersion": 1,
        "scope": "NR",
        "generatedFrom": "vault/concepts",
        "notes": [entry],
    }
    codes = {finding.code for finding in audit.validate_inventory(inventory)}
    assert codes == {
        "inventory-batch-counts",
        "inventory-count",
        "inventory-override-completeness",
    }


def test_inventory_rejects_invalid_status_source_batch_hash_and_headings() -> None:
    note = make_nr_note("demo")
    mutations = (
        ("status", "not-a-status", "inventory-status"),
        ("sourceStatus", "unknown", "inventory-source-status"),
        ("batch", "batch-01", "inventory-batch"),
        ("originalSha256", "A" * 64, "inventory-sha256"),
        ("summaryHeadings", "Summary", "inventory-summary-headings"),
    )
    for field, invalid_value, expected_code in mutations:
        entry = make_inventory_entry(note, batch="unassigned")
        entry[field] = invalid_value
        inventory = {
            "schemaVersion": 1,
            "scope": "NR",
            "generatedFrom": "vault/concepts",
            "notes": [entry],
        }
        codes = {finding.code for finding in audit.validate_inventory(inventory)}
        assert expected_code in codes, (field, codes)


def test_inventory_enum_fields_reject_unhashable_json_values_without_raising() -> None:
    note = make_nr_note("demo")
    mutations = (
        ("type", [], "inventory-type"),
        ("status", {}, "inventory-status"),
        ("sourceStatus", [], "inventory-source-status"),
        ("batch", {}, "inventory-batch"),
    )
    for field, invalid_value, expected_code in mutations:
        entry = make_inventory_entry(note, batch="unassigned")
        entry[field] = invalid_value
        inventory = {
            "schemaVersion": 1,
            "scope": "NR",
            "generatedFrom": "vault/concepts",
            "notes": [entry],
        }
        try:
            findings = audit.validate_inventory(inventory)
        except TypeError as error:
            raise AssertionError(f"{field} raised TypeError for JSON value") from error
        assert expected_code in {finding.code for finding in findings}, field


def test_inventory_against_notes_enforces_full_phase1_contract_on_small_fixture() -> None:
    inventory, notes = make_pilot_inventory()
    codes = {
        finding.code
        for finding in audit.validate_inventory_against_notes(inventory, notes)
    }
    assert {
        "inventory-batch-counts",
        "inventory-count",
        "inventory-override-completeness",
    } <= codes


def test_inventory_rejects_regenerated_215_note_scope_after_nonpilot_missing() -> None:
    root = Path(__file__).resolve().parents[1]
    checked_in = json.loads(
        (
            root / "docs" / "reports" / "nr-summary-rewrite" / "inventory.json"
        ).read_text(encoding="utf-8")
    )
    removed_slug = next(
        entry["slug"]
        for entry in checked_in["notes"]
        if entry["slug"] not in PILOT_SLUGS
    )
    regenerated = json.loads(json.dumps(checked_in))
    regenerated["notes"] = [
        entry for entry in regenerated["notes"] if entry["slug"] != removed_slug
    ]
    notes = {
        entry["slug"]: make_nr_note(entry["slug"])
        for entry in regenerated["notes"]
    }

    codes = {
        finding.code
        for finding in audit.validate_inventory_against_notes(regenerated, notes)
    }
    assert "inventory-count" in codes
    assert "inventory-override-completeness" in codes


def test_inventory_against_notes_rejects_path_hash_and_heading_mismatches() -> None:
    inventory, notes = make_pilot_inventory()
    mutated_entry = inventory["notes"][0]
    mutated_entry["path"] = "vault/concepts/wrong.md"
    mutated_entry["originalSha256"] = "b" * 64
    mutated_entry["summaryHeadings"] = ["Summary — wrong"]
    codes = {
        finding.code
        for finding in audit.validate_inventory_against_notes(inventory, notes)
    }
    assert {
        "inventory-path-mismatch",
        "inventory-trusted-baseline-mismatch",
        "inventory-summary-headings-mismatch",
    } <= codes


def test_inventory_against_notes_rejects_fixed_pilot_membership_drift() -> None:
    inventory, notes = make_pilot_inventory()
    inventory["notes"][0]["batch"] = "unassigned"
    codes = {
        finding.code
        for finding in audit.validate_inventory_against_notes(inventory, notes)
    }
    assert "inventory-batch-membership" in codes


def test_inventory_against_notes_handles_malformed_entries_without_raising() -> None:
    inventory, notes = make_pilot_inventory()
    inventory["notes"].extend(["bad-entry", 7, None])
    findings = audit.validate_inventory_against_notes(inventory, notes)
    assert "inventory-schema" in {finding.code for finding in findings}


def test_inventory_membership_rejects_unhashable_slug_without_raising() -> None:
    inventory, notes = make_pilot_inventory()
    inventory["notes"][0]["slug"] = []
    try:
        findings = audit.validate_inventory_against_notes(inventory, notes)
    except TypeError as error:
        raise AssertionError("list-valued inventory slug raised TypeError") from error
    assert "inventory-batch-membership" in {finding.code for finding in findings}


def test_inventory_cli_generates_and_checks_deterministically() -> None:
    fixture_slugs = tuple(sorted(audit.NOTE_TYPE_OVERRIDES))
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "concepts"
        root.mkdir()
        for slug in fixture_slugs:
            (root / f"{slug}.md").write_text(NR_DEMO_TEXT, encoding="utf-8")
        output_path = Path(directory) / "inventory.json"

        with redirect_stdout(io.StringIO()):
            assert (
                audit.main(
                    [
                        "inventory",
                        "--root",
                        str(root),
                        "--output",
                        str(output_path),
                    ]
                )
                == 0
            )
        first_bytes = output_path.read_bytes()
        generated = json.loads(first_bytes)
        facial_entry = next(
            entry
            for entry in generated["notes"]
            if entry["slug"] == "facial-fracture-complications"
        )
        assert facial_entry["type"] == "pattern-ddx"
        assert [entry["slug"] for entry in generated["notes"]] == sorted(fixture_slugs)

        with redirect_stdout(io.StringIO()):
            assert (
                audit.main(
                    [
                        "inventory",
                        "--root",
                        str(root),
                        "--output",
                        str(output_path),
                    ]
                )
                == 0
            )
        assert output_path.read_bytes() == first_bytes

        check_output = io.StringIO()
        with redirect_stdout(check_output):
            check_exit = audit.main(
                [
                    "inventory",
                    "--root",
                    str(root),
                    "--output",
                    str(output_path),
                    "--check",
                ]
            )
        assert check_exit == 0
        assert check_output.getvalue().splitlines() == [
            "NR notes: 216",
            "Duplicate slugs: 0",
            "Unclassified: 0",
            "Batch 00: 10",
            "Unassigned: 206",
        ]

        generated["notes"][0]["status"] = "verified"
        output_path.write_text(
            json.dumps(generated, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        mutated_output = io.StringIO()
        with redirect_stdout(mutated_output):
            mutated_exit = audit.main(
                [
                    "inventory",
                    "--root",
                    str(root),
                    "--output",
                    str(output_path),
                    "--check",
                ]
            )
        assert mutated_exit == 1
        assert "inventory-not-deterministic" in mutated_output.getvalue()


def test_final_inventory_check_preserves_pilot_baselines_but_checks_nonpilots() -> None:
    root = Path(__file__).resolve().parents[1]
    inventory_path = (
        root / "docs" / "reports" / "nr-summary-rewrite" / "inventory.json"
    )
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    _, notes = audit._inventory(root / "vault" / "concepts")

    findings = audit.validate_inventory_against_notes(
        inventory,
        notes,
        repo_root=root,
    )
    assert "inventory-hash-mismatch" not in {
        finding.code for finding in findings
    }

    mutated = json.loads(json.dumps(inventory))
    nonpilot = next(
        entry for entry in mutated["notes"] if entry["slug"] not in audit.PILOT_SLUGS
    )
    nonpilot["originalSha256"] = "0" * 64
    findings = audit.validate_inventory_against_notes(
        mutated,
        notes,
    )
    assert "inventory-hash-mismatch" in {
        finding.code for finding in findings
    }

    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = audit.main(
            [
                "inventory",
                "--root",
                str(root / "vault" / "concepts"),
                "--output",
                str(inventory_path),
                "--check",
            ]
        )
    assert exit_code == 0, output.getvalue()


def test_public_inventory_binds_reviewed_hashes_with_explicit_root() -> None:
    root = Path(__file__).resolve().parents[1]
    inventory = json.loads(
        (
            root / "docs" / "reports" / "nr-summary-rewrite" / "inventory.json"
        ).read_text(encoding="utf-8")
    )
    _, notes = audit._inventory(root / "vault" / "concepts")
    assert (
        audit.validate_inventory_against_notes(
            inventory,
            notes,
            repo_root=root,
        )
        == []
    )

    replaced = json.loads(json.dumps(inventory))
    for entry in replaced["notes"]:
        if entry["slug"] in PILOT_SLUGS:
            entry["originalSha256"] = notes[entry["slug"]].sha256
    codes = {
        finding.code
        for finding in audit.validate_inventory_against_notes(
            replaced,
            notes,
            repo_root=root,
        )
    }
    assert "inventory-trusted-baseline-mismatch" in codes

    fixture_trust = {
        slug: notes[slug].sha256 for slug in PILOT_SLUGS
    }
    assert validate_inventory_with_fixture_trust(
        replaced,
        notes,
        fixture_trust,
        repo_root=root,
    ) == []


def test_coordinated_pilot_hash_replacement_is_rejected_by_trusted_baseline() -> None:
    root = Path(__file__).resolve().parents[1]
    evidence_root = root / "docs" / "reports" / "nr-summary-rewrite"
    inventory = json.loads(
        (evidence_root / "inventory.json").read_text(encoding="utf-8")
    )
    report = json.loads(
        (evidence_root / "batch-00.json").read_text(encoding="utf-8")
    )
    inventory_hashes = {
        entry["slug"]: entry["originalSha256"]
        for entry in inventory["notes"]
        if entry["slug"] in PILOT_SLUGS
    }
    report_hashes = {
        entry["slug"]: entry["originalSha256"] for entry in report["notes"]
    }
    assert set(audit.TRUSTED_PILOT_ORIGINAL_SHA256) == set(PILOT_SLUGS)
    assert inventory_hashes == audit.TRUSTED_PILOT_ORIGINAL_SHA256
    assert report_hashes == audit.TRUSTED_PILOT_ORIGINAL_SHA256

    target_slug = "acute-stroke-management"
    replacement = "0" * 64
    next(
        entry for entry in inventory["notes"] if entry["slug"] == target_slug
    )["originalSha256"] = replacement
    next(
        entry for entry in report["notes"] if entry["slug"] == target_slug
    )["originalSha256"] = replacement

    with tempfile.TemporaryDirectory(dir=root) as directory:
        copied_evidence_root = Path(directory)
        inventory_path = copied_evidence_root / "inventory.json"
        batch_path = copied_evidence_root / "batch-00.json"
        inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
        batch_path.write_text(json.dumps(report), encoding="utf-8")

        inventory_output = io.StringIO()
        with redirect_stdout(inventory_output), redirect_stderr(inventory_output):
            inventory_exit = audit.main(
                [
                    "inventory",
                    "--root",
                    str(root / "vault" / "concepts"),
                    "--output",
                    str(inventory_path),
                    "--check",
                ]
            )
        batch_exit, batch_output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
            use_fixture_trust=False,
        )

    assert (inventory_exit, batch_exit) == (1, 1), (
        inventory_output.getvalue(),
        batch_output,
    )
    assert "inventory-trusted-baseline-mismatch" in inventory_output.getvalue()
    assert "evidence-trusted-baseline-mismatch" in batch_output


def test_public_validate_evidence_rejects_coordinated_pilot_hash_replacement() -> None:
    report, notes = load_real_batch_and_notes()
    assert "evidence-trusted-baseline-mismatch" not in {
        finding.code for finding in audit.validate_evidence(report, notes)
    }

    target = next(
        entry
        for entry in report["notes"]
        if entry["slug"] == "acute-stroke-management"
    )
    target["originalSha256"] = "a" * 64
    codes = {finding.code for finding in audit.validate_evidence(report, notes)}
    assert "evidence-trusted-baseline-mismatch" in codes


def test_shadow_checkout_validate_batch_rejects_coordinated_pilot_hash_replacement() -> None:
    root = Path(__file__).resolve().parents[1]
    evidence_root = root / "docs" / "reports" / "nr-summary-rewrite"
    inventory = json.loads(
        (evidence_root / "inventory.json").read_text(encoding="utf-8")
    )
    report = json.loads(
        (evidence_root / "batch-00.json").read_text(encoding="utf-8")
    )
    target_slug = "acute-stroke-management"
    next(
        entry for entry in inventory["notes"] if entry["slug"] == target_slug
    )["originalSha256"] = "a" * 64
    next(
        entry for entry in report["notes"] if entry["slug"] == target_slug
    )["originalSha256"] = "a" * 64

    with tempfile.TemporaryDirectory() as directory:
        shadow = Path(directory)
        concepts = shadow / "vault" / "concepts"
        report_dir = shadow / "docs" / "reports" / "nr-summary-rewrite"
        concepts.mkdir(parents=True)
        report_dir.mkdir(parents=True)
        for slug in PILOT_SLUGS:
            shutil.copy2(
                root / "vault" / "concepts" / f"{slug}.md",
                concepts / f"{slug}.md",
            )
        shutil.copytree(root / "data", shadow / "data")
        (report_dir / "inventory.json").write_text(
            json.dumps(inventory),
            encoding="utf-8",
        )
        batch_path = report_dir / "batch-00.json"
        batch_path.write_text(json.dumps(report), encoding="utf-8")
        exit_code, output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
            use_fixture_trust=False,
        )

    assert exit_code == 1, output
    assert "evidence-trusted-baseline-mismatch" in output


def test_canonical_inventory_generation_emits_trusted_pilot_hashes_and_checks() -> None:
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as directory:
        output_path = Path(directory) / "inventory.json"
        with redirect_stdout(io.StringIO()):
            generated_exit = audit.main(
                [
                    "inventory",
                    "--root",
                    str(root / "vault" / "concepts"),
                    "--output",
                    str(output_path),
                ]
            )
        generated = json.loads(output_path.read_text(encoding="utf-8"))
        generated_pilot_hashes = {
            entry["slug"]: entry["originalSha256"]
            for entry in generated["notes"]
            if entry["slug"] in PILOT_SLUGS
        }
        with redirect_stdout(io.StringIO()):
            check_exit = audit.main(
                [
                    "inventory",
                    "--root",
                    str(root / "vault" / "concepts"),
                    "--output",
                    str(output_path),
                    "--check",
                ]
            )

    assert generated_exit == 0
    assert generated_pilot_hashes == audit.TRUSTED_PILOT_ORIGINAL_SHA256
    assert check_exit == 0


def test_shadow_final_review_and_phase2_mutation_is_rejected_everywhere() -> None:
    root = Path(__file__).resolve().parents[1]
    evidence_root = root / "docs" / "reports" / "nr-summary-rewrite"
    inventory = json.loads(
        (evidence_root / "inventory.json").read_text(encoding="utf-8")
    )
    report = json.loads(
        (evidence_root / "batch-00.json").read_text(encoding="utf-8")
    )
    promote_manual_queue_to_verified(report)

    with tempfile.TemporaryDirectory() as directory:
        batch_path, shadow_notes = write_real_shadow_checkout(
            root,
            Path(directory),
            inventory,
            report,
        )
        public_codes = {
            finding.code
            for finding in audit.validate_evidence(report, shadow_notes)
        }
        exit_code, output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
            use_fixture_trust=False,
        )

    assert {
        "evidence-trusted-final-mismatch",
        "evidence-manual-queue-mismatch",
        "evidence-phase1-verification",
    } <= public_codes
    assert exit_code == 1, output
    assert "evidence-trusted-final-mismatch" in output
    assert "evidence-manual-queue-mismatch" in output
    assert "evidence-phase1-verification" in output


def test_validate_batch_rejects_ten_pilot_only_sibling_inventory() -> None:
    root = Path(__file__).resolve().parents[1]
    evidence_root = root / "docs" / "reports" / "nr-summary-rewrite"
    inventory = json.loads(
        (evidence_root / "inventory.json").read_text(encoding="utf-8")
    )
    report = json.loads(
        (evidence_root / "batch-00.json").read_text(encoding="utf-8")
    )
    pilot_only_inventory = json.loads(json.dumps(inventory))
    pilot_only_inventory["notes"] = [
        entry
        for entry in pilot_only_inventory["notes"]
        if entry["slug"] in PILOT_SLUGS
    ]

    with tempfile.TemporaryDirectory() as directory:
        batch_path, _ = write_real_shadow_checkout(
            root,
            Path(directory),
            inventory,
            report,
            written_inventory=pilot_only_inventory,
        )
        exit_code, output = run_validate_batch_cli(
            batch_path,
            allow_pending=False,
            use_fixture_trust=False,
        )

    assert exit_code == 1, output
    assert "inventory-count" in output
    assert "inventory-override-completeness" in output
    assert "inventory-batch-counts" in output


def test_inventory_cli_reports_malformed_json_and_nonobject_root_without_traceback() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "concepts"
        root.mkdir()
        for slug in sorted(audit.NOTE_TYPE_OVERRIDES):
            (root / f"{slug}.md").write_text(NR_DEMO_TEXT, encoding="utf-8")
        output_path = Path(directory) / "inventory.json"
        for payload, expected_code in (
            ("{", "inventory-json-invalid"),
            ("[]", "inventory-root"),
        ):
            output_path.write_text(payload, encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                exit_code = audit.main(
                    [
                        "inventory",
                        "--root",
                        str(root),
                        "--output",
                        str(output_path),
                        "--check",
                    ]
                )
            assert exit_code == 1
            assert expected_code in output.getvalue()
            assert "Traceback" not in output.getvalue()


def _production_phase2a_batch01() -> tuple[Path, Path, audit.BatchContext]:
    root = Path(__file__).resolve().parents[1]
    assignment_path = Path(
        "docs/reports/nr-summary-rewrite/phase2-assignment.json"
    )
    context = audit.load_phase2_batch(
        root,
        assignment_path,
        "batch-01-anatomy",
    )
    return root, assignment_path, context


BATCH02_DISEASE_SLUGS = (
    "2-hydroxyglutarate-idh-mutant-glioma",
    "adrenoleukodystrophy",
    "aicardi-syndrome",
    "als-imaging",
    "angioinvasive-aspergillosis",
    "anti-nmda-encephalitis",
    "arterial-dissection-mri",
    "atypical-teratoid-rhabdoid-tumor",
    "autoimmune-encephalitis",
    "basilar-artery-occlusion",
)
BATCH02_PREEDIT_SHA256 = {
    "2-hydroxyglutarate-idh-mutant-glioma": (
        "956c9af7339798ed5659248453e267a918bccf7876c2b099bf6bfbf8ca60f205"
    ),
    "adrenoleukodystrophy": (
        "792affd2ce3e0ccbb8f84eb4b2e31db8cd196fb2cbaa2506a64668a1dddafa8a"
    ),
    "aicardi-syndrome": (
        "74769c738b4ed0f4be58f9ddb0d8b4208bf8372a5f0a5a844bab3aa92bed8a5b"
    ),
    "als-imaging": (
        "10985b1e45e93c4ad95624b1cd7a6cb680e4f1297c1f304caa61cabdd08d39a0"
    ),
    "angioinvasive-aspergillosis": (
        "42998c7340d8a5e33388c7daf269a2c547473ced4457e088fbaadc1a363a68cf"
    ),
    "anti-nmda-encephalitis": (
        "fcd551d46ba7e5934367c16c63fab0b10983b4f38fe43803c13e5c961f408855"
    ),
    "arterial-dissection-mri": (
        "5d0c5a8cb2736985da542e4b21dfca56a367b17c80c8113486ddbafac3b17521"
    ),
    "atypical-teratoid-rhabdoid-tumor": (
        "b5bf97074c2dc1591e24750c78b2aa344c150c97a5b2f51d38b0c04871c5f947"
    ),
    "autoimmune-encephalitis": (
        "25727f01bde2d53b3151531e15f6b107b4de3546e5bccacac9a6cf51c873fb5c"
    ),
    "basilar-artery-occlusion": (
        "f5deb355d9f0728350ff84a51176666a2044cfcc5840cba870e39e8bfc8b883b"
    ),
}
BATCH02_STATEMENT_FACT_REF_COUNTS = {
    "2-hydroxyglutarate-idh-mutant-glioma": (4, 7, 3),
    "adrenoleukodystrophy": (28, 70, 11),
    "aicardi-syndrome": (6, 7, 2),
    "als-imaging": (3, 4, 1),
    "angioinvasive-aspergillosis": (5, 6, 1),
    "anti-nmda-encephalitis": (4, 7, 2),
    "arterial-dissection-mri": (5, 7, 2),
    "atypical-teratoid-rhabdoid-tumor": (5, 12, 2),
    "autoimmune-encephalitis": (4, 4, 1),
    "basilar-artery-occlusion": (5, 7, 4),
}
BATCH01_APPROVED_ARTIFACT_SHA256 = {
    "docs/reports/nr-summary-rewrite/phase2a/baselines/batch-01-anatomy.json": (
        "6b05caff4e2cbd618a9c15478f914853701b4be2587af58469b013917d0a7934"
    ),
    "docs/reports/nr-summary-rewrite/phase2a/evidence/batch-01-anatomy.json": (
        "0225a5e6c7a6fca4d2abe6abe9d73540ef186c064dc5d3b89690d0d74857f70b"
    ),
    "docs/reports/nr-summary-rewrite/phase2a/generated/batch-01-anatomy.json": (
        "bd1d2be10b9045c17b3f7ff540414623b8ecee4b6f2dd38f576aa3d118fbbbdb"
    ),
}


def _production_phase2a_batch02() -> tuple[Path, Path, audit.BatchContext]:
    root = Path(__file__).resolve().parents[1]
    assignment_path = Path(
        "docs/reports/nr-summary-rewrite/phase2-assignment.json"
    )
    context = audit.load_phase2_batch(
        root,
        assignment_path,
        "batch-02-disease",
    )
    return root, assignment_path, context


def _copy_production_phase2a_batch01_checkout(destination: Path) -> Path:
    """Copy the complete batch-01 validation surface to a relocated checkout."""
    root, assignment_path, context = _production_phase2a_batch01()
    additional_trusted_baselines = [
        context.baseline_path.parent / f"{batch_id}.json"
        for batch_id in audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
        if batch_id != context.batch["id"]
    ]
    relative_files = [
        assignment_path,
        context.inventory_path,
        context.baseline_path,
        context.evidence_path,
        Path("data/concepts-index.json"),
        *additional_trusted_baselines,
        *(
            Path(record.path)
            for record in context.note_records.values()
        ),
    ]
    manifest_path = (
        Path("docs/reports/nr-summary-rewrite/phase2a/generated")
        / "batch-01-anatomy.json"
    )
    if (root / manifest_path).is_file():
        relative_files.append(manifest_path)
    for relative in relative_files:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / relative, target)
    shutil.copytree(
        root / "data" / "concepts",
        destination / "data" / "concepts",
    )
    return assignment_path


def _baseline_fact_templates(baseline: dict) -> dict[str, list[dict]]:
    return {
        entry["slug"]: [
            {
                "text": fact["text"],
                "sourceStatement": fact["sourceStatement"],
                "sourceRefs": fact["sourceRefs"],
            }
            for fact in entry["factUnits"]
        ]
        for entry in baseline["notes"]
    }


def _validate_resealed_baseline(
    context: audit.BatchContext,
    baseline: dict,
    *,
    registry: dict[str, str] | None = None,
) -> set[str]:
    original_registry = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
    audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = (
        {
            **original_registry,
            context.batch["id"]: canonical_sha256(baseline),
        }
        if registry is None
        else registry
    )
    try:
        return {
            finding.code
            for finding in audit.validate_baseline_lock(
                replace(context, baseline=baseline)
            )
        }
    finally:
        audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_registry


def test_phase2a_batch01_baseline_is_lossless_and_regenerates_byte_identically() -> None:
    root, _, context = _production_phase2a_batch01()
    baseline = context.baseline
    assert isinstance(baseline, dict)
    baseline_path = root / context.baseline_path
    expected_slugs = list(
        audit.ACTIVE_PHASE2A_BATCHES["batch-01-anatomy"]["slugs"]
    )

    assert [entry["slug"] for entry in baseline["notes"]] == expected_slugs
    assert audit.validate_baseline_lock(context) == []
    for entry in baseline["notes"]:
        note = context.note_records[entry["slug"]]
        assert (
            audit._phase2_reconstructed_original_sha256(context, entry, note)
            == entry["originalSha256"]
        )
        assert entry["summaryHeadings"] == [
            section.heading for section in note.summaries
        ]

    deterministic_bytes = (
        json.dumps(baseline, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    assert deterministic_bytes == baseline_path.read_bytes()
    try:
        audit.build_phase2_baseline_lock(
            context,
            _baseline_fact_templates(baseline),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("A post-rewrite checkout must not reseal its baseline.")
    assert hashlib.sha256(deterministic_bytes).hexdigest() == hashlib.sha256(
        baseline_path.read_bytes()
    ).hexdigest()


def test_phase2a_batch01_fact_units_cover_source_statements_in_stable_order() -> None:
    _, _, context = _production_phase2a_batch01()
    baseline = context.baseline
    assert isinstance(baseline, dict)
    for entry in baseline["notes"]:
        slug = entry["slug"]
        facts = entry["factUnits"]
        assert [fact["id"] for fact in facts] == [
            f"{slug}-f{index:02d}" for index in range(1, len(facts) + 1)
        ]
        assert all(fact["text"].strip() for fact in facts)
        locked_note = audit.parse_note_text(
            context.note_records[slug].path,
            "---\nsubspecialty: [NR]\n---\n" + entry["originalSummary"],
        )
        source_statements = audit.phase2_summary_source_statements(
            locked_note
        )
        assert list(dict.fromkeys(fact["sourceStatement"] for fact in facts)) == [
            statement["text"] for statement in source_statements
        ]


def test_phase2_baseline_rejects_ungrounded_blank_and_lost_source_statements() -> None:
    _, _, context = _production_phase2a_batch01()
    baseline = context.baseline
    assert isinstance(baseline, dict)

    for mutation in ("ungrounded", "blank", "lost-statement"):
        changed = deepcopy(baseline)
        facts = changed["notes"][0]["factUnits"]
        if mutation == "ungrounded":
            facts[0]["text"] = "Injected relationship absent from the Summary."
        elif mutation == "blank":
            facts[0]["text"] = "   "
        else:
            source_statement = facts[0]["sourceStatement"]
            changed["notes"][0]["factUnits"] = [
                fact
                for fact in facts
                if fact["sourceStatement"] != source_statement
            ]
            for index, fact in enumerate(
                changed["notes"][0]["factUnits"], start=1
            ):
                fact["id"] = (
                    f"{changed['notes'][0]['slug']}-f{index:02d}"
                )
        assert "phase2-baseline-schema" in _validate_resealed_baseline(
            context, changed
        ), mutation


def test_phase2_baseline_rejects_malformed_duplicate_and_undefined_source_refs() -> None:
    _, _, context = _production_phase2a_batch01()
    baseline = context.baseline
    assert isinstance(baseline, dict)
    first_fact = baseline["notes"][0]["factUnits"][0]

    for source_refs in (
        "1",
        [1],
        [first_fact["sourceRefs"][0], first_fact["sourceRefs"][0]],
        ["undefined"],
    ):
        changed = deepcopy(baseline)
        changed["notes"][0]["factUnits"][0]["sourceRefs"] = source_refs
        assert "phase2-baseline-schema" in _validate_resealed_baseline(
            context, changed
        ), source_refs


def test_phase2_baseline_rejects_missing_extra_and_duplicate_notes() -> None:
    _, _, context = _production_phase2a_batch01()
    baseline = context.baseline
    assert isinstance(baseline, dict)
    mutations = []

    missing = deepcopy(baseline)
    missing["notes"].pop()
    mutations.append(missing)

    duplicate = deepcopy(baseline)
    duplicate["notes"].append(deepcopy(duplicate["notes"][0]))
    mutations.append(duplicate)

    extra = deepcopy(baseline)
    extra_entry = deepcopy(extra["notes"][0])
    extra_entry["slug"] = "unexpected-note"
    extra["notes"].append(extra_entry)
    mutations.append(extra)

    for changed in mutations:
        assert "phase2-baseline-inventory-mismatch" in _validate_resealed_baseline(
            context, changed
        )


def test_phase2a_batch01_registry_digest_remains_central_and_fail_closed() -> None:
    root, _, context = _production_phase2a_batch01()
    baseline = context.baseline
    assert isinstance(baseline, dict)
    digest = canonical_sha256(baseline)
    assert audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256["batch-01-anatomy"] == digest
    assert set(audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256) == {
        "batch-01-anatomy",
        "batch-02-disease",
    }
    assert not list(
        (
            root
            / "docs"
            / "reports"
            / "nr-summary-rewrite"
            / "phase2a"
            / "baselines"
        ).glob("batch-03-*.json")
    )

    for registry in (
        {},
        {"batch-01-anatomy": "0" * 64},
        {
            "batch-01-anatomy": digest,
            "unknown-batch": "1" * 64,
        },
    ):
        assert "phase2-trusted-batch-lock-mismatch" in _validate_resealed_baseline(
            context,
            deepcopy(baseline),
            registry=registry,
        ), registry


def test_phase2a_batch01_rejects_coordinated_mutable_baseline_replacement() -> None:
    root, assignment_path, context = _production_phase2a_batch01()
    with tempfile.TemporaryDirectory() as directory:
        shadow = Path(directory) / "coordinated-mutation"
        paths = [
            assignment_path,
            context.inventory_path,
            context.baseline_path,
            context.evidence_path,
            *(
                context.baseline_path.parent / f"{batch_id}.json"
                for batch_id in audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
                if batch_id != context.batch["id"]
            ),
            *(
                Path(record.path)
                for record in context.note_records.values()
            ),
        ]
        for relative in paths:
            destination = shadow / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / relative, destination)

        target_slug = context.batch["slugs"][0]
        target_path = shadow / context.note_records[target_slug].path
        target_path.write_bytes(target_path.read_bytes() + b"\n")
        replacement_hash = hashlib.sha256(target_path.read_bytes()).hexdigest()

        inventory_path = shadow / context.inventory_path
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        inventory_entry = next(
            entry for entry in inventory["notes"] if entry["slug"] == target_slug
        )
        inventory_entry["originalSha256"] = replacement_hash
        assignment = audit.build_phase2_assignment(inventory)
        inventory = audit.synchronize_phase2_inventory(inventory, assignment)
        inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
        (shadow / assignment_path).write_text(
            json.dumps(assignment), encoding="utf-8"
        )

        baseline_path = shadow / context.baseline_path
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        baseline["assignmentSha256"] = canonical_sha256(assignment)
        baseline_entry = next(
            entry for entry in baseline["notes"] if entry["slug"] == target_slug
        )
        baseline_entry["originalSha256"] = replacement_hash
        baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

        evidence_path = shadow / context.evidence_path
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["baselineLock"]["sha256"] = canonical_sha256(baseline)
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

        attacked_context = audit.load_phase2_batch(
            shadow,
            assignment_path,
            "batch-01-anatomy",
        )
        codes = {
            finding.code
            for finding in audit.validate_baseline_lock(attacked_context)
        }

    assert codes == {"phase2-trusted-batch-lock-mismatch"}


def test_phase2a_batch01_pending_scaffold_is_deterministic_but_nonterminal() -> None:
    root, _, context = _production_phase2a_batch01()
    baseline = context.baseline
    assert isinstance(baseline, dict)
    evidence = audit.build_phase2_pending_evidence_scaffold(
        context,
        implementer="/root/phase2a_task2_1_impl",
    )

    assert evidence["status"] == "baseline"
    assert evidence["workflow"] == {
        "sequence": 1,
        "predecessor": None,
        "implementer": "/root/phase2a_task2_1_impl",
        "reviewer": None,
        "reviewStatus": "not-started",
        "reviewedBaselineSha256": None,
    }
    assert evidence["manualReviewFactIds"] == []
    assert all(entry["status"] == "pending" for entry in evidence["notes"])
    assert all(
        fact["disposition"] == "pending"
        for entry in evidence["notes"]
        for fact in entry["facts"]
    )
    assert all(
        "coverageEvidenceSha256" not in entry
        and "validation" not in entry
        and "newUnsupportedFacts" not in entry
        for entry in evidence["notes"]
    )
    assert json.loads(
        audit.build_phase2_pending_evidence_scaffold_bytes(
            context,
            implementer="/root/phase2a_task2_1_impl",
        )
    ) == evidence
    pending_context = replace(context, evidence=evidence)
    assert audit.validate_phase2_batch(
        pending_context,
        check_source_hashes=False,
        check_generated=False,
    )
    assert audit.build_phase2_pending_evidence_scaffold_bytes(
        context,
        implementer="/root/phase2a_task2_1_impl",
    ).endswith(b"\n")


def test_phase2a_batch01_baseline_validation_has_shadow_checkout_parity() -> None:
    root, assignment_path, context = _production_phase2a_batch01()
    canonical_codes = [
        finding.code
        for finding in audit.validate_baseline_lock(context)
    ]
    with tempfile.TemporaryDirectory() as directory:
        shadow = Path(directory) / "relocated" / "shadow"
        paths = [
            assignment_path,
            context.inventory_path,
            context.baseline_path,
            context.evidence_path,
            *(
                context.baseline_path.parent / f"{batch_id}.json"
                for batch_id in audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
                if batch_id != context.batch["id"]
            ),
            *(
                Path(record.path)
                for record in context.note_records.values()
            ),
        ]
        for relative in paths:
            destination = shadow / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / relative, destination)
        shadow_context = audit.load_phase2_batch(
            shadow,
            assignment_path,
            "batch-01-anatomy",
        )
        shadow_codes = [
            finding.code
            for finding in audit.validate_baseline_lock(shadow_context)
        ]
    assert canonical_codes == shadow_codes == []


def test_phase2_noncovered_empty_refs_are_queued_but_covered_empty_refs_fail() -> None:
    results: dict[str, set[str]] = {}
    for disposition in ("research-needed", "covered"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assignment_path, baseline_digest = write_phase2_api_fixture(root)
            evidence_path = (
                root
                / "docs"
                / "reports"
                / "nr-summary-rewrite"
                / "phase2a"
                / "evidence"
                / "batch-01-anatomy.json"
            )
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            entry = evidence["notes"][0]
            fact = entry["facts"][0]
            fact["sourceRefs"] = []
            fact["disposition"] = disposition
            if disposition == "research-needed":
                entry["sourceDefinitions"] = {}
                entry["status"] = "research-needed"
                entry["sourceStatus"] = "research-needed"
                entry["validation"]["factCoverage"] = {
                    "total": 1,
                    "covered": 0,
                    "researchNeeded": 1,
                    "manualReview": 0,
                }
                evidence["manualReviewFactIds"] = [fact["id"]]
                evidence["status"] = "needs-review"
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

            original_trust = audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256
            audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = {
                "batch-01-anatomy": baseline_digest
            }
            try:
                context = audit.load_phase2_batch(
                    root, assignment_path, "batch-01-anatomy"
                )
                results[disposition] = {
                    finding.code
                    for finding in audit.validate_phase2_batch(
                        context,
                        check_source_hashes=False,
                        check_generated=False,
                    )
                }
            finally:
                audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 = original_trust

    assert "evidence-source-definition" not in results["research-needed"]
    assert "evidence-source-definition" in results["covered"]


def test_phase2a_batch01_rewrite_preserves_every_non_summary_byte() -> None:
    root, _, context = _production_phase2a_batch01()
    baseline = context.baseline
    assert isinstance(baseline, dict)

    for locked in baseline["notes"]:
        note = context.note_records[locked["slug"]]
        current_bytes = (root / note.path).read_bytes()
        current_summary = note.original_summary.encode("utf-8")
        assert current_bytes.count(current_summary) == 1
        reconstructed = current_bytes.replace(
            current_summary,
            locked["originalSummary"].encode("utf-8"),
            1,
        )
        assert hashlib.sha256(reconstructed).hexdigest() == locked["originalSha256"]


def test_phase2a_batch01_rewrite_evidence_is_deterministic_and_reviewed() -> None:
    root, _, context = _production_phase2a_batch01()
    expected_queue = ["brain-herniation-syndromes-f03"]
    regenerated = audit.build_phase2_rewrite_evidence(
        context,
        implementer="/root/phase2a_task2_2_impl",
        reviewer="/root/phase2a_task2_3_review",
        research_needed_fact_ids=expected_queue,
    )
    reviewed = deepcopy(regenerated)
    baseline_digest = canonical_sha256(context.baseline)
    reviewed["workflow"]["reviewStatus"] = "approved"
    reviewed["workflow"]["reviewedBaselineSha256"] = baseline_digest
    assert reviewed == context.evidence
    assert (
        json.dumps(reviewed, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8") == (root / context.evidence_path).read_bytes()

    evidence = reviewed
    assert evidence["status"] == "needs-review"
    assert evidence["manualReviewFactIds"] == expected_queue
    assert evidence["workflow"] == {
        "sequence": 1,
        "predecessor": None,
        "implementer": "/root/phase2a_task2_2_impl",
        "reviewer": "/root/phase2a_task2_3_review",
        "reviewStatus": "approved",
        "reviewedBaselineSha256": baseline_digest,
    }
    facts = [
        fact for entry in evidence["notes"] for fact in entry["facts"]
    ]
    assert len(facts) == 121
    assert sum(fact["disposition"] == "covered" for fact in facts) == 120
    assert sum(fact["disposition"] == "research-needed" for fact in facts) == 1
    assert all(
        entry["newUnsupportedFacts"] == 0 for entry in evidence["notes"]
    )

    findings = audit.validate_phase2_batch(
        replace(context, evidence=reviewed),
        check_source_hashes=False,
        check_generated=False,
    )
    assert findings == []


def test_phase2a_batch01_summaries_are_flat_sourced_cards_with_stable_facts() -> None:
    _, _, context = _production_phase2a_batch01()
    baseline = context.baseline
    evidence = context.evidence
    assert isinstance(baseline, dict)
    assert isinstance(evidence, dict)
    evidence_by_slug = {entry["slug"]: entry for entry in evidence["notes"]}

    for locked in baseline["notes"]:
        slug = locked["slug"]
        note = context.note_records[slug]
        entry = evidence_by_slug[slug]
        assert audit.validate_summary(note) == []
        lines = [
            line
            for section in note.summaries
            for line in section.content.splitlines()
            if line.strip()
        ]
        assert lines
        assert all(audit.VALID_BULLET_RE.match(line) for line in lines)
        assert all(audit.FOOTNOTE_REFERENCE_RE.search(line) for line in lines)
        assert entry["summaryBulletEvidence"] == audit._generated_keypoints(note)
        assert [fact["id"] for fact in entry["facts"]] == [
            fact["id"] for fact in locked["factUnits"]
        ]

        current_text = note.original_summary
        critical_markers = {
            marker
            for fact in locked["factUnits"]
            for marker in re.findall(
                r"(?:第\s*\d+\s*版|[<>≤≥]?\d+(?:[.–-]\d+)*(?:\s*(?:mm|cm|%|天))?|"
                r"non-HPV|p16−|不必然|不能|無|勿|少見|唯一|例外|另分)",
                fact["text"],
            )
        }
        compact_current = re.sub(r"\s+", "", current_text)
        assert all(
            re.sub(r"\s+", "", marker) in compact_current
            for marker in critical_markers
        )

    unresolved = evidence_by_slug["brain-herniation-syndromes"]["facts"][2]
    assert unresolved == {
        "id": "brain-herniation-syndromes-f03",
        "sourceRefs": [],
        "disposition": "research-needed",
    }
    assert "顳葉鉤回內移" not in context.note_records[
        "brain-herniation-syndromes"
    ].original_summary


def test_phase2a_batch01_production_generated_seal_is_genuine_and_relocation_stable() -> None:
    root, assignment_path, context = _production_phase2a_batch01()
    evidence = context.evidence
    assert isinstance(evidence, dict)
    baseline_digest = canonical_sha256(context.baseline)
    assert evidence["workflow"] == {
        "sequence": 1,
        "predecessor": None,
        "implementer": "/root/phase2a_task2_2_impl",
        "reviewer": "/root/phase2a_task2_3_review",
        "reviewStatus": "approved",
        "reviewedBaselineSha256": baseline_digest,
    }
    assert audit.validate_phase2_batch(
        context,
        check_source_hashes=False,
        check_generated=True,
    ) == []

    manifest_path = (
        root
        / "docs"
        / "reports"
        / "nr-summary-rewrite"
        / "phase2a"
        / "generated"
        / "batch-01-anatomy.json"
    )
    checked = json.loads(manifest_path.read_text(encoding="utf-8"))
    observation_digest = canonical_sha256(
        audit._phase2_generated_observation_projection(checked)
    )
    assert audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 == {
        "batch-01-anatomy": observation_digest
    }

    before = audit._phase2_generated_snapshot(context)
    rerun = audit.run_phase2_generated_observation_workflow(
        root, "batch-01-anatomy"
    )
    after = audit._phase2_generated_snapshot(context)
    assert rerun == {
        "manifest": checked,
        "observationSha256": observation_digest,
    }
    assert before == after

    with tempfile.TemporaryDirectory() as directory:
        shadow = Path(directory) / "relocated" / "checkout"
        shadow_assignment = _copy_production_phase2a_batch01_checkout(shadow)
        assert shadow_assignment == assignment_path
        shadow_context = audit.load_phase2_batch(
            shadow,
            shadow_assignment,
            "batch-01-anatomy",
        )
        assert audit.validate_phase2_batch(
            shadow_context,
            check_source_hashes=False,
            check_generated=True,
        ) == []
        shadow_before = audit._phase2_generated_snapshot(shadow_context)
        shadow_rerun = audit.run_phase2_generated_observation_workflow(
            shadow, "batch-01-anatomy"
        )
        shadow_after = audit._phase2_generated_snapshot(shadow_context)
        assert shadow_rerun == rerun
        assert shadow_before == shadow_after


def test_phase2a_batch01_generated_registry_rejects_missing_wrong_and_extra_trust() -> None:
    _, _, context = _production_phase2a_batch01()
    original_registry = audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256
    valid_digest = original_registry.get("batch-01-anatomy")
    assert isinstance(valid_digest, str)
    registries = (
        {},
        {"batch-01-anatomy": "0" * 64},
        {
            "batch-01-anatomy": valid_digest,
            "batch-02-disease": "1" * 64,
        },
        {
            "batch-01-anatomy": valid_digest,
            "unknown-batch": "1" * 64,
        },
    )
    try:
        for registry in registries:
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = registry
            codes = {
                finding.code
                for finding in audit.validate_phase2_batch(
                    context,
                    check_source_hashes=False,
                    check_generated=True,
                )
            }
            assert "generated-observation-untrusted" in codes, registry
    finally:
        audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = original_registry


def test_phase2a_batch01_workflow_rejects_unapproved_or_same_identity_before_write() -> None:
    cases = (
        ("not-started", "phase2-review-sequence"),
        ("same-identity", "phase2-reviewer-conflict"),
    )
    for mutation, expected_code in cases:
        with tempfile.TemporaryDirectory() as directory:
            shadow = Path(directory) / mutation
            assignment_path = _copy_production_phase2a_batch01_checkout(shadow)
            evidence_path = (
                shadow
                / "docs"
                / "reports"
                / "nr-summary-rewrite"
                / "phase2a"
                / "evidence"
                / "batch-01-anatomy.json"
            )
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            if mutation == "not-started":
                evidence["workflow"]["reviewStatus"] = "not-started"
                evidence["workflow"]["reviewedBaselineSha256"] = None
            else:
                evidence["workflow"]["reviewer"] = evidence["workflow"][
                    "implementer"
                ]
            evidence_path.write_text(
                json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            context = audit.load_phase2_batch(
                shadow, assignment_path, "batch-01-anatomy"
            )
            before = audit._phase2_generated_snapshot(context)
            try:
                audit.run_phase2_generated_observation_workflow(
                    shadow, "batch-01-anatomy"
                )
            except audit.Phase2LoadError as error:
                failure_code = error.code
            else:
                failure_code = None
            after = audit._phase2_generated_snapshot(context)
            assert failure_code == expected_code, mutation
            assert after == before, mutation


def test_phase2a_batch01_workflow_rejects_nonselected_byte_or_mtime_write() -> None:
    import build_concepts as concept_builder

    original_builder = concept_builder.build_selected_concepts
    for mutation in ("bytes", "mtime"):
        with tempfile.TemporaryDirectory() as directory:
            shadow = Path(directory) / mutation
            assignment_path = _copy_production_phase2a_batch01_checkout(shadow)
            context = audit.load_phase2_batch(
                shadow, assignment_path, "batch-01-anatomy"
            )
            selected = set(context.batch["slugs"])
            victim = next(
                path
                for path in sorted((shadow / context.generated_root).glob("*.json"))
                if path.stem not in selected
            )
            calls = 0

            def mutating_builder(*args, **kwargs):
                nonlocal calls
                result = original_builder(*args, **kwargs)
                calls += 1
                if calls == 1:
                    if mutation == "bytes":
                        victim.write_bytes(victim.read_bytes() + b"\n")
                    else:
                        stat = victim.stat()
                        os.utime(
                            victim,
                            ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000_000),
                        )
                return result

            concept_builder.build_selected_concepts = mutating_builder
            try:
                try:
                    audit.run_phase2_generated_observation_workflow(
                        shadow, "batch-01-anatomy"
                    )
                except audit.Phase2LoadError as error:
                    failure_code = error.code
                else:
                    failure_code = None
            finally:
                concept_builder.build_selected_concepts = original_builder
            assert failure_code == "generated-unrelated-write", mutation


def test_phase2a_batch01_workflow_rejects_second_run_byte_or_mtime_drift() -> None:
    import build_concepts as concept_builder

    original_builder = concept_builder.build_selected_concepts
    for mutation in ("bytes", "mtime"):
        with tempfile.TemporaryDirectory() as directory:
            shadow = Path(directory) / mutation
            assignment_path = _copy_production_phase2a_batch01_checkout(shadow)
            context = audit.load_phase2_batch(
                shadow, assignment_path, "batch-01-anatomy"
            )
            victim = (
                shadow
                / context.generated_root
                / f"{context.batch['slugs'][0]}.json"
            )
            calls = 0

            def mutating_builder(*args, **kwargs):
                nonlocal calls
                result = original_builder(*args, **kwargs)
                calls += 1
                if calls == 2:
                    if mutation == "bytes":
                        victim.write_bytes(victim.read_bytes() + b"\n")
                    else:
                        stat = victim.stat()
                        os.utime(
                            victim,
                            ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000_000),
                        )
                return result

            concept_builder.build_selected_concepts = mutating_builder
            try:
                try:
                    audit.run_phase2_generated_observation_workflow(
                        shadow, "batch-01-anatomy"
                    )
                except audit.Phase2LoadError as error:
                    failure_code = error.code
                else:
                    failure_code = None
            finally:
                concept_builder.build_selected_concepts = original_builder
            assert failure_code == "generated-non-idempotent", mutation


def test_phase2a_batch01_selected_keypoints_and_detail_drift_are_rejected() -> None:
    with tempfile.TemporaryDirectory() as directory:
        shadow = Path(directory) / "selected-drift"
        assignment_path = _copy_production_phase2a_batch01_checkout(shadow)
        context = audit.load_phase2_batch(
            shadow, assignment_path, "batch-01-anatomy"
        )
        slug = context.batch["slugs"][0]
        detail_path = shadow / context.generated_root / f"{slug}.json"
        detail = json.loads(detail_path.read_text(encoding="utf-8"))
        detail["keyPoints"] = ["forged"]
        detail_path.write_text(
            json.dumps(detail, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        attacked_context = audit.load_phase2_batch(
            shadow, assignment_path, "batch-01-anatomy"
        )
        codes = {
            finding.code
            for finding in audit.validate_phase2_batch(
                attacked_context,
                check_source_hashes=False,
                check_generated=True,
            )
        }
    assert "generated-keypoints-mismatch" in codes
    assert "generated-manifest-mismatch" in codes


def test_phase2a_batch01_coordinated_evidence_manifest_detail_mutation_is_untrusted() -> None:
    with tempfile.TemporaryDirectory() as directory:
        shadow = Path(directory) / "coordinated-mutation"
        assignment_path = _copy_production_phase2a_batch01_checkout(shadow)
        context = audit.load_phase2_batch(
            shadow, assignment_path, "batch-01-anatomy"
        )
        slug = context.batch["slugs"][0]
        note_path = shadow / context.note_records[slug].path
        note_text = note_path.read_text(encoding="utf-8")
        assert "**版本變革**" in note_text
        note_path.write_text(
            note_text.replace("**版本變革**", "**版本變革核對**", 1),
            encoding="utf-8",
            newline="",
        )
        mutated_note = audit.parse_note(note_path)

        evidence_path = shadow / context.evidence_path
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence_entry = next(
            entry for entry in evidence["notes"] if entry["slug"] == slug
        )
        evidence_entry["rewrittenSummary"] = mutated_note.original_summary
        evidence_entry["summaryBulletEvidence"] = audit._generated_keypoints(
            mutated_note
        )
        evidence_entry["coverageEvidenceSha256"] = (
            audit.phase2_coverage_evidence_sha256(
                evidence["baselineLock"]["sha256"],
                evidence_entry,
            )
        )
        evidence_path.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        detail_path = shadow / context.generated_root / f"{slug}.json"
        detail = json.loads(detail_path.read_text(encoding="utf-8"))
        detail["keyPoints"] = audit._generated_keypoints(mutated_note)
        detail_path.write_text(
            json.dumps(detail, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        manifest_path = (
            shadow
            / "docs"
            / "reports"
            / "nr-summary-rewrite"
            / "phase2a"
            / "generated"
            / "batch-01-anatomy.json"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        detail_relative = (
            context.generated_root / f"{slug}.json"
        ).as_posix()
        manifest["detailFiles"][detail_relative] = hashlib.sha256(
            detail_path.read_bytes()
        ).hexdigest()
        historical_hashes = dict(manifest["nonselectedAfter"])
        historical_hashes.update(manifest["detailFiles"])
        manifest["detailTreeSha256"] = canonical_sha256(
            [
                {"path": path, "sha256": historical_hashes[path]}
                for path in sorted(historical_hashes)
            ]
        )
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        attacked_context = audit.load_phase2_batch(
            shadow, assignment_path, "batch-01-anatomy"
        )
        codes = {
            finding.code
            for finding in audit.validate_phase2_batch(
                attacked_context,
                check_source_hashes=False,
                check_generated=True,
            )
        }
    assert "generated-observation-untrusted" in codes


def test_phase2a_batch01_unresolved_fact_is_accepted_only_as_needs_review() -> None:
    _, _, context = _production_phase2a_batch01()
    evidence = context.evidence
    assert isinstance(evidence, dict)
    assert audit.validate_phase2_batch(
        context,
        check_source_hashes=False,
        check_generated=True,
    ) == []
    assert evidence["status"] == "needs-review"
    assert evidence["manualReviewFactIds"] == [
        "brain-herniation-syndromes-f03"
    ]
    assert sum(entry["status"] == "verified" for entry in evidence["notes"]) == 9
    affected = next(
        entry
        for entry in evidence["notes"]
        if entry["slug"] == "brain-herniation-syndromes"
    )
    assert affected["status"] == "research-needed"
    assert affected["facts"][2] == {
        "id": "brain-herniation-syndromes-f03",
        "sourceRefs": [],
        "disposition": "research-needed",
    }

    forged = deepcopy(evidence)
    forged["status"] = "verified"
    forged["manualReviewFactIds"] = []
    forged_affected = next(
        entry
        for entry in forged["notes"]
        if entry["slug"] == "brain-herniation-syndromes"
    )
    forged_affected["status"] = "verified"
    codes = {
        finding.code
        for finding in audit.validate_phase2_batch(
            replace(context, evidence=forged),
            check_source_hashes=False,
            check_generated=False,
        )
    }
    assert "phase2-manual-queue-mismatch" in codes
    assert "phase2-evidence-schema" in codes


def _batch02_resealed_codes(baseline: dict) -> set[str]:
    _, _, context = _production_phase2a_batch02()
    batch01 = json.loads(
        (
            context.repo_root
            / "docs"
            / "reports"
            / "nr-summary-rewrite"
            / "phase2a"
            / "baselines"
            / "batch-01-anatomy.json"
        ).read_text(encoding="utf-8")
    )
    return _validate_resealed_baseline(
        context,
        baseline,
        registry={
            "batch-01-anatomy": canonical_sha256(batch01),
            "batch-02-disease": canonical_sha256(baseline),
        },
    )


def test_phase2a_batch02_baseline_is_exact_lossless_and_byte_deterministic() -> None:
    root, _, context = _production_phase2a_batch02()
    baseline = context.baseline
    assert isinstance(baseline, dict)
    assert context.batch["type"] == "disease"
    assert context.batch["slugs"] == list(BATCH02_DISEASE_SLUGS)
    assert [entry["slug"] for entry in baseline["notes"]] == list(
        BATCH02_DISEASE_SLUGS
    )
    assert baseline["assignmentSha256"] == canonical_sha256(context.assignment)
    assert audit.validate_baseline_lock(context) == []
    assert audit._validate_phase2_source_state(context, pre_edit=True) == []

    for entry in baseline["notes"]:
        slug = entry["slug"]
        note = context.note_records[slug]
        assert entry["path"] == f"vault/concepts/{slug}.md"
        assert entry["type"] == "disease"
        assert entry["originalSha256"] == BATCH02_PREEDIT_SHA256[slug]
        assert note.sha256 == BATCH02_PREEDIT_SHA256[slug]
        assert entry["originalSummary"] == note.original_summary
        assert entry["summaryHeadings"] == [
            section.heading for section in note.summaries
        ]

    templates = _baseline_fact_templates(baseline)
    regenerated = audit.build_phase2_baseline_lock(context, templates)
    regenerated_bytes = audit.build_phase2_baseline_lock_bytes(
        context, templates
    )
    baseline_path = root / context.baseline_path
    assert regenerated == baseline
    assert regenerated_bytes == baseline_path.read_bytes()
    assert (
        hashlib.sha256(regenerated_bytes).hexdigest()
        == hashlib.sha256(baseline_path.read_bytes()).hexdigest()
    )


def test_phase2a_batch02_fact_units_cover_every_source_statement_in_order() -> None:
    _, _, context = _production_phase2a_batch02()
    baseline = context.baseline
    assert isinstance(baseline, dict)

    observed_counts: dict[str, tuple[int, int, int]] = {}
    for entry in baseline["notes"]:
        slug = entry["slug"]
        note = context.note_records[slug]
        facts = entry["factUnits"]
        statements = audit.phase2_summary_source_statements(note)
        referenced = list(
            dict.fromkeys(
                ref
                for fact in facts
                for ref in fact["sourceRefs"]
            )
        )
        observed_counts[slug] = (
            len(statements),
            len(facts),
            len(referenced),
        )
        assert [fact["id"] for fact in facts] == [
            f"{slug}-f{index:02d}"
            for index in range(1, len(facts) + 1)
        ]
        assert list(
            dict.fromkeys(fact["sourceStatement"] for fact in facts)
        ) == [statement["text"] for statement in statements]
        assert [
            {
                "text": fact["text"],
                "sourceStatement": fact["sourceStatement"],
                "sourceRefs": fact["sourceRefs"],
            }
            for fact in facts
        ] == audit.phase2_default_fact_templates(note)
        assert all(fact["text"].strip() for fact in facts)
        assert all(
            isinstance(fact["sourceRefs"], list)
            and len(fact["sourceRefs"]) == len(set(fact["sourceRefs"]))
            and all(ref in note.footnote_defs for ref in fact["sourceRefs"])
            for fact in facts
        )

    assert observed_counts == BATCH02_STATEMENT_FACT_REF_COUNTS
    assert sum(counts[0] for counts in observed_counts.values()) == 69
    assert sum(counts[1] for counts in observed_counts.values()) == 131


def test_phase2a_batch02_rejects_note_and_fact_membership_order_attacks() -> None:
    _, _, context = _production_phase2a_batch02()
    baseline = context.baseline
    assert isinstance(baseline, dict)

    note_mutations = []
    missing_note = deepcopy(baseline)
    missing_note["notes"].pop()
    note_mutations.append(missing_note)
    duplicate_note = deepcopy(baseline)
    duplicate_note["notes"].append(deepcopy(duplicate_note["notes"][0]))
    note_mutations.append(duplicate_note)
    extra_note = deepcopy(baseline)
    extra_entry = deepcopy(extra_note["notes"][0])
    extra_entry["slug"] = "not-in-batch-02"
    extra_note["notes"].append(extra_entry)
    note_mutations.append(extra_note)
    reordered_notes = deepcopy(baseline)
    reordered_notes["notes"][0], reordered_notes["notes"][1] = (
        reordered_notes["notes"][1],
        reordered_notes["notes"][0],
    )
    note_mutations.append(reordered_notes)
    for changed in note_mutations:
        assert "phase2-baseline-inventory-mismatch" in _batch02_resealed_codes(
            changed
        )

    duplicate_fact_id = deepcopy(baseline)
    duplicate_fact_id["notes"][0]["factUnits"][1]["id"] = (
        duplicate_fact_id["notes"][0]["factUnits"][0]["id"]
    )
    reordered_facts = deepcopy(baseline)
    reordered_facts["notes"][0]["factUnits"][0:2] = reversed(
        reordered_facts["notes"][0]["factUnits"][0:2]
    )
    lost_statement = deepcopy(baseline)
    source_statement = lost_statement["notes"][0]["factUnits"][0][
        "sourceStatement"
    ]
    lost_statement["notes"][0]["factUnits"] = [
        fact
        for fact in lost_statement["notes"][0]["factUnits"]
        if fact["sourceStatement"] != source_statement
    ]
    for index, fact in enumerate(
        lost_statement["notes"][0]["factUnits"], start=1
    ):
        fact["id"] = (
            f"{lost_statement['notes'][0]['slug']}-f{index:02d}"
        )
    for changed in (duplicate_fact_id, reordered_facts, lost_statement):
        assert "phase2-baseline-schema" in _batch02_resealed_codes(changed)


def test_phase2a_batch02_rejects_blank_ungrounded_and_source_ref_attacks() -> None:
    _, _, context = _production_phase2a_batch02()
    baseline = context.baseline
    assert isinstance(baseline, dict)

    blank = deepcopy(baseline)
    blank["notes"][0]["factUnits"][0]["text"] = " "
    ungrounded = deepcopy(baseline)
    ungrounded["notes"][0]["factUnits"][0]["text"] = (
        "Injected medical relationship absent from the Summary."
    )
    malformed_refs = deepcopy(baseline)
    malformed_refs["notes"][0]["factUnits"][0]["sourceRefs"] = "1"
    undefined_ref = deepcopy(baseline)
    undefined_ref["notes"][0]["factUnits"][0]["sourceRefs"] = ["undefined"]
    duplicate_ref = deepcopy(baseline)
    fact_with_ref = next(
        fact
        for fact in duplicate_ref["notes"][0]["factUnits"]
        if fact["sourceRefs"]
    )
    fact_with_ref["sourceRefs"] = [
        fact_with_ref["sourceRefs"][0],
        fact_with_ref["sourceRefs"][0],
    ]

    for changed in (
        blank,
        ungrounded,
        malformed_refs,
        undefined_ref,
        duplicate_ref,
    ):
        assert "phase2-baseline-schema" in _batch02_resealed_codes(changed)


def test_phase2a_batch02_registry_is_exact_contiguous_prefix_and_fail_closed() -> None:
    root, _, context = _production_phase2a_batch02()
    baseline = context.baseline
    assert isinstance(baseline, dict)
    batch01 = json.loads(
        (
            root
            / "docs"
            / "reports"
            / "nr-summary-rewrite"
            / "phase2a"
            / "baselines"
            / "batch-01-anatomy.json"
        ).read_text(encoding="utf-8")
    )
    expected_registry = {
        "batch-01-anatomy": canonical_sha256(batch01),
        "batch-02-disease": canonical_sha256(baseline),
    }
    assert audit.TRUSTED_PHASE2A_BATCH_LOCK_SHA256 == expected_registry
    assert not (
        root
        / "docs"
        / "reports"
        / "nr-summary-rewrite"
        / "phase2a"
        / "baselines"
        / "batch-03-pattern.json"
    ).exists()

    for registry in (
        {},
        {"batch-01-anatomy": expected_registry["batch-01-anatomy"]},
        {"batch-02-disease": expected_registry["batch-02-disease"]},
        {
            **expected_registry,
            "batch-02-disease": "0" * 64,
        },
        {
            **expected_registry,
            "batch-03-pattern": "1" * 64,
        },
        {
            **expected_registry,
            "unknown-batch": "1" * 64,
        },
    ):
        codes = _validate_resealed_baseline(
            context,
            deepcopy(baseline),
            registry=registry,
        )
        assert "phase2-trusted-batch-lock-mismatch" in codes, registry


def test_phase2a_batch02_rejects_coordinated_mutable_baseline_replacement() -> None:
    root, assignment_path, context = _production_phase2a_batch02()
    with tempfile.TemporaryDirectory() as directory:
        shadow = Path(directory) / "coordinated-mutation"
        batch01_baseline = (
            context.baseline_path.parent / "batch-01-anatomy.json"
        )
        paths = [
            assignment_path,
            context.inventory_path,
            batch01_baseline,
            context.baseline_path,
            context.evidence_path,
            *(Path(record.path) for record in context.note_records.values()),
        ]
        for relative in paths:
            destination = shadow / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / relative, destination)

        target_slug = context.batch["slugs"][0]
        target_path = shadow / context.note_records[target_slug].path
        target_path.write_bytes(target_path.read_bytes() + b"\n")
        replacement_hash = hashlib.sha256(target_path.read_bytes()).hexdigest()

        inventory_path = shadow / context.inventory_path
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        inventory_entry = next(
            entry
            for entry in inventory["notes"]
            if entry["slug"] == target_slug
        )
        inventory_entry["originalSha256"] = replacement_hash
        assignment = audit.build_phase2_assignment(inventory)
        inventory = audit.synchronize_phase2_inventory(inventory, assignment)
        inventory_path.write_text(
            json.dumps(inventory), encoding="utf-8"
        )
        (shadow / assignment_path).write_text(
            json.dumps(assignment), encoding="utf-8"
        )

        baseline_path = shadow / context.baseline_path
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        baseline["assignmentSha256"] = canonical_sha256(assignment)
        baseline_entry = next(
            entry
            for entry in baseline["notes"]
            if entry["slug"] == target_slug
        )
        baseline_entry["originalSha256"] = replacement_hash
        baseline_path.write_text(
            json.dumps(baseline), encoding="utf-8"
        )

        evidence_path = shadow / context.evidence_path
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["baselineLock"]["sha256"] = canonical_sha256(baseline)
        evidence_path.write_text(
            json.dumps(evidence), encoding="utf-8"
        )

        attacked_context = audit.load_phase2_batch(
            shadow,
            assignment_path,
            "batch-02-disease",
        )
        codes = {
            finding.code
            for finding in audit.validate_baseline_lock(attacked_context)
        }

    assert codes == {"phase2-trusted-batch-lock-mismatch"}


def test_phase2a_batch02_pending_scaffold_is_honest_and_nonterminal() -> None:
    root, _, context = _production_phase2a_batch02()
    baseline = context.baseline
    evidence = context.evidence
    assert isinstance(baseline, dict)
    assert isinstance(evidence, dict)
    assert evidence["status"] == "baseline"
    assert evidence["workflow"] == {
        "sequence": 2,
        "predecessor": "batch-01-anatomy",
        "implementer": "/root/phase2a_task3_1_impl",
        "reviewer": None,
        "reviewStatus": "not-started",
        "reviewedBaselineSha256": None,
    }
    assert evidence["manualReviewFactIds"] == []
    assert evidence["generatedManifest"] == (
        "docs/reports/nr-summary-rewrite/phase2a/generated/"
        "batch-02-disease.json"
    )
    assert [entry["slug"] for entry in evidence["notes"]] == list(
        BATCH02_DISEASE_SLUGS
    )
    assert all(entry["status"] == "pending" for entry in evidence["notes"])
    assert all(
        fact["disposition"] == "pending"
        for entry in evidence["notes"]
        for fact in entry["facts"]
    )
    assert all(
        "coverageEvidenceSha256" not in entry
        and "validation" not in entry
        and "newUnsupportedFacts" not in entry
        for entry in evidence["notes"]
    )
    assert audit.build_phase2_pending_evidence_scaffold(
        context,
        implementer="/root/phase2a_task3_1_impl",
    ) == evidence
    assert audit.build_phase2_pending_evidence_scaffold_bytes(
        context,
        implementer="/root/phase2a_task3_1_impl",
    ) == (root / context.evidence_path).read_bytes()
    terminal_findings = audit.validate_phase2_batch(
        context,
        check_source_hashes=True,
        check_generated=False,
    )
    assert any(
        finding.severity == "error" for finding in terminal_findings
    )


def test_phase2a_batch02_baseline_has_relocated_checkout_parity() -> None:
    root, assignment_path, context = _production_phase2a_batch02()
    canonical_codes = [
        finding.code
        for finding in (
            audit.validate_baseline_lock(context)
            + audit._validate_phase2_source_state(context, pre_edit=True)
        )
    ]
    with tempfile.TemporaryDirectory() as directory:
        shadow = Path(directory) / "relocated" / "shadow"
        paths = [
            assignment_path,
            context.inventory_path,
            context.baseline_path.parent / "batch-01-anatomy.json",
            context.baseline_path,
            context.evidence_path,
            *(Path(record.path) for record in context.note_records.values()),
        ]
        for relative in paths:
            destination = shadow / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / relative, destination)
        shadow_context = audit.load_phase2_batch(
            shadow,
            assignment_path,
            "batch-02-disease",
        )
        shadow_codes = [
            finding.code
            for finding in (
                audit.validate_baseline_lock(shadow_context)
                + audit._validate_phase2_source_state(
                    shadow_context, pre_edit=True
                )
            )
        ]
    assert canonical_codes == shadow_codes == []


def test_phase2a_batch02_preserves_approved_batch01_prerequisite() -> None:
    root, _, batch01_context = _production_phase2a_batch01()
    for relative, expected_sha256 in BATCH01_APPROVED_ARTIFACT_SHA256.items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == (
            expected_sha256
        )
    assert audit.validate_phase2_batch(
        batch01_context,
        check_source_hashes=False,
        check_generated=True,
    ) == []
    manifest = json.loads(
        (
            root
            / "docs"
            / "reports"
            / "nr-summary-rewrite"
            / "phase2a"
            / "generated"
            / "batch-01-anatomy.json"
        ).read_text(encoding="utf-8")
    )
    assert audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256[
        "batch-01-anatomy"
    ] == canonical_sha256(
        audit._phase2_generated_observation_projection(manifest)
    )

    _, _, batch02_context = _production_phase2a_batch02()
    expected_baseline_bytes = audit.build_phase2_baseline_lock_bytes(
        batch02_context,
        _baseline_fact_templates(batch02_context.baseline),
    )
    original_observation_registry = (
        audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256
    )
    try:
        for registry in (
            {},
            {"batch-01-anatomy": "f" * 64},
        ):
            audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = registry
            assert audit.build_phase2_baseline_lock_bytes(
                batch02_context,
                _baseline_fact_templates(batch02_context.baseline),
            ) == expected_baseline_bytes
    finally:
        audit.TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = (
            original_observation_registry
        )


def run_smoke() -> None:
    test_evidence_rejects_unmapped_or_unresolved_fact_units()
    test_evidence_rejects_source_ref_not_defined_in_note()
    test_evidence_rejects_invalid_root_membership_hash_and_snapshot()
    test_evidence_rejects_malformed_note_and_fact_schema_without_raising()
    test_evidence_rejects_invalid_fact_identity_text_disposition_and_refs()
    test_evidence_requires_research_status_for_explicitly_unresolved_fact()
    test_evidence_enum_fields_reject_unhashable_json_values_without_raising()
    test_evidence_accepts_fact_derived_baseline_status_combinations()
    test_evidence_rejects_statuses_that_contradict_fact_dispositions()
    test_evidence_rejects_stale_validation_metadata_and_nonsequential_ids()
    test_validate_batch_cli_requires_allow_pending_for_baseline()
    test_validate_batch_cli_supports_explicit_pre_edit_hash_gate()
    test_validate_batch_cli_accepts_final_rewrites_and_explicit_manual_review()
    test_validate_batch_cli_rejects_generated_keypoints_mismatch()
    test_validate_batch_cli_rejects_all_generated_keypoints_shape_failures()
    test_generated_keypoints_preserve_all_variants_and_subheading_order()
    test_generated_data_root_is_bound_to_source_checkout_not_shadow_tree()
    test_validate_batch_cli_rejects_dangling_generated_index_entry()
    test_validate_batch_cli_rejects_nonpilot_index_metadata_drift()
    test_generated_manifest_rejects_nonpilot_drift_and_missing_output()
    test_lint_baseline_parser_accepts_exact_baseline_and_rejects_third_error()
    test_validate_batch_cli_rejects_rewritten_summary_drift()
    test_validate_batch_cli_rejects_final_integrity_mutations()
    test_validate_batch_cli_rejects_new_summary_bullet_even_when_snapshot_is_updated()
    test_trusted_baseline_anchor_rejects_coordinated_batch_reseal()
    test_trusted_summary_anchor_rejects_coordinated_existing_bullet_reseal()
    test_trusted_final_anchor_rejects_coordinated_manual_queue_reseal()
    test_plain_summary_prose_reseal_is_structurally_and_cryptographically_rejected()
    test_validate_batch_loader_rejects_redirected_duplicate_and_unsafe_paths()
    test_validate_batch_cli_allow_pending_retains_mutation_findings()
    test_real_batch_keeps_acute_stroke_legacy_claims_on_source_one()
    test_fix_round1_content_and_evidence_regressions()
    test_validate_batch_cli_handles_invalid_json_without_raising()
    test_parse_note_hashes_exact_source_bytes()
    test_note_preserves_lossless_summary_snapshot()
    test_summary_variants_are_extracted()
    test_non_nr_note_is_not_in_scope()
    test_validator_rejects_unlabeled_and_undefined_footnote()
    test_validator_rejects_callout_table_and_nested_bullet()
    test_validator_rejects_every_other_nonblank_summary_content_line()
    test_validator_accepts_level_three_subheadings_and_labeled_bullets_only()
    test_summary_heading_rejects_unapproved_suffix()
    test_validator_rejects_missing_empty_and_alternate_table_summaries()
    test_note_line_numbers_include_frontmatter()
    test_cli_prints_findings_and_uses_error_exit_code()
    test_inventory_requires_allowed_type_and_status()
    test_inventory_requires_root_contract()
    test_inventory_malformed_roots_return_stable_findings_without_raising()
    test_inventory_rejects_duplicate_slug_and_missing_nr_note()
    test_inventory_schema_accepts_closed_enum_values_but_enforces_phase1_count()
    test_inventory_rejects_invalid_status_source_batch_hash_and_headings()
    test_inventory_enum_fields_reject_unhashable_json_values_without_raising()
    test_inventory_against_notes_enforces_full_phase1_contract_on_small_fixture()
    test_inventory_rejects_regenerated_215_note_scope_after_nonpilot_missing()
    test_inventory_against_notes_rejects_path_hash_and_heading_mismatches()
    test_inventory_against_notes_rejects_fixed_pilot_membership_drift()
    test_inventory_against_notes_handles_malformed_entries_without_raising()
    test_inventory_membership_rejects_unhashable_slug_without_raising()
    test_inventory_cli_generates_and_checks_deterministically()
    test_final_inventory_check_preserves_pilot_baselines_but_checks_nonpilots()
    test_public_inventory_binds_reviewed_hashes_with_explicit_root()
    test_coordinated_pilot_hash_replacement_is_rejected_by_trusted_baseline()
    test_public_validate_evidence_rejects_coordinated_pilot_hash_replacement()
    test_shadow_checkout_validate_batch_rejects_coordinated_pilot_hash_replacement()
    test_canonical_inventory_generation_emits_trusted_pilot_hashes_and_checks()
    test_shadow_final_review_and_phase2_mutation_is_rejected_everywhere()
    test_validate_batch_rejects_ten_pilot_only_sibling_inventory()
    test_inventory_cli_reports_malformed_json_and_nonobject_root_without_traceback()
    print("NR_SUMMARY_AUDIT_OK")


if __name__ == "__main__":
    run_smoke()
