"""Smoke tests for the NR Summary audit interfaces.

Run directly with ``python scripts/test_nr_summary_audit.py``; no test runner
or third-party dependency is required.
"""

import hashlib
import io
import json
import tempfile
from contextlib import redirect_stderr, redirect_stdout
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
) -> tuple[int, str]:
    argv = ["validate-batch", str(batch_path)]
    if allow_pending:
        argv.append("--allow-pending")
    if check_source_hashes:
        argv.append("--check-source-hashes")
    output = io.StringIO()
    try:
        with redirect_stdout(output), redirect_stderr(output):
            exit_code = audit.main(argv)
    except SystemExit as error:
        exit_code = error.code
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
        "inventory-hash-mismatch",
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
        immutable_hash_slugs=audit.PILOT_SLUGS,
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
        immutable_hash_slugs=audit.PILOT_SLUGS,
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
    test_inventory_cli_reports_malformed_json_and_nonobject_root_without_traceback()
    print("NR_SUMMARY_AUDIT_OK")


if __name__ == "__main__":
    run_smoke()
