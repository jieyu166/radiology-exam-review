# vault-generation Specification

## Purpose

TBD - created by archiving change 'obsidian-exam-vault'. Update Purpose after archive.

## Requirements

### Requirement: Publish verified 100-note Phase 2B concept summaries from the vault

The generation workflow SHALL derive Phase 2B concept detail JSON and the concept index from validated vault Summary content for exactly the 100 notes in `scheduled-disease-01` through `scheduled-disease-10`. It MUST validate and publish one ten-note scheduled sub-batch at a time, and it MUST reject a publication attempt unless every selected note in that sub-batch has passed its evidence and structure gates.

#### Scenario: Publish one validated disease sub-batch

- **WHEN** all ten notes in `scheduled-disease-01` pass Phase 2B validation
- **THEN** the generation workflow writes only the ten matching concept detail JSON files and `data/concepts-index.json` from the vault Summary content

#### Scenario: Refuse a sub-batch with an unvalidated disease note

- **WHEN** one `scheduled-disease-07` note has `newUnsupportedFacts` greater than zero or fails its footnote gate
- **THEN** the generation workflow rejects that sub-batch and writes no selected detail JSON file


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
### Requirement: Preserve sub-batch publication isolation

The generation workflow MUST serialize Phase 2B scoped builds and generated-manifest seals. The workflow SHALL permit a validated sub-batch to coexist with other evidence and Markdown rewrites in progress, but it MUST NOT accept unrelated selected-detail or index drift as part of its own two-run observation.

#### Scenario: Isolate a later sub-batch build

- **WHEN** `scheduled-disease-03` has a sealed generated observation and `scheduled-disease-04` begins its scoped build
- **THEN** validation preserves the sealed observation for `scheduled-disease-03` and evaluates `scheduled-disease-04` only against its own selected detail files and shared-index snapshot

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
