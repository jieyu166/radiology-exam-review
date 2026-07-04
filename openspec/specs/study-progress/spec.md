# study-progress Specification

## Purpose

TBD - created by archiving change 'user-study-records'. Update Purpose after archive.

## Requirements

### Requirement: Local study-progress store

The system SHALL persist per-user study progress in a single localStorage entry `rex_progress`, holding four categories keyed by question id: `seen`, `starred`, `answers`, and `examHistory`. Reads MUST tolerate a missing or malformed entry by returning an empty progress object without throwing.

#### Scenario: First read with no stored progress

- **WHEN** the application reads study progress and no `rex_progress` entry exists
- **THEN** an empty progress object with `seen`, `starred`, `answers`, and `examHistory` defaults is returned and no error is thrown

#### Scenario: Malformed stored progress

- **WHEN** the `rex_progress` entry contains invalid JSON
- **THEN** an empty progress object is returned and a warning is logged, without throwing


<!-- @trace
source: user-study-records
updated: 2026-07-04
code:
  - index.html
  - js/data-loader.js
  - vault/concepts/pyloric-stenosis.md
  - vault/questions/2016/2016-105.md
  - js/question-store.js
  - js/concept-cards.js
  - .agents/skills/spectra-analyze/SKILL.md
  - js/card-mode.js
  - js/app.js
  - vault/questions/2016/2016-256.md
  - js/exam-mode.js
  - .agents/skills/spectra-verify/SKILL.md
  - vault/concepts/hepatic-hemangioma.md
  - css/main.css
  - js/editor.js
-->

---
### Requirement: Mark question as seen

The system SHALL record a question as seen when its card is rendered, storing a timestamp under `seen[<id>]`.

#### Scenario: Viewing a card marks it seen

- **WHEN** a question card for id `2017-008` is rendered
- **THEN** `seen["2017-008"]` is set to the current timestamp and persists across reloads


<!-- @trace
source: user-study-records
updated: 2026-07-04
code:
  - index.html
  - js/data-loader.js
  - vault/concepts/pyloric-stenosis.md
  - vault/questions/2016/2016-105.md
  - js/question-store.js
  - js/concept-cards.js
  - .agents/skills/spectra-analyze/SKILL.md
  - js/card-mode.js
  - js/app.js
  - vault/questions/2016/2016-256.md
  - js/exam-mode.js
  - .agents/skills/spectra-verify/SKILL.md
  - vault/concepts/hepatic-hemangioma.md
  - css/main.css
  - js/editor.js
-->

---
### Requirement: Bookmark a question

The system SHALL let the user toggle a bookmark (starred) on a question, persisting `starred[<id>]`, and MUST reflect the current state in the card.

#### Scenario: Toggle bookmark on

- **WHEN** the user activates the bookmark control on question `2017-008` that is not starred
- **THEN** `starred["2017-008"]` becomes `true`, the control shows the active state, and the state persists across reloads

#### Scenario: Toggle bookmark off

- **WHEN** the user activates the bookmark control on question `2017-008` that is already starred
- **THEN** the bookmark for `2017-008` is removed and the control shows the inactive state


<!-- @trace
source: user-study-records
updated: 2026-07-04
code:
  - index.html
  - js/data-loader.js
  - vault/concepts/pyloric-stenosis.md
  - vault/questions/2016/2016-105.md
  - js/question-store.js
  - js/concept-cards.js
  - .agents/skills/spectra-analyze/SKILL.md
  - js/card-mode.js
  - js/app.js
  - vault/questions/2016/2016-256.md
  - js/exam-mode.js
  - .agents/skills/spectra-verify/SKILL.md
  - vault/concepts/hepatic-hemangioma.md
  - css/main.css
  - js/editor.js
-->

---
### Requirement: Record answers and exam history

The system SHALL record each answered question's latest choice and correctness under `answers[<id>]` during exam scoring, and SHALL prepend one summary record to `examHistory` per completed exam.

#### Scenario: Completing an exam records results

- **WHEN** the user finishes a mock exam containing question `2017-008` answered incorrectly
- **THEN** `answers["2017-008"].correct` is `false` and one record is prepended to `examHistory` with total, correct, wrong, skipped, pct, and wrongIds


<!-- @trace
source: user-study-records
updated: 2026-07-04
code:
  - index.html
  - js/data-loader.js
  - vault/concepts/pyloric-stenosis.md
  - vault/questions/2016/2016-105.md
  - js/question-store.js
  - js/concept-cards.js
  - .agents/skills/spectra-analyze/SKILL.md
  - js/card-mode.js
  - js/app.js
  - vault/questions/2016/2016-256.md
  - js/exam-mode.js
  - .agents/skills/spectra-verify/SKILL.md
  - vault/concepts/hepatic-hemangioma.md
  - css/main.css
  - js/editor.js
-->

---
### Requirement: Filter questions by progress state

The system SHALL support filtering the card and list views to only bookmarked questions and to only previously wrong-answered questions, combinable with existing year, subspecialty, and checked filters.

#### Scenario: Only starred

- **WHEN** the "only bookmarked" filter is enabled
- **THEN** the visible set contains exactly the questions whose id is starred

#### Scenario: Only wrong-answered

- **WHEN** the "only wrong-answered" filter is enabled
- **THEN** the visible set contains exactly the questions whose `answers[<id>].correct` is `false`


<!-- @trace
source: user-study-records
updated: 2026-07-04
code:
  - index.html
  - js/data-loader.js
  - vault/concepts/pyloric-stenosis.md
  - vault/questions/2016/2016-105.md
  - js/question-store.js
  - js/concept-cards.js
  - .agents/skills/spectra-analyze/SKILL.md
  - js/card-mode.js
  - js/app.js
  - vault/questions/2016/2016-256.md
  - js/exam-mode.js
  - .agents/skills/spectra-verify/SKILL.md
  - vault/concepts/hepatic-hemangioma.md
  - css/main.css
  - js/editor.js
-->

---
### Requirement: Surface progress in the interface

The system SHALL indicate seen, starred, and wrong-answered state on the question card, and SHALL display a recent-scores list on the exam setup view derived from `examHistory`.

#### Scenario: Card shows progress badges

- **WHEN** a card is shown for a question that is seen, starred, and previously answered incorrectly
- **THEN** the card header displays seen, bookmarked, and wrong-answered indicators

#### Scenario: Recent scores listed

- **WHEN** the exam setup view is opened and `examHistory` has at least one record
- **THEN** a recent-scores list shows each record's date, percentage, and correct/wrong counts, newest first

<!-- @trace
source: user-study-records
updated: 2026-07-04
code:
  - index.html
  - js/data-loader.js
  - vault/concepts/pyloric-stenosis.md
  - vault/questions/2016/2016-105.md
  - js/question-store.js
  - js/concept-cards.js
  - .agents/skills/spectra-analyze/SKILL.md
  - js/card-mode.js
  - js/app.js
  - vault/questions/2016/2016-256.md
  - js/exam-mode.js
  - .agents/skills/spectra-verify/SKILL.md
  - vault/concepts/hepatic-hemangioma.md
  - css/main.css
  - js/editor.js
-->