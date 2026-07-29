# Task 1.1 implementation report

## RED evidence

- Baseline before Task 1.1: `74 passed in 56.77s`.
- First focused RED:
  - command: `python -m pytest -q scripts/test_build_concepts.py scripts/test_nr_summary_audit.py -k "phase2 or scoped_build_validates_entire_selection or explicit_root"`
  - result: `8 failed, 1 passed, 74 deselected`
  - expected failures proved the missing contracts: no `--repo-root` build CLI, no Phase 2 assignment/context APIs, no `validate-assignment` CLI, and selected build did not emit a stable missing-source code before write eligibility.
- Second RED:
  - command: `python -m pytest -q scripts/test_nr_summary_audit.py -k "baseline_batch_cli or path_attack_cli"`
  - result: `1 failed, 1 passed, 73 deselected`
  - expected failure: a changed selected detail produced only `generated-manifest-mismatch`; the independent `generated-keypoints-mismatch` gate was still absent.

## Changed files

- `scripts/nr_summary_audit.py`
- `scripts/test_nr_summary_audit.py`
- `scripts/build_concepts.py`
- `scripts/test_build_concepts.py`
- Active Phase 2A OpenSpec artifacts are included unchanged except for the Task 1.1 checkbox update performed after all gates pass.

No file below `vault/concepts/` and no production Phase 2 assignment, inventory, baseline, evidence, lock, or generated manifest was created or edited.

## Implemented contracts

- Preserved the Phase 1 public interfaces and legacy CLI behavior.
- Added deterministic Phase 2 assignment generation/validation, immutable `BatchContext`, explicit-root batch loading, baseline/batch validation, and deterministic generated-manifest construction.
- Added explicit-root `validate-assignment`, `validate-baseline`, and Phase 2 `validate-batch` CLI forms.
- Enforced repo-relative POSIX JSON/CLI paths and stable failure codes without cwd, checkout name, or absolute-path identity trust decisions.
- Added explicit-root scoped builds, complete preflight before the first output write, prospective full-index validation, byte-difference-only writes, nonselected protection, and second-run byte/mtime idempotence.
- Retained aggregation of every accepted `## Summary` variant in source order and added independent generated `keyPoints` comparison.

## Verification

- `python -m pytest -q scripts/test_nr_summary_audit.py scripts/test_build_concepts.py`
  - `85 passed in 32.50s`
- `python scripts/test_nr_summary_audit.py`
  - `NR_SUMMARY_AUDIT_OK`
- `python scripts/test_build_concepts.py`
  - `BUILD_CONCEPTS_TEST_OK`
- `python -m py_compile scripts/nr_summary_audit.py scripts/test_nr_summary_audit.py scripts/build_concepts.py scripts/test_build_concepts.py`
  - exit 0
- Canonical/relocated and attack-focused regression selection
  - `9 passed, 76 deselected in 0.59s`
  - covers identical relocated assignment CLI exits/output, identical generated manifests/digests, explicit-root path attacks, generated-keyPoints mutation, malformed detail trees, missing selected sources, and fail-before-write snapshots.
- `git diff --check`
  - exit 0
- `git diff --cached --check -- scripts tmp/sdd/restructure-nr-concept-summaries-phase2a/task-1-1-report.md`
  - exit 0; the full staged check reports only the pre-existing trailing blank lines in the intentionally untracked binding OpenSpec Markdown, which were preserved as instructed.
- `git diff --exit-code -- vault/concepts`
  - exit 0

## Limitation / staged trust state

`TRUSTED_PHASE2A_BATCH_LOCK_SHA256` intentionally remains fail-closed and empty in Task 1.1 because Tasks 2.1, 3.1, and 4.1 create and independently review the three production baseline locks. Isolated tests inject fixture-only reviewed digests. A production baseline cannot pass until its later task adds the corresponding code-owned digest.
