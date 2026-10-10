# study-progress Specification

## Purpose

TBD - created by archiving change 'user-study-records'. Update Purpose after archive.

## Requirements

### Requirement: Local study-progress store

The system SHALL persist per-user study progress in a single localStorage entry `rex_progress`, holding four categories keyed by question id: `seen`, `starred`, `answers`, and `examHistory`. Reads MUST tolerate a missing or malformed entry by returning an empty progress object without throwing.

#### Scenario: First read with no stored progress

- **WHEN** the application reads study progress and no `rex_progress` entry exists
- **THEN** an empty progress object with `seen`, `starred`, `answers`, and `examHistory` defaults is returned and no error is thrown

#### Scenario: Malformed stored progress

- **WHEN** the `rex_progress` entry contains invalid JSON
- **THEN** an empty progress object is returned and a warning is logged, without throwing


<!-- @trace
source: user-study-records
updated: 2026-07-04
code:
  - index.html
  - js/data-loader.js
  - js/question-store.js
  - js/concept-cards.js
  - js/card-mode.js
  - js/app.js
  - js/exam-mode.js
  - css/main.css
  - js/editor.js
-->

---
### Requirement: Mark question as seen

The system SHALL record a question as seen when its card is rendered, storing a timestamp under `seen[<id>]`.

#### Scenario: Viewing a card marks it seen

- **WHEN** a question card for id `2017-008` is rendered
- **THEN** `seen["2017-008"]` is set to the current timestamp and persists across reloads


<!-- @trace
source: user-study-records
updated: 2026-07-04
code:
  - index.html
  - js/data-loader.js
  - js/question-store.js
  - js/concept-cards.js
  - js/card-mode.js
  - js/app.js
  - js/exam-mode.js
  - css/main.css
  - js/editor.js
-->

---
### Requirement: Bookmark a question

The system SHALL let the user toggle a bookmark (starred) on a question, persisting `starred[<id>]`, and MUST reflect the current state in the card.

#### Scenario: Toggle bookmark on

- **WHEN** the user activates the bookmark control on question `2017-008` that is not starred
- **THEN** `starred["2017-008"]` becomes `true`, the control shows the active state, and the state persists across reloads

#### Scenario: Toggle bookmark off

- **WHEN** the user activates the bookmark control on question `2017-008` that is already starred
- **THEN** the bookmark for `2017-008` is removed and the control shows the inactive state


<!-- @trace
source: user-study-records
updated: 2026-07-04
code:
  - index.html
  - js/data-loader.js
  - js/question-store.js
  - js/concept-cards.js
  - js/card-mode.js
  - js/app.js
  - js/exam-mode.js
  - css/main.css
  - js/editor.js
-->

---
### Requirement: Record answers and exam history

The system SHALL record each answered question's latest choice and correctness under `answers[<id>]` during exam scoring, and SHALL prepend one summary record to `examHistory` per completed exam.

#### Scenario: Completing an exam records results

- **WHEN** the user finishes a mock exam containing question `2017-008` answered incorrectly
- **THEN** `answers["2017-008"].correct` is `false` and one record is prepended to `examHistory` with total, correct, wrong, skipped, pct, and wrongIds


<!-- @trace
source: user-study-records
updated: 2026-07-04
code:
  - index.html
  - js/data-loader.js
  - js/question-store.js
  - js/concept-cards.js
  - js/card-mode.js
  - js/app.js
  - js/exam-mode.js
  - css/main.css
  - js/editor.js
-->

---
### Requirement: Filter questions by progress state

The system SHALL support filtering the card and list views to only bookmarked questions and to only previously wrong-answered questions, combinable with existing year, subspecialty, and checked filters.

#### Scenario: Only starred

- **WHEN** the "only bookmarked" filter is enabled
- **THEN** the visible set contains exactly the questions whose id is starred

#### Scenario: Only wrong-answered

- **WHEN** the "only wrong-answered" filter is enabled
- **THEN** the visible set contains exactly the questions whose `answers[<id>].correct` is `false`


<!-- @trace
source: user-study-records
updated: 2026-07-04
code:
  - index.html
  - js/data-loader.js
  - js/question-store.js
  - js/concept-cards.js
  - js/card-mode.js
  - js/app.js
  - js/exam-mode.js
  - css/main.css
  - js/editor.js
-->

---
### Requirement: Surface progress in the interface

The system SHALL indicate seen, starred, and wrong-answered state on the question card, and SHALL display a recent-scores list on the exam setup view derived from `examHistory`.

#### Scenario: Card shows progress badges

- **WHEN** a card is shown for a question that is seen, starred, and previously answered incorrectly
- **THEN** the card header displays seen, bookmarked, and wrong-answered indicators

#### Scenario: Recent scores listed

- **WHEN** the exam setup view is opened and `examHistory` has at least one record
- **THEN** a recent-scores list shows each record's date, percentage, and correct/wrong counts, newest first

<!-- @trace
source: user-study-records
updated: 2026-07-04
code:
  - index.html
  - js/data-loader.js
  - js/question-store.js
  - js/concept-cards.js
  - js/card-mode.js
  - js/app.js
  - js/exam-mode.js
  - css/main.css
  - js/editor.js
-->

---
### Requirement: Answer history records the source revision

The system SHALL store `sourceSha256` with every answer entry and every completed exam history record that contains published question results. A current question record SHALL remain the source of displayed content even when an older progress entry has a different source hash.

#### Scenario: Preserve an old attempt after a question revision

- **WHEN** an answer history entry for `2021-001` has source hash `old-hash` and the published question record has source hash `new-hash`
- **THEN** the current question renders from `new-hash` source content while the old attempt remains identifiable as an attempt against `old-hash`


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
### Requirement: Study progress does not override published content

The system SHALL use `rex_progress` only for study state. The system SHALL not use `rex_edits_*` to override titles, question text, options, answers, explanations, concept fields, or any published raw Markdown. The system SHALL provide an explicit export of detected `rex_edits_*` entries before removing legacy content-edit controls.

#### Scenario: Export legacy patches without applying them

- **WHEN** browser storage contains one or more `rex_edits_*` entries during migration
- **THEN** the user can export the entries and the displayed published content remains unchanged by those entries

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