# Task 4.1 implementation report — `batch-03-pattern` baseline

Status: **DONE_WITH_CONCERNS**

Implementer: `/root/phase2a_task4_1_impl`

Scope: pre-edit baseline lock and honest pending evidence scaffold only. No
concept Markdown, generated concept JSON/index, assignment, inventory, Batch
01/02 artifact, generated manifest, or Spectra task checkbox was changed.

## Prerequisite and source-state proof

- `batch-01-anatomy validate-batch --check-generated`: exact `[]`.
- `batch-02-disease validate-batch --check-generated`: exact `[]`.
- All ten Batch 03 source SHA-256 values equal their inventory anchors before
  generation.
- All ten locked `originalSummary` values equal the current accepted Summary
  projection byte-for-byte.
- Approved predecessor artifact SHA-256 values remained:
  - Batch 01 baseline `6b05caff4e2cbd618a9c15478f914853701b4be2587af58469b013917d0a7934`
  - Batch 01 evidence `0225a5e6c7a6fca4d2abe6abe9d73540ef186c064dc5d3b89690d0d74857f70b`
  - Batch 01 generated `bd1d2be10b9045c17b3f7ff540414623b8ecee4b6f2dd38f576aa3d118fbbbdb`
  - Batch 02 baseline `334c132f12d60c8f5eb51373a11fe97ea228d14d9c7729ee9953f1972c03e5d9`
  - Batch 02 evidence `0d58513e040e5e5564eb7da983e37c9d0bc8f821a38c75971048796c9c751614`
  - Batch 02 generated `e2f069c345410b018ac33b84fa7bfea98c4d0157e307973bf4d30dc8dea55c0e`

## RED → GREEN

Focused RED:

```text
test_phase2a_batch03_builder_accepts_only_the_exact_empty_summary_projection
1 failed, 151 deselected
ValueError: Fact templates for 'cerebrovascular-malformations'
are not the audited source projection.
```

Cause: `cerebrovascular-malformations` has only
`## Summary（...）` headings, which intentionally do not match the accepted
Summary grammar. Inventory therefore correctly records
`summaryHeadings=[]`; the lossless accepted projection is
`originalSummary=""`, `factUnits=[]`. The builder incorrectly rejected every
empty projection.

Minimal GREEN fix:

- do not expand the accepted Summary heading regex;
- accept an empty fact projection only when the current parser has no accepted
  Summary span and both accepted heading and original Summary projections are
  empty;
- validator accepts only the exact triple
  `summaryHeadings=[]`, `originalSummary=""`, `factUnits=[]`;
- an accepted Summary with zero facts and a forged empty lock hiding a real
  accepted span remain rejected.

Targeted GREEN after the fix:

```text
1 passed, 151 deselected
```

Final Batch 03 focused suite, including production, mutation, pending,
predecessor zero-write, and relocation attacks:

```text
11 passed, 151 deselected
```

## Locked projection

| slug | statements | facts | unique refs | empty-ref facts | definitions |
| --- | ---: | ---: | ---: | ---: | ---: |
| `brain-tumor-imaging` | 5 | 7 | 1 | 0 | 1 |
| `cerebral-infarction-fogging` | 5 | 5 | 1 | 0 | 1 |
| `cerebral-microbleeds` | 8 | 11 | 3 | 0 | 3 |
| `cerebrovascular-malformations` | 0 | 0 | 0 | 0 | 0 |
| `chemical-shift-artifact` | 19 | 34 | 5 | 0 | 5 |
| `cns-opportunistic-infection` | 5 | 7 | 2 | 1 | 2 |
| `cranial-nerve-muscle-atrophy` | 4 | 6 | 2 | 0 | 2 |
| `dural-based-masses-aids` | 6 | 7 | 1 | 3 | 1 |
| `facial-fracture-complications` | 14 | 14 | 1 | 0 | 1 |
| `gbm-vs-pcnsl` | 3 | 3 | 1 | 0 | 1 |
| **Total** | **69** | **94** | — | **4** | — |

Projection boundary review:

- footnote definition lines and their continuations produce no facts;
- ordered and unordered nested children remain in source order;
- semantic parents appear exactly once;
- `cerebral-microbleeds` parent refs are inherited by its nested children;
- the `dural-based-masses-aids` parent retains the union ref while children
  without explicit/enclosing refs remain honestly empty;
