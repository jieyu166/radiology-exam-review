#!/usr/bin/env python3
"""Read-only audit for the vault-native production cutover boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from vault_site.compiler import build_package, discover_sources


LEGACY_PRODUCTION_NAMES = (
    "build_concepts.py", "vault_to_json.py", "json_to_vault.py", "concept-cards.js",
    "exam-mode.js", "question-store.js", "editor.js", "card-mode.js", "list-mode.js",
)


def _hash_sources(vault: Path) -> dict[str, str]:
    result = {}
    for note in discover_sources(vault):
        result[note.relative_path] = hashlib.sha256(note.source_bytes).hexdigest()
    return result


def audit(repo_root: Path, vault: Path) -> dict:
    repo_root = Path(repo_root).resolve()
    vault = Path(vault).resolve()
    before = _hash_sources(vault)
    compiled = build_package(vault, repo_root / "tmp" / "vault-native-cutover-audit", strict=False, write=False)
    after = _hash_sources(vault)
    changed = sorted(path for path in before if before.get(path) != after.get(path))
    index_text = (repo_root / "index.html").read_text(encoding="utf-8")
    workflow_text = (repo_root / ".github" / "workflows" / "deploy-pages.yml").read_text(encoding="utf-8")
    legacy_index_refs = [name for name in LEGACY_PRODUCTION_NAMES if name in index_text]
    legacy_workflow_refs = [name for name in LEGACY_PRODUCTION_NAMES if name in workflow_text]
    return {
        "sourceIntegrity": "clean" if not changed else "changed",
        "changedSourcePaths": changed,
        "publicationCounts": compiled.report.get("counts", {}),
        "publicationErrors": compiled.errors,
        "legacyIndexRefs": legacy_index_refs,
        "legacyWorkflowRefs": legacy_workflow_refs,
        "legacyRecoveryToolsPresent": all((repo_root / "scripts" / name).exists() for name in ("vault_to_json.py", "json_to_vault.py")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit vault-native cutover without modifying source notes")
    parser.add_argument("--vault", type=Path, default=Path("vault"))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    result = audit(repo_root, (repo_root / args.vault).resolve() if not args.vault.is_absolute() else args.vault)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"sourceIntegrity": result["sourceIntegrity"], "publicationErrors": len(result["publicationErrors"]), "legacyIndexRefs": result["legacyIndexRefs"], "legacyWorkflowRefs": result["legacyWorkflowRefs"]}, ensure_ascii=False))
    return 0 if result["sourceIntegrity"] == "clean" and not result["legacyIndexRefs"] and not result["legacyWorkflowRefs"] and result["legacyRecoveryToolsPresent"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
