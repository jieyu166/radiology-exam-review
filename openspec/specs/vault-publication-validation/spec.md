# vault-publication-validation Specification

## Purpose

TBD - created by archiving change 'vault-native-review-site'. Update Purpose after archive.

## Requirements

### Requirement: Produce a complete publication inventory

The validation command SHALL classify every Markdown file below `vault/questions/` and `vault/concepts/` as published, excluded by `publish: false`, excluded by underscore basename, warning, or hard error. The build report SHALL list the count and source path for each classification. The command SHALL fail when an eligible note lacks a raw asset, record, or manifest entry.

#### Scenario: Detect a missing record

- **WHEN** an eligible note has a manifest entry and raw asset but no record
- **THEN** validation exits nonzero with a hard error identifying the source path and missing record


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
### Requirement: Validate source identity and question contracts

Validation SHALL fail for duplicate published ids, duplicate output paths, paths outside the configured output root, a published question without exactly one SR front/back boundary, a correct answer outside A through E, conflicting parsed answer values, or an ambiguous required asset. Validation SHALL not infer a replacement answer or silently skip an invalid eligible note.

#### Scenario: Reject a conflicting answer

- **WHEN** a published question frontmatter declares `correctAnswer: A` and its SR back declares `Ans: B`
- **THEN** validation exits nonzero with a hard error that identifies the question source path and both values


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
### Requirement: Preserve unknown source content explicitly

Validation SHALL compare every published raw asset hash to its source hash and SHALL confirm that every source heading appears in the emitted outline. Unsupported safe Markdown constructs SHALL produce warnings with source path and line number. The renderer contract fixture suite SHALL include every syntax class observed by the syntax inventory.

#### Scenario: Report an unknown safe construct

- **WHEN** a published note contains a syntax inventory entry that is not in the renderer support list and is not required for question interaction
- **THEN** validation records a warning with source path and line number while retaining the raw source asset


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
### Requirement: Produce deterministic publication output

Two compiler executions with identical vault input and compiler version SHALL produce byte-identical manifest, records, indexes, raw assets, assets, and build report except for an explicitly excluded ephemeral workflow log. Package files SHALL use stable path ordering and SHALL not contain build timestamps.

#### Scenario: Repeat an unchanged build

- **WHEN** the compiler runs twice against unchanged source input
- **THEN** the SHA-256 of every file below the output root is identical between runs


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
### Requirement: Validate explicit review and answer states

Validation SHALL accept `answerStatus` values `confirmed`, `unresolved`, and `no_valid_answer`, `answerMode` values `single`, `any`, `all`, and `none`, and an `acceptedAnswers` list containing only A-E letters. An explicit `unresolved` or `no_valid_answer` state SHALL downgrade a missing or conflicting answer value to a review diagnostic and SHALL emit a non-scorable projection. It SHALL NOT bypass invalid option structure, duplicate identity, path, or required-asset errors. Validation SHALL NOT infer `any` versus `all` from a multi-letter legacy answer.

#### Scenario: Preserve an unresolved answer state

- **WHEN** a published question has `answerStatus: unresolved`, `answerMode: none`, and no valid `Ans:` value
- **THEN** validation emits a non-scorable question projection with a review diagnostic instead of inventing an answer

#### Scenario: Reject an invalid answer-state value

- **WHEN** a published question declares `answerMode: maybe` or an accepted answer outside A-E
- **THEN** validation exits nonzero with a hard error identifying the source path and invalid value

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