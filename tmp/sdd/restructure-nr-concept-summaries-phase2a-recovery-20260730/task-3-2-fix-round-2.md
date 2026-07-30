# Task 3.2 review round 2 fix

## Result

`DONE_WITH_CONCERNS`

The single Important finding in `review-task-3-2-round-2.md` is fixed. No
production anchor, evidence checksum, generated JSON, or medical-content file
changed.

## Finding closure

`_phase2_coverage_anchor_is_valid()` now derives the strict bullet prefix from
`VALID_BULLET_RE` and evaluates every exact occurrence of the quote. An anchor
is accepted only when at least one occurrence overlaps eight or more
non-whitespace characters in the medical body after the bold label and colon.
Characters inside rendered Obsidian footnote references do not count toward
that body intersection.

This retains the existing requirements for:

- exact `bulletIndex` / `quote` schema;
- one-based integer index with Boolean rejection;
- trimmed quote and minimum quote length;
- exact substring matching;
- complete source-reference rendering;
- nonempty, duplicate-free per-fact anchor arrays;
- Batch01 legacy evidence without anchors.

Quotes may include the label and body, but the label cannot subsidize the
eight-character medical-body requirement. When the same plain text occurs in
both label and body, any exact occurrence that independently satisfies the
body requirement is accepted.

## TDD evidence

The initial production attack changed 2HG f06 coverage to:

```json
{"bulletIndex": 4, "quote": "**IDH-mutant 腫瘤**"}
```

and recomputed `coverageEvidenceSha256`. Before the fix, full Batch02
validation returned only `phase2-review-sequence`; the new test failed because
`evidence-fact-coverage` was absent.

A second RED case demonstrated that `**ABCDEFGH**：A` still passed when the
minimum length applied to the whole quote. The final implementation applies
the minimum to the medical-body intersection instead:

- `**ABCDEFGH**` — rejected;
- `**ABCDEFGH**：A` — rejected;
- plain body `ABCDEFGH` — accepted;
- `**ABCDEFGH**：ABCDEFGH` — accepted;
- footnote-only `[^1][^3]` — rejected.

The checksum-reseal production attack now emits `evidence-fact-coverage`.

## Verification

| Gate | Result |
|---|---|
| Focused round-2 regressions | PASS: 6 |
| Forged long-label checksum-reseal attack | PASS |
| Forged locked-clause deletion attack | PASS |
| Coverage schema positive/negative cases | PASS |
| Batch01 legacy deterministic evidence | PASS |
| Batch02 deterministic evidence and semantic fidelity | PASS |
| Strict disease notes | PASS: 10/10 exact `[]` |
| Full audit/build pytest | PASS: `158 passed in 111.96s` |
| Batch02 base validation | Exactly expected `phase2-review-sequence` |
| Four-file `py_compile` | PASS |
| Spectra strict validation | PASS |
| `git diff --check` | PASS |

## Scope

Changed:

- `scripts/nr_summary_audit.py`;
- `scripts/test_nr_summary_audit.py`;
- round-2 independent review and this fix report.

Unchanged:

- all 131 production anchors;
- Batch02 evidence and its checksums;
- all vault concept Markdown;
- all generated concept JSON and indexes;
- baseline locks, trust digests, assignment, inventory, Batch01 and Batch03
  artifacts, task checkbox, and scheduled notes.

## Remaining concerns

1. ALD f30 and f33 remain explicitly `research-needed`; this fix does not
   reinterpret them as covered.
2. A different reviewer must confirm this round-2 schema correction and
   complete Task 3.3 before Batch02 approval or Batch03 work.
