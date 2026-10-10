## MODIFIED Requirements

### Requirement: Local study-progress store

The system SHALL persist per-user study progress in a single localStorage entry `rex_progress` with `schemaVersion: 3`, holding `seen`, `starred`, `answers`, `examHistory`, an append-only `attempts` list (at most 5,000 newest items), `cards` keyed by question id, an append-only `reviewLogs` list (at most 5,000 newest items), `settings` (`newPerDay` default 20, `dayStartHour` default 4, `examSecondsPerQuestion` default 90), `activeExam` or null, an `outbox` with `attempts`, `bookmarks`, `exams`, `cards` and `reviewLogs` queues, and a `sync` object `{latestAttemptId, latestReviewLogId, lastSyncAt, migratedLegacy}`. `answers[<id>]` SHALL be derived from the newest attempt for that question whenever progress is read. Reads MUST tolerate a missing or malformed entry by returning an empty progress object without throwing, MUST fill missing `cards`, `reviewLogs`, `settings` and queues with empty defaults for v3 entries written before this change, and MUST upgrade a schema v2 entry in place by converting its `answers` and `examHistory` into deterministic `legacy` attempts and exam results.

#### Scenario: First read with no stored progress

- **WHEN** the application reads study progress and no `rex_progress` entry exists
- **THEN** an empty v3 progress object with empty `cards`, `reviewLogs`, default `settings` and empty queues is returned and no error is thrown

#### Scenario: Older v3 entry without scheduler fields

- **WHEN** the stored v3 entry has no `cards` key
- **THEN** reading returns `cards: {}`, `reviewLogs: []`, default `settings`, and existing attempts are untouched

#### Scenario: Upgrade a v2 entry

- **WHEN** the stored entry has `schemaVersion: 2` with `answers["2017-008"] = {last: "C", correct: false, ts: 1700000000000}`
- **THEN** the returned progress has `schemaVersion: 3`, an attempt with `clientId: "legacy:2017-008:1700000000000"`, `source: "legacy"`, `chosen: "C"`, and `answers["2017-008"].correct` still `false`
