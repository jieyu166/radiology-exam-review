## MODIFIED Requirements

### Requirement: Local study-progress store

The system SHALL persist per-user study progress in a single localStorage entry `rex_progress` with `schemaVersion: 3`, holding `seen`, `starred`, `answers`, `examHistory`, an append-only `attempts` list (at most 5,000 newest items), an `outbox` with `attempts`, `bookmarks` and `exams` queues, and a `sync` object `{latestAttemptId, lastSyncAt, migratedLegacy}`. `answers[<id>]` SHALL be derived from the newest attempt for that question whenever progress is read. Reads MUST tolerate a missing or malformed entry by returning an empty progress object without throwing, and MUST upgrade a schema v2 entry in place by converting its `answers` and `examHistory` into deterministic `legacy` attempts and exam results.

#### Scenario: First read with no stored progress

- **WHEN** the application reads study progress and no `rex_progress` entry exists
- **THEN** an empty v3 progress object is returned and no error is thrown

#### Scenario: Malformed stored progress

- **WHEN** the `rex_progress` entry contains invalid JSON
- **THEN** an empty progress object is returned and a warning is logged, without throwing

#### Scenario: Upgrade a v2 entry

- **WHEN** the stored entry has `schemaVersion: 2` with `answers["2017-008"] = {last: "C", correct: false, ts: 1700000000000}`
- **THEN** the returned progress has `schemaVersion: 3`, an attempt with `clientId: "legacy:2017-008:1700000000000"`, `source: "legacy"`, `chosen: "C"`, and `answers["2017-008"].correct` still `false`

### Requirement: Record answers and exam history

The system SHALL record each answered question as an attempt event (card or exam source, with elapsed time, optional confidence and source hash), derive `answers[<id>]` from the newest attempt, enqueue the attempt in the outbox, and SHALL prepend one summary record to `examHistory` per completed exam while also enqueuing it as an exam result.

#### Scenario: Completing an exam records results

- **WHEN** the user finishes a mock exam containing question `2017-008` answered incorrectly
- **THEN** an attempt with `source: "exam"` exists for `2017-008`, `answers["2017-008"].correct` is `false`, and one record is prepended to `examHistory` with total, correct, wrong, skipped, pct, and wrongIds

#### Scenario: Card answer with timing and confidence

- **WHEN** the user picks confidence `3`, answers `2020-100` after 42 seconds in card mode and reveals
- **THEN** the newest attempt for `2020-100` has `source: "card"`, `confidence: 3`, `elapsedMs` of about 42000, and the outbox contains it
