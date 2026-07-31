## ADDED Requirements

### Requirement: Phase 2 assignment is complete, deterministic, and activates only the Phase 2A tranche

The system SHALL create `phase2-assignment.json` for every one of the 206 NR notes that is not a Phase 1 `batch-00` pilot. Each assignment entry MUST contain the unique slug, vault-relative note path, exactly one classified type, deterministic batch identifier, and a Phase 2 state. The assignment manifest MUST contain each of the 206 slugs exactly once; it MUST NOT contain a pilot, a duplicate slug, an unsupported type, or an unclassified note.

The assignment algorithm SHALL keep a batch type-homogeneous, sort future members by type and then slug, and deterministically produce the same mapping for unchanged inventory input. A future batch SHALL contain fewer than 10 notes only when it is the final remaining batch for its type. Phase 2A SHALL activate exactly the following three 10-note batches and SHALL leave every other assigned note in `scheduled-not-started` state:

- `batch-01-anatomy`: `ajcc-8th-head-neck-n-staging`, `aneurysm-coiling-recurrence`, `atlantodental-interval`, `brachial-plexus-anatomy`, `brain-herniation-syndromes`, `carotid-vertebrobasilar-anastomoses`, `cerebral-border-zone-infarct-arteries`, `cerebral-deep-venous-cortex`, `cerebral-herniation-types`, and `cerebral-infarction-evolution`.
- `batch-02-disease`: `2-hydroxyglutarate-idh-mutant-glioma`, `adrenoleukodystrophy`, `aicardi-syndrome`, `als-imaging`, `angioinvasive-aspergillosis`, `anti-nmda-encephalitis`, `arterial-dissection-mri`, `atypical-teratoid-rhabdoid-tumor`, `autoimmune-encephalitis`, and `basilar-artery-occlusion`.
- `batch-03-pattern`: `brain-tumor-imaging`, `cerebral-infarction-fogging`, `cerebral-microbleeds`, `cerebrovascular-malformations`, `chemical-shift-artifact`, `cns-opportunistic-infection`, `cranial-nerve-muscle-atrophy`, `dural-based-masses-aids`, `facial-fracture-complications`, and `gbm-vs-pcnsl`.

The system MUST reject an assignment manifest if an active batch has other than 10 members, if a listed member has the wrong type, if an active member is absent or replaced, or if the arithmetic is not 216 total NR notes = 10 Phase 1 pilots + 30 Phase 2A active notes + 176 scheduled-not-started notes.

#### Scenario: Complete assignment has the fixed Phase 2A mapping

- **WHEN** assignment validation runs against the current 216-note NR inventory
- **THEN** it reports 206 non-pilot assignments, 30 active Phase 2A members in the exact three fixed batches, and 176 `scheduled-not-started` members

#### Scenario: Deterministic future mapping is regenerated

- **GIVEN** unchanged slug and type classifications for the 206 non-pilot notes
- **WHEN** the assignment generator runs twice
- **THEN** the two canonical `phase2-assignment.json` byte sequences are identical, each non-Phase-2A batch contains one type only, and its members appear in slug order within that type

#### Scenario: A fixed batch substitution is rejected

- **WHEN** `brain-tumor-imaging` is replaced with any other pattern-ddx slug in `batch-03-pattern`
- **THEN** assignment validation emits a stable active-batch-membership finding and exits nonzero

### Requirement: Each active batch has a lossless baseline lock and independently trusted digest

Before a Phase 2A note is edited, the system SHALL record it in that batch's baseline lock. A lock entry MUST include the vault-relative note path, assigned type, original file SHA-256, accepted Summary heading variant, lossless original Summary text, and stable IDs for every independent original fact unit. Stable fact-unit IDs MUST remain addressable by the corresponding evidence report; a fact unit MUST NOT be silently merged, deleted, or renumbered to make coverage appear complete.

The canonical bytes of each complete baseline lock MUST be SHA-256 sealed by exactly one entry for that batch in a central, code-owned batch trust registry. The expected digest MUST be independent of mutable inventory, assignment, baseline-lock, and evidence-report files. The registry SHALL contain one digest per active batch rather than one code constant per note. Validation MUST recompute the lock digest and compare it with the registry entry before accepting any evidence, rewrite, or status for that batch.

#### Scenario: A valid baseline lock is accepted

- **WHEN** the `batch-02-disease` lock has 10 entries, every entry matches its assigned path and type, and its canonical SHA-256 equals the `batch-02-disease` registry digest
- **THEN** baseline validation passes and the batch is permitted to transition from `scheduled-not-started` to `baseline-locked`

#### Scenario: Mutable coordinated baseline replacement is rejected

- **WHEN** an actor changes an active note's `originalSha256` in both the assignment-related evidence and the batch baseline lock without changing the code-owned registry digest
- **THEN** validation emits a stable baseline-trust-mismatch finding, exits nonzero, and does not accept the altered note as baseline-locked

