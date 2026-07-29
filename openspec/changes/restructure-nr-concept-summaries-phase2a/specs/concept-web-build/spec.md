## ADDED Requirements

### Requirement: Scoped concept build supports safe production batches

The system SHALL provide a re-runnable `scripts/build_concepts.py` that reads concept Markdown under `vault/concepts/` (excluding files whose basename starts with `_`) and emits `data/concepts-index.json` plus per-concept `data/concepts/<slug>.json` files. Every detail file SHALL use the filename slug as its `slug` field, and a concept declaring inline `concepts: [<slug>]` SHALL emit the corresponding filename slug. Every index entry SHALL contain exactly the published index fields for that detail file.

Without a selection argument, the script SHALL retain the full-build behavior: it SHALL regenerate the eligible corpus from the current vault and reconcile the generated detail tree with that corpus. With `--batch-file <path>` or `--slugs <slug>...`, it SHALL perform a scoped build. A batch file SHALL declare a nonempty, duplicate-free collection of safe lowercase filename slugs in its `notes` entries; the selected set SHALL be deterministic regardless of input order. The script SHALL reject an invalid batch, unsafe or duplicate slug, missing selected source note, or unbuildable selected note before changing generated output.

For a scoped build, the script SHALL write only the selected detail files whose deterministic UTF-8 JSON bytes differ from their current bytes. It SHALL neither create, rewrite, delete, nor otherwise change a nonselected detail file. After selected detail generation, it SHALL rebuild `data/concepts-index.json` from every valid detail file currently present in `data/concepts/`, sorted by slug, so that the index is complete and coherent with the checked-in detail tree at the current corpus size. The index SHALL be written only when its deterministic bytes differ. A successful scoped build SHALL report the selected slugs, files actually written, and final index entry count.

For identical inputs and an unchanged generated tree, a repeated full or scoped invocation SHALL be byte-identical and SHALL perform zero writes; consequently, it SHALL preserve the modification times of every detail file and the index.

#### Scenario: A Phase 2A batch updates only its selected detail files

- **GIVEN** `batch-02-disease` declares exactly ten Phase 2A disease slugs, including `aicardi-syndrome`, and `data/concepts/brain-tumor-imaging.json` is already present
- **WHEN** `python scripts/build_concepts.py --batch-file docs/reports/nr-summary-rewrite/phase2a/evidence/batch-02-disease.json --quiet` runs
- **THEN** detail files for the ten declared disease slugs are the only detail files eligible to be written, `brain-tumor-imaging.json` is not written or deleted, and the index is rebuilt from all currently present detail files rather than from only the ten selected files

#### Scenario: An unscoped run retains complete-corpus behavior

- **GIVEN** `vault/concepts/` contains N eligible concept Markdown files
- **WHEN** `python scripts/build_concepts.py --quiet` runs without a selection argument
- **THEN** `data/concepts/` contains exactly N generated detail files and `data/concepts-index.json` contains exactly N entries

#### Scenario: The index remains coherent when its bytes do not need changing

- **GIVEN** a selected detail file is already byte-identical to its deterministic build output and the complete detail tree already agrees with `data/concepts-index.json`
- **WHEN** the corresponding scoped build runs
- **THEN** the script reports zero written files, leaves the selected detail file and index modification times unchanged, and the index entry count still equals the number of detail JSON files

#### Scenario: An invalid selected set fails without output drift

- **GIVEN** a batch file contains a duplicate slug or a slug whose Markdown source is missing
- **WHEN** a scoped build is requested
- **THEN** the command fails with a stable selection error before modifying any detail file or the index

##### Example: index entry shape

- **GIVEN** a file `vault/concepts/adrenal-adenoma.md` with frontmatter name `Adrenal Adenoma`, subspecialty `[ABD]`, and Chinese alias `腎上腺腺瘤`
- **WHEN** the build script runs
- **THEN** the index entry is `{"slug":"adrenal-adenoma","name":"Adrenal Adenoma","nameZh":"腎上腺腺瘤","subspecialty":"ABD"}`

### Requirement: Generated keyPoints aggregate every accepted Summary variant for every scoped batch note

For every concept selected by a checked-in Phase 2 batch, the build output `keyPoints` array SHALL equal the aggregate of all top-level source Markdown bullets from every accepted level-two Summary variant, in source order, after footnote-reference removal and the build script's established normalization. Accepted variants are exactly `## Summary` and `## Summary — <nonblank suffix>`; a note with more than one accepted variant SHALL contribute bullets from each variant, not only the first. Content from a non-Summary level-two section SHALL NOT be included merely because it follows a Summary section.

