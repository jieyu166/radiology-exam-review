# nr-summary-phase2b-disease-batch Specification

## Purpose

TBD - created by archiving change 'restructure-nr-concept-summaries-phase2b'. Update Purpose after archive.

## Requirements

### Requirement: UTF-8 Phase 2B change artifacts

The Phase 2B proposal, design, and task artifacts SHALL be valid UTF-8 and SHALL preserve their Traditional Chinese content without replacement `0x3F` bytes introduced by a shell encoding conversion. Artifact verification MUST inspect file bytes independently of terminal rendering.

#### Scenario: Detect a replacement-byte artifact

- **WHEN** a Phase 2B artifact contains replacement `0x3F` bytes in place of expected Traditional Chinese characters
- **THEN** the artifact verification fails before implementation starts


<!-- @trace
source: restructure-nr-concept-summaries-phase2b
updated: 2026-08-02
code:
  - scripts/build_phase2b_evidence.py
  - scripts/nr_summary_audit.py
  - scripts/rewrite_phase2b_summary.py
  - scripts/build_concepts.py
tests:
  - scripts/test_build_concepts.py
  - scripts/test_nr_summary_audit.py
-->

---
### Requirement: Fixed 100-note Phase 2B disease batch scope

The Phase 2B workflow SHALL contain exactly the 100 assignment members in `scheduled-disease-01` through `scheduled-disease-10`, with ten members in each scheduled batch. The workflow MUST reject a baseline, evidence record, rewrite, generated manifest, or review record containing an omitted, duplicate, or out-of-scope member.

#### Scenario: Reject an incomplete batch range

- **WHEN** Phase 2B includes `scheduled-disease-01` through `scheduled-disease-09` but omits `scheduled-disease-10`
- **THEN** scope validation fails because the member count is 90 rather than 100

#### Scenario: Reject a non-disease scheduled member

- **WHEN** a Phase 2B evidence record adds `ct-venography` from `scheduled-anatomy-01`
- **THEN** validation fails before Summary publication or generated-output acceptance


<!-- @trace
source: restructure-nr-concept-summaries-phase2b
updated: 2026-08-02
code:
  - scripts/build_phase2b_evidence.py
  - scripts/nr_summary_audit.py
  - scripts/rewrite_phase2b_summary.py
  - scripts/build_concepts.py
tests:
  - scripts/test_build_concepts.py
  - scripts/test_nr_summary_audit.py
-->

---
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


<!-- @trace
source: restructure-nr-concept-summaries-phase2b
updated: 2026-08-02
code:
  - scripts/build_phase2b_evidence.py
  - scripts/nr_summary_audit.py
  - scripts/rewrite_phase2b_summary.py
  - scripts/build_concepts.py
tests:
  - scripts/test_build_concepts.py
  - scripts/test_nr_summary_audit.py
-->

---
### Requirement: Verifiable 100-note batch acceptance

A Phase 2B note MUST NOT be marked verified unless its source hash, lossless pre-edit Summary lock, Summary structure, footnotes, and fact coverage all pass with `newUnsupportedFacts` equal to zero. The 100-note tranche MUST NOT be accepted unless every sub-batch has an independent approved review and the derived manual queue matches every unresolved fact ID. Acceptance evidence SHALL be recorded under `docs/reports/nr-summary-rewrite/phase2b/` and SHALL remain byte-for-byte unchanged after the audit tooling is retired. Acceptance MUST NOT depend on any generated JSON under `data/`; the vault Summary section is the final published form of each note.

#### Scenario: Block publication when a fact lacks coverage

- **WHEN** any locked fact unit has no covered, research-needed, or manual-review disposition
- **THEN** validation fails and the note and its sub-batch remain unverified

##### Example: Missing disposition

- **GIVEN** `brain-abscess-f03` is present in the baseline lock and absent from every evidence disposition
- **WHEN** batch validation runs
- **THEN** validation reports fact-coverage failure and does not mark `brain-abscess` verified

#### Scenario: Preserve sealed evidence after tooling retirement

- **WHEN** the audit scripts are deleted from `scripts/`
- **THEN** every file under `docs/reports/nr-summary-rewrite/phase2b/` keeps the same SHA-256 as in the preservation commit, and the vault Summary sections of the 100 notes are unchanged

<!-- @trace
source: remove-legacy-data-json
updated: 2026-10-10
code:
  - scripts/image_asset_manager.js
  - output/imagegen/adrenoleukodystrophy-background-draft.png
  - scripts/image_asset_manager.py
  - scripts/start_image_asset_manager.ps1
  - start-image-manager.cmd
  - docs/image-asset-manager.md
  - scripts/image_asset_manager.html
  - docs/concept-summary-review-publication.md
tests:
  - scripts/test_image_asset_manager.py
  - scripts/test_image_asset_manager.js
-->