## ADDED Requirements

### Requirement: Generated keyPoints preserve source Summary bullets

For each Phase 1 pilot concept, the build output keyPoints array SHALL equal the source Markdown Summary top-level bullets after footnote-reference removal and the build script's established normalization. The validation workflow MUST report generated-keypoints-mismatch when the arrays differ.

#### Scenario: Pilot keyPoints match the vault Summary

- **WHEN** scripts/build_concepts.py generates a per-concept JSON file for a pilot note whose Summary has labeled top-level bullets
- **THEN** the generated keyPoints entries preserve the same bullet content and ordering after footnote-reference removal

##### Example: labeled bullet mapping

- **GIVEN** the source bullet "- **Imaging**: Bilateral symmetric GP T1 hyperintensity.[^1]"
- **WHEN** the concept build runs
- **THEN** the corresponding keyPoints entry is "**Imaging**: Bilateral symmetric GP T1 hyperintensity."

#### Scenario: Extraction mismatch is surfaced

- **WHEN** a Summary variant, nested section, or normalization difference causes generated keyPoints to differ from the validated source bullets
- **THEN** batch validation emits generated-keypoints-mismatch and the note cannot be marked verified

