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

Every nonblank line inside an accepted Summary variant must be either a nonempty level-3 heading or a valid top-level bold-label bullet with at least one defined footnote reference. Plain prose, block quotes, fenced code, Markdown tables, callouts, and nested bullets are rejected. This closed grammar prevents content from being silently excluded from generated keyPoints.

Alternative considered: validate only lines that already look like bullets. Rejected because arbitrary prose could otherwise survive note validation while disappearing from generated output.

### Manual classification uses a closed enum and complete inventory

Every NR entry will have exactly one type: disease, pattern-ddx, or anatomy-measurement-management. The tool may consume a checked-in override map, but unknown values and unclassified notes fail validation. Phase 1 assigns the 10 fixed pilot slugs to batch-00 and leaves the other 206 as unassigned.

Alternative considered: infer type from filename keywords. Rejected because entities such as scores, syndromes, signal patterns, and management notes overlap lexically.

### Fact coverage is an explicit batch evidence contract

batch-00.json stores the original Summary losslessly, stable fact-unit IDs, source refs, dispositions, rewritten Summary, hashes, per-note status, and validation results. A note can be verified only when every original fact unit is covered and there are zero unsupported new facts.

Alternative considered: rely only on git diff review. Rejected because a compact rewrite can omit a qualifier or exception without creating an obvious structural defect.

The trusted final-review anchor covers every fact disposition and source mapping, per-note sourceStatus and status, current and rewritten Summary snapshots, validation results, root status, and Phase 1 verification metadata. Coordinated evidence changes require resealing the anchor; changing both content and its self-reported digest without updating the trusted anchor fails with evidence-trusted-final-mismatch.

Alternative considered: trust only digests stored inside batch-00.json. Rejected because an attacker or accidental edit could change both evidence and its colocated digest.

### Source research is exception-driven

radiology-topic-research is triggered only for unmapped facts, source conflicts, time-sensitive guidelines, weak-source-dependent claims, or prose that cannot be compressed without interpretation. Public and already accessible sources are used first. Authenticated platforms require the user to log in and leave a readable tab; credentials and restricted PDF downloads are out of scope.

Alternative considered: run the complete five-source workflow on all 216 notes. Rejected because it expands Phase 1 without improving already well-sourced claims.

### Lint acceptance compares against a fixed baseline

The project-wide linter is expected to retain exactly the two known unrelated errors and 124 warnings. Any additional error fails the pilot. Independently, the 10 NR pilot notes must have zero structural and footnote errors in the new validator.

Alternative considered: repair unrelated lint defects in this branch. Rejected to preserve scope and avoid mixing question-image migration with NR content restructuring.

### Generated keyPoints must match source Summary bullets

After scripts/build_concepts.py runs, each pilot JSON keyPoints array must equal the aggregate of top-level bullets from all accepted Summary variants, in source order, after footnote-marker removal and the build script's established normalization. Mismatch is reported as generated-keypoints-mismatch.

Alternative considered: visual spot checks only. Rejected because multi-Summary variants and nested sections can produce subtle extraction differences.

The build runs as `python scripts/build_concepts.py --batch-file docs/reports/nr-summary-rewrite/batch-00.json --quiet`. It writes only selected pilot detail files whose deterministic bytes changed, reconstructs a coherent index from checked-in detail files, and performs no unrelated writes. The Phase 1 generated manifest records the exact 10 pilot hashes, index hash and entry count, total detail-file count, and a digest of the whole detail tree. Any missing, added, or changed non-pilot detail file fails validation.

Alternative considered: run the unscoped repository-wide generator and inspect the diff manually. Rejected because write scope and non-pilot drift would not be machine-enforced.

## Implementation Contract

### Observable behavior

- The audit CLI provides inventory, validate-note, and validate-batch commands.
- Inventory contains exactly 216 NR notes, no duplicate slugs, no unclassified entries, 10 batch-00 notes, and 206 unassigned notes.
- validate-note reports stable finding codes and exits 1 on structural or footnote errors.
- Task 1 provides a syntactically callable `validate_evidence()`/`validate-batch` placeholder only; a successful Task 1 `validate-batch` invocation is not evidence verification.
- Task 3 extends that stable interface to verify source hashes, evidence schema, fact-source mappings, fact dispositions, rewritten Summary coverage, and generated keyPoints.
- Every nonblank line in each accepted pilot Summary variant is either a nonempty level-3 heading or a valid bold-label top-level bullet with a defined footnote; prose, quotes, code, tables, callouts, and nested bullets are rejected.
- Generated keyPoints aggregate all accepted Summary variants in source order.
- The batch-scoped build performs no unrelated writes and its manifest seals the exact pilot files, index, counts, and whole detail tree.
- Notes that require unavailable research remain research-needed or manual-review and are never reported as verified.
- The Phase 1 batch root remains needs-review while the four derived manual fact units remain unresolved.

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
- Any nonblank Summary line outside the closed heading-or-bullet grammar produces summary-content-line.
- Duplicate/unclassified/missing inventory entries fail inventory validation.
- A source hash mismatch stops edits to that note and changes its status to manual-review.
- Missing or undefined source refs prevent a fact unit from being covered.
- Unresolved research does not block safe sibling notes, but prevents the affected note and batch root from being verified.
- A generated keyPoints mismatch fails batch validation.
- A generated manifest mismatch or trusted final-review anchor mismatch fails batch validation.
- Any new project lint error fails Phase 1; the two named baseline errors remain recorded and unchanged.

### Acceptance criteria

- scripts/test_nr_summary_audit.py prints NR_SUMMARY_AUDIT_OK and exits 0.
- Python compilation succeeds for the audit module and smoke tests.
- Inventory verification reports 216 NR notes, 0 duplicate slugs, 0 unclassified, 10 batch-00, and 206 unassigned.
- The 10 pilot notes pass validate-note.
- Batch validation reports no missing sources, no unsupported new facts, and complete fact coverage for every verified note.
- Concept build succeeds and generated keyPoints match source Summary bullets.
- The scoped build is byte-idempotent, writes no unrelated detail file, and validates the exact 10-file/index/count/whole-tree manifest.
- Project lint reports exactly the two named errors and 124 warnings, and no pilot note appears in the error list.
- Final evidence passes the trusted-anchor gate and the batch root is needs-review with Phase 2 disabled.

### Scope boundaries

In scope: the audit tool, smoke tests, inventory, batch-00 evidence, the 10 fixed pilot Summary sections, and corresponding deterministic concept JSON outputs.

Out of scope: the remaining 206 Summary rewrites, unrelated question/vault edits, baseline lint repairs, renderer/schema changes, authentication handling, and restricted PDF downloads.

## Risks / Trade-offs

- [Risk] Semantic fact units require judgment and cannot be fully derived mechanically. -> Mitigation: lossless original snapshots, stable IDs, explicit source refs, and per-note review.
- [Risk] Summary compression may drop qualifiers or versions. -> Mitigation: fact-unit coverage includes polarity, qualifiers, numbers, dates, and guideline version layers.
- [Risk] Existing project lint is not clean. -> Mitigation: pin the exact baseline and reject any new error while requiring pilot-local zero errors.
- [Risk] A concept build could drift non-pilot generated data. -> Mitigation: use the batch-scoped deterministic command and validate exact pilot/index/count hashes plus the whole detail-tree digest.
- [Risk] Authenticated literature may be unavailable. -> Mitigation: park only affected notes as research-needed and continue safe notes.
