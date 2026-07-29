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

## Independent review round 1 fixes

### Adversarial RED

- Command:
  - `python -m pytest -q scripts/test_nr_summary_audit.py scripts/test_build_concepts.py -k "pilot_nonpilot_batch_swap or separates_pre_edit_source_gate or shrunken_membership or coordinated_nonselected or scoped_cli_requires_explicit_root"`
- Result before implementation:
  - `5 failed, 85 deselected`
- The five failures reproduced every Important review scenario:
  1. mutable `batch-00` pilot/nonpilot swap was accepted;
  2. `check_source_hashes=False` still emitted pre-edit lock mismatches;
  3. shrunken evidence and forged workflow metadata emitted no findings;
  4. coordinated nonselected mutation/manifest regeneration lacked `generated-unrelated-write` and `generated-non-idempotent`;
  5. scoped build accepted omitted `--repo-root`.

### Fixes

- Pilot identity now comes only from immutable `PILOT_SLUGS`; inventory `batch-00` membership is independently required to equal that set.
- Baseline trust/membership validation is separate from the optional pre-edit current-source gate. Rewrite-mode validation compares the current Summary with the evidence snapshot.
- Evidence validation now enforces exact ordered membership, root/note schema, derived validation/status/queue data, baseline reference, workflow sequence/predecessor, nonblank distinct identities, review state, and reviewed baseline snapshot.
- Generated manifests preserve nonselected observations across regeneration, execute and record a real second idempotence run, and emit the two specific stable failure codes.
- `--batch-file` and `--slugs` require explicit `--repo-root`; legacy unscoped full build retains its fallback behavior.
- The empty production trusted registry remains unchanged and fail-closed.

### Review-round verification

- Five focused exploit tests:
  - `5 passed, 85 deselected`
- Full audit/build suite:
  - `90 passed in 30.70s`
- Existing direct Phase 1 suites:
  - `NR_SUMMARY_AUDIT_OK`
  - `BUILD_CONCEPTS_TEST_OK`
- Four-file `py_compile`:
  - exit 0
- Combined original relocation/attack and review-attack selection:
  - `14 passed, 76 deselected in 0.88s`
- `git diff --check`:
  - exit 0
- `git diff --exit-code -- vault/concepts`:
  - exit 0

## Independent review round 2 fixes

### Adversarial RED

- Command:
  - `python -m pytest -q scripts/test_nr_summary_audit.py -k "duplicate_pilot_and_217 or requires_approval_and_predecessor or derives_current_footnotes or public_manifest_builder_is_read_only"`
- Result before implementation:
  - `4 failed, 79 deselected`
- The failures reproduced all four Important review scenarios:
  1. a duplicate pilot plus 217 inventory rows was accepted;
  2. terminal evidence did not require approval/current-baseline review, and batch 2 did not require valid batch 1 evidence;
  3. deleted rendered footnote definitions were hidden by self-claimed zero counters;
  4. the public manifest builder wrote generated data while the trusted registry was empty.

### Fixes

- Assignment projection and validation now require exactly 216 globally unique string slugs and exactly one occurrence of every immutable pilot.
- Terminal `verified`/`needs-review` evidence now requires approved review of the current baseline; every later batch loads and validates its approved terminal predecessor evidence.
- Batch evidence validation derives current `validate_summary()` findings and checks source-definition kind, locator, citation, and rendered-footnote correspondence before comparing derived error counts with evidence.
- Public generated-manifest construction is read-only. It observes current bytes and existing evidence only, so untrusted callers cannot trigger scoped writes.
- The empty production trusted registry remains unchanged and fail-closed.

### Review-round verification

- Four focused exploit tests:
  - `4 passed, 79 deselected`
- Full audit/build suite:
  - `94 passed in 33.58s`
- Existing direct Phase 1 suites:
  - `NR_SUMMARY_AUDIT_OK`
  - `BUILD_CONCEPTS_TEST_OK`
- Consolidated relocation/adversarial selection:
  - `18 passed, 76 deselected in 1.48s`
- Four-file `py_compile`:
  - exit 0
- `git diff --check`:
  - exit 0
- `git diff --exit-code -- vault/concepts`:
  - exit 0