#### Scenario: One bad entry does not invalidate an independent sibling baseline

- **WHEN** the digest for `batch-01-anatomy` mismatches while the locks and registry digest for `batch-02-disease` match
- **THEN** `batch-01-anatomy` cannot start, and `batch-02-disease` retains its independently valid baseline status subject to the tranche sequencing gate

### Requirement: Evidence reports provide complete, source-defined fact dispositions

Each Phase 2A active note SHALL have an evidence report that references its locked baseline and includes source definitions, per-fact dispositions, rewritten Summary snapshot, `newUnsupportedFacts` count, validation blocks, derived manual-review queue, per-note status, and batch root status. Every locked fact unit MUST have exactly one final disposition: `covered`, `manual-review`, or another explicitly named non-covered blocking disposition. A `manual-review` or blocking disposition MUST NOT be represented as `covered`.

A covered fact MUST preserve the original subject, relationship, polarity, qualifiers, numbers, dates, versions, negations, exceptions, and applicable source references. The report MUST identify one or more defined source references for each covered fact. The rewritten Summary MUST NOT introduce a medical relationship, threshold, version, value, causal claim, or other conclusion unless it is supported by an existing verified source or an auditable exception-research source. `newUnsupportedFacts` MUST equal the count of new rewritten fact units that lack such support.

Every nonblank accepted Summary line MUST be either a nonempty level-3 heading or a top-level bullet beginning with a bold label followed by a full-width or ASCII colon and containing at least one defined Obsidian footnote. Disease notes SHALL use sourced disease axes only; pattern-ddx notes SHALL use discriminating imaging axes; anatomy-measurement-management notes SHALL use sourced structure, measurement, threshold, grading, clinical-meaning, operation-order, or pitfall labels. Missing categories MUST be omitted rather than inferred.

#### Scenario: A fully covered disease fact verifies

- **WHEN** an `anti-nmda-encephalitis` locked fact unit preserves its qualified imaging relationship, maps to a defined source reference, has a matching defined footnote in the rewritten labeled bullet, and `newUnsupportedFacts` is 0
- **THEN** the fact disposition is `covered` and it contributes to the note's verified eligibility

#### Scenario: An unsupported rewritten threshold blocks verification

- **WHEN** a rewritten anatomy Summary adds a numeric threshold that is absent from all defined source references
- **THEN** the report increments `newUnsupportedFacts`, validation emits unsupported-fact, and the affected note cannot be marked `verified`

#### Scenario: Invalid Summary grammar is rejected

- **WHEN** an active Summary contains plain prose, a nested bullet, a table, a callout, a bullet without a bold label and colon, or a reference to an undefined footnote
- **THEN** strict note validation emits the applicable stable structural or footnote finding and exits nonzero

### Requirement: Literature research is exception-only, auditable, and access-safe

The workflow SHALL invoke `radiology-topic-research` only when a fact is unmapped, sources conflict, a diagnostic or management rule is time-sensitive, a weak-source-dependent claim cannot be safely compressed, or the requested wording requires unsupported interpretation. A newly researched fact MUST have an article-level or chapter-level Obsidian footnote, a defined source entry, and an evidence disposition that names the research result. Conflicting sources MUST be preserved in the evidence report and represented with conservative wording; they MUST NOT be collapsed into an unsupported single value.

The workflow MUST NOT handle credentials, bypass access controls, or download a restricted PDF. When an authenticated source is required, the workflow SHALL request that the user log in and leave the relevant page readable; until then, the affected fact SHALL remain `manual-review` or `research-needed` and SHALL not be covered.

#### Scenario: Authenticated source remains unresolved

- **WHEN** a required ClinicalKey chapter is inaccessible without authentication
- **THEN** the system records `research-needed`, asks the user to authenticate and leave the chapter readable, and does not create a credential, download a restricted PDF, or mark the fact covered

#### Scenario: Research supplies a permitted new fact

- **WHEN** exception research verifies a previously unmapped imaging fact in a journal article
- **THEN** the rewritten bullet includes an article-level footnote, the source definition identifies that article, and the evidence report records the fact's research-backed disposition

### Requirement: Batch workflow enforces independent implementation and review gates

An active Phase 2A batch SHALL follow the state sequence `scheduled-not-started` -> `baseline-locked` -> `in-progress` -> `ready-for-independent-review` -> (`verified` or `needs-review`). The batch implementation MUST be performed by an independent subagent, and the review MUST be performed by a different subagent. The review record MUST identify both roles and establish that the reviewer did not implement the batch. A subsequent active batch MUST NOT transition to `in-progress` until its predecessor has received independent review.

