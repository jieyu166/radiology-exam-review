# Independent task review — Task 4.3 `batch-03-pattern`

Commit reviewed: `51c0749` relative to `70ae850`

Reviewer: `/root/phase2a_task4_3_task_review`

Verdict: **APPROVED**

## Findings

- Critical: none.
- Important: none.
- Suggestion: none.

The retained CNS research queue is an intentional, correctly represented
content limitation rather than a review finding.

## Scope review

`git diff --name-status 70ae850 51c0749` contains only:

- approved Batch 03 evidence workflow metadata;
- the new Batch 03 generated observation manifest;
- one Batch 03 code-owned generated-observation digest;
- Task 4.3 transition and attack tests;
- the Task 4.3 implementation report.

There is no concept Markdown, selected or nonselected detail JSON, index,
inventory, assignment, baseline, Batch 01/02 artifact, Phase 1 artifact,
Spectra task checkbox, scheduled-note, or later-phase diff.

`git diff --check 70ae850 51c0749` passed.

## Independent evidence and content checks

I independently enumerated the baseline fact ledger, evidence dispositions,
coverage anchors, rewritten Summary clauses, source definitions, and the
three high-risk content areas.

- Exact fact arithmetic: 94 total = 91 `covered` + 3 `research-needed`.
- Exact coverage arithmetic: 91 nonempty clause-level anchors, with no covered
  fact lacking a source ref or coverage entry.
- Exact unresolved queue:
  - `cns-opportunistic-infection-f03`
  - `cns-opportunistic-infection-f06`
  - `cns-opportunistic-infection-f07`
- Those three entries alone have `sourceRefs=[]`, `coverage=null`, and
  `disposition=research-needed`; they remain absent from the accepted Summary.
- Root remains `needs-review`; nine notes are `verified` and only
  `cns-opportunistic-infection` is `research-needed`.
- Implementer `/root/phase2a_task4_2_impl` and reviewer
  `/root/phase2a_task4_3_review` are canonical and distinct.
- `reviewStatus=approved`, and `reviewedBaselineSha256` exactly equals the
  trusted Batch 03 lock digest
  `3a93bfbe332067f06b5dda7ac47c6484107f52afd152059701f44ea3d7394e98`.

High-risk manual checks passed:

- Dural facts f04/f05/f06 use rendered `[^1]`; its RadioGraphics citation
  explicitly enumerates the complete neoplastic, granulomatous, and
  lymphoproliferative groups used by the Summary.
- The Pial AVF bullet retains 1.6%, higher hemorrhage risk than AVM, the
  smaller symptomatic-hemorrhage proportion qualifier, absent nidus, and
  possible spontaneous occlusion in a small low-flow lesion.
- `cerebrovascular-malformations` remains an authenticated zero-fact migration:
  its lock has no accepted Summary, empty `originalSummary`, and no fact units.
  The current note has exactly one canonical three-bullet `## Summary`, retains
  all three legacy parenthesized Summary sections, and removing the one
  evidence `rewrittenSummary` span reconstructs the exact locked source SHA
  `5a19d890855886093f4525cc9fff0a9748b7d92faa27947a151d1d7ef9d0f280`.

All 94 baseline fact texts were compared with their dispositions and anchors.
The 91 covered mappings preserve the material subject, relationship, polarity,
qualifier, number, timing/version, exception, comparison, and DDx content.

## Generated observation and trust

Independent inspection and a fresh genuine workflow rerun established:

- selected slugs: exact ordered 10 Batch 03 members;
- selected detail entries: 10;
- nonselected detail entries: 970 before and 970 after, identical;
- complete detail count: 980;
- complete index count: 980;
- allowed writes: index plus the exact ten selected detail paths;
- first-run byte delta: `[]`;
- first-run mtime delta: `[]`;
- second-run byte delta: `[]`;
- second-run mtime delta: `[]`;
- detail-tree SHA:
  `5d53aa489719c43f585c0fead74faf484e62fe9c30c6a6b14f1b10378d4f4ad9`;
- index SHA:
  `ae01c3105477a18c170238df777eed62556fdc199b80a60256d00a9cb3d9e35f`;
