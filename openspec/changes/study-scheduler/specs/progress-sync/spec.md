## MODIFIED Requirements

### Requirement: Snapshot download and merge

`GET /sync/snapshot?sinceAttemptId=<n>&sinceReviewLogId=<m>` SHALL return all of the caller's attempts with server id greater than `n`, all review logs with id greater than `m`, all bookmarks, all cards, all exam results, the caller's scheduler settings, `latestAttemptId` and `latestReviewLogId`. The client SHALL merge a snapshot by `clientId` (attempts, review logs, exams), by newest `updatedAt` (bookmarks, cards, settings), recompute `answers[<id>]` from the latest attempt per question, and store both cursors.

#### Scenario: Second device sees the first device's answers

- **WHEN** device A uploads attempts for `2020-100` (wrong) and `2019-521` (correct) and device B logs in and pulls a snapshot
- **THEN** device B's `answers["2020-100"].correct` is `false`, `answers["2019-521"].correct` is `true`, and no duplicate attempts exist locally after a second pull

#### Scenario: Cards and logs arrive with the snapshot

- **WHEN** device A rated three questions and device B pulls a snapshot
- **THEN** device B holds those three cards and three review logs, and a second pull with the returned `sinceReviewLogId` returns zero review logs

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
