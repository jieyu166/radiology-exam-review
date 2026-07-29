## ADDED Requirements

### Requirement: NR concept inventory is complete and explicitly classified

The system SHALL inventory every concept Markdown file whose frontmatter subspecialty array contains NR. Each inventoried note MUST have exactly one type from disease, pattern-ddx, or anatomy-measurement-management. The system MUST reject duplicate slugs, unsupported types, and missing NR notes. Phase 1 SHALL assign exactly 10 fixed pilot slugs to batch-00 and SHALL leave the remaining 206 NR notes unassigned.

#### Scenario: Complete Phase 1 inventory

- **WHEN** the inventory command scans the current vault/concepts directory
- **THEN** it reports 216 NR notes, 0 duplicate slugs, 0 unclassified notes, 10 batch-00 notes, and 206 unassigned notes

##### Example: fixed pilot membership

- **GIVEN** the current 216-note NR inventory
- **WHEN** batch assignment is validated
- **THEN** batch-00 contains exactly clippers, cerebral-amyloid-angiopathy, craniopharyngioma, basal-ganglia-t1-shortening, cpa-masses, bilateral-subcortical-dwi-hyperintensity-ddx, artery-of-adamkiewicz, aspects-score, acute-stroke-management, and dementia-neuroimaging-overview

### Requirement: NR Summary bullets follow a type-specific labeled format

Each rewritten pilot Summary SHALL use top-level bullets that begin with a bold label followed by a full-width or ASCII colon. A Summary MUST NOT contain nested bullets, callouts, or Markdown tables. Disease notes SHALL use only sourced disease labels, pattern-ddx notes SHALL order content by discriminating imaging axes, and anatomy-measurement-management notes SHALL use only sourced structure, measurement, threshold, grading, clinical-meaning, operation-order, or pitfall labels. Missing categories MUST be omitted rather than inferred.

#### Scenario: Disease note omits an unsupported age category

- **WHEN** a disease note has sourced imaging and pathology facts but no sourced age fact
- **THEN** its rewritten Summary contains imaging and pathology bullets and contains no age bullet

#### Scenario: Invalid Summary structure is rejected

- **WHEN** a pilot Summary contains a nested bullet, callout, Markdown table, or bullet without a bold label
- **THEN** validate-note returns a stable error finding and exits with status 1

### Requirement: Summary rewriting preserves sourced medical facts

The rewrite MUST preserve every independent fact from the original Summary, including subject, relationship, polarity, qualifier, numeric value, time range, version, negation, exception, and source reference. The rewrite MUST NOT introduce a medical relationship, value, threshold, version, or causal claim that is absent from an existing verified source or a source verified during the triggered research workflow.

#### Scenario: Qualifier preservation

- **WHEN** an original fact states that a finding is typically present or relatively preserved
- **THEN** the rewritten fact retains the corresponding non-absolute qualifier

#### Scenario: Unsupported new fact blocks verification

- **WHEN** a rewritten Summary contains a fact unit with no mapped source
- **THEN** batch validation reports an unsupported-fact error and the note cannot have verified status

### Requirement: Batch evidence provides lossless and source-mapped coverage

Before editing a pilot note, the system SHALL store a lossless original Summary snapshot and current file SHA-256. Each independent original claim MUST have a stable fact-unit ID, one or more defined source references or an explicit unresolved disposition, and a final coverage disposition. A note SHALL have verified status only when all original facts are covered, the source hash matched before editing, and newUnsupportedFacts equals 0.

#### Scenario: Concurrent edit prevents overwrite

- **WHEN** a pilot note SHA-256 differs from its recorded originalSha256 before Summary editing
- **THEN** the workflow stops editing that note and records manual-review

#### Scenario: Complete fact coverage verifies a note

- **WHEN** every original fact unit is covered, every source ref is defined, structure and footnotes pass, and newUnsupportedFacts is 0
- **THEN** the note can be marked verified

### Requirement: Literature research is exception-driven and auditable

The workflow SHALL trigger radiology-topic-research only for an unmapped fact, a source conflict, a time-sensitive diagnostic or management rule, a weak-source-dependent claim that cannot be safely compressed, or prose that requires unsupported interpretation. New content MUST include an article-level or chapter-level footnote. Conflicting sources MUST be recorded with conservative wording and MUST NOT be collapsed into an unsupported single value. The workflow MUST NOT handle credentials, bypass access controls, or download a restricted PDF.

#### Scenario: Authenticated source is required

- **WHEN** a required STATdx, ClinicalKey, RadioGraphics, or AJR page is inaccessible without authentication
- **THEN** the affected note remains research-needed while the user is asked to log in and leave the relevant page readable

### Requirement: Phase 1 validation permits only the fixed non-NR lint baseline

The 10 pilot notes MUST have zero Summary structural errors and zero undefined footnotes. Project lint MUST NOT contain any error beyond the two recorded baseline errors: the undefined [^*] reference in ceap-classification.md and the Obsidian embed in question 2022-264. Any additional project lint error MUST fail Phase 1 validation.

#### Scenario: Baseline is unchanged

- **WHEN** project lint reports exactly the two named baseline errors and no pilot note error
- **THEN** the lint-baseline gate passes despite the linter process returning status 1

#### Scenario: New error fails the batch

- **WHEN** project lint reports either a third error or an error in a pilot note
- **THEN** the lint-baseline gate fails and batch-00 cannot be verified

