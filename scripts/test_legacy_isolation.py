#!/usr/bin/env python3
from pathlib import Path
import shutil
import tempfile
import unittest

from audit_vault_native_cutover import LEGACY_PRODUCTION_NAMES, RETIRED_SCRIPTS, audit, audit_passed, legacy_residue


ROOT = Path(__file__).resolve().parent.parent


class LegacyIsolationTests(unittest.TestCase):
    def test_production_entry_uses_vault_native_modules(self) -> None:
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        for name in LEGACY_PRODUCTION_NAMES:
            self.assertNotIn(name, index)
        self.assertIn("js/content-store.js", index)
        self.assertIn("js/note-renderer.js", index)
        self.assertIn("js/vault-app.js", index)

    def test_workflow_keeps_legacy_tools_out_of_production(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "deploy-pages.yml").read_text(encoding="utf-8")
        for name in RETIRED_SCRIPTS:
            self.assertNotIn(name, workflow)
        self.assertNotIn("data/", workflow)

    def test_legacy_data_flow_is_absent_from_checkout(self) -> None:
        self.assertEqual(legacy_residue(ROOT), [])
        self.assertFalse((ROOT / "data").exists())
        for name in RETIRED_SCRIPTS:
            self.assertFalse((ROOT / "scripts" / name).exists(), name)

    def test_cutover_audit_preserves_vault_source_hashes(self) -> None:
        result = audit(ROOT, ROOT / "vault")
        self.assertEqual(result["sourceIntegrity"], "clean")
        self.assertEqual(result["legacyIndexRefs"], [])
        self.assertEqual(result["legacyWorkflowRefs"], [])
        self.assertTrue(result["legacyToolsAbsent"], result["legacyResidue"])
        self.assertTrue(audit_passed(result))

    def test_cutover_audit_fails_on_legacy_residue(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            (repo / "vault" / "concepts").mkdir(parents=True)
            (repo / "vault" / "concepts" / "brain-abscess.md").write_text("---\nname: Brain abscess\n---\n# Brain abscess\n", encoding="utf-8")
            (repo / "scripts").mkdir()
            (repo / ".github" / "workflows").mkdir(parents=True)
            shutil.copy(ROOT / "index.html", repo / "index.html")
            shutil.copy(ROOT / ".github" / "workflows" / "deploy-pages.yml", repo / ".github" / "workflows" / "deploy-pages.yml")

            clean = audit(repo, repo / "vault")
            self.assertTrue(clean["legacyToolsAbsent"])
            self.assertEqual(clean["legacyResidue"], [])
            self.assertTrue(audit_passed(clean))

            (repo / "scripts" / "merge_edits.py").write_text("# residue\n", encoding="utf-8")
            (repo / "data").mkdir()
            dirty = audit(repo, repo / "vault")
            self.assertFalse(dirty["legacyToolsAbsent"])
            self.assertEqual(dirty["legacyResidue"], ["data", "scripts/merge_edits.py"])
            self.assertFalse(audit_passed(dirty))
            self.assertNotIn("legacyRecoveryToolsPresent", dirty)


if __name__ == "__main__":
    unittest.main()
