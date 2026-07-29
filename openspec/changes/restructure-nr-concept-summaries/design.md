## Context

The vault concept Markdown files are the content source of truth, and scripts/build_concepts.py generates per-concept website JSON. NR currently contains 216 concept notes with heterogeneous Summary structures, including exact Summary headings and heading variants. Phase 1 is a calibration run over 10 fixed notes before the remaining 206 notes are assigned to production batches.

The current concept linter starts with a known non-NR baseline of 2 errors and 124 warnings. The two errors are an undefined [^*] reference in ceap-classification.md and an Obsidian embed in question 2022-264. This change does not repair those unrelated defects; it must not add any new lint error.

## Goals / Non-Goals

**Goals:**

- Provide deterministic parsing and validation for NR Summary headings, top-level bullets, bold labels, footnotes, inventory, and batch evidence.
- Classify all 216 NR notes into disease, pattern-ddx, or anatomy-measurement-management without silent keyword inference.
- Establish a lossless original Summary snapshot and source-mapped fact ledger before editing the 10 pilot notes.
- Rewrite only the 10 pilot Summaries while preserving all sourced fact units, qualifiers, polarity, numbers, versions, and exceptions.
- Verify generated keyPoints against source Summary bullets and keep non-pilot generated output unchanged.

**Non-Goals:**

- Rewriting the remaining 206 NR notes in Phase 1.
- Changing concept body sections, questions, frontmatter, images, Dataview blocks, or existing references except when a triggered source investigation adds a verified article/chapter citation.
- Changing the website renderer or concept JSON schema.
- Fixing the two known non-NR lint errors.
- Performing full five-source research for every NR note.

## Decisions

### Deterministic audit tooling does not generate medical prose

scripts/nr_summary_audit.py will parse, inventory, and validate content but will not compose or classify medical facts automatically. Semantic rewriting remains a reviewed content operation because keyword heuristics cannot safely preserve qualifiers, negation, version context, and causal direction.

Alternative considered: automatic Summary generation from headings and body text. Rejected because it can introduce unsupported relationships or silently drop conditions.

### Manual classification uses a closed enum and complete inventory

Every NR entry will have exactly one type: disease, pattern-ddx, or anatomy-measurement-management. The tool may consume a checked-in override map, but unknown values and unclassified notes fail validation. Phase 1 assigns the 10 fixed pilot slugs to batch-00 and leaves the other 206 as unassigned.

Alternative considered: infer type from filename keywords. Rejected because entities such as scores, syndromes, signal patterns, and management notes overlap lexically.

### Fact coverage is an explicit batch evidence contract

batch-00.json stores the original Summary losslessly, stable fact-unit IDs, source refs, dispositions, rewritten Summary, hashes, per-note status, and validation results. A note can be verified only when every original fact unit is covered and there are zero unsupported new facts.

Alternative considered: rely only on git diff review. Rejected because a compact rewrite can omit a qualifier or exception without creating an obvious structural defect.

### Source research is exception-driven

radiology-topic-research is triggered only for unmapped facts, source conflicts, time-sensitive guidelines, weak-source-dependent claims, or prose that cannot be compressed without interpretation. Public and already accessible sources are used first. Authenticated platforms require the user to log in and leave a readable tab; credentials and restricted PDF downloads are out of scope.

Alternative considered: run the complete five-source workflow on all 216 notes. Rejected because it expands Phase 1 without improving already well-sourced claims.

### Lint acceptance compares against a fixed baseline

The project-wide linter is expected to retain exactly the two known unrelated errors and 124 warnings. Any additional error fails the pilot. Independently, the 10 NR pilot notes must have zero structural and footnote errors in the new validator.

Alternative considered: repair unrelated lint defects in this branch. Rejected to preserve scope and avoid mixing question-image migration with NR content restructuring.

### Generated keyPoints must match source Summary bullets

After scripts/build_concepts.py runs, each pilot JSON keyPoints array must equal the corresponding top-level Summary bullets after footnote-marker removal and the build script's established normalization. Mismatch is reported as generated-keypoints-mismatch.

Alternative considered: visual spot checks only. Rejected because multi-Summary variants and nested sections can produce subtle extraction differences.

## Implementation Contract

### Observable behavior

