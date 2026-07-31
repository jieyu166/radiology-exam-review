# Task 2.3 independent task-level verification

## Verdict

`CHANGES_REQUESTED`

- Reviewed commit: `4431cd9f6e3e3d00fba979dad0d323240d38c5b6`
- Review base: `bb8356a`
- Reviewer: `/root/phase2a_task2_3_verification`
- Critical: 0
- Important: 1
- Suggestion: 0
- Production files edited by this reviewer: none

The checked `batch-01-anatomy` evidence, generated manifest, and code-owned
observation seal are internally correct. However, the generated workflow does
not enforce that the immediately preceding batch has a valid generated
observation before a later batch writes. This violates the binding sequential
acceptance gate and must be fixed before Task 2.3 is marked complete.

## Important finding

### Important 1 — a later batch can write before its predecessor has any generated manifest or seal

The design requires that batch N+1 cannot begin until batch N is approved and
its acceptance gate succeeds (`design.md:225-231`). A later generated-tree
change is authorized only when the earlier chain includes valid baseline,
evidence, independent approval, generated-observation seal, and selected
detail hash (`design.md:274-283`; `concept-web-build/spec.md:81-88`).

The implementation does not enforce that invariant before writes:

- `run_phase2_generated_observation_workflow()` calls
  `validate_phase2_batch(..., check_generated=False)` at
  `scripts/nr_summary_audit.py:2469-2477`, then proceeds to the first scoped
  build at lines 2481-2488.
- The predecessor branch inside `validate_phase2_batch()` also validates the
  predecessor with `check_generated=False` at
  `scripts/nr_summary_audit.py:2938-2959`.
- The new continuous-prefix registry check exists only inside
  `_validate_phase2_own_generated_result()` at
  `scripts/nr_summary_audit.py:2215-2247`, which is reached only when the
  caller requests `check_generated=True` at lines 2999-3003.

Independent attack:

1. Create the repository's coherent approved three-batch fixture.
2. Install the valid code-owned baseline-lock digests.
3. Set `TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256 = {}`.
4. Confirm that no `batch-01-anatomy` generated manifest exists.
5. Call
   `run_phase2_generated_observation_workflow(root, "batch-02-disease")`.

Observed result:

```text
workflow_succeeded_without_batch1_seal = True
batch1_manifest_exists = False
```

The call changed bytes and mtimes for all ten batch-02 selected details plus
`data/concepts-index.json` (11 paths). It did not fail before writes.

The production regression fixture itself exposes the same assumption:
`prepare_phase2_later_update_fixture()` runs batch-02 and batch-03 workflows
before it creates the batch-01 manifest
(`scripts/test_nr_summary_audit.py:805-839`). Consequently the new 472-line
regression addition does not cover the binding predecessor-before-write gate.

Why Important:

- Current batch-01 bytes are not corrupted.
- But Task 2.3 is the gate that is supposed to make batch-01 acceptance a
  prerequisite for batch-02. The current API permits precisely the out-of-order
  production write that the Spectra change rejects.

Minimal correction:

1. Before any later-batch build, load its immediate predecessor and require
   `validate_phase2_batch(predecessor, check_source_hashes=False,
   check_generated=True)` to have no errors. This must run before the first
   snapshot/build write.
2. Add a regression with valid approved later-batch evidence but missing,
   wrong, and untrusted predecessor generated observations; assert the stable
   sequencing/generated failure and exact zero byte/mtime delta.
3. Retain the normal continuous-prefix cases
   `{batch-01}`, `{batch-01,batch-02}`, and
   `{batch-01,batch-02,batch-03}` and the skipped-prefix rejection.

## Confirmed-correct current batch state

### Genuine reviewer identity and approval

- Collaboration runtime contains the completed task
  `/root/phase2a_task2_3_review`.
- Evidence implementer is `/root/phase2a_task2_2_impl`.
- Both IDs are canonical and distinct.
- `reviewStatus=approved`.
- `reviewedBaselineSha256` equals the trusted baseline digest
  `1ba97cdc318b16deaf60cc768dc4b7424f01759287c91e43c85bd6c1601b0b64`.
