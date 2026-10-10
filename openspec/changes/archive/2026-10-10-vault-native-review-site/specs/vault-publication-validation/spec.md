## ADDED Requirements

### Requirement: Produce a complete publication inventory

The validation command SHALL classify every Markdown file below `vault/questions/` and `vault/concepts/` as published, excluded by `publish: false`, excluded by underscore basename, warning, or hard error. The build report SHALL list the count and source path for each classification. The command SHALL fail when an eligible note lacks a raw asset, record, or manifest entry.

#### Scenario: Detect a missing record

- **WHEN** an eligible note has a manifest entry and raw asset but no record
- **THEN** validation exits nonzero with a hard error identifying the source path and missing record

### Requirement: Validate source identity and question contracts

Validation SHALL fail for duplicate published ids, duplicate output paths, paths outside the configured output root, a published question without exactly one SR front/back boundary, a correct answer outside A through E, conflicting parsed answer values, or an ambiguous required asset. Validation SHALL not infer a replacement answer or silently skip an invalid eligible note.

#### Scenario: Reject a conflicting answer

- **WHEN** a published question frontmatter declares `correctAnswer: A` and its SR back declares `Ans: B`
- **THEN** validation exits nonzero with a hard error that identifies the question source path and both values

### Requirement: Preserve unknown source content explicitly

Validation SHALL compare every published raw asset hash to its source hash and SHALL confirm that every source heading appears in the emitted outline. Unsupported safe Markdown constructs SHALL produce warnings with source path and line number. The renderer contract fixture suite SHALL include every syntax class observed by the syntax inventory.

#### Scenario: Report an unknown safe construct

- **WHEN** a published note contains a syntax inventory entry that is not in the renderer support list and is not required for question interaction
- **THEN** validation records a warning with source path and line number while retaining the raw source asset

### Requirement: Produce deterministic publication output

Two compiler executions with identical vault input and compiler version SHALL produce byte-identical manifest, records, indexes, raw assets, assets, and build report except for an explicitly excluded ephemeral workflow log. Package files SHALL use stable path ordering and SHALL not contain build timestamps.

#### Scenario: Repeat an unchanged build

- **WHEN** the compiler runs twice against unchanged source input
- **THEN** the SHA-256 of every file below the output root is identical between runs
### Requirement: Validate explicit review and answer states

Validation SHALL accept `answerStatus` values `confirmed`, `unresolved`, and `no_valid_answer`, `answerMode` values `single`, `any`, `all`, and `none`, and an `acceptedAnswers` list containing only A-E letters. An explicit `unresolved` or `no_valid_answer` state SHALL downgrade a missing or conflicting answer value to a review diagnostic and SHALL emit a non-scorable projection. It SHALL NOT bypass invalid option structure, duplicate identity, path, or required-asset errors. Validation SHALL NOT infer `any` versus `all` from a multi-letter legacy answer.

#### Scenario: Preserve an unresolved answer state

- **WHEN** a published question has `answerStatus: unresolved`, `answerMode: none`, and no valid `Ans:` value
- **THEN** validation emits a non-scorable question projection with a review diagnostic instead of inventing an answer

#### Scenario: Reject an invalid answer-state value

- **WHEN** a published question declares `answerMode: maybe` or an accepted answer outside A-E
- **THEN** validation exits nonzero with a hard error identifying the source path and invalid value
