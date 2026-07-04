## ADDED Requirements

### Requirement: Export study progress independently

The system SHALL provide an action that exports only the `rex_progress` data as a downloadable JSON file named `rex-progress-YYYY-MM-DD.json`. The exported file MUST NOT contain any `rex_edits_*` question-edit data.

#### Scenario: Export produces a progress-only file

- **WHEN** the user activates "export study records"
- **THEN** a file `rex-progress-<date>.json` is downloaded containing the `rex_progress` object and no `rex_edits_*` keys

### Requirement: Import study progress by merge

The system SHALL provide an action that imports a study-progress JSON file and merges it into local progress: `seen`, `starred`, and `answers` merge by key, and `examHistory` records concatenate and de-duplicate by timestamp. Importing MUST NOT modify any `rex_edits_*` data. Invalid JSON MUST surface an error and leave local data unchanged.

#### Scenario: Merge imported progress

- **WHEN** the user imports a valid `rex-progress-*.json` after having local progress
- **THEN** bookmarks, seen, answers, and exam history from the file are merged into local progress and the current view refreshes

#### Scenario: Import does not touch question edits

- **WHEN** a study-progress file is imported
- **THEN** the count of pending question edits is unchanged

#### Scenario: Invalid import file

- **WHEN** the user selects a file that is not valid JSON
- **THEN** an error notification is shown and local progress is left unchanged

### Requirement: Clear study progress only

The system SHALL provide an action that removes the `rex_progress` entry without affecting any `rex_edits_*` question-edit data.

#### Scenario: Clearing progress preserves edits

- **WHEN** the user activates "clear study records"
- **THEN** `rex_progress` is removed and pending question edits remain intact

### Requirement: Question-edit export stays separate

The existing question-edit export SHALL continue to output only `rex_edits_*` data to `rex-edits-*.json` and MUST NOT include `rex_progress`.

#### Scenario: Edit export excludes progress

- **WHEN** the user activates the question-edit export
- **THEN** the downloaded `rex-edits-*.json` contains only `rex_edits_*` keys and no `rex_progress`