- canonical observation SHA:
  `fa0bca4f69a2bcc8ee914aac4ce364e86dc260d272e65697b672f0481f49dec9`.

The canonical observation SHA exactly matches the sole Batch 03 entry in the
code-owned trust mapping. The mapping has exactly the three active batches;
the Batch 01/02 values are unchanged.

The fresh workflow rerun returned the same observation SHA and zero deltas.
The checked-in manifest SHA remained
`8de399a3c8a73c01479a2dc2a97a52675ee056312924331c3c8c1fde7b364c6d`,
its mtime remained identical, and Git status remained identical.

## Test-strength review

The test diff contains no `skip`, `xfail`, or disabled test. Historical
post-transition assertions now require exact `[]`, and the trusted registry is
still tested as an exact three-key mapping. Missing, wrong, extra, or
noncontiguous keys fail. Batch 01 and Batch 02 tests continue to bind their own
fixed observation digests rather than accepting arbitrary extra keys.

Focused attack coverage verifies:

- review status, reviewer identity, reviewed baseline, and manual queue forgery
  fail before writes;
- missing/wrong/extra trust and predecessor loss fail closed;
- deleted, label-only, short-fragment, duplicate, incomplete-source, and
  unresolved-as-covered attacks fail;
- relocated checkout parity holds;
- selected keyPoints/detail mutation, coordinated manifest/detail resealing,
  and second-run drift fail with stable findings;
- current and predecessor generated results validate only with the exact
  three-batch chain.

## Fresh verification commands and results

### Tests

```text
python -m pytest scripts/test_nr_summary_audit.py -q -k
  "task43 or batch03_task42 or batch03_preserves_both_approved_predecessors
   or batch01_production_generated_seal_is_genuine
   or batch02_reviewed_generated_seal_and_relocation_are_genuine
   or batch02_generated_registry_and_manual_queue_are_fail_closed"
14 passed, 158 deselected in 80.98s

python -m pytest scripts/test_nr_summary_audit.py
  scripts/test_build_concepts.py -q
185 passed in 264.94s
```

### Terminal batch, assignment, inventory, and strict-note gates

```text
python scripts/nr_summary_audit.py validate-batch ... --batch batch-01-anatomy
  --check-generated
[]
exit 0

python scripts/nr_summary_audit.py validate-batch ... --batch batch-02-disease
  --check-generated
[]
exit 0

python scripts/nr_summary_audit.py validate-batch ... --batch batch-03-pattern
  --check-generated
[]
exit 0

python scripts/nr_summary_audit.py validate-assignment ...
NR total: 216
Phase 1 pilots: 10
Phase 2 non-pilots: 206
Phase 2A active: 30
Scheduled: 176
[]
exit 0

python scripts/nr_summary_audit.py inventory ... --check
NR notes: 216
Duplicate slugs: 0
Unclassified: 0
Batch 00: 10
Unassigned: 0
exit 0

python scripts/nr_summary_audit.py validate-note <each Batch 03 path>
10/10 exact []
```

### Direct, compile, lint, and Spectra gates

```text
python scripts/test_nr_summary_audit.py
NR_SUMMARY_AUDIT_OK

python scripts/test_build_concepts.py
BUILD_CONCEPTS_TEST_OK

python -m py_compile scripts/nr_summary_audit.py
  scripts/test_nr_summary_audit.py scripts/build_concepts.py
  scripts/test_build_concepts.py
exit 0

python scripts/lint_concepts.py --quiet
exact two inherited errors:
  [footnote 未定義] ceap-classification.md 用了 [^*] 但無定義
  [json 殘留 ![[...]]] 2022-264
exact 124 warnings: 65 + 37 + 22
no warning-count delta

spectra validate restructure-nr-concept-summaries-phase2a --strict
valid, exit 0

spectra analyze restructure-nr-concept-summaries-phase2a --json
Coverage clean; Consistency clean; Gaps clean; two inherited nonblocking
Ambiguity Suggestions; no Critical or Warning; exit 0
```

## Final assessment

Commit `51c0749` satisfies Task 4.3's independent-review, honest derived-queue,
genuine two-run observation, narrow-scope, idempotence, predecessor-chain,
relocation, and fail-closed attack contracts. It is ready for the controller
to record Task 4.3 complete.