The root status MUST be derived from its note statuses and manual queue; it MUST NOT be hand-authored to hide an unresolved fact. A note SHALL be `verified` only if its baseline digest matched, every locked fact is covered, all source definitions and footnotes validate, strict Summary grammar validates, and `newUnsupportedFacts` equals 0. A batch with an explicitly retained manual-review fact SHALL finish independent review with root status `needs-review`; the affected note MUST NOT be `verified` and the fact MUST NOT be counted as covered. A verified sibling note and a separately valid sibling batch MUST NOT be downgraded merely because another note is in manual review.

#### Scenario: Reviewer independence is enforced

- **WHEN** the same subagent identity is recorded as both implementer and reviewer for `batch-01-anatomy`
- **THEN** the workflow rejects the review gate and `batch-02-disease` remains unable to enter `in-progress`

#### Scenario: Manual review is note-scoped

- **WHEN** one `batch-02-disease` note retains a source conflict as `manual-review` while its nine siblings meet all verified conditions
- **THEN** the conflicted note is not verified, the batch root is `needs-review`, and the nine sibling notes retain their verified statuses

#### Scenario: Reviewed predecessor permits the next batch

- **WHEN** `batch-01-anatomy` has a valid baseline, an implementation record, and an independent reviewer record with terminal root status `verified` or `needs-review`
- **THEN** `batch-02-disease` is permitted to transition from `baseline-locked` to `in-progress`

### Requirement: Batch-scoped generation is coherent, narrow, and idempotent

For an active batch, the concept build SHALL write only the selected detail JSON files whose deterministic bytes change, the required generated manifest, and the coherent corpus index metadata. It MUST preserve index/detail coherence at the current corpus size, MUST NOT write unrelated detail files, and MUST be byte- and mtime-idempotent on a second build with unchanged inputs. Generated `keyPoints` and manifest entries MUST correspond to the rewritten Summary and selected batch membership.

#### Scenario: Unchanged rebuild writes nothing

- **GIVEN** a successful `batch-03-pattern` scoped build with unchanged selected notes and inputs
- **WHEN** the identical scoped build runs a second time
- **THEN** no generated file bytes or mtimes change and the build reports zero writes

#### Scenario: Unrelated detail JSON is protected

- **WHEN** a scoped build runs for `batch-01-anatomy`
- **THEN** a detail JSON for a non-selected disease or pattern note is neither rewritten nor touched, while the corpus index remains coherent with the current corpus size

### Requirement: Tranche acceptance is exhaustive and does not start later work

Phase 2A tranche acceptance SHALL require validation of all three fixed batches, strict validation of all 30 active notes, a complete 216-note NR inventory, valid trusted baseline locks for every active batch, evidence/source/footnote/fact-coverage validation, and generated-corpus coherence. The lint gate MUST report exactly the two inherited named errors -- the undefined `[^*]` reference in `ceap-classification.md` and the Obsidian embed in `question 2022-264` -- and MUST reject every new error or error in an active note. Any warning-count delta from the inherited 124-warning baseline MUST be explicitly enumerated with its finding, affected path, and rationale; an unaccounted warning delta MUST fail acceptance.

Phase 2A review completion SHALL require all 30 active notes to reach an independently reviewed terminal state with zero structural, footnote, hash, source-definition, unsupported-fact, generated-output, or unexplained-lint errors. A note with a retained `manual-review` or `research-needed` fact MUST remain non-verified and MUST appear in the derived manual queue. When every active note is verified and the queue is empty, the tranche root SHALL be `verified`. When all mechanical and evidence-integrity gates pass but the derived queue is nonempty, the tranche root SHALL be `phase2a-complete-with-manual-queue` and MUST NOT claim that all 30 notes are verified. The remaining 176 assignments MUST remain `scheduled-not-started`: they MUST have no Summary rewrite, no generated detail update, no Phase 2 evidence disposition claiming coverage, and no implementation or reviewer record. Phase 1 pilots and their evidence MUST remain unchanged.

#### Scenario: Exact inherited lint baseline passes

- **WHEN** project lint reports only the two named inherited errors, no error in any of the 30 active notes, and 124 warnings
- **THEN** the error baseline passes and the zero warning delta is accepted

#### Scenario: Explained warning delta is required

- **WHEN** project lint reports the two named inherited errors and 126 warnings
- **THEN** acceptance passes the warning gate only if the two additional warnings are each recorded with an affected path, finding, and rationale; otherwise it emits an unexplained-warning-delta finding and fails

#### Scenario: Review completion preserves the remaining plan

- **WHEN** all three fixed batches and all 30 active notes reach independently reviewed terminal states and every non-manual gate passes
- **THEN** Phase 2A is marked `verified` when the manual queue is empty or `phase2a-complete-with-manual-queue` when it is nonempty, the inventory still reports 176 `scheduled-not-started` assignments, and validation confirms that none of those 176 notes or their generated detail JSON files were started by Phase 2A

