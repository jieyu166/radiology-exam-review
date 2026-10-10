# progress-sync Specification

## Purpose

TBD - created by archiving change 'account-progress-sync'. Update Purpose after archive.

## Requirements

### Requirement: Append-only attempt events

Every answered question SHALL produce an attempt event `{clientId, questionId, chosen, isCorrect, source, elapsedMs, confidence, sourceSha256, clientTs}` where `clientId` is a UUID generated on the client, `chosen` is one of A–E or null, `source` is `card`, `exam`, `review` or `legacy`, `elapsedMs` is null or an integer clamped to 0–1,800,000, and `confidence` is null or 1–3. The server SHALL store events in `attempts` with `UNIQUE(user_id, client_id)` and insert with `INSERT OR IGNORE`, so re-sending an event is a no-op. Events MUST NOT be updated or deleted by any API.

#### Scenario: Idempotent upload

- **WHEN** a batch of 3 attempts is posted twice
- **THEN** the first response is `{accepted: 3, ignored: 0}` and the second is `{accepted: 0, ignored: 3}`, and the table holds exactly 3 rows

#### Scenario: Review attempts are accepted

- **WHEN** an attempt with `source: "review"` is posted
- **THEN** it is stored like any other attempt

#### Scenario: Reject an invalid item without dropping the batch silently

- **WHEN** one item in a batch has `chosen: "F"`
- **THEN** the API responds 400 with `errors: [{index, reason}]` and inserts nothing from that batch


<!-- @trace
source: study-scheduler
updated: 2026-10-10
code:
  - scripts/start_image_asset_manager.ps1
  - scripts/image_asset_manager.js
  - scripts/image_asset_manager.py
  - docs/concept-summary-review-publication.md
  - scripts/image_asset_manager.html
  - docs/image-asset-manager.md
  - output/imagegen/adrenoleukodystrophy-background-draft.png
  - start-image-manager.cmd
tests:
  - scripts/test_image_asset_manager.js
  - scripts/test_image_asset_manager.py
-->

---
### Requirement: Offline outbox with ordered idempotent flush

The client SHALL enqueue every attempt, bookmark change and exam result into a localStorage outbox before attempting any network call, keeping at most 300 attempt items (oldest dropped) and at most one item per `clientId`. Flush SHALL send items sequentially in queue order in batches of at most 40, stop at the first failed batch, and remove only accepted or ignored items. Flush SHALL be triggered on app start, on `online`, on `visibilitychange` to visible, and on `pagehide` when the outbox is non-empty, and SHALL be skipped entirely while no session exists.

#### Scenario: Answer while offline

- **WHEN** a logged-in user answers two questions with no network
- **THEN** both attempts are visible in local progress immediately, the outbox holds 2 items, and the settings panel shows "待同步 2 筆"

#### Scenario: Flush after reconnect

- **WHEN** the browser fires `online` and the server accepts the batch
- **THEN** the outbox becomes empty and `sync.lastSyncAt` is updated

#### Scenario: Partial failure keeps order

- **WHEN** the first batch succeeds and the second batch fails with a network error
- **THEN** the first batch's items are removed, the second batch's items remain in their original order, and no later batch is attempted in that flush


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
### Requirement: Snapshot download and merge

`GET /sync/snapshot?sinceAttemptId=<n>&sinceReviewLogId=<m>` SHALL return all of the caller's attempts with server id greater than `n`, all review logs with id greater than `m`, all bookmarks, all cards, all exam results, the caller's scheduler settings, `latestAttemptId` and `latestReviewLogId`. The client SHALL merge a snapshot by `clientId` (attempts, review logs, exams), by newest `updatedAt` (bookmarks, cards, settings), recompute `answers[<id>]` from the latest attempt per question, and store both cursors.

#### Scenario: Second device sees the first device's answers

- **WHEN** device A uploads attempts for `2020-100` (wrong) and `2019-521` (correct) and device B logs in and pulls a snapshot
- **THEN** device B's `answers["2020-100"].correct` is `false`, `answers["2019-521"].correct` is `true`, and no duplicate attempts exist locally after a second pull

#### Scenario: Cards and logs arrive with the snapshot

- **WHEN** device A rated three questions and device B pulls a snapshot
- **THEN** device B holds those three cards and three review logs, and a second pull with the returned `sinceReviewLogId` returns zero review logs


<!-- @trace
source: study-scheduler
updated: 2026-10-10
code:
  - scripts/start_image_asset_manager.ps1
  - scripts/image_asset_manager.js
  - scripts/image_asset_manager.py
  - docs/concept-summary-review-publication.md
  - scripts/image_asset_manager.html
  - docs/image-asset-manager.md
  - output/imagegen/adrenoleukodystrophy-background-draft.png
  - start-image-manager.cmd
tests:
  - scripts/test_image_asset_manager.js
  - scripts/test_image_asset_manager.py
-->

---
### Requirement: One-time migration of schema v2 progress

On the first login of a device whose local progress contains v2 `answers` or `examHistory`, the client SHALL convert each `answers[<id>]` into a `legacy` attempt with `clientId = "legacy:<id>:<ts>"` and each exam record into an exam result with `clientId = "legacy-exam:<ts>"`, enqueue them, and mark the progress as migrated. The conversion MUST be deterministic so that repeating it produces identical `clientId` values.

#### Scenario: Migrate once

- **WHEN** a device with 120 v2 answers logs in, syncs, reloads and logs in again
- **THEN** the server holds exactly 120 legacy attempts for that user


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
### Requirement: Bookmarks and exam results sync last-write-wins

Bookmarks SHALL sync as `{questionId, starred, updatedAt}` and the server SHALL keep the row with the newest `updatedAt`. Exam results SHALL sync as append-only records keyed by `clientId` with `total, correct, wrong, skipped, pct, wrongIds, sourceSha256ByQuestion, clientTs`.

#### Scenario: Newer bookmark wins

- **WHEN** device A unstars `2017-008` at t=100 and device B stars it at t=200 and both sync
- **THEN** the server and both devices end with `2017-008` starred

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