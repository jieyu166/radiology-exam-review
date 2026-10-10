# exam-builder Specification

## Purpose

TBD - created by archiving change 'study-scheduler'. Update Purpose after archive.

## Requirements

### Requirement: Exam pool from status, scope and count filters

The exam setup SHALL accept filters `{status[], years[], subspecialties[], concepts[], count, tutor, timed}` where status values are limited to `unseen`, `wrong`, `correct`, `bookmarked` (unknown values dropped, duplicates removed, order kept), empty lists mean no restriction, `count` is clamped to 1–100 with default 20, `tutor` is true only when strictly `true`, and `timed` is true unless strictly `false`. The pool SHALL contain scorable questions matching any selected status (OR) and every selected scope dimension (AND). The pool size SHALL be shown live as filters change. Sampling SHALL use a seeded Fisher–Yates shuffle whose seed is stored with the exam so the paper can be reproduced.

#### Scenario: OR between statuses, AND across dimensions

- **WHEN** status is `[wrong, bookmarked]`, years is `[2020]`, subspecialties is `[CH]`
- **THEN** the pool is every scorable 2020 CH question that is currently wrong or starred

##### Example: Filter normalization

| raw | normalized |
| --- | --- |
| `{status: ["wrong","wrong","nope"], count: 500}` | `{status: ["wrong"], count: 100, tutor: false, timed: true}` |
| `{count: 0, tutor: "yes", timed: false}` | `{count: 1, tutor: false, timed: false}` |


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
### Requirement: Tutor and timed modes

In tutor mode each answer SHALL be revealed and scored immediately; in timed mode each question SHALL show a countdown (default 90 seconds per question, configurable in settings) and SHALL advance as unanswered when it reaches zero. Both modes SHALL record `exam` attempts and one exam result.

#### Scenario: Timed question expires

- **WHEN** the countdown reaches zero on question 3
- **THEN** question 3 is recorded as unanswered and question 4 is shown


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
### Requirement: Resume an in-progress exam

An in-progress exam (`entryIds, answers, index, startedAt, filters, seed`) SHALL persist in `rex_progress.activeExam`; reloading SHALL resume at the first unanswered question, or at index 0 when every question is answered. Questions whose id no longer exists in the current index SHALL be skipped and noted on the result page.

#### Scenario: Resume after reload

- **WHEN** questions 1–4 are answered, question 5 is not, and the page reloads
- **THEN** the exam resumes at question 5

#### Scenario: All answered

- **WHEN** every question has an answer and the page reloads before submission
- **THEN** the exam resumes at index 0 with a submit control available

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