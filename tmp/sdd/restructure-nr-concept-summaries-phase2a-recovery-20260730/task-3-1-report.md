# Task 3.1 implementation report

## Result

- Status: DONE_WITH_CONCERNS
- Base: `bd6de344c7041f993300901cbe5634a5943143d4`
- Scope: Spectra Task 3.1 only; the Task 3.1 checkbox remains unchanged for
  controller review.
- Batch: `batch-02-disease`, exact assignment-order membership of 10 notes.
- No concept Markdown, generated concept JSON, inventory, assignment, Phase 1
  artifact, batch-01 artifact/trust, generated-observation trust, batch-03
  artifact, or scheduled note was modified.
- No literature research was performed and no medical statement was added,
  corrected, translated, inferred, or reclassified.

## TDD evidence

The production baseline/evidence artifacts and the second central trust entry
were absent when the Task 3.1 tests first ran.

- RED command:
  `pytest scripts/test_nr_summary_audit.py -q -k "phase2a_batch02 or phase2a_batch01_registry_digest"`
- RED result: `10 failed, 123 deselected in 1.37s`.
- Nine failures were caused by missing `batch-02-disease` baseline/evidence;
  the registry regression failed because only `batch-01-anatomy` was present.
- One prerequisite test initially made an incorrect assumption that the
  generated manifest directly stored `observationSha256`. The test was fixed
  to recompute the canonical generated-observation projection, then rerun
  alone. It still failed (`1 failed, 132 deselected in 0.65s`) solely because
  the batch-02 baseline did not yet exist.
- Minimal GREEN used the existing audited
  `build_phase2_baseline_lock_bytes` and
  `build_phase2_pending_evidence_scaffold_bytes` helpers, created the two
  checked JSON artifacts, and added one code-owned batch digest.
- Targeted GREEN: `10 passed, 123 deselected in 1.10s`.

The first complete audit/build run returned `140 passed, 5 failed`. All five
failures were stale batch-01 relocated-checkout fixtures: after the trust
registry became a two-lock contiguous prefix, a coherent relocated checkout
also had to copy the batch-02 lock. The minimal test-helper update copied all
currently trusted locks without weakening validation. Focused reruns passed,
and the final complete suite returned `145 passed in 113.69s`.

## Deterministic artifacts and central trust

Two independent read-only builder processes produced the same projection and
matched the checked files byte-for-byte:

- assignment canonical SHA-256:
  `b9dfbf5361392c03178928b591c09839fa7f6fc08e7c0072867657bc361a8c0e`;
- batch-02 canonical baseline trust SHA-256:
  `9d10c8fc2e927b19f273ca06e96d3c61b814aabb958c765267f5d5014e2c9516`;
- baseline file SHA-256:
  `b81f0d46cee639c1d07758c2b9fd7951668798336fc5c4eb12018dd86d6128af`;
- baseline bytes: `92,586`;
- pending evidence file SHA-256:
  `325e31a59dd3b29feaccd2a05c6d842d5875a2cc83d54e0bad85d857aa484bd6`;
- evidence bytes: `54,162`.

`TRUSTED_PHASE2A_BATCH_LOCK_SHA256` now contains exactly the contiguous
checked baseline prefix:

1. `batch-01-anatomy` ->
   `1ba97cdc318b16deaf60cc768dc4b7424f01759287c91e43c85bd6c1601b0b64`
   (unchanged);
2. `batch-02-disease` ->
   `9d10c8fc2e927b19f273ca06e96d3c61b814aabb958c765267f5d5014e2c9516`.

There is no batch-03 key, per-note trust map, mutable registry file, or
batch-02 generated-observation seal.

## Source-statement-to-fact coverage

The audited builder is the only content source. The baseline contains 69 exact
factual source statements and 131 stable fact units. Every statement appears
in original order in at least one fact's exact `sourceStatement`; IDs are
`<slug>-fNN` without gaps. Existing or enclosing footnotes are copied without
substitution.

