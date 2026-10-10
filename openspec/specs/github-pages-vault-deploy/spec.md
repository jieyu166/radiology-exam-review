# github-pages-vault-deploy Specification

## Purpose

TBD - created by archiving change 'vault-native-review-site'. Update Purpose after archive.

## Requirements

### Requirement: Build and validate Pages artifacts on main

The GitHub Actions workflow SHALL run on pushes to `main` that affect vault publication inputs, review website source, compiler source, validation source, or workflow configuration. The workflow SHALL execute inventory, validation, compiler, static website build, and browser smoke tests before deployment.

#### Scenario: Deploy a valid main build

- **WHEN** a push to `main` passes inventory, validation, compiler, static build, and browser smoke tests
- **THEN** the workflow deploys the generated `dist/` artifact to GitHub Pages


<!-- @trace
source: vault-native-review-site
updated: 2026-10-10
code:
  - scripts/vault_site/compiler.py
  - scripts/build_static_site.py
  - start-image-manager.cmd
  - js/content-store.js
  - scripts/image_asset_manager.js
  - scripts/rewrite_phase2b_summary.py
  - scripts/audit_vault_native_cutover.py
  - docs/image-asset-manager.md
  - js/vault-app.js
  - js/exam-mode.js
  - scripts/build_phase2b_evidence.py
  - scripts/start_image_asset_manager.ps1
  - scripts/nr_summary_audit.py
  - js/data-loader.js
  - .github/workflows/deploy-pages.yml
  - scripts/validate_vault_site.py
  - index.html
  - scripts/vault_site/__init__.py
  - README.md
  - scripts/image_asset_manager.html
  - css/main.css
  - scripts/build_vault_site.py
  - docs/concept-summary-review-publication.md
  - js/vault-question-view.js
  - scripts/accept_vault_native_migration.py
  - scripts/image_asset_manager.py
  - output/imagegen/adrenoleukodystrophy-background-draft.png
  - js/note-renderer.js
  - scripts/build_concepts.py
tests:
  - scripts/test_build_concepts.py
  - scripts/test_image_asset_manager.js
  - scripts/test_study_progress.js
  - scripts/test_deploy_workflow.py
  - scripts/test_vault_question_view.js
  - scripts/test_image_asset_manager.py
  - scripts/test_legacy_isolation.py
  - scripts/test_vault_site.py
  - scripts/test_content_store.js
  - scripts/test_nr_summary_audit.py
  - scripts/test_note_renderer.js
-->

---
### Requirement: Block deployment after a hard publication failure

The workflow SHALL not deploy when inventory, validation, compiler, static build, or browser smoke tests return nonzero. A failed workflow SHALL publish a machine-readable build report containing hard errors, warnings, published counts, excluded counts, and source hashes. The failed run SHALL not replace the last successful GitHub Pages deployment.

#### Scenario: Preserve the previous deployment

- **WHEN** a main push contains a published question with an invalid SR boundary
- **THEN** the workflow records the validation error, skips Pages deployment, and leaves the prior successful Pages version available


<!-- @trace
source: vault-native-review-site
updated: 2026-10-10
code:
  - scripts/vault_site/compiler.py
  - scripts/build_static_site.py
  - start-image-manager.cmd
  - js/content-store.js
  - scripts/image_asset_manager.js
  - scripts/rewrite_phase2b_summary.py
  - scripts/audit_vault_native_cutover.py
  - docs/image-asset-manager.md
  - js/vault-app.js
  - js/exam-mode.js
  - scripts/build_phase2b_evidence.py
  - scripts/start_image_asset_manager.ps1
  - scripts/nr_summary_audit.py
  - js/data-loader.js
  - .github/workflows/deploy-pages.yml
  - scripts/validate_vault_site.py
  - index.html
  - scripts/vault_site/__init__.py
  - README.md
  - scripts/image_asset_manager.html
  - css/main.css
  - scripts/build_vault_site.py
  - docs/concept-summary-review-publication.md
  - js/vault-question-view.js
  - scripts/accept_vault_native_migration.py
  - scripts/image_asset_manager.py
  - output/imagegen/adrenoleukodystrophy-background-draft.png
  - js/note-renderer.js
  - scripts/build_concepts.py
tests:
  - scripts/test_build_concepts.py
  - scripts/test_image_asset_manager.js
  - scripts/test_study_progress.js
  - scripts/test_deploy_workflow.py
  - scripts/test_vault_question_view.js
  - scripts/test_image_asset_manager.py
  - scripts/test_legacy_isolation.py
  - scripts/test_vault_site.py
  - scripts/test_content_store.js
  - scripts/test_nr_summary_audit.py
  - scripts/test_note_renderer.js
-->

---
### Requirement: Keep generated artifacts outside the authoring workflow

The deployment artifact SHALL be generated inside Actions or an equivalent reproducible build environment. The repository SHALL not require authors to edit or routinely commit `dist/` content in order to publish vault changes.

#### Scenario: Publish a vault-only change

- **WHEN** an author changes only `vault/concepts/brain-abscess.md` and pushes the commit to `main`
- **THEN** Actions rebuilds and deploys the affected publication package without requiring a manually edited generated JSON file

<!-- @trace
source: vault-native-review-site
updated: 2026-10-10
code:
  - scripts/vault_site/compiler.py
  - scripts/build_static_site.py
  - start-image-manager.cmd
  - js/content-store.js
  - scripts/image_asset_manager.js
  - scripts/rewrite_phase2b_summary.py
  - scripts/audit_vault_native_cutover.py
  - docs/image-asset-manager.md
  - js/vault-app.js
  - js/exam-mode.js
  - scripts/build_phase2b_evidence.py
  - scripts/start_image_asset_manager.ps1
  - scripts/nr_summary_audit.py
  - js/data-loader.js
  - .github/workflows/deploy-pages.yml
  - scripts/validate_vault_site.py
  - index.html
  - scripts/vault_site/__init__.py
  - README.md
  - scripts/image_asset_manager.html
  - css/main.css
  - scripts/build_vault_site.py
  - docs/concept-summary-review-publication.md
  - js/vault-question-view.js
  - scripts/accept_vault_native_migration.py
  - scripts/image_asset_manager.py
  - output/imagegen/adrenoleukodystrophy-background-draft.png
  - js/note-renderer.js
  - scripts/build_concepts.py
tests:
  - scripts/test_build_concepts.py
  - scripts/test_image_asset_manager.js
  - scripts/test_study_progress.js
  - scripts/test_deploy_workflow.py
  - scripts/test_vault_question_view.js
  - scripts/test_image_asset_manager.py
  - scripts/test_legacy_isolation.py
  - scripts/test_vault_site.py
  - scripts/test_content_store.js
  - scripts/test_nr_summary_audit.py
  - scripts/test_note_renderer.js
-->