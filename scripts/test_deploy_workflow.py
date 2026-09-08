#!/usr/bin/env python3
"""Static checks for the Pages workflow contract."""
from pathlib import Path
import subprocess
import unittest


class DeployWorkflowTests(unittest.TestCase):
    def test_workflow_builds_validates_smokes_before_deploy(self) -> None:
        text = Path(".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
        self.assertIn("branches: [main]", text)
        self.assertIn("scripts/build_vault_site.py", text)
        self.assertIn("scripts/validate_vault_site.py", text)
        self.assertIn("scripts/build_static_site.py", text)
        self.assertIn("actions/upload-pages-artifact@v3", text)
        self.assertIn("actions/deploy-pages@v4", text)
        self.assertIn("needs: build", text)
        self.assertIn("if: always()", text)

    def test_static_builder_does_not_copy_generated_data_sources(self) -> None:
        text = Path("scripts/build_static_site.py").read_text(encoding="utf-8")
        self.assertIn('("index.html", "css", "js")', text)
        self.assertNotIn('"data"', text)

    def test_dist_is_ignored_and_build_is_source_hash_neutral(self) -> None:
        ignored = subprocess.run(
            ["git", "check-ignore", "--no-index", "dist/"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(ignored.returncode, 0, ignored.stderr)
        self.assertIn("dist/", ignored.stdout)
        self.assertIn("copytree", Path("scripts/build_static_site.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