- The audit CLI provides inventory, validate-note, and validate-batch commands.
- Inventory contains exactly 216 NR notes, no duplicate slugs, no unclassified entries, 10 batch-00 notes, and 206 unassigned notes.
- validate-note reports stable finding codes and exits 1 on structural or footnote errors.
- Task 1 provides a syntactically callable `validate_evidence()`/`validate-batch` placeholder only; a successful Task 1 `validate-batch` invocation is not evidence verification.
- Task 3 extends that stable interface to verify source hashes, evidence schema, fact-source mappings, fact dispositions, rewritten Summary coverage, and generated keyPoints.
- The 10 pilot Summary sections use bold-label top-level bullets without Summary tables, callouts, or nested bullets.
- Notes that require unavailable research remain research-needed or manual-review and are never reported as verified.

### Public Python interfaces

- parse_note(path: Path) -> NoteRecord
- parse_note_text(path: Path, text: str) -> NoteRecord
- extract_summary_sections(body: str) -> list[SummarySection]
- validate_summary(note: NoteRecord) -> list[Finding]
- validate_inventory(inventory: dict) -> list[Finding]
- validate_inventory_against_notes(inventory: dict, notes: dict[str, NoteRecord]) -> list[Finding]
- validate_evidence(report: dict, notes: dict[str, NoteRecord]) -> list[Finding]

SummarySection, NoteRecord, and Finding are immutable dataclasses. Finding contains severity, code, path, and message.
`validate_evidence()` is intentionally a no-op interface in Task 1; Task 3 owns all evidence-content semantics and preserves its signature.

### JSON data shapes

inventory.json has schemaVersion 1, scope NR, generatedFrom vault/concepts, and notes. Each note contains slug, path, type, batch, status, sourceStatus, originalSha256, and summaryHeadings.

batch-00.json has schemaVersion 1, batch batch-00, scope NR, status, and notes. Each note contains slug, type, originalSha256, originalSummary, factUnits, sourceStatus, status, rewrittenSummary, and validation. Each fact unit contains a stable ID, text, sourceRefs, and disposition.

### Failure modes

- Missing Summary, invalid bold-label bullet, nested bullet, callout, table, empty bullet, or undefined footnote produces an error finding and nonzero CLI exit.
- Duplicate/unclassified/missing inventory entries fail inventory validation.
- A source hash mismatch stops edits to that note and changes its status to manual-review.
- Missing or undefined source refs prevent a fact unit from being covered.
- Unresolved research does not block safe sibling notes, but prevents the affected note and batch root from being verified.
- A generated keyPoints mismatch fails batch validation.
- Any new project lint error fails Phase 1; the two named baseline errors remain recorded and unchanged.

### Acceptance criteria

- scripts/test_nr_summary_audit.py prints NR_SUMMARY_AUDIT_OK and exits 0.
- Python compilation succeeds for the audit module and smoke tests.
- Inventory verification reports 216 NR notes, 0 duplicate slugs, 0 unclassified, 10 batch-00, and 206 unassigned.
- The 10 pilot notes pass validate-note.
- Batch validation reports no missing sources, no unsupported new facts, and complete fact coverage for every verified note.
- Concept build succeeds and generated keyPoints match source Summary bullets.
- Project lint shows no errors beyond the two fixed baseline errors and no pilot note appears in the error list.

### Scope boundaries

In scope: the audit tool, smoke tests, inventory, batch-00 evidence, the 10 fixed pilot Summary sections, and corresponding deterministic concept JSON outputs.

Out of scope: the remaining 206 Summary rewrites, unrelated question/vault edits, baseline lint repairs, renderer/schema changes, authentication handling, and restricted PDF downloads.

## Risks / Trade-offs

- [Risk] Semantic fact units require judgment and cannot be fully derived mechanically. -> Mitigation: lossless original snapshots, stable IDs, explicit source refs, and per-note review.
- [Risk] Summary compression may drop qualifiers or versions. -> Mitigation: fact-unit coverage includes polarity, qualifiers, numbers, dates, and guideline version layers.
- [Risk] Existing project lint is not clean. -> Mitigation: pin the exact baseline and reject any new error while requiring pilot-local zero errors.
- [Risk] build_concepts.py regenerates all concept JSON. -> Mitigation: compare changed paths and stage only the 10 pilot outputs plus a deterministic index diff when present.
- [Risk] Authenticated literature may be unavailable. -> Mitigation: park only affected notes as research-needed and continue safe notes.