- The Task 2.2 implementer and recorded workflow reviewer are therefore
  genuine distinct tasks; this task-level verifier is a third distinct task.

### Evidence and queue

- Root: `needs-review`.
- Notes: 9 `verified`, one `research-needed`.
- Facts: 121 total = 120 `covered` + one `research-needed`.
- `newUnsupportedFacts=0`.
- Derived queue contains only
  `brain-herniation-syndromes-f03`.
- That fact has `sourceRefs=[]`, remains absent from the rewritten Summary,
  and is not counted as covered.
- The three prior Task 2.2 Important findings have recorded independent
  `ADDRESSED` review, and the focused production regressions preserve their
  restored qualifiers.

### Generated observation and corpus

Independent canonical rerun returned:

- observation digest
  `7adfa693cf5a178e1a393c250b1322f4e7ea4de990fdac16c0afae26f6f9cefd`;
- exact equality with the sole code-owned
  `batch-01-anatomy` registry entry;
- byte-identical regenerated manifest;
- zero pre/post generated bytes and mtime drift;
- checked first run: zero byte and mtime delta;
- checked second run: zero byte and mtime delta;
- 10 selected slugs and 10 selected detail hashes;
- 968 nonselected hashes before and after, exactly equal to current;
- 978 detail files and 978 index entries;
- 11 exact allowed writes;
- zero selected detail-hash mismatch;
- 10/10 generated `keyPoints` equal current Summary bullets.

The manifest contains no self-declared observation digest or trust value. Its
canonical observation projection is authenticated only by the code-owned
registry.

## Independent gates

| Gate | Result |
|---|---|
| Canonical `validate-batch --check-generated` | PASS, exit 0, `[]` |
| Strict `validate-note` | PASS, 10/10 |
| Real unchanged-input two-run rerun | PASS, byte/mtime/Git zero drift |
| Canonical observation digest | PASS, equals sole code-owned seal |
| Selected/nonselected/count/index/keyPoints parity | PASS |
| Focused Task 2.3 production regressions | PASS, 17/17 |
| Relocated checkout regression | PASS within focused suite |
| Missing/wrong/extra trust attacks | PASS within focused suite |
| Selected detail/keyPoints attack | PASS within focused suite |
| Nonselected byte/mtime attacks | PASS within focused suite |
| Coordinated evidence/detail/manifest attack | PASS within focused suite |
| Second-run byte/mtime attacks | PASS within focused suite |
| Exact full lint | PASS baseline: 2 named errors / 124 warnings |
| Four-file `py_compile` | PASS |
| `git diff --check` | PASS |
| Task 2.3 changed-file scope | PASS |
| Later-batch predecessor-seal-before-write attack | **FAIL — Important 1** |

The independent full pytest rerun was stopped at the controller's request
after progressing beyond 53% with no observed failure. The completed focused
17-test suite exercises every Task 2.3 production regression; the implementer
report records 135/135 for its full run, but this review does not present that
full result as independently reproduced.

## Scope audit

Relative to `bb8356a`, commit `4431cd9` changes only:

1. batch-01 evidence review metadata;
2. the new batch-01 generated manifest;
3. the single generated-observation registry seal and first-run mtime/write
   enforcement;
4. focused validator regressions;
5. the Task 2.3 implementation report.

It does not change concept Markdown, selected or nonselected detail JSON,
`data/concepts-index.json`, inventory, assignment, baseline, Phase 1,
batch-02/batch-03 artifacts, Spectra task checkboxes, or Phase 2B work.

## Re-review requirement

Fix Important 1, add the predecessor-seal-before-write regression, then rerun:

1. the new missing/wrong predecessor attacks with byte/mtime snapshots;
2. the 17 focused production regressions;
3. canonical and relocated `validate-batch --check-generated`;
4. current genuine workflow/digest parity;
5. lint baseline and `git diff --check`.

No content rewrite or medical-source change is requested.