The validation workflow SHALL compare the generated array with independently extracted expected bullets for every selected note and SHALL report `generated-keypoints-mismatch` for a difference. A mismatched note SHALL not pass strict batch or tranche verification.

#### Scenario: Multiple Summary variants contribute in source order

- **GIVEN** a selected note contains `## Summary` with `- **Imaging**: First fact.[^a]` followed later by `## Summary — Management` with `- **Action**: Second fact.[^b]`
- **WHEN** the scoped concept build runs
- **THEN** its `keyPoints` is `["**Imaging**: First fact.", "**Action**: Second fact."]` in that order

#### Scenario: A later non-Summary section is excluded

- **GIVEN** a selected note contains a valid `## Summary` and then `## Clinical points` with a bullet
- **WHEN** the scoped concept build runs
- **THEN** the Clinical points bullet is not appended to `keyPoints`

### Requirement: Every completed Phase 2A batch has an auditable generated-output manifest and rejects nonselected drift

For each completed Phase 2A batch, the evidence workflow SHALL create a deterministic generated-output manifest below `docs/reports/nr-summary-rewrite/phase2a/generated/`. The manifest SHALL identify the batch, list its exact selected slugs in canonical order, record a SHA-256 for each selected detail file, record the SHA-256 and entry count of `data/concepts-index.json`, record the total detail-file count, and record a canonical SHA-256 over the complete detail tree as sorted `(slug, file SHA-256)` pairs.

Before and after that batch's scoped build, validation SHALL compare the paths and byte hashes of every nonselected detail file. Any added, missing, or byte-changed nonselected detail file SHALL fail the batch gate with `generated-manifest-mismatch`, identify the changed path or paths, and prevent the batch from being marked generated-output verified. The validation SHALL allow later batches to change their own selected files; it SHALL not reinterpret those authorized later writes as a failure of an earlier batch's historical scope check.

#### Scenario: Unrelated detail drift fails a batch gate

- **GIVEN** `batch-01-anatomy` selects ten anatomy slugs and a build or concurrent edit changes `data/concepts/gbm-vs-pcnsl.json`
- **WHEN** the batch-01 generated-output validation compares its pre-build and post-build nonselected detail trees
- **THEN** it reports `generated-manifest-mismatch` for `gbm-vs-pcnsl.json` and batch-01 cannot pass its generated-output gate

#### Scenario: A later selected batch does not invalidate earlier historical scope evidence

- **GIVEN** batch-01 completed with a passing nonselected-drift check and batch-03 later selects `brain-tumor-imaging`
- **WHEN** batch-03 legitimately writes `data/concepts/brain-tumor-imaging.json`
- **THEN** batch-03 records that file in its own manifest and batch-01 retains its passing historical scope result rather than failing retroactively

### Requirement: Phase 2A tranche verification proves all three batches and the complete generated corpus

The Phase 2A acceptance workflow SHALL verify the union of `batch-01-anatomy`, `batch-02-disease`, and `batch-03-pattern` as exactly 30 unique selected notes. It SHALL verify, for every one of those 30 notes, the strict generated `keyPoints` comparison, the corresponding per-batch generated-output manifest, and the selected detail-file SHA-256. It SHALL also verify a final tranche manifest for the complete current generated tree, whose index hash, index entry count, total detail-file count, and canonical detail-tree digest agree with the current files.

Tranche acceptance SHALL fail if a selected slug is absent, repeated, assigned to the wrong batch, lacks generated JSON, has a generated `keyPoints` mismatch, has a selected-detail hash mismatch, or if the final index is incomplete or inconsistent with the detail tree. Passing tranche verification SHALL not start, rewrite, or mark complete any of the remaining 176 scheduled-but-not-started NR notes.

#### Scenario: All 30 selected notes pass as one tranche

- **GIVEN** each of the three checked-in Phase 2A batch files declares ten unique notes, every batch manifest passes, and the final index contains one entry for every current detail JSON file
- **WHEN** tranche verification runs
- **THEN** it reports 30 strict notes verified across three batches and accepts the generated corpus only if all 30 `keyPoints` arrays and all recorded hashes match

#### Scenario: A coherent-looking index cannot hide a missing selected detail file

- **GIVEN** `data/concepts/anti-nmda-encephalitis.json` is missing but an index rebuilt from the remaining detail files is internally coherent
- **WHEN** Phase 2A tranche verification runs
- **THEN** it fails because the batch-02 selected detail file and its manifest hash are missing, even though the index itself is coherent

