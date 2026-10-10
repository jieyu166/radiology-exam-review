#!/usr/bin/env python3
"""Run the vault-native migration acceptance suite and write one audit report.

This is intentionally a migration gate rather than a deployment shortcut.  It
checks the real vault inventory and deterministic publication output, then
executes the fixture and browser-compatible smoke tests.  Existing physician
notes are never rewritten by this command.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.audit_vault_native_cutover import audit, audit_passed
from scripts.vault_site.compiler import build_package, discover_sources


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _run(label: str, command: list[str], repo_root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "label": label,
        "command": command,
        "passed": completed.returncode == 0,
        "returnCode": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def _real_vault_acceptance(vault: Path, temp_root: Path) -> dict[str, Any]:
    first_root = temp_root / "publication-a"
    second_root = temp_root / "publication-b"
    first = build_package(vault, first_root, strict=False, write=True)
    second = build_package(vault, second_root, strict=False, write=True)
    manifest_path = first_root / "manifest.json"
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    notes = discover_sources(vault)
    eligible = [note for note in notes if note.excluded_reason is None]
    inventory = first.report.get("inventory", [])
    inventory_paths = {
        item.get("sourcePath")
        for item in inventory
        if item.get("status") in {"published", "warning", "hard_error"}
    }
    expected_paths = {note.relative_path for note in eligible}
    manifest_entries = manifest.get("entries", [])
    raw_hash_mismatches: list[str] = []
    for entry in manifest_entries:
        source = vault / entry["sourcePath"]
        raw = first_root / entry["rawPath"]
        if not source.exists() or not raw.exists() or hashlib.sha256(raw.read_bytes()).hexdigest() != entry["sourceSha256"]:
            raw_hash_mismatches.append(entry.get("sourcePath", ""))

    error_counts = Counter(error.get("code", "unknown") for error in first.errors)
    return {
        "scanned": len(notes),
        "eligible": len(eligible),
        "excluded": len(notes) - len(eligible),
        "published": first.report.get("counts", {}).get("published", 0),
        "manifestEntries": len(manifest_entries),
        "inventoryComplete": expected_paths == inventory_paths,
        "manifestRawHashesValid": not raw_hash_mismatches,
        "rawHashMismatches": raw_hash_mismatches,
        "deterministic": _tree_hashes(first_root) == _tree_hashes(second_root),
        "publicationPassed": first.ok and second.ok,
        "publicationErrors": len(first.errors),
        "publicationErrorCounts": dict(sorted(error_counts.items())),
        "publicationErrorExamples": first.errors[:20],
        "publicationErrorItems": first.errors,
        "publicationWarnings": len(first.warnings),
        "syntaxClasses": first.report.get("syntaxClasses", {}),
        "inventoryStatusCounts": dict(Counter(item.get("status", "unknown") for item in inventory)),
    }


def _failed_deploy_retention(repo_root: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="vault-native-retention-") as raw_temp:
        root = Path(raw_temp)
        vault = root / "vault"
        output = root / "dist"
        (vault / "questions" / "2024").mkdir(parents=True)
        (vault / "questions" / "2024" / "invalid.md").write_text(
            "---\nid: invalid\n---\n(A) One\n(B) Two\n(C) Three\n??\n",
            encoding="utf-8",
        )
        output.mkdir()
        sentinel = output / "previous-pages-artifact.txt"
        sentinel.write_text("keep previous artifact", encoding="utf-8")
        result = build_package(vault, output, strict=True, write=True)
        report_path = output / "build-report.json"
        return {
            "passed": bool(result.errors) and sentinel.read_text(encoding="utf-8") == "keep previous artifact" and report_path.exists() and not (output / "manifest.json").exists(),
            "hardErrors": len(result.errors),
            "previousArtifactPreserved": sentinel.exists(),
            "buildReportWritten": report_path.exists(),
            "newManifestSuppressed": not (output / "manifest.json").exists(),
        }


def _review_annotation_acceptance(vault: Path, errors: list[dict[str, Any]]) -> dict[str, Any]:
    notes = {note.relative_path: note for note in discover_sources(vault)}
    queue = sorted({item.get("sourcePath") for item in errors if item.get("sourcePath")})
    missing_review_status = [path for path in queue if notes.get(path) and notes[path].frontmatter.get("reviewStatus") != "needs_review"]
    reviewed_sources = sorted(path for path, note in notes.items() if note.frontmatter.get("reviewStatus") == "needs_review")
    expected_unresolved = sorted(path for path, note in notes.items() if note.frontmatter.get("answerStatus") == "unresolved")
    wrong_unresolved: list[str] = []
    for path in sorted(expected_unresolved):
        frontmatter = notes[path].frontmatter
        if frontmatter.get("answerStatus") != "unresolved" or frontmatter.get("answerMode") != "none" or frontmatter.get("acceptedAnswers") != []:
            wrong_unresolved.append(path)
    multi = notes.get("questions/2017/2017-010.md")
    multi_ok = bool(multi and multi.frontmatter.get("answerStatus") == "confirmed" and multi.frontmatter.get("answerMode") == "any" and multi.frontmatter.get("acceptedAnswers") == ["B", "D"])
    return {
        "queueSources": len(queue),
        "reviewedSources": len(reviewed_sources),
        "unresolvedSources": len(expected_unresolved),
        "missingReviewStatus": missing_review_status,
        "wrongUnresolvedAnnotations": wrong_unresolved,
        "multiAnswer2017_010": multi_ok,
        # 49 notes from the 2026-09 migration review queue + 2021-334 (rebuilt 2026-10-10 without its figure)
        "passed": len(reviewed_sources) == 50 and len(expected_unresolved) == 19 and not missing_review_status and not wrong_unresolved and multi_ok,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run vault-native migration acceptance")
    parser.add_argument("--vault", type=Path, default=Path("vault"))
    parser.add_argument("--report", type=Path, default=Path("tmp/vault-native-migration-acceptance.json"))
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    vault = (repo_root / args.vault).resolve() if not args.vault.is_absolute() else args.vault.resolve()
    args.report = (repo_root / args.report).resolve() if not args.report.is_absolute() else args.report.resolve()

    python_exe = sys.executable
    with tempfile.TemporaryDirectory(prefix="vault-native-acceptance-") as raw_temp:
        temp_root = Path(raw_temp)
        real_vault = _real_vault_acceptance(vault, temp_root)
        failed_deploy = _failed_deploy_retention(repo_root)
        checks = [
            _run("compiler fixture suite", [python_exe, "scripts/test_vault_site.py"], repo_root),
            _run("deployment workflow contract", [python_exe, "scripts/test_deploy_workflow.py"], repo_root),
            _run("legacy isolation", [python_exe, "scripts/test_legacy_isolation.py"], repo_root),
            _run("content store browser smoke", ["node", "scripts/test_content_store.js"], repo_root),
            _run("note renderer browser smoke", ["node", "scripts/test_note_renderer.js"], repo_root),
            _run("question view browser smoke", ["node", "scripts/test_vault_question_view.js"], repo_root),
            _run("study progress and legacy patch export", ["node", "scripts/test_study_progress.js"], repo_root),
        ]

    cutover = audit(repo_root, vault)
    annotations = _review_annotation_acceptance(vault, real_vault.get("publicationErrorItems", []))
    report: dict[str, Any] = {
        "schemaVersion": "vault-native-migration-acceptance/v1",
        "vault": str(vault),
        "realVault": real_vault,
        "failedDeployRetention": failed_deploy,
        "reviewAnnotations": annotations,
        "cutover": cutover,
        "checks": checks,
    }
    blockers: list[str] = []
    for key in ("inventoryComplete", "manifestRawHashesValid", "deterministic", "publicationPassed"):
        if not real_vault[key]:
            blockers.append(f"realVault.{key}")
    if not failed_deploy["passed"]:
        blockers.append("failedDeployRetention")
    if not annotations["passed"]:
        blockers.append("reviewAnnotations")
    if not audit_passed(cutover):
        blockers.append("cutover")
    blockers.extend(check["label"] for check in checks if not check["passed"])
    report["passed"] = not blockers
    report["blockers"] = blockers
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "blockers": blockers, "report": str(args.report)}, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