| Slug | Statements | Facts | Empty refs | Existing refs used | Source SHA-256 |
|---|---:|---:|---:|---|---|
| `2-hydroxyglutarate-idh-mutant-glioma` | 4 | 7 | 0 | 1, 2, 3 | `956c9af7339798ed5659248453e267a918bccf7876c2b099bf6bfbf8ca60f205` |
| `adrenoleukodystrophy` | 28 | 70 | 2 | 1–11 | `792affd2ce3e0ccbb8f84eb4b2e31db8cd196fb2cbaa2506a64668a1dddafa8a` |
| `aicardi-syndrome` | 6 | 7 | 3 | 1, 2 | `74769c738b4ed0f4be58f9ddb0d8b4208bf8372a5f0a5a844bab3aa92bed8a5b` |
| `als-imaging` | 3 | 4 | 0 | 1 | `10985b1e45e93c4ad95624b1cd7a6cb680e4f1297c1f304caa61cabdd08d39a0` |
| `angioinvasive-aspergillosis` | 5 | 6 | 0 | 1 | `42998c7340d8a5e33388c7daf269a2c547473ced4457e088fbaadc1a363a68cf` |
| `anti-nmda-encephalitis` | 4 | 7 | 0 | 1, 2 | `fcd551d46ba7e5934367c16c63fab0b10983b4f38fe43803c13e5c961f408855` |
| `arterial-dissection-mri` | 5 | 7 | 0 | 1, 2 | `5d0c5a8cb2736985da542e4b21dfca56a367b17c80c8113486ddbafac3b17521` |
| `atypical-teratoid-rhabdoid-tumor` | 5 | 12 | 0 | 1, 2 | `b5bf97074c2dc1591e24750c78b2aa344c150c97a5b2f51d38b0c04871c5f947` |
| `autoimmune-encephalitis` | 4 | 4 | 0 | 1 | `25727f01bde2d53b3151531e15f6b107b4de3546e5bccacac9a6cf51c873fb5c` |
| `basilar-artery-occlusion` | 5 | 7 | 0 | 1–4 | `f5deb355d9f0728350ff84a51176666a2044cfcc5840cba870e39e8bfc8b883b` |
| **Total** | **69** | **131** | **5** | — | — |

All ten current hashes, paths, type values, accepted Summary headings, and
lossless Summary snapshots match inventory, assignment, and lock.

The five original facts without an applicable footnote are preserved with
`sourceRefs: []`:

- `adrenoleukodystrophy-f29`
- `adrenoleukodystrophy-f32`
- `aicardi-syndrome-f03`
- `aicardi-syndrome-f04`
- `aicardi-syndrome-f05`

No source was guessed or researched at baseline time.

## Pending evidence scaffold

The checked scaffold is explicitly nonterminal:

- root status: `baseline`;
- sequence: `2`;
- predecessor: `batch-01-anatomy`;
- implementer: `/root/phase2a_task3_1_impl`;
- reviewer: `null`;
- review status: `not-started`;
- reviewed baseline SHA: `null`;
- all 10 note statuses: `pending`;
- all 131 fact dispositions: `pending`;
- rewritten Summary: exact pre-edit `originalSummary`;
- source definitions: only actual existing definitions referenced by facts;
- manual queue: `[]`;
- generated field: future batch-02 manifest path only;
- no approval, coverage checksum, validation block, generated observation, or
  tranche verification claim.

The terminal `validate-batch --check-source-hashes` gate returned exit `1`
with 233 expected findings. Its stable codes included
`evidence-fact-coverage`, `evidence-source-definition`,
`evidence-unsupported-fact`, `phase2-evidence-schema`,
`phase2-review-sequence`, and `phase2-reviewer-conflict`; therefore the
pending scaffold cannot be mistaken for accepted evidence.

## Predecessor, mutation, and relocation gates

- Production batch-01
  `validate-batch --batch batch-01-anatomy --check-generated` returned `[]`.
- Batch-01 approved artifact byte hashes remained unchanged:
  - baseline:
    `6b05caff4e2cbd618a9c15478f914853701b4be2587af58469b013917d0a7934`;
  - evidence:
    `0225a5e6c7a6fca4d2abe6abe9d73540ef186c064dc5d3b89690d0d74857f70b`;
  - generated manifest:
    `bd1d2be10b9045c17b3f7ff540414623b8ecee4b6f2dd38f576aa3d118fbbbdb`.
