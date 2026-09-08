#!/usr/bin/env python3
from pathlib import Path
import unittest

from audit_vault_native_cutover import LEGACY_PRODUCTION_NAMES, audit


class LegacyIsolationTests(unittest.TestCase):
    def test_production_entry_uses_vault_native_modules(self) -> None:
        root = Path(__file__).resolve().parent.parent
        index = (root / "index.html").read_text(encoding="utf-8")
        for name in LEGACY_PRODUCTION_NAMES:
            self.assertNotIn(name, index)
        self.assertIn("js/content-store.js", index)
        self.assertIn("js/note-renderer.js", index)
        self.assertIn("js/vault-app.js", index)

    def test_workflow_keeps_legacy_tools_out_of_production(self) -> None:
        root = Path(__file__).resolve().parent.parent
        workflow = (root / ".github" / "workflows" / "deploy-pages.yml").read_text(encoding="utf-8")
        for name in ("build_concepts.py", "vault_to_json.py", "json_to_vault.py"):
            self.assertNotIn(name, workflow)
        self.assertTrue((root / "scripts" / "vault_to_json.py").exists())
        self.assertTrue((root / "scripts" / "json_to_vault.py").exists())

    def test_cutover_audit_preserves_vault_source_hashes(self) -> None:
        root = Path(__file__).resolve().parent.parent
        result = audit(root, root / "vault")
        self.assertEqual(result["sourceIntegrity"], "clean")
        self.assertEqual(result["legacyIndexRefs"], [])
        self.assertEqual(result["legacyWorkflowRefs"], [])


if __name__ == "__main__":
    unittest.main()
