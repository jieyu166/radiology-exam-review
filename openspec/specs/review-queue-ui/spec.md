# review-queue-ui Specification

## Purpose

TBD - created by archiving change 'study-scheduler'. Update Purpose after archive.

## Requirements

### Requirement: Today's review route

The website SHALL provide a `#/review` route reachable from the top and bottom navigation, showing counts of learning, due and new cards (with remaining allowance and the number available under the current year/subspecialty filter), the current question rendered by the question view in card mode, and after reveal four rating buttons `again / hard / good / easy` each labelled with its previewed next interval. Rating SHALL record the card, the review log and a `review` attempt, then show the next question. Keys 1–4 SHALL trigger the four buttons and space SHALL reveal. When the queue is empty the route SHALL show a completion message with tomorrow's due count.

#### Scenario: Rate and advance

- **WHEN** the user reveals a question and presses `3`
- **THEN** the card is rated `good`, a `review` attempt and a review log are enqueued, and the next queue item is shown

#### Scenario: Empty queue

- **WHEN** no learning, due or allowed new cards remain
- **THEN** the route shows `今日完成` and the count of cards due tomorrow

##### Example: Interval labels

| scheduledDays / minutes | Label |
| --- | --- |
| less than 1 minute | `<1 分` |
| 10 minutes | `10 分` |
| 3 days | `3 天` |
| 45 days | `1.5 月` |


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
### Requirement: Default rating focus follows correctness

After reveal, the focused rating button SHALL be `good` when the attempt was correct and `again` when it was incorrect, so pressing Enter applies that rating; the user MAY choose any other grade.

#### Scenario: Wrong answer defaults to again

- **WHEN** the user answers incorrectly and reveals
- **THEN** the `again` button has focus and Enter rates `again`

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