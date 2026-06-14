## ADDED Requirements

### Requirement: Generate SR question cards from question JSON

The system SHALL convert each question in `data/{year}.json` into one Obsidian
Spaced-Repetition card file at `vault/questions/{year}/{id}.md`. The file SHALL contain,
in order: a YAML frontmatter block with `id`, `year`, `subspecialty`, `correctAnswer`,
`concepts`, and `checked`; a tag line `#交換 #{year}交換 #{subspecialty}`; the question
stem and options; a line containing exactly `??`; the answer line `**Ans: {correctAnswer}**`;
the explanation; and a concept link line listing each concept as `[[{concept-id}]]`.
The question stem and options SHALL appear before the `??` separator and the answer and
explanation SHALL appear after it.

#### Scenario: Convert a question with an explanation

- **WHEN** the converter processes a question whose `explanation` is non-empty
- **THEN** a card file is written with the stem and options before `??`, and `**Ans: D**`
  plus the explanation after `??`

#### Scenario: Question links concepts in body for backlinks

- **WHEN** a question has one or more entries in its `concepts` list
- **THEN** the card body contains a `[[{concept-id}]]` wikilink for each concept so the
  concept note aggregates it via backlinks

##### Example: 2016-001 field mapping

| JSON field | Card output |
| ---------- | ----------- |
| id 2016-001 | frontmatter id 2016-001 and filename vault/questions/2016/2016-001.md |
| subspecialty NR | tag line includes #NR and frontmatter subspecialty NR |
| correctAnswer D | after the separator, line Ans D in bold |
| concepts upj-obstruction | frontmatter concepts list and body wikilink to upj-obstruction |

### Requirement: Mark questions with insufficient explanations

The system SHALL detect questions whose explanation is insufficient and SHALL emit a
visible placeholder instead of an empty back side. A question SHALL be treated as
insufficient when its `explanation` is empty or does not explain options per-option
(as determined by the existing audit check in `scripts/audit_questions.py`).

#### Scenario: Question with empty explanation

- **WHEN** the converter processes a question whose `explanation` is empty
- **THEN** the card back side contains the bold answer line followed by a
  `> [!todo] 待補詳解` callout placeholder

#### Scenario: Question with sufficient per-option explanation

- **WHEN** the converter processes a question whose explanation passes the audit
  per-option check
- **THEN** no placeholder callout is added and the explanation is written verbatim

### Requirement: Generate concept notes that aggregate their questions

The system SHALL write one concept note at `vault/concepts/{concept-id}.md` for each
concept referenced by any converted question. The note SHALL contain frontmatter with
`concept`, `name`, and `subspecialty`; a heading; the concept description sourced from
`data/concepts.json` when available; and a Dataview query block that lists questions whose
`concepts` field contains the concept id.

#### Scenario: Referenced concept produces a note

- **WHEN** at least one converted question references concept id `upj-obstruction`
- **THEN** `vault/concepts/upj-obstruction.md` is written with a Dataview list block
  filtering questions whose `concepts` contains `upj-obstruction`

#### Scenario: Concept missing from concepts.json

- **WHEN** a referenced concept id has no entry in `data/concepts.json`
- **THEN** the concept note is still created with the id-derived name and an empty
  description section for later completion

### Requirement: Idempotent regeneration preserving SR scheduling

The system SHALL NOT overwrite an existing card or concept file by default, so that user
edits and Spaced-Repetition scheduling are preserved. When run with an explicit force
option, the system SHALL overwrite the target file but SHALL preserve every existing
`<!--SR:` scheduling comment line from the prior file content.

#### Scenario: Existing file preserved by default

- **WHEN** the converter runs and `vault/questions/2016/2016-001.md` already exists and no
  force option is given
- **THEN** the existing file is left unchanged and is reported as skipped

#### Scenario: Force overwrite keeps SR comments

- **WHEN** the converter runs with the force option and the existing card contains a line
  beginning with `<!--SR:`
- **THEN** the regenerated card retains that scheduling comment line

### Requirement: Write SR plugin configuration

The system SHALL create a minimal `vault/.obsidian/` configuration that sets the Spaced
Repetition plugin flashcard tag to `#交換`. The system SHALL NOT attempt to install any
Obsidian community plugin.

#### Scenario: Flashcard tag configured

- **WHEN** the vault is generated
- **THEN** the Spaced Repetition plugin data file under `vault/.obsidian/` declares `#交換`
  as a flashcard tag
