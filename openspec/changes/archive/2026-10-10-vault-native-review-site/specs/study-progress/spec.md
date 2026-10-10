## ADDED Requirements

### Requirement: Answer history records the source revision

The system SHALL store `sourceSha256` with every answer entry and every completed exam history record that contains published question results. A current question record SHALL remain the source of displayed content even when an older progress entry has a different source hash.

#### Scenario: Preserve an old attempt after a question revision

- **WHEN** an answer history entry for `2021-001` has source hash `old-hash` and the published question record has source hash `new-hash`
- **THEN** the current question renders from `new-hash` source content while the old attempt remains identifiable as an attempt against `old-hash`

### Requirement: Study progress does not override published content

The system SHALL use `rex_progress` only for study state. The system SHALL not use `rex_edits_*` to override titles, question text, options, answers, explanations, concept fields, or any published raw Markdown. The system SHALL provide an explicit export of detected `rex_edits_*` entries before removing legacy content-edit controls.

#### Scenario: Export legacy patches without applying them

- **WHEN** browser storage contains one or more `rex_edits_*` entries during migration
- **THEN** the user can export the entries and the displayed published content remains unchanged by those entries
