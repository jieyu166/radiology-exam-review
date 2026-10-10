## ADDED Requirements

### Requirement: Load vault-native publication data lazily

The review website SHALL load manifest and lightweight indexes before loading an individual record or raw Markdown note. A concept route and question route SHALL lazy-load only the selected record and raw note. The website SHALL not require legacy concept detail JSON or legacy year JSON to render a vault-native route.

#### Scenario: Open a concept route

- **WHEN** a user navigates to the published concept `brain-abscess`
- **THEN** the website loads its manifest/index metadata and the selected concept record/raw note without loading every concept raw note

### Requirement: Render raw note content without silent omission

The website SHALL render supported headings, paragraphs, lists, tables, footnotes, callouts, wikilinks, supported image embeds, and math from the published raw Markdown. For an unsupported safe source block, the website SHALL display the original block in an explicit degraded rendering and show a non-content warning. The website SHALL not omit a source block solely because it lacks a website schema mapping.

#### Scenario: Render an unmapped heading

- **WHEN** a concept raw note contains `## Teaching Pearls`
- **THEN** the rendered note contains the heading and its source body even though no specialized concept field exists

### Requirement: Provide question review and examination from SR projections

The website SHALL render a question front from the published SR projection, reveal the projected back on answer review, record selected answers against the current question source hash, and show linked concepts through the relation index. Exam scoring SHALL use the projected correct answer and SHALL not mutate published question content.

#### Scenario: Review a question answer

- **WHEN** a user chooses option `C` for a question whose projected correct answer is `B`
- **THEN** the website marks the attempt incorrect, records the current source hash with the attempt, and can reveal the source back content

### Requirement: Preserve existing study progress without content overrides

The website SHALL continue to use `rex_progress` for seen, starred, answers, and exam history. The website SHALL not read, merge, write, or display `rex_edits_*` as published question or concept content. Before the migration removes content editing controls, the website SHALL provide an export of existing `rex_edits_*` data.

#### Scenario: Ignore a legacy content patch

- **WHEN** browser storage contains `rex_edits_concepts` with a replacement title for `brain-abscess`
- **THEN** the concept route displays the title from the published vault-native record and raw note, and the legacy patch remains exportable but is not merged
### Requirement: Render answer states without false scoring

The question view SHALL render `answerMode: single` and `answerMode: any` as single-choice controls, `answerMode: all` as multi-select controls, and `answerMode: none` as a review-only question. Exam pools SHALL exclude questions with `scorable: false`; card and concept routes MAY display them with an explicit unresolved/no-valid-answer badge. Scoring SHALL compare the selected set with `acceptedAnswers` according to `answerMode`.

#### Scenario: Do not score an unresolved question

- **WHEN** a question record has `scorable: false` and `answerStatus: unresolved`
- **THEN** the exam pool excludes it and the card view shows that it is pending review rather than marking a guessed option correct