## Independent review round 3 fixes

### Adversarial RED

- Command:
  - `python -m pytest -q scripts/test_nr_summary_audit.py -k "requires_explicit_build_observations or statuses_are_closed_and_exactly_derived"`
- Result before implementation:
  - `2 failed, 83 deselected`
- The failures reproduced both Important review scenarios:
  1. manifest construction succeeded without independently supplied pre-build, post-build, or second-run observations;
  2. a `research-needed` fact accepted arbitrary note/source status strings.
- A follow-up RED assertion proved that a syntactically valid but stale explicit post-build snapshot also succeeded before the final observation gate.

### Fixes

- The read-only manifest constructor now requires explicit pre-build, post-build, and second-run observations. Missing observations fail with `generated-observation-missing`; malformed or stale observations fail with `generated-observation-invalid`.
- The post-build nonselected snapshot must match the current read-only generated tree. No observation is synthesized from an existing manifest or defaulted to empty success.
- Batch validation reads only the fixed expected manifest path and passes its explicit historical observations into read-only reconstruction.
- Phase 2 note status is exactly derived as `manual-review`, `research-needed`, or `verified` from fact dispositions. `sourceStatus` is derived from unresolved dispositions and the kinds of definitions actually referenced; root status remains exactly derived from the batch unresolved queue.
- The empty production trusted registry remains unchanged and fail-closed.

### Review-round verification

- Two focused exploit tests:
  - `2 passed, 83 deselected`
- Full audit/build suite:
  - `96 passed in 32.68s`
- Consolidated relocation/adversarial selection:
  - `20 passed, 76 deselected in 1.86s`
- Existing direct Phase 1 suites:
  - `NR_SUMMARY_AUDIT_OK`
  - `BUILD_CONCEPTS_TEST_OK`
- Four-file `py_compile`:
  - exit 0
- `git diff --check`:
  - exit 0
- `git diff --exit-code -- vault/concepts`:
  - exit 0

## Independent review round 4 fixes

### Adversarial RED

- Command:
  - `python -m pytest -q scripts/test_nr_summary_audit.py -k "self_attested_no_build or gated_two_run_workflow or two_run_workflow_fails_before_write"`
- Result before implementation:
  - `3 failed, 85 deselected`
- The failures proved that a no-build manifest could self-attest current hashes, while no genuine gated two-run API or fail-before-write workflow existed.

### Fixes

- Added `run_phase2_generated_observation_workflow()`: it validates assignment, baseline, evidence, and code-owned baseline trust before writes; captures generated bytes/mtimes; performs the scoped build; captures post-state; performs the actual second build; and compares both byte and mtime deltas.
- Added one initially empty, fail-closed `TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256` entry per reviewed active batch. The observation projection binds batch membership, allowed writes, nonselected pre/post hashes, first/second run deltas, selected detail hashes, index, and final tree.
- Batch validation authenticates that projection against the code-owned digest and independently derives current generated output fields. It no longer recycles checked manifest observations into their own validation truth.
- A self-attested no-build manifest fails with `generated-observation-untrusted`; failed preflight trust leaves every repository byte and mtime unchanged.
- Updated the Phase 2A design, concept-web-build specification, and Implementation Contract with the Task 1.1 empty-registry state and Tasks 2.3/3.3/4.3 sealing responsibility.

### Review-round verification

- Three focused regressions:
  - `3 passed, 85 deselected`
- Full audit/build suite:
  - `99 passed in 33.86s`
- Consolidated relocation/adversarial selection:
  - `23 passed, 76 deselected in 2.19s`
- Existing direct Phase 1 suites:
  - `NR_SUMMARY_AUDIT_OK`
  - `BUILD_CONCEPTS_TEST_OK`
- Four-file `py_compile`, `git diff --check`, and `git diff --exit-code -- vault/concepts`:
  - exit 0
- `spectra validate restructure-nr-concept-summaries-phase2a --strict --json`:
  - valid, 0 errors, 0 warnings
- `spectra analyze restructure-nr-concept-summaries-phase2a --json`:
  - 0 Critical/Warning; 2 pre-existing Suggestions for missing concrete examples in unrelated medical scenarios