- four `facial-fracture-complications` semantic parents and all nested child
  facts are retained;
- callout labels are not facts, while factual callout bodies in
  `brain-tumor-imaging` and `chemical-shift-artifact` are retained;
- no accepted Summary span contains a table in this batch.

The four empty-ref fact IDs are:

- `cns-opportunistic-infection-f06`
- `dural-based-masses-aids-f04`
- `dural-based-masses-aids-f05`
- `dural-based-masses-aids-f06`

## Canonical artifacts and trust

- Baseline bytes SHA-256:
  `2c4de39b3d410f33009fb0613faeaa8d112080e4e5dcdbbcbae8e6b58fe2a3ae`
- Baseline canonical lock SHA-256:
  `3a93bfbe332067f06b5dda7ac47c6484107f52afd152059701f44ea3d7394e98`
- Evidence scaffold bytes SHA-256:
  `2a474f66730af8f541b2fd7024553132b548a3f1d83620fda920022bbf6104c4`
- Builder regeneration is byte-identical to the checked baseline.
- The code-owned trust registry is exactly the active contiguous prefix:
  1. `batch-01-anatomy`
     `1ba97cdc318b16deaf60cc768dc4b7424f01759287c91e43c85bd6c1601b0b64`
  2. `batch-02-disease`
     `3c294b4e098fc971ec6cbc67945cc24620752108f7d31bf3c1ba574ef6fd8fa8`
  3. `batch-03-pattern`
     `3a93bfbe332067f06b5dda7ac47c6484107f52afd152059701f44ea3d7394e98`

## Pending scaffold state

```text
status = baseline
workflow.sequence = 3
workflow.predecessor = batch-02-disease
workflow.implementer = /root/phase2a_task4_1_impl
workflow.reviewer = null
workflow.reviewStatus = not-started
workflow.reviewedBaselineSha256 = null
manualReviewFactIds = []
```

Every evidence note is `pending`; rewritten Summary equals the locked original;
every locked fact is copied with `pending`; only actually referenced rendered
footnote definitions are present. There are no coverage anchors, validation
claims, unsupported-fact claims, approval, generated observation, or tranche
state. The final validator rejects this scaffold with stable content/review
codes including `evidence-fact-coverage`, `phase2-evidence-schema`,
`phase2-review-sequence`, and `phase2-reviewer-conflict`.

## Mutation, sequencing, and relocation attacks

- missing, extra, duplicate, and out-of-order notes fail;
- duplicate/out-of-order facts, malformed refs, and accepted Summary with empty
  facts fail;
- coordinated source/inventory/assignment/lock/evidence replacement fails with
  `phase2-trusted-batch-lock-mismatch`;
- registry missing, gapped, unknown, or wrong-own-digest shapes fail;
- missing Batch 02 baseline and wrong Batch 02 generated seal both fail with
  `phase2-review-sequence` before any generated byte or mtime changes;
- canonical and relocated checkout baseline bytes and validation findings are
  identical.

## Final gates

- Batch 03 `validate-baseline`: exact `[]`.
- Assignment validation: 216 NR, 10 Phase 1, 206 Phase 2 non-pilot, 30 active,
  176 scheduled, exact `[]`.
- Inventory deterministic check: 216 notes, 0 duplicates, 0 unclassified,
  exact `[]`.
- Full tests: `175 passed in 218.43s`.
- Direct smokes: `NR_SUMMARY_AUDIT_OK`,
  `BUILD_CONCEPTS_TEST_OK`.
- Four-file `py_compile`: pass.
- `spectra validate ... --strict`: valid.
- `spectra analyze`: Coverage/Consistency/Gaps clean; two pre-existing
  nonblocking scenario-example suggestions only.
- `git diff --check`: pass.
- No diff under `vault/concepts`, `data/concepts`,
  `data/concepts-index.json`, any Batch 01/02 artifact, or any scheduled
  artifact.

## Concerns handed to Task 4.2

1. `cerebrovascular-malformations` has no accepted Summary span. Its
   parenthesized `## Summary（...）` sections are intentionally outside the
   locked grammar and cannot be claimed as covered in Task 4.2 without a
   separately justified, source-preserving rewrite.
2. The four empty-ref facts above must remain unresolved or receive auditable
   source mapping. Task 4.1 does not infer a citation or mark them covered.

