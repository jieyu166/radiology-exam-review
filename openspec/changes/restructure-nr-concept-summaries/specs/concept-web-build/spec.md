## ADDED Requirements

### Requirement: Generated keyPoints preserve source Summary bullets

For each Phase 1 pilot concept, the build output keyPoints array SHALL equal the aggregate of source Markdown top-level bullets from all accepted Summary variants, in source order, after footnote-reference removal and the build script's established normalization. The validation workflow MUST report generated-keypoints-mismatch when the arrays differ.

#### Scenario: Pilot keyPoints match the vault Summary

- **WHEN** scripts/build_concepts.py generates a per-concept JSON file for a pilot note whose accepted Summary variants have labeled top-level bullets
- **THEN** the generated keyPoints entries preserve every variant's bullet content in source order after footnote-reference removal

##### Example: labeled bullet mapping

- **GIVEN** the source bullet "- **Imaging**: Bilateral symmetric GP T1 hyperintensity.[^1]"
- **WHEN** the concept build runs
- **THEN** the corresponding keyPoints entry is "**Imaging**: Bilateral symmetric GP T1 hyperintensity."

#### Scenario: Extraction mismatch is surfaced

- **WHEN** a Summary variant, nested section, or normalization difference causes generated keyPoints to differ from the validated source bullets
- **THEN** batch validation emits generated-keypoints-mismatch and the note cannot be marked verified

The Phase 1 build SHALL run as `python scripts/build_concepts.py --batch-file docs/reports/nr-summary-rewrite/batch-00.json --quiet`. It MUST select slugs from the checked-in batch, write a selected detail file only when its deterministic bytes differ, rebuild a coherent index from checked-in detail files, and perform no unrelated writes. Repeating the command without input changes MUST be byte-identical and MUST write zero files.

#### Scenario: Scoped rerun is idempotent

- **WHEN** the batch-scoped build is run twice without source or detail-file changes
- **THEN** the second run changes zero bytes, preserves file modification times, and does not write any non-pilot detail file

Phase 1 verification SHALL record and validate the exact hashes of the 10 pilot detail files, the index hash and entry count, the total detail-file count, and a canonical digest of the whole detail tree. A missing, added, or changed detail file outside the pilot MUST fail the generated-output gate.

#### Scenario: Non-pilot drift is rejected

- **WHEN** any non-pilot detail file is missing or its bytes change while the 10 pilot files and index remain unchanged
- **THEN** batch validation reports a generated-manifest mismatch and Phase 1 verification fails
