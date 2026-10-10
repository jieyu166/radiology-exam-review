# answer-analytics Specification

## Purpose

TBD - created by archiving change 'study-scheduler'. Update Purpose after archive.

## Requirements

### Requirement: Wrong-answer criterion is the latest attempt

A question SHALL count as wrong only when its latest attempt is incorrect (`answers[<id>].correct === false`). The "only wrong-answered" filter, the exam builder `wrong` status and the weakness grouping SHALL all use this single criterion; a question answered correctly once after being wrong SHALL leave every wrong list.

#### Scenario: Correct answer clears the wrong list

- **WHEN** `2017-008` was answered wrong yesterday and correctly today
- **THEN** it is absent from the "only wrong-answered" filter and from weakness groups


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
### Requirement: Confidence calibration and hypercorrection list

The statistics route SHALL show, for confidence levels 1, 2 and 3, the number of attempts, correct count and accuracy (null when no attempts), computed from attempts that carry a confidence value; and SHALL list up to 20 most recent attempts with `confidence 3` and `isCorrect false`, each linking to `#/card?qid=<id>`.

#### Scenario: Calibration buckets

- **WHEN** attempts contain confidence 3 on 10 questions with 6 correct and no confidence 1 attempts
- **THEN** the table shows level 3 with n 10, correct 6, accuracy 0.6 and level 1 with n 0 and accuracy null

#### Scenario: Hypercorrection list order

- **WHEN** 25 attempts have confidence 3 and are incorrect
- **THEN** the list shows the 20 newest by `clientTs`, newest first


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
### Requirement: Weakness grouping and interleaved drill

The statistics route SHALL group the user's currently-wrong questions first by subspecialty and then by concept id, keeping groups with at least 2 questions, ordering groups by size descending then label, limiting to 12 groups, and marking as anchor the most recently wrong question in each group. Each group SHALL offer a drill that picks up to 10 questions interleaved across years with a seeded deterministic shuffle (LCG 1664525 / 1013904223, Fisher–Yates), excluding the anchor and deduplicating ids. Concept pages SHALL offer the same interleaved drill over the concept's related questions.

#### Scenario: Grouping

- **WHEN** wrong questions are 3 in MSK (two tagged `foot-ankle-soft-tissue-masses`), 2 in CH and 1 in NR
- **THEN** groups are MSK (3), CH (2), foot-ankle-soft-tissue-masses (2); NR is omitted

#### Scenario: Deterministic interleaving

- **WHEN** `pickInterleaved` is called twice with the same hits, anchor, n and seed
- **THEN** both calls return the same ordered ids, alternating years round-robin

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