- Batch-01 lock trust remains
  `1ba97cdc318b16deaf60cc768dc4b7424f01759287c91e43c85bd6c1601b0b64`;
  generated-observation trust remains
  `7adfa693cf5a178e1a393c250b1322f4e7ea4de990fdac16c0afae26f6f9cefd`.
- Existing no-write attack
  `test_phase2_later_workflow_requires_generated_predecessor_before_write`
  passed for both a missing and wrong batch-01 generated seal. Each stopped
  later workflow with `phase2-review-sequence` and zero byte/mtime drift.
- Baseline creation remained deterministic when the generated-observation
  registry was missing or wrong; the generated prerequisite applies only to a
  later writing workflow.
- Missing, extra, duplicate, or reordered batch-02 notes were rejected.
- Duplicate, missing, or reordered fact units and renumbered coverage loss
  were rejected.
- Blank/ungrounded fact text and malformed, duplicate, or undefined refs were
  rejected with `phase2-baseline-schema`.
- Missing, wrong, extra, unknown, or noncontiguous trust registries failed
  closed with `phase2-trusted-batch-lock-mismatch`.
- A coordinated mutation of source bytes, inventory hash, regenerated
  assignment, lock hash/digest reference, and evidence lock reference produced
  exactly `phase2-trusted-batch-lock-mismatch`.
- Canonical and coherent relocated checkout validation both returned no
  baseline/source findings.

## Verification gates

- Production `validate-baseline --batch batch-02-disease`: exit 0, `[]`.
- Production assignment: 216 total, 10 Phase 1 pilots, 206 non-pilots, 30
  Phase 2A active, 176 scheduled; findings `[]`.
- Production inventory check: 216 NR notes, 0 duplicates, 0 unclassified, 10
  batch-00, 0 unassigned; findings `[]`.
- Task 3.1 targeted GREEN: 10/10 passed.
- Complete audit/build pytest: `145 passed in 113.69s`.
- Direct Phase 1 audit smoke: `NR_SUMMARY_AUDIT_OK`.
- Direct Phase 1 build smoke: `BUILD_CONCEPTS_TEST_OK`.
- Four-file `py_compile`: exit 0.
- Spectra strict validation: valid.
- Spectra artifact analysis: 0 Critical, 0 Warning; two pre-existing
  Suggestion-only ambiguities remain.
- `git diff --check`: exit 0.
- Scope diff from `bd6de34` for `vault/concepts`, `data/concepts`,
  `data/concepts-index.json`, inventory, assignment, every batch-01 artifact,
  and the Task 3.1 checkbox: exit 0.
- All ten disease concept SHA-256 values after artifact generation equal the
  pre-edit literals above.
- Baseline directory contains only batch-01 and batch-02; evidence directory
  contains only batch-01 and batch-02; generated directory contains only
  batch-01. No batch-03 or scheduled artifact exists.

## Changed files

- `scripts/nr_summary_audit.py`
- `scripts/test_nr_summary_audit.py`
- `docs/reports/nr-summary-rewrite/phase2a/baselines/batch-02-disease.json`
- `docs/reports/nr-summary-rewrite/phase2a/evidence/batch-02-disease.json`
- `tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-3-1-report.md`

## Concerns

- Five locked source facts have no applicable original footnote. Task 3.2
  must retain them in a derived research/manual queue or use the permitted
  exception-only `radiology-topic-research` workflow; it must not mark them
  covered from the baseline text alone.
- The source-exact deterministic split is mechanically complete, but semantic
  granularity remains an independent-review responsibility. Exact
  `sourceStatement` values and the table above provide the audit trail.
- Spectra still reports two unrelated Suggestion-level ambiguities for later
  Summary grammar/research scenarios. They are not Critical or Warning.
- Git emits a managed-sandbox warning that the user-level
  `C:\Users\jai16\.config\git\ignore` cannot be read. Repository status, diff,
  and check commands still succeed.
