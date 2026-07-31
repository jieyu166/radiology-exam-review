# Task 5.1 implementation brief — Phase 2A tranche acceptance

## Binding role and task

Implement only Spectra Task 5.1 for
`restructure-nr-concept-summaries-phase2a`, starting after reviewed commit
`d6a95e9`.

The implementation subagent is:

`/root/phase2a_task5_1_impl`

Read the complete change design/spec/tasks, all three approved batch evidence
files and generated manifests, the Task 2.3/3.3/4.3 reports and independent
reviews, `scripts/nr_summary_audit.py`, `scripts/build_concepts.py`, and their
full test suites before acting. Use TDD and verification-before-completion.

This is aggregate acceptance, not a fourth content batch. Do not edit any
concept Markdown, generated detail JSON, generated index, assignment,
inventory, baseline lock, Phase 1 artifact, or any of the 176 scheduled notes.
Do not start Phase 2B or a later tranche. Do not mark the Spectra checkbox; the
controller will obtain a new independent final reviewer after the focused
implementation commit.

## Exact current tranche truth

Derive these values from checked artifacts; tests and implementation must not
silently replace them with looser counts:

- 216 NR inventory notes = 10 immutable Phase 1 pilots + 206 non-pilots;
- exactly 30 unique active Phase 2A notes in the fixed ordered batches:
  `batch-01-anatomy`, `batch-02-disease`, `batch-03-pattern`;
- exactly 176 `scheduled-not-started` notes;
- exactly three trusted baseline locks, three approved evidence reports, and
  three authenticated generated-output manifests;
- current generated corpus: 980 detail files and 980 index entries;
- 27 note statuses are `verified`; the three affected notes remain
  `research-needed`;
- the exact sorted aggregate manual queue has six fact IDs:
  `adrenoleukodystrophy-f30`,
  `adrenoleukodystrophy-f33`,
  `brain-herniation-syndromes-f03`,
  `cns-opportunistic-infection-f03`,
  `cns-opportunistic-infection-f06`,
  `cns-opportunistic-infection-f07`;
- therefore the tranche root must be
  `phase2a-complete-with-manual-queue`, never `verified`;
- full lint must retain exactly the inherited undefined `[^*]` error in
  `ceap-classification.md`, the Obsidian embed error in question 2022-264, and
  124 warnings. The warning delta is exactly
  `{before: 124, after: 124, delta: 0, explanations: []}` unless current
  evidence proves otherwise.

## Public tranche validator and deterministic artifact

Use RED tests before production code. Add a repo-root-explicit, relocation-safe
public function and CLI for Phase 2A tranche verification. Follow existing
interface and JSON-finding conventions; choose the narrowest coherent command
name and checked artifact path. The artifact must be a deterministic,
repo-relative JSON report/manifest under the existing Phase 2A report tree and
must contain at least the design's `phase2aVerification` fields:

- honest tranche status;
- assignment SHA-256;
- exact three active batch IDs;
- strict note count and verified note count;
- exact derived sorted manual queue;
- exact two named lint errors and fully audited warning delta;
- authenticated per-batch manifest digests plus a final current generated-tree
  observation/manifest binding all selected detail hashes, index hash/count,
  detail count, and canonical detail-tree digest;
- current corpus coherence;
- `phase2BStarted=false`.

The verifier must derive acceptance from assignment, inventory, trusted locks,
approved evidence, code-owned generated-observation trust, current Markdown,
all accepted Summary variants, generated detail files, the complete index/tree,
lint output/baseline, and immutable/scheduled scope. A mutable report must not
authenticate itself. If a separate code-owned final digest is required, keep
one narrowly scoped central constant and prove coordinated artifact/tree
resealing fails. Do not add per-note constants or trust arbitrary extra keys.

The acceptance artifact may be created only after all three batch terminal
validators pass. Re-running its audited workflow must produce identical bytes,
zero mtime drift, and zero Git drift.

## Required fail-closed attacks

Tests must cover stable nonzero findings for at least:

1. missing, duplicate, wrong-batch, wrong-type, or extra active member;
2. fewer or more than 30 unique active notes, or any scheduled member started;
3. missing/untrusted baseline, unapproved evidence, reviewer conflict, forged
   reviewed baseline, forged note status, or forged derived queue;
4. a manual/research fact counted as covered or a nonempty queue paired with
   root `verified`;
5. missing/changed selected detail, keyPoints mismatch, selected-detail
   manifest hash mismatch, missing or duplicate index entry, incoherent index,
   wrong corpus counts/tree digest, or coordinated mutable-manifest reseal;
6. a later/scheduled detail or evidence/report change attributed to Phase 2A;
7. Phase 1 pilot/evidence drift;
8. either named lint error missing/changed, any new error, any selected-note
   error, or an unexplained warning-count delta;
9. missing/true/ambiguous `phase2BStarted`;
10. path escape, absolute path, current-working-directory dependence, or an
    incomplete coherent shadow checkout.

Canonical and complete relocated checkouts must yield the same findings,
digests, JSON, and exit codes. Do not weaken any existing batch, baseline,
evidence, coverage, generated-output, empty-projection, assignment, inventory,
lint, or path-validation gate.

## Required acceptance gates

- three final `validate-batch --check-generated` results are exact `[]`;
- assignment reports exact 216/10/206/30/176 and exact fixed memberships;
- inventory reports 216, duplicate 0, unclassified 0, batch-00 10,
  unassigned 0;
- all three trusted baseline/evidence/review/manifest chains pass;
- all 30 active notes pass strict structure, footnote, source, fact,
  unsupported, hash, and generated keyPoints checks;
- all accepted `## Summary` and `## Summary — suffix` variants contribute
  top-level bullets in source order, with non-Summary sections excluded;
- final complete tree/index is coherent at 980/980 and all three historical
  manifests still authenticate their own selected detail hashes;
- exact six-item derived queue and 27 verified notes produce only
  `phase2a-complete-with-manual-queue`;
- exact inherited lint 2 errors / 124 warnings and zero unexplained delta;
- 176 scheduled notes have no Phase 2A Summary rewrite, generated detail
  update, lock, evidence disposition, implementation record, reviewer record,
  or later-phase state;
- Phase 1 artifacts and evidence are byte-identical to their trusted state;
- scoped/tranche workflow rerun has zero byte, mtime, and Git drift;
- full audit/build pytest, Phase 1 direct smokes, four-file `py_compile`,
  30 strict notes, attacks, relocation parity, Spectra strict/analyze, and
  `git diff --check` pass.

## Scope, report, and commit

Allowed changes are only:

- the narrow tranche validator/workflow and CLI;
- strictly necessary tests;
- one deterministic final Phase 2A verification/generated manifest artifact;
- at most one narrowly justified code-owned tranche observation digest;
- Task 5.1 implementation report.

Write:

`tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-5-1-report.md`

Record RED/GREEN, exact file/schema/interface choices, all counts and hashes,
the six-item queue, lint details, attacks and stable codes, relocation results,
two-run byte/mtime/Git proof, full test and CLI outputs, changed-file scope,
and concerns.

Make one focused commit and return DONE, DONE_WITH_CONCERNS, or BLOCKED with
the SHA. The expected honest result is DONE_WITH_CONCERNS only because six
facts remain in the derived manual queue; mechanical or integrity failures are
blocking and must not be relabeled as manual queue.
