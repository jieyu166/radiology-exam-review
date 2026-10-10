# spaced-repetition-scheduling Specification

## Purpose

TBD - created by archiving change 'study-scheduler'. Update Purpose after archive.

## Requirements

### Requirement: FSRS card per question with four-grade rating

The client SHALL keep at most one FSRS card per question in `rex_progress.cards[<questionId>]` with fields `dueAt, stability, difficulty, elapsedDays, scheduledDays, learningSteps, reps, lapses, state, lastReviewAt, updatedAt` (epoch milliseconds and numbers). Rating a question with `again`, `hard`, `good` or `easy` SHALL apply ts-fsrs 5.4.2 `next()` with parameters `request_retention 0.9`, `maximum_interval 36500`, `enable_fuzz false`, `enable_short_term true`, `learning_steps ['1m','10m']`, `relearning_steps ['10m']`, replace the card, append a review log `{clientId, questionId, rating, state, dueAt, stability, difficulty, elapsedDays, lastElapsedDays, scheduledDays, learningSteps, reviewedAt}` where `state` is the state before rating, and enqueue both for sync. A preview of the four outcomes SHALL be computable without mutating the card. When the global `FSRS` library is unavailable the scheduler SHALL report unavailability instead of throwing.

#### Scenario: First rating of a new question

- **WHEN** a question without a card is rated `good` at time T
- **THEN** a card exists with `reps: 1`, `state` Learning (1), `dueAt` 10 minutes after T, and a review log with `state: 0` and `rating: "good"`

#### Scenario: Preview matches rating

- **WHEN** the preview for a card reports `good.dueAt = D`
- **THEN** rating that card `good` at the same instant yields a card whose `dueAt` equals `D`

#### Scenario: Library missing

- **WHEN** `window.FSRS` is undefined
- **THEN** `RexScheduler.fsrs.available()` is false and the review route shows the degraded message while other routes work


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
### Requirement: Day window at 04:00 Taiwan time

The scheduler SHALL compute the study day using a fixed UTC+8 offset and a configurable day-start hour (default 4, clamped to 0–23, invalid values fall back to 4). A question with no card or a New card SHALL be due today; a Learning or Relearning card SHALL be due only when `dueAt <= now`; a Review card SHALL be due when `dueAt <= dayEnd`.

#### Scenario: Review card due later today

- **WHEN** now is 2026-10-10 09:00 Taipei and a Review card has `dueAt` 2026-10-10 22:00 Taipei
- **THEN** it is due today

#### Scenario: Learning step not yet reached

- **WHEN** a Learning card has `dueAt` five minutes in the future
- **THEN** it is not served yet

##### Example: Day keys around the boundary

| now (Taipei) | dayStartHour | dayKey |
| --- | --- | --- |
| 2026-10-10 03:59 | 4 | 2026-10-09 |
| 2026-10-10 04:00 | 4 | 2026-10-10 |
| 2026-10-10 00:30 | 0 | 2026-10-10 |


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
### Requirement: Queue mixing and daily new-card limit

The review queue SHALL serve a learning card whenever one is due; otherwise, when due review cards remain, it SHALL serve a new card on every fourth served item (`(served + 1) % 4 === 0`) provided new cards are available and the daily remaining allowance is positive, and a due card otherwise; when no due review cards remain it SHALL serve new cards while allowance remains, else nothing. The daily allowance SHALL be `max(0, newPerDay − introducedToday)` where `newPerDay` defaults to 20 and is clamped to 0–200 and `introducedToday` counts questions whose first review log of the current day window has `state: 0`.

#### Scenario: Interleave new cards

- **WHEN** learning is 0, dueReview is 10, newAvailable is 50, newRemaining is 20
- **THEN** the kinds served for served = 0..7 are `due, due, due, new, due, due, due, new`

#### Scenario: Learning always first

- **WHEN** learning is 1 regardless of other counts
- **THEN** the next kind is `learning`

##### Example: New limit parsing

| raw | newPerDay |
| --- | --- |
| `undefined` | 20 |
| `"35"` | 35 |
| `"999"` | 200 |
| `"-3"` | 20 |


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
### Requirement: Cards and review logs sync across devices

Cards SHALL sync last-write-wins by `updatedAt` through `POST /sync/cards` and review logs SHALL sync append-only by `clientId` through `POST /sync/review-logs`; `GET /sync/snapshot` SHALL return all cards, review logs with id greater than `sinceReviewLogId`, `latestReviewLogId` and the user's scheduler settings. Scheduler settings (`newPerDay`, `dayStartHour`, `examSecondsPerQuestion`) SHALL sync last-write-wins.

#### Scenario: Second device continues the schedule

- **WHEN** device A rates five questions and syncs, and device B logs in and pulls a snapshot
- **THEN** device B holds the same five cards and its review queue counts equal device A's

#### Scenario: Conflicting offline ratings

- **WHEN** devices A and B rate the same question offline at `updatedAt` 100 and 200 and both sync
- **THEN** the server card is B's and both review logs are stored

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