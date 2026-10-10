# vault-native-publication Specification

## Purpose

TBD - created by archiving change 'vault-native-review-site'. Update Purpose after archive.

## Requirements

### Requirement: Publish every eligible vault note as raw Markdown

The publication compiler SHALL discover every Markdown file under `vault/questions/` and `vault/concepts/` whose basename does not start with `_` and whose frontmatter does not set `publish: false`. For every eligible source, the compiler SHALL emit one raw Markdown asset below `dist/notes/` at the same vault-relative path, one manifest entry, and one typed record. The raw asset SHA-256 SHALL equal the SHA-256 of the source bytes.

#### Scenario: Publish an eligible concept note

- **WHEN** `vault/concepts/brain-abscess.md` has no `publish: false` frontmatter
- **THEN** the package contains `notes/concepts/brain-abscess.md`, one `concept` record, and one manifest entry with the source path and matching SHA-256

#### Scenario: Exclude an explicit draft

- **WHEN** `vault/concepts/draft-topic.md` has frontmatter `publish: false`
- **THEN** no raw asset, record, manifest entry, search entry, or relation entry is emitted for that note


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
### Requirement: Emit lossless publication records and indexes

The compiler SHALL emit one schema-versioned record per eligible note and schema-versioned manifest, concept index, question index, relation index, search index, and build report. Every record SHALL contain `id`, `kind`, `sourcePath`, `sourceSha256`, `rawPath`, `frontmatter`, `outline`, `links`, `embeds`, and `diagnostics`. Records SHALL NOT define medical-content fields such as `definition`, `imagingFindings`, `keyPoints`, or `management`.

#### Scenario: Preserve an unknown concept section

- **WHEN** an eligible concept contains a level-two heading named `Teaching Pearls` that has no website-specific mapping
- **THEN** the raw Markdown contains that heading and body unchanged, the record outline lists the heading, and no semantic content field is created for it

##### Example: generic outline entry

- **GIVEN** source line 21 is `## Teaching Pearls`
- **WHEN** the compiler emits the concept record
- **THEN** the outline contains an entry with `level` equal to 2, `heading` equal to `Teaching Pearls`, and `startLine` equal to 21


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
### Requirement: Emit minimal question interaction projections

For an eligible question note, the compiler SHALL emit an `sr` projection containing front and back source line ranges, option line ranges, the parsed correct answer, and linked concept ids. The projection SHALL reference the raw Markdown and SHALL NOT become an editable content source.

#### Scenario: Build a question projection

- **WHEN** an eligible question contains one SR front/back boundary, options A through E, `Ans: B`, and `[[brain-abscess]]`
- **THEN** its question record contains the front and back line ranges, five option ranges, correct answer `B`, and concept id `brain-abscess`


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
### Requirement: Publish resolved static assets

The compiler SHALL resolve every supported published Markdown embed to one content-addressed asset path below `dist/assets/` and record the resolved path in the owning record. A supported required embed that is missing or has more than one valid source candidate SHALL be reported as a hard validation error.

#### Scenario: Publish an image embed

- **WHEN** an eligible note embeds `![[brain-abscess.png]]` and exactly one supported source asset resolves
- **THEN** the package contains one content-addressed asset and the note record maps the embed to that asset path


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
### Requirement: Emit explicit answer-state projections

For every eligible question, the `sr` projection SHALL contain `answerStatus`, `answerMode`, `acceptedAnswers`, and `scorable`. `acceptedAnswers` SHALL contain normalized option letters only. A `confirmed` question SHALL have a non-empty accepted set and a scoring mode other than `none`; an `unresolved` or `no_valid_answer` question SHALL have an empty accepted set and `scorable: false`.

#### Scenario: Publish a question where either of two answers is acceptable

- **WHEN** a question declares `answerStatus: confirmed`, `answerMode: any`, and `acceptedAnswers: [B, D]`
- **THEN** its projection preserves both letters, renders single-choice interaction, and scores either `B` or `D` as correct

#### Scenario: Publish an unresolved question without a scored answer

- **WHEN** a question declares `answerStatus: unresolved`, `answerMode: none`, and `acceptedAnswers: []`
- **THEN** its raw note and record are published with `scorable: false`, and the projection does not invent a correct answer

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