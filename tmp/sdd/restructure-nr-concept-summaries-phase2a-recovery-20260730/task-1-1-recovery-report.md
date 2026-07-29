# Task 1.1 recovery report

## Scope and base

- Recovery base: `89df5cabf9ca442322f94aaefee409a3cb7d430d`.
- Implemented only the remaining Task 1.1 historical-scope/current-coherence
  blocker.
- Did not modify `vault/concepts/`, create production Phase 2 assignment,
  baseline, evidence, generated-manifest, or generated-output data, start Task
  1.2, or mark Task 1.1 complete.

## RED evidence

The first isolated regression used genuine gated two-run observations for an
approved chain. It sealed batch 1, then changed only
`brain-tumor-imaging` through a separately approved and sealed batch 3.

- Command:
  `python -m pytest -q scripts/test_nr_summary_audit.py -k "later_trusted_batch_update_preserves_earlier_historical_scope"`
- Pre-fix result: `1 failed, 88 deselected in 1.37s`.
- Expected failure: batch 3 itself had zero findings, but revalidating batch 1
  returned `generated-manifest-mismatch`.

The complete six-regression recovery slice then covered the approved later
change, invalid later reviewer/evidence/generated trust, unattributed current
detail drift, earlier selected-detail drift, forged/incoherent current index,
and canonical/relocated equivalence.

- Command:
  `python -m pytest -q scripts/test_nr_summary_audit.py -k "later_trusted_batch_update or later_update_without_independent_trust or unassigned_current_detail_drift or earlier_selected_detail_drift or incoherent_current_index or authorized_later_update_is_relocation_stable"`
- Pre-fix result: `2 failed, 4 passed, 88 deselected in 6.71s`.
- Only the two coherent authorized-later expectations failed; all four
  fail-closed controls already passed.

## Design choice

Validation now has two explicit layers:

1. The checked batch manifest remains an immutable historical observation. Its
   code-owned generated-observation digest authenticates the projection, and
   its historical full detail map is derived from authenticated
   `detailFiles + nonselectedAfter`. Historical selected paths, allowed writes,
   index/count, and complete-tree digest are checked for internal coherence.
2. The current complete detail tree and `data/concepts-index.json` are derived
   and checked independently. The earlier batch's selected detail hashes and
   generated keyPoints must still match current files. Every other current
   detail delta must belong to a strictly later active batch, and that later
   batch must independently pass assignment, baseline trust, evidence,
   predecessor/reviewer approval, generated-observation trust, current
   selected hash, and its own current-corpus gate.

A later batch ID, assignment membership, or mutable manifest claim is never
sufficient authorization. Missing or changed earlier selected details,
unattributed added/missing/changed details, invalid later gates, and an
incoherent or forged current index retain stable generated-output failures.
Later validation recurses only in increasing batch sequence, so it cannot
cycle back to an earlier batch.

Decision 6, the Implementation Contract, and the modified
`concept-web-build` requirement now state this historical/current separation
explicitly without weakening final tranche current-corpus coherence.

## Changed files

- `scripts/nr_summary_audit.py`
- `scripts/test_nr_summary_audit.py`
- `openspec/changes/restructure-nr-concept-summaries-phase2a/design.md`
- `openspec/changes/restructure-nr-concept-summaries-phase2a/specs/concept-web-build/spec.md`
- `tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-1-1-recovery-report.md`

## Verification

- Focused recovery GREEN:
  - six required regressions: `6 passed, 88 deselected in 8.33s`
  - coherent-forged/incoherent index control:
    `1 passed, 93 deselected in 1.35s`
- Final complete audit/build pytest matrix:
  - command:
    `python -m pytest -q scripts/test_nr_summary_audit.py scripts/test_build_concepts.py`
  - result: `105 passed in 43.51s`
- Existing direct Phase 1 smoke suites:
  - `python scripts/test_nr_summary_audit.py`:
    `NR_SUMMARY_AUDIT_OK`
  - `python scripts/test_build_concepts.py`:
    `BUILD_CONCEPTS_TEST_OK`
- Four-file compile:
  - command:
    `python -m py_compile scripts/nr_summary_audit.py scripts/test_nr_summary_audit.py scripts/build_concepts.py scripts/test_build_concepts.py`
  - result: exit 0
- Consolidated canonical/shadow and all prior/new Task 1.1 attacks:
  - command:
    `python -m pytest -q scripts/test_nr_summary_audit.py scripts/test_build_concepts.py -k "phase2 or scoped_build or explicit_root"`
  - result: `33 passed, 72 deselected in 20.29s`
- Spectra:
  - `spectra validate restructure-nr-concept-summaries-phase2a --strict --json`:
    valid, 0 errors, 0 warnings
  - `spectra analyze restructure-nr-concept-summaries-phase2a --json`:
    0 Critical, 0 Warning; 2 pre-existing unrelated Suggestions
- Scope and whitespace:
  - `git diff --check`: exit 0
  - `git diff --exit-code -- vault/concepts`: exit 0
  - Task 1.1 checkbox diff: empty
  - changed implementation/artifact scope before this report was exactly the
    four files listed above

## Concerns

- The production baseline and generated-observation trust registries remain
  intentionally empty and fail-closed in Task 1.1. Later Tasks 2.3, 3.3, and
  4.3 must seal only independently reviewed genuine observations.
- Spectra analyze continues to report two pre-existing Suggestions for missing
  concrete examples in unrelated medical scenarios. There are no
  Critical/Warning findings.
