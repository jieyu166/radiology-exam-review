# Task 3.3 implementation brief — batch-02 final review and generated seal

## Binding role and task

Implement only Spectra Task 3.3 for `batch-02-disease`, starting from
`d9c96f6`.

This subagent is the actual independent batch reviewer that must be recorded
in the evidence workflow:

`/root/phase2a_task3_3_review`

The Task 3.2 implementer is `/root/phase2a_task3_2_impl`; the identities must
remain distinct. Read the complete change design/spec/tasks, approved baseline,
all Task 3.1/3.2 implementation and fix reports, all Task 3.1/3.2 independent
review reports, the coverage-anchor audit, and the current checked artifacts
before acting.

Do not mark the Spectra checkbox. The controller will obtain a second,
independent task-level verification after this batch reviewer commits.

## Independent content and coverage review gate

Before approval, independently recheck:

- exact trusted baseline digest and ordered 10-note membership;
- all 98 locked fact IDs/order/text and applicable source refs/definitions;
- 96 covered facts preserve subject, relationship, polarity, qualifiers,
  numbers, versions, negations, exceptions, order, comparisons, and DDx;
- ALD f30/f33 remain absent from Summary, `research-needed`,
  `sourceRefs=[]`, `coverage=null`, and are the only derived queue items;
- all 131 coverage anchors are valid clause-level medical-body evidence, not
  labels, footnotes, or generic fragments; multi-anchor facts collectively
  support every component;
- Aicardi triad and ALD Schaumburg center-to-outside parent/child contexts
  remain exact;
- all Task 3.2 round-1/round-2 Important findings remain closed;
- 10/10 Summary spans use bold labels, short top-level bullets, sourced
  disease axes only, and defined Obsidian footnotes;
- `newUnsupportedFacts=0`;
- bytes outside the ten accepted Summary spans reconstruct the locked hashes;
- generated `keyPoints` equal all current Summary bullets.

Re-run the forged deleted-clause, label-only, long-label-plus-one-body-character,
source-incomplete, stale-index, duplicate-anchor, and unresolved-coverage
attacks.

If any Critical or Important content/source/coverage finding remains, do not
approve evidence and do not seal generated observation. Record
`changes-requested`, report exact facts, and return BLOCKED.

## Evidence approval

Only after the independent review is clean, update
`docs/reports/nr-summary-rewrite/phase2a/evidence/batch-02-disease.json`:

- retain root `status=needs-review`;
- retain exactly 96 covered + two research-needed facts, 131 anchors, two null
  coverage values, and the two-item derived queue;
- retain implementer `/root/phase2a_task3_2_impl`;
- set reviewer `/root/phase2a_task3_3_review`;
- set `reviewStatus=approved`;
- set `reviewedBaselineSha256` to the canonical trusted Batch 02 baseline
  digest;
- do not convert ALD f30/f33 or their note to verified;
- do not change note-local `coverageEvidenceSha256` unless the schema truly
  binds workflow metadata;
- do not claim tranche acceptance or start Batch 03.

## Genuine generated observation

Use the audited
`run_phase2_generated_observation_workflow(repo_root, "batch-02-disease")`.
Do not hand-author or self-attest the manifest.

The workflow must:

1. fail before writes unless assignment, contiguous trusted baselines,
   predecessor approval/seal, current evidence/content, reviewer approval, and
   derived queue all pass;
2. snapshot the complete current generated tree and index;
3. run the exact selected build twice;
4. prove nonselected detail hashes unchanged;
5. record actual first/second-run byte and mtime deltas;
6. build a coherent 980-detail/980-index manifest.

Task 3.2 already synchronized the selected details. A genuine first run may
therefore be zero-delta. Record the actual observation; do not fabricate prior
writes or force a file to change.

Create:

`docs/reports/nr-summary-rewrite/phase2a/generated/batch-02-disease.json`

Seal its canonical generated-observation projection by adding exactly one
code-owned entry for `batch-02-disease` to
`TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256`.

Preserve the existing Batch 01 seal byte-for-byte. Do not add Batch 03,
per-note constants, or a mutable JSON trust registry.

## TDD and attacks

Before production approval/seal, add RED production regressions for at least:

1. unapproved, same-identity, wrong-baseline, or unresolved-queue-forged review
   cannot start the workflow;
2. missing/wrong/extra or noncontiguous generated-observation trust fails;
3. Batch 02 cannot be trusted without the exact approved/sealed Batch 01
   predecessor;
4. coordinated manifest/evidence/detail mutation cannot bypass the code-owned
   digest;
5. selected keyPoints/detail or nonselected detail byte/mtime mutation fails;
6. second-run byte/mtime drift fails;
7. canonical and coherent relocated checkout paths validate the same;
8. ALD f30/f33 remain accepted only as derived `needs-review`, never verified;
9. both Batch 01 and Batch 02 terminal `validate-batch --check-generated`
   return exact `[]` only after the new seal exists.

Use stable finding codes. Do not weaken chain, evidence, coverage, or
generated-output validation to make the manifest pass.

## Required gates

- Batch 01 and Batch 02 final `validate-batch --check-generated` each return
  exact `[]`, exit 0;
- reviewer differs from implementer and reviewed digest equals trusted lock;
- root is `needs-review`, nine notes verified, ALD research-needed, queue
  exactly f30/f33;
- 10/10 strict note validation;
- 98 facts = 96 covered + 2 research-needed; 131 valid anchors; unsupported 0;
- manifest has exact selected slugs/detail hashes, 980 detail files, 980 index
  entries, coherent tree/index, exact allowed writes, and actual deltas;
- rerunning the workflow is byte-identical with zero byte/mtime/Git drift;
- trust/predecessor/coverage/selected/nonselected/coordinated/second-run
  attacks fail with stable codes;
- full lint remains exactly the two named inherited errors and 124 warnings,
  with no selected-note error;
- full audit/build pytest, direct Phase 1 smokes, four-file `py_compile`,
  inventory/assignment/baselines, Spectra strict/analyze, and
  `git diff --check` pass;
- no concept Markdown, detail JSON, index, inventory, assignment, baseline,
  Batch 01 artifact, Phase 1, Batch 03, or scheduled artifact changes;
- no Phase 2B work starts.

## Report and commit

Write:

`tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-3-3-report.md`

Include:

- independent reviewer identity and content/anchor verdict;
- prior finding closure;
- final evidence state and exact queue;
- two-run snapshots/deltas and observation digest;
- manifest hashes/counts/write scope/keyPoints parity;
- lint summary and named inherited errors;
- attack results and stable codes;
- canonical/relocated parity;
- all test/CLI/Spectra gates;
- changed files and concerns.

Allowed production changes are only:

- Batch 02 evidence workflow approval;
- the new Batch 02 generated manifest;
- one new Batch 02 code-owned observation digest;
- strictly necessary validator/tests;
- the Task 3.3 report.

Make one focused commit and return DONE, DONE_WITH_CONCERNS, or BLOCKED with
the SHA. Do not mark Task 3.3 complete.
