## MODIFIED Requirements

### Requirement: Export study progress independently

The system SHALL provide an action that exports only the `rex_progress` data (schema v3, including `attempts`) as a downloadable JSON file named `rex-progress-YYYY-MM-DD.json`. The exported file MUST NOT contain any `rex_edits_*` question-edit data and MUST NOT contain the session token.

#### Scenario: Export produces a progress-only file

- **WHEN** the user activates "export study records"
- **THEN** a file `rex-progress-<date>.json` is downloaded containing the v3 `rex_progress` object with its `attempts`, and no `rex_edits_*` keys or `rex_session` data

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
