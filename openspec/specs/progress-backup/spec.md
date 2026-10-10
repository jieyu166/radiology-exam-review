# progress-backup Specification

## Purpose

TBD - created by archiving change 'user-study-records'. Update Purpose after archive.

## Requirements

### Requirement: Export study progress independently

The system SHALL provide an action that exports only the `rex_progress` data (schema v3, including `attempts`) as a downloadable JSON file named `rex-progress-YYYY-MM-DD.json`. The exported file MUST NOT contain any `rex_edits_*` question-edit data and MUST NOT contain the session token.

#### Scenario: Export produces a progress-only file

- **WHEN** the user activates "export study records"
- **THEN** a file `rex-progress-<date>.json` is downloaded containing the v3 `rex_progress` object with its `attempts`, and no `rex_edits_*` keys or `rex_session` data


<!-- @trace
source: account-progress-sync
updated: 2026-10-10
code:
  - output/imagegen/adrenoleukodystrophy-background-draft.png
  - scripts/start_image_asset_manager.ps1
  - start-image-manager.cmd
  - scripts/image_asset_manager.js
  - scripts/image_asset_manager.py
  - scripts/image_asset_manager.html
  - docs/concept-summary-review-publication.md
  - docs/image-asset-manager.md
tests:
  - scripts/test_image_asset_manager.js
  - scripts/test_image_asset_manager.py
-->

---
### Requirement: Import study progress by merge

The system SHALL provide an action that imports a study-progress JSON file (schema v2 or v3) and merges it into local progress: `attempts` and exam results merge by `clientId`, `seen` and `starred` merge by key (newest `updatedAt` wins for bookmarks), `answers` are recomputed from the merged attempts, and v2 files are first converted with the same deterministic legacy conversion used on upgrade. Imported attempts SHALL be enqueued for sync when a session exists. Importing MUST NOT modify any `rex_edits_*` data. Invalid JSON MUST surface an error and leave local data unchanged.

#### Scenario: Merge imported progress

- **WHEN** the user imports a valid `rex-progress-*.json` after having local progress
- **THEN** bookmarks, seen, attempts and exam history from the file are merged into local progress without duplicate `clientId` values and the current view refreshes

#### Scenario: Import a v2 file

- **WHEN** the imported file has `schemaVersion: 2`
- **THEN** its answers become `legacy` attempts and the merge result equals importing the equivalent v3 file

#### Scenario: Invalid import file

- **WHEN** the user selects a file that is not valid JSON
- **THEN** an error notification is shown and local progress is left unchanged


<!-- @trace
source: account-progress-sync
updated: 2026-10-10
code:
  - output/imagegen/adrenoleukodystrophy-background-draft.png
  - scripts/start_image_asset_manager.ps1
  - start-image-manager.cmd
  - scripts/image_asset_manager.js
  - scripts/image_asset_manager.py
  - scripts/image_asset_manager.html
  - docs/concept-summary-review-publication.md
  - docs/image-asset-manager.md
tests:
  - scripts/test_image_asset_manager.js
  - scripts/test_image_asset_manager.py
-->

---
### Requirement: Clear study progress only

The system SHALL provide an action that removes the `rex_progress` entry without affecting any `rex_edits_*` question-edit data.

#### Scenario: Clearing progress preserves edits

- **WHEN** the user activates "clear study records"
- **THEN** `rex_progress` is removed and pending question edits remain intact


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
### Requirement: Question-edit export stays separate

The existing question-edit export SHALL continue to output only `rex_edits_*` data to `rex-edits-*.json` and MUST NOT include `rex_progress`.

#### Scenario: Edit export excludes progress

- **WHEN** the user activates the question-edit export
- **THEN** the downloaded `rex-edits-*.json` contains only `rex_edits_*` keys and no `rex_progress`

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