# Task 4.3 implementation report — `batch-03-pattern` independent review and seal

Status: **DONE_WITH_CONCERNS**

Independent reviewer / seal implementer:
`/root/phase2a_task4_3_review`

Task 4.2 implementer:
`/root/phase2a_task4_2_impl`

The identities are canonical and distinct. This task approved only the Batch
03 review, generated its audited observation, added one code-owned observation
seal, and strengthened transition/attack tests. It did not mark the Spectra
checkbox or start Task 5.

## Independent medical, source, and anchor verdict

Verdict: **APPROVED**. No Critical or Important finding remains.

I independently reviewed all 94 locked fact IDs in source order against their
current Summary clauses, evidence dispositions, source refs, rendered source
definitions, and coverage anchors.

- 94 facts = 91 `covered` + 3 `research-needed`.
- All 91 covered facts retain their governing subject, relationship, polarity,
  qualifier, number/unit, timing/version, exception, ordering, comparison,
  sequence/signal, distribution, clinical context, DDx, and exam-answer
  context.
- All 91 covered facts have nonempty defined source refs and exactly one valid
  clause-level medical-body coverage anchor.
- No anchor is a label, footnote, generic fragment, short fragment, or wrong
  sibling bullet.
- `newUnsupportedFacts=0` for every note.
- All Task 4.2 round-1 findings remain closed; that review had no Critical or
  Important finding.

High-risk findings specifically rechecked:

- `dural-based-masses-aids-f04/f05/f06` use the existing rendered
  RadioGraphics `[^1]`. Its citation explicitly lists the complete neoplastic,
  granulomatous, and lymphoproliferative groups reproduced in the bullets.
- The `cerebrovascular-malformations` trusted empty projection remains
  `summaryHeadings=[]`, `originalSummary=""`, `factUnits=[]`. The migration
  adds no fact ID and inserts only the authenticated three-bullet canonical
  Summary. Removing that Summary reconstructs the trusted original file hash;
  the legacy parenthesized Summary sections remain unchanged.
- The Pial AVF bullet retains both the higher hemorrhage risk than AVM and the
  qualifier that a smaller proportion of PAVF presents with symptomatic
  hemorrhage, plus 1.6%, no nidus, and possible spontaneous occlusion in a
  small low-flow lesion.
- All ten notes pass strict Summary grammar and all current generated
  `keyPoints` equal the accepted Summary bullets in source order. Per-note
  counts are `5,5,6,3,19,2,4,5,4,3`.

## Honest unresolved queue and final evidence state

The root remains `needs-review`. Nine notes are `verified`; only
`cns-opportunistic-infection` is `research-needed`.

The exact derived queue is:

```text
cns-opportunistic-infection-f03
cns-opportunistic-infection-f06
cns-opportunistic-infection-f07
```

All three facts remain absent from the Summary, have `sourceRefs=[]`,
`coverage=null`, and `disposition=research-needed`. Existing refs provide only
partial support and do not support each complete fungal/exam-answer compound
claim. They were not converted to covered or verified.

The evidence workflow is now:

```text
sequence = 3
predecessor = batch-02-disease
implementer = /root/phase2a_task4_2_impl
reviewer = /root/phase2a_task4_3_review
reviewStatus = approved
reviewedBaselineSha256 =
  3a93bfbe332067f06b5dda7ac47c6484107f52afd152059701f44ea3d7394e98
```

Artifact byte SHA-256 values:

- Batch 03 baseline:
  `2c4de39b3d410f33009fb0613faeaa8d112080e4e5dcdbbcbae8e6b58fe2a3ae`
- Approved Batch 03 evidence:
  `b95dc78a6d21fdd01f2584f728f319f592bf3dfa5da4c53d5efbc3e32727885b`
- Batch 03 generated manifest:
  `8de399a3c8a73c01479a2dc2a97a52675ee056312924331c3c8c1fde7b364c6d`

## TDD RED → GREEN

The new Task 4.3 production tests were added before approval/seal.

RED:

```text
4 failed, 167 deselected
```

The failures proved that the evidence was not approved and the Batch 03
manifest/code-owned seal did not yet exist. No build or artifact write occurred
on the failed preflight.

After independent approval and the genuine workflow, the focused suite became:

```text
6 passed, 166 deselected
```

The two additional focused tests cover deleted coverage, label-only coverage,
short fragments, duplicate anchors, source-incomplete evidence, unresolved
coverage forgery, review/identity/baseline/queue forgery, registry shape,
relocation, selected detail mutation, second-run drift, and coordinated
manifest/detail resealing.

Four Task 4.2 historical assertions and five earlier Batch 01/02 transition
assertions were updated from the deliberate pre-seal state to the exact
three-seal production truth. They still verify each predecessor's fixed
manifest digest and require the registry to contain exactly the three active
batches; no extra key or generalized trust was allowed.

All Batch 03 regressions:

```text
20 passed, 151 deselected
```

Complete audit/build suite:

```text
185 passed in 263.19s
```

## Genuine generated observation

The manifest was produced only by:

`run_phase2_generated_observation_workflow(repo_root, "batch-03-pattern")`

It was not hand-authored or self-attested.

- selected slugs: exact ordered 10 Batch 03 members;
- selected detail files: 10;
- nonselected detail files: 970;
- complete detail files: 980;
- complete index entries: 980;
- nonselected before/after maps: identical;
- nonselected canonical digest:
  `9a5622207f87e3770ba60082923946781ab82548464e4e31540df1f2bed1078e`;
