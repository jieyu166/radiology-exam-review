# Task 3.1 fix report — round 1

## Result

- Status: DONE_WITH_CONCERNS
- Fix base: `298b30b4bd6b31b144c7648b579c17620c7eb7bd`
- Scope: the three Important findings in
  `review-task-3-1-round-1.md`; the Task 3.1 checkbox remains unchanged for
  independent re-review.
- No concept Markdown, generated concept JSON, assignment, inventory,
  batch-01 artifact, or scheduled-note artifact was modified.
- No literature research was needed: every correction is a lossless parser or
  trust-registry fix against the existing source notes.

## Findings addressed

### 1. Footnote definitions are no longer facts

`phase2_summary_source_statements` now excludes footnote-definition lines and
their four-space/tab continuation lines from the fact projection. Definitions
remain available through `sourceDefinitions`.

- ALD now has 18 factual source statements and 36 fact units.
- The batch contains 60 statements and 98 fact units in total.
- No `sourceStatement` matches a footnote definition.
- ALD still preserves all 11 entries in `sourceDefinitions`.

### 2. Nested semantic context and enclosing references are preserved

The deterministic representation is:

- a pure-label parent followed by contiguous nested children creates exactly
  one context fact;
- that fact preserves the parent's exact source text and uses a source-order
  union of the parent and child explicit references;
- child facts preserve their exact source lines and use explicit references,
  otherwise inheriting the parent references;
- indented ordered-list children and unordered-list children are both
  recognized.

Production assertions now prove:

- `aicardi-syndrome-f03` is the exact triad parent context, with
  `sourceRefs: ["1", "2"]`;
- Aicardi child facts `f04` through `f06` each have
  `sourceRefs: ["1", "2"]`;
- `adrenoleukodystrophy-f09` is the exact Schaumburg-zone context, with
  `sourceRefs: ["4", "3"]`;
- the Aicardi triad relation and ALD center-to-outside zone relation each
  appear exactly once;
- the only genuinely empty reference sets are
  `adrenoleukodystrophy-f30` and `adrenoleukodystrophy-f33`.

### 3. The checked baseline registry requires an exact active prefix

`_phase2_trust_registry_is_valid` now requires both the registry keys and
present active baseline files to equal the first N active batch IDs.

Regression attacks prove:

- batch-02-only is rejected;
- batch-01 plus batch-03 is rejected;
- batch-01 plus batch-02 plus batch-03 is accepted when all corresponding
  files and digests are valid.

The rejection code is `phase2-trusted-batch-lock-mismatch`.

## TDD evidence

The five new regressions were run before the production fix:

- RED: `5 failed, 132 deselected in 1.15s`.
- Focused GREEN after the minimal implementation:
  `11 passed, 127 deselected in 0.90s`.
- Complete audit/build suite:
  `150 passed in 106.51s (0:01:46)`.

The first complete run after the implementation exposed one stale batch-01
projection expectation (`149 passed, 1 failed`). The minimal correction added
`_phase2_legacy_batch01_fact_templates` solely for the immutable
`batch-01-anatomy` baseline. Its fail-closed regression proves that a resealed
injected fact still returns `phase2-baseline-schema`, and a wrong batch-01
digest still returns `phase2-trusted-batch-lock-mismatch`. Digest, source-hash,
lossless-summary, evidence, generated-observation, and review-sequence gates
remain active.

## Regenerated deterministic artifacts

The two batch-02 JSON files were regenerated through the audited builders.
Two independent builder processes produced identical bytes:

- canonical baseline digest:
  `3c294b4e098fc971ec6cbc67945cc24620752108f7d31bf3c1ba574ef6fd8fa8`;
- baseline file SHA-256:
  `334c132f12d60c8f5eb51373a11fe97ea228d14d9c7729ee9953f1972c03e5d9`;
- baseline bytes: `69,906`;
- evidence file SHA-256:
  `b7119473e60ad87134ec58c7d4087078ab32598b89fcf3a7b4ea897e09626477`;
- evidence bytes: `49,204`;
- batch totals: 60 statements and 98 facts;
- footnote-definition facts: 0.

## Terminal gates

- `validate-baseline --batch batch-02-disease`: exit 0, exact findings `[]`.
- Batch-01 `validate-batch --check-generated`: exit 0, exact findings `[]`.
- Direct smoke tests: `NR_SUMMARY_AUDIT_OK` and `BUILD_CONCEPTS_TEST_OK`.
- Four-file `py_compile`: exit 0.
- Spectra strict validation: valid.
- Spectra analysis: 0 Critical, 0 Warning, 2 pre-existing Suggestions.
- `git diff --check`: exit 0.
- Scope diff from `298b30b` confirms no change to `vault/concepts`,
  `data/concepts`, `data/concepts-index.json`, inventory, assignment,
  batch-01 artifacts, or the Task 3.1 checkbox.

Batch-01 artifact SHA-256 values remain unchanged:

- baseline:
  `6b05caff4e2cbd618a9c15478f914853701b4be2587af58469b013917d0a7934`;
- evidence:
  `0225a5e6c7a6fca4d2abe6abe9d73540ef186c064dc5d3b89690d0d74857f70b`;
- generated manifest:
  `bd1d2be10b9045c17b3f7ff540414623b8ecee4b6f2dd38f576aa3d118fbbbdb`.

## Changed files

- `scripts/nr_summary_audit.py`
- `scripts/test_nr_summary_audit.py`
- `docs/reports/nr-summary-rewrite/phase2a/baselines/batch-02-disease.json`
- `docs/reports/nr-summary-rewrite/phase2a/evidence/batch-02-disease.json`
- `tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-3-1-fix-round-1.md`

## Concerns

- Two ALD facts remain without source references because their exact original
  source statements have no applicable footnote. This is intentional and must
  remain visible to Task 3.2 coverage/research handling.
- The user-level Git ignore file is unreadable in the managed sandbox, so Git
  prints a warning; repository status, diff, staging, and checks still
  complete successfully.
