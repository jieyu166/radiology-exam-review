## ADDED Requirements

### Requirement: UTF-8 Phase 2B change artifacts

The Phase 2B proposal, design, and task artifacts SHALL be valid UTF-8 and SHALL preserve their Traditional Chinese content without replacement `0x3F` bytes introduced by a shell encoding conversion. Artifact verification MUST inspect file bytes independently of terminal rendering.

#### Scenario: Detect a replacement-byte artifact

- **WHEN** a Phase 2B artifact contains replacement `0x3F` bytes in place of expected Traditional Chinese characters
- **THEN** the artifact verification fails before implementation starts

### Requirement: Fixed 100-note Phase 2B disease batch scope

The Phase 2B workflow SHALL contain exactly the 100 assignment members in `scheduled-disease-01` through `scheduled-disease-10`, with ten members in each scheduled batch. The workflow MUST reject a baseline, evidence record, rewrite, generated manifest, or review record containing an omitted, duplicate, or out-of-scope member.

#### Scenario: Reject an incomplete batch range

- **WHEN** Phase 2B includes `scheduled-disease-01` through `scheduled-disease-09` but omits `scheduled-disease-10`
- **THEN** scope validation fails because the member count is 90 rather than 100

#### Scenario: Reject a non-disease scheduled member

- **WHEN** a Phase 2B evidence record adds `ct-venography` from `scheduled-anatomy-01`
- **THEN** validation fails before Summary publication or generated-output acceptance

### Requirement: Source-bounded disease card summaries

Each Phase 2B Summary SHALL use bold labels followed by short bullets. A note SHALL display only source-supported disease axes equivalent to age or population, clinical presentation, etiology or pathology, examination, imaging, or differential diagnosis. Every retained factual bullet MUST map to an original fact unit and its existing note source reference; unsupported axes and unsupported factual bullets MUST be omitted or recorded as `research-needed` or `manual-review`.

#### Scenario: Omit an unsupported clinical axis

- **WHEN** the locked original Summary and its existing footnotes contain imaging facts but no clinical-presentation fact
- **THEN** the rewritten Summary contains an imaging block and does not contain a clinical-presentation block

##### Example: Imaging-only evidence lock

- **GIVEN** a locked note has one covered imaging fact unit and zero clinical-presentation fact units
- **WHEN** its Phase 2B Summary is rewritten
- **THEN** the Summary has a bold imaging label and no bold clinical-presentation label

#### Scenario: Preserve a qualified imaging fact

- **WHEN** an original fact unit includes a qualifier and a source reference `[^2]`
- **THEN** the rewritten bullet preserves the qualifier, cites `[^2]`, and maps that bullet to the same fact unit

### Requirement: Verifiable 100-note batch acceptance

A Phase 2B note MUST NOT be marked verified unless its source hash, lossless pre-edit Summary lock, Summary structure, footnotes, fact coverage, and generated keyPoints validation all pass with `newUnsupportedFacts` equal to zero. Each ten-note scheduled sub-batch MUST NOT be accepted unless its scoped build writes only its selected detail JSON files and the concept index on its first execution and produces no byte or mtime changes on its second execution. The 100-note tranche MUST NOT be accepted unless every sub-batch has an independent approved review and the derived manual queue matches every unresolved fact ID.

#### Scenario: Block publication when a fact lacks coverage

- **WHEN** any locked fact unit has no covered, research-needed, or manual-review disposition
- **THEN** validation fails and the note and its sub-batch remain unverified

##### Example: Missing disposition

- **GIVEN** `brain-abscess-f03` is present in the baseline lock and absent from every evidence disposition
- **WHEN** batch validation runs
- **THEN** validation reports fact-coverage failure and does not mark `brain-abscess` verified

#### Scenario: Block publication for a non-idempotent build

- **WHEN** the second scoped build changes a selected detail JSON byte or modification time
- **THEN** generated-output validation fails and the affected sub-batch remains unaccepted

##### Example: Second-run JSON mutation

- **GIVEN** the first scoped build records `data/concepts/brain-abscess.json` as an allowed selected output
- **WHEN** the second scoped build changes that file's byte hash or modification time
- **THEN** generated-output validation fails and the affected sub-batch remains unaccepted
