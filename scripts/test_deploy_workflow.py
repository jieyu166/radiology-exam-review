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

    def test_worker_workflow_tests_and_migrates_before_deploy(self) -> None:
        text = Path(".github/workflows/deploy-worker.yml").read_text(encoding="utf-8")
        self.assertIn("branches: [main]", text)
        self.assertIn("'worker/**'", text)
        self.assertIn("npm test", text)
        self.assertIn("wrangler d1 migrations apply rex-progress --remote", text)
        self.assertIn("wrangler deploy", text)
        self.assertLess(text.index("npm test"), text.index("migrations apply"), "tests run before migrations")
        self.assertLess(text.index("migrations apply"), text.index("wrangler deploy"), "migrations run before deploy")
        self.assertIn("secrets.CLOUDFLARE_API_TOKEN", text)
        self.assertNotIn("BOOTSTRAP_INVITE_CODE", text, "bootstrap secret stays in wrangler secrets, not in CI")
        pages = Path(".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
        self.assertNotIn("worker/", pages, "pages workflow does not build or deploy the worker")

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