- detail tree SHA-256:
  `5d53aa489719c43f585c0fead74faf484e62fe9c30c6a6b14f1b10378d4f4ad9`;
- index SHA-256:
  `ae01c3105477a18c170238df777eed62556fdc199b80a60256d00a9cb3d9e35f`;
- first run byte delta: `[]`;
- first run mtime delta: `[]`;
- second run byte delta: `[]`;
- second run mtime delta: `[]`.

Task 4.2 had already synchronized all ten selected details, so the genuine
first run was correctly zero-delta.

The canonical observation digest is:

`fa0bca4f69a2bcc8ee914aac4ce364e86dc260d272e65697b672f0481f49dec9`

Exactly one Batch 03 entry with this digest was added to
`TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256`. The Batch 01 and Batch 02
values were not changed.

A subsequent full workflow rerun proved:

```text
manifestBytesIdentical = true
manifestMtimeIdentical = true
firstRun.changedPaths = []
firstRun.mtimeChangedPaths = []
secondRun.changedPaths = []
secondRun.mtimeChangedPaths = []
observationSha256 = fa0bca4f...dec9
```

A final direct scoped build also exited 0 without output, followed by three
terminal validations that remained exact `[]`.

## Attack and relocation results

The following attacks fail closed with stable codes:

- unapproved/wrong reviewed baseline:
  `phase2-review-sequence`;
- same implementer/reviewer:
  `phase2-reviewer-conflict`;
- forged queue:
  `phase2-manual-queue-mismatch`;
- deleted, label-only, short, duplicate, or unresolved coverage:
  `evidence-fact-coverage`;
- incomplete/resealed source definition:
  `evidence-source-definition`;
- missing/wrong/extra/noncontiguous observation trust:
  `generated-observation-untrusted` or the terminal chain code
  `generated-manifest-mismatch`, according to which batch owns the invalid
  state;
- selected `keyPoints` mutation:
  `generated-keypoints-mismatch` plus
  `generated-manifest-mismatch`;
- coordinated detail/manifest mutation:
  `generated-observation-untrusted`;
- second-run byte/mtime drift:
  `generated-non-idempotent`;
- nonselected byte/mtime drift:
  `generated-unrelated-write`;
- missing/wrong Batch 01 or Batch 02 predecessor seal:
  `phase2-review-sequence`;
- empty-projection wrong batch/slug/lock, invented fact, extra accepted
  Summary, changed non-Summary byte, and unsourced bullet:
  the existing narrow empty-projection/source/inventory findings.

The complete relocated checkout with all three predecessor/current artifacts
validates identically to canonical. Mutating its selected detail is rejected.

## Final gates

- Three terminal `validate-batch --check-generated` commands:
  exact `[]`, exact `[]`, exact `[]`, all exit 0.
- Pure `validate_baseline_lock` for Batch 01/02/03:
  exact `[]`, exact `[]`, exact `[]`.
- Standalone `validate-baseline` was also probed and, by design, reports
  pre-edit source/hash mismatches after a rewrite. It performs the pre-edit
  gate and is not the post-rewrite terminal command; it wrote nothing. The
  trusted-lock gate and terminal batch gate above are the applicable final
  validations.
- Strict selected notes: 10/10 exact `[]`.
- Assignment: 216 NR, 10 Phase 1, 206 non-pilot, 30 active, 176 scheduled,
  exact `[]`.
- Inventory check: 216 notes, 0 duplicates, 0 unclassified, 10 Batch 00,
  0 unassigned.
- Direct smokes: `NR_SUMMARY_AUDIT_OK`,
  `BUILD_CONCEPTS_TEST_OK`.
- Four-file `py_compile`: exit 0.
- Full lint: exact inherited two errors and 124 warnings:
  - `[footnote 未定義] ceap-classification.md 用了 [^*] 但無定義`;
  - `[json 殘留 ![[...]]] 2022-264`;
  - warnings: 65 missing `correctAnswer`, 37 missing question Dataview,
    22 unreferenced footnotes.
- No warning-count delta and no selected-note lint error.
- Spectra strict validation: valid.
- Spectra analyze: Coverage/Consistency/Gaps clean; exactly two inherited
  nonblocking Ambiguity Suggestions, no Critical or Warning.
- `git diff --check`: clean.

## Scope and predecessor integrity

Approved predecessor artifact byte hashes remain unchanged:

- Batch 01 baseline/evidence/generated:
  `6b05caff...7934`, `0225a5e6...70b`, `bd1d2be1...bdb`;
- Batch 02 baseline/evidence/generated:
  `334c132f...e5d9`, `0d58513e...1614`, `e2f069c3...c0e`.

Production changes are limited to:

- Batch 03 evidence review approval;
- generated Batch 03 manifest;
- one Batch 03 code-owned generated-observation digest;
- Task 4.3 transition/attack tests;
- this report.

There is no diff to any concept Markdown, selected or nonselected detail JSON,
the index, inventory, assignment, baselines, Batch 01/02 artifacts, Phase 1
artifacts, scheduled notes, task checkbox, or later-phase artifact.

## Concern

The three CNS compound claims remain in the honest research queue. This is the
only concern and is intentionally preserved; it does not weaken mechanical,
source-integrity, generated-output, or sequencing acceptance.
