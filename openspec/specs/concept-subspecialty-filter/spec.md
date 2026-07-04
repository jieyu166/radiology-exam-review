# concept-subspecialty-filter Specification

## Purpose

TBD - created by archiving change 'concept-subspecialty-filter'. Update Purpose after archive.

## Requirements

### Requirement: Subspecialty filter on the concept list

The concept list view SHALL render a row of subspecialty filter controls above the concept grid. The first control SHALL be an "All" control, followed by one control per subspecialty. The controls SHALL be derived by de-duplicating the `subspecialty` values present in the already-loaded `data/concepts-index.json`; the view MUST NOT issue any additional network request to build them. Each subspecialty control SHALL display the count of concepts in that subspecialty. Concepts whose `subspecialty` is empty SHALL be grouped under an "Uncategorized" control.

#### Scenario: Filter controls derived from loaded index

- **WHEN** the concept list view renders with the concept index already loaded
- **THEN** an "All" control plus one control per distinct subspecialty present in the index is shown, each subspecialty control showing its concept count, with no extra network request

#### Scenario: Empty subspecialty grouped as Uncategorized

- **WHEN** one or more concepts have an empty subspecialty value
- **THEN** those concepts are represented by a single "Uncategorized" control


<!-- @trace
source: concept-subspecialty-filter
updated: 2026-07-04
code:
  - js/question-store.js
  - js/editor.js
  - vault/concepts/hepatic-hemangioma.md
  - js/concept-cards.js
  - vault/questions/2016/2016-105.md
  - vault/concepts/pyloric-stenosis.md
  - js/exam-mode.js
  - .agents/skills/spectra-analyze/SKILL.md
  - .agents/skills/spectra-verify/SKILL.md
  - js/card-mode.js
  - vault/questions/2016/2016-256.md
  - js/app.js
  - index.html
  - css/main.css
  - js/data-loader.js
-->

---
### Requirement: Filter control ordering

The subspecialty controls SHALL be ordered with the exam question subspecialties first in their canonical order (ABD, CV, CH, NR, MSK, H&N, PED, IR, Physics, Breast, US), followed by any concept-only subspecialty values, with "Uncategorized" (if present) last.

#### Scenario: Canonical order then extras

- **WHEN** the index contains both canonical subspecialties and concept-only values such as GU and GI
- **THEN** the canonical subspecialties appear first in the fixed order, and the concept-only values appear after them

##### Example: Ordering

| Present in index | Rendered order (after "All") |
| ---------------- | ---------------------------- |
| NR, ABD, GU, GI, Breast, (empty) | ABD, NR, Breast, GU, GI, Uncategorized |


<!-- @trace
source: concept-subspecialty-filter
updated: 2026-07-04
code:
  - js/question-store.js
  - js/editor.js
  - vault/concepts/hepatic-hemangioma.md
  - js/concept-cards.js
  - vault/questions/2016/2016-105.md
  - vault/concepts/pyloric-stenosis.md
  - js/exam-mode.js
  - .agents/skills/spectra-analyze/SKILL.md
  - .agents/skills/spectra-verify/SKILL.md
  - js/card-mode.js
  - vault/questions/2016/2016-256.md
  - js/app.js
  - index.html
  - css/main.css
  - js/data-loader.js
-->

---
### Requirement: Selecting a subspecialty filters the grid

Selecting a subspecialty control SHALL filter the concept grid to that subspecialty using only already-loaded data (no re-fetch), and SHALL mark the selected control as active. Selecting "All" SHALL show every concept. The related-question count on each concept and the "concepts to be created" block SHALL be unaffected by the filter.

#### Scenario: Filter to one subspecialty

- **WHEN** the user selects the "Breast" control
- **THEN** the grid shows exactly the concepts whose subspecialty is Breast, the "Breast" control is marked active, and no network request is made

#### Scenario: Reset with All

- **WHEN** the user selects the "All" control after a subspecialty was selected
- **THEN** the grid shows all concepts again and "All" is marked active

<!-- @trace
source: concept-subspecialty-filter
updated: 2026-07-04
code:
  - js/question-store.js
  - js/editor.js
  - vault/concepts/hepatic-hemangioma.md
  - js/concept-cards.js
  - vault/questions/2016/2016-105.md
  - vault/concepts/pyloric-stenosis.md
  - js/exam-mode.js
  - .agents/skills/spectra-analyze/SKILL.md
  - .agents/skills/spectra-verify/SKILL.md
  - js/card-mode.js
  - vault/questions/2016/2016-256.md
  - js/app.js
  - index.html
  - css/main.css
  - js/data-loader.js
-->