# Task 4.2 implementation report — batch-03 pattern Summary rewrite

## Outcome

- Status: `DONE_WITH_CONCERNS`
- Approved Task 4.1 base: `abfcac6`
- Implementation dispatch HEAD: `89fa3d8`
- Batch: `batch-03-pattern`
- Implementer: `/root/phase2a_task4_2_impl`
- Intended independent reviewer: `/root/phase2a_task4_3_review`
- Task 4.2 checkbox was not changed.
- Task 4.3 approval, generated manifest, and generated-observation seal were
  not created or claimed.
- No scheduled note or Phase 2B artifact was started.

The ten pattern/DDx summaries now use sourced bold-label short bullets. The
approved lock remains immutable at 69 accepted source statements and 94 stable
facts. Final pre-review dispositions are 91 `covered` and three
`research-needed`; every note has `newUnsupportedFacts=0`.

## TDD evidence

Production tests were added before production edits.

- Pre-edit hash gate: all ten current source SHA-256 values exactly matched
  their approved Batch 03 lock.
- Initial focused RED: `4 failed, 162 deselected`.
  - final dispositions were still pending;
  - the zero-fact note had no accepted canonical Summary;
  - final evidence and anchors did not yet exist;
  - workflow still named the Task 4.1 implementer and no Task 4.3 reviewer.
- Focused GREEN: `4 passed, 162 deselected in 0.46s`.
- The first complete regression run then exposed 14 state-transition failures:
  `14 failed, 165 passed in 198.76s`. These were not waived or relabeled.
  The implementation was corrected so Task 4.1 tests reconstruct an
  authenticated pre-edit shadow, inventory accepts only the exact Batch 03
  empty-projection migration, and Batch 01/02 tests distinguish their own
  reviewed generated state from the intentionally unsealed later Batch 03
  chain. The second complete run passed:
  `180 passed in 230.44s` (exit `0`, empty stderr).
- The expanded Task 4.2 focused set, including narrow exception and inventory
  authentication attacks, passed `5/5`; the complete affected regression set
  passed `15/15`.

The regressions bind:

- all 94 immutable fact IDs/order and exact final dispositions;
- clause-level medical-body coverage anchors for all covered facts;
- strict bold-label bullets with defined inline Obsidian refs;
- omission and derived queueing of all unsupported CNS compound claims;
- the exact empty-projection migration and its source definitions;
- rejection of invented zero-lock fact IDs and mismatched source definitions;
- `newUnsupportedFacts=0`;
- exact byte reconstruction outside allowed Summary edits/addition;
- pre-review workflow with no Task 4.3 approval or generated seal.

## Per-note rewrite and coverage

| Slug | Locked statements | Rewritten bullets | Facts | Covered | Research-needed | Source definitions |
|---|---:|---:|---:|---:|---:|---:|
| `brain-tumor-imaging` | 5 | 5 | 7 | 7 | 0 | 1 |
| `cerebral-infarction-fogging` | 5 | 5 | 5 | 5 | 0 | 1 |
| `cerebral-microbleeds` | 8 | 6 | 11 | 11 | 0 | 3 |
| `cerebrovascular-malformations` | 0 | 3 | 0 | 0 | 0 | 3 |
| `chemical-shift-artifact` | 19 | 19 | 34 | 34 | 0 | 5 |
| `cns-opportunistic-infection` | 5 | 2 | 7 | 4 | 3 | 2 |
| `cranial-nerve-muscle-atrophy` | 4 | 4 | 6 | 6 | 0 | 2 |
| `dural-based-masses-aids` | 6 | 5 | 7 | 7 | 0 | 1 |
| `facial-fracture-complications` | 14 | 4 | 14 | 14 | 0 | 1 |
| `gbm-vs-pcnsl` | 3 | 3 | 3 | 3 | 0 | 1 |
| **Total** | **69** | **56** | **94** | **91** | **3** | — |

Every covered fact has one deterministic source-order, clause-level anchor in
the correct current bullet. Every retained source ref is rendered inline and
has an exact rendered `sourceDefinitions` entry.

### High-risk relationship preservation

- Fogging retains CT 2–3 weeks, MRI T2 6–36 days/median 10 days, approximately
  50%, contrast delineation, and all three negative timing/mimic clauses.
- Microbleed distribution keeps CAA lobar/posterior/deep-sparing separate from
  hypertensive deep distribution, DAI, Zabramski IV cavernoma, and other
  mimics/noncauses.
- Chemical shift retains 3.5 ppm, 1.5T/3T frequencies, 32 kHz/256/125 Hz and
  1.8-pixel example, first-vs-second-type directionality, in/opposed-phase
  distinctions, pure-fat and hemosiderosis reversals, Dixon pitfalls, and the
  2016-092 exam polarity.
- Cranial-nerve denervation retains the complete motor/sensory nerve lists and
  acute `<1 month` → subacute `1–20 months` → chronic `>20 months` ordering.
- Facial fracture complications remain governed by SOF/orbital apex/V2/V3
  location before nerve and symptom consequences.
- GBM-vs-PCNSL retains the direction `PCNSL ADC < GBM` and does not reverse the
  governing subject of morphology or incidence.

## Exact empty-projection migration

`cerebrovascular-malformations` retains its approved exact empty lock:

```text
summaryHeadings=[]
originalSummary=""
factUnits=[]
```

Its three existing parenthesized legacy `## Summary（...）` sections and every
other original byte remain unchanged. One accepted canonical `## Summary` was
inserted with exactly three direct source-backed bullets:

1. AV-shunting classification from `[^1]`;
2. DAVF transverse/sigmoid site from `[^2]`;
3. Pial AVF 1.6%, higher hemorrhage risk with the original symptomatic-
   hemorrhage qualifier, no nidus, and possible small/low-flow spontaneous
   occlusion from `[^3]`.

The evidence derives refs `1,2,3` from those actual bullets and reproduces
their rendered definitions. It does not invent fact IDs or claim locked-fact
coverage. Removing the inserted accepted Summary reconstructs the exact
locked full-file SHA-256. Tests reject an invented fact and a resealed
mismatched definition; the builder rejects absent/undefined/unsourced bullets
and any non-exact empty lock.

## Exception-only source decisions

No external literature search, authentication, credential handling, access
control bypass, or restricted PDF download was needed.

Evidence was generated only after the user-approved write step. The
repo-local `task4_2_build_evidence.py` is dry-run by default, performs no
network or subprocess work, and permits `--write-evidence` only when the
approved pending-scaffold SHA-256 is exact. A subagent Python usage limit was
not bypassed; the controller executed the reviewed, bounded script after
approval.

### Existing source resolved the dural nested facts

The rendered Tier-1 `[^1]` citation in `dural-based-masses-aids` explicitly
lists the complete tumor, granulomatous, and lymphoproliferative categories.
Therefore f04/f05/f06 receive an auditable new mapping to existing rendered
ref `1` and remain in the Summary with clause-level anchors.

### Derived unresolved CNS queue

```text
cns-opportunistic-infection-f03
cns-opportunistic-infection-f06
cns-opportunistic-infection-f07
```

- f03 originally points to `[^1]`, but that rendered source covers cerebral
  abscess DWI and does not support the CNS fungal/opportunistic-host claim.
- f06 has no original source ref for the complete 2016-184 answer-D claim.
- f07 combines DWI, fungal host, toxoplasmosis, and answer D; refs `[^1][^2]`
  do not support the fungal component or the complete exam-answer conclusion.

All three facts are absent from the rewritten Summary, have `sourceRefs=[]`,
`coverage=null`, and `disposition=research-needed`. Only the CNS opportunistic
infection note is `research-needed`; the other nine notes remain `verified`.
The batch root is honestly `needs-review`.

## Evidence and validation

- Evidence SHA-256:
  `de931f6fcbdf35ca9f455b024c6d6ea5b8ac7b0f08ca0d187395bc7087c94b8c`.
- Trusted baseline file SHA-256 remains:
  `2c4de39b3d410f33009fb0613faeaa8d112080e4e5dcdbbcbae8e6b58fe2a3ae`.
- Final dispositions: 94 = 91 covered + 3 research-needed.
- Workflow remains:
  - sequence `3`;
  - predecessor `batch-02-disease`;
  - implementer `/root/phase2a_task4_2_impl`;
  - reviewer `/root/phase2a_task4_3_review`;
  - `reviewStatus=not-started`;
  - `reviewedBaselineSha256=null`.
- Batch03 pre-review validator has exactly one expected finding:
  `phase2-review-sequence`.
- There are no content, source-definition, structure, footnote, coverage,
  unsupported-fact, membership, predecessor, manual-queue, or
  empty-projection integrity findings.

## Byte scope and generated output

For the nine ordinary notes, replacing the current accepted Summary with the
locked `originalSummary` reconstructs the exact locked full-file SHA-256. For
the empty-projection note, removing only the inserted canonical Summary does
the same. Thus all bytes outside the allowed Summary replacement/addition are
unchanged.

The scoped build selected exactly the ten assignment slugs.

- First run: 10 selected; 10 writes, all ten selected detail JSON files.
- `data/concepts-index.json` was already coherent and was neither changed nor
  touched; its SHA-256 remains
  `ae01c3105477a18c170238df777eed62556fdc199b80a60256d00a9cb3d9e35f`.
- Second identical scoped build: 0 writes.
- Nonselected 970 detail files retained the exact combined bytes+mtime digest
  before and after both runs:
  `4299f68697ee8bb443c689d4c1ee45119edfbe25bb7334164929f0bb6f876a92`.
- Current corpus is coherent: 980 unique detail files = 980 unique index
  entries, with zero missing or orphan entries.
- All ten selected generated `keyPoints` arrays equal all current accepted
  Summary bullets in source order (per-note counts
  `5,5,6,3,19,2,4,5,4,3`).
- No Batch03 generated manifest was created in Task 4.2.
- A scoped-build attempt using a Windows-backslash batch-file value was
  rejected before writes by the repo-relative POSIX path contract. The same
  explicit path expressed in POSIX form succeeded. This safe failure was not
  worked around by weakening path validation.

Until Task 4.3 independently reviews and seals the Batch03 generated
observation, Batch01 and Batch02 terminal `--check-generated` validation each
have exactly one expected fail-closed `generated-manifest-mismatch`:
`Complete contiguous generated-observation chain is invalid.` This is the
same pre-seal trust state established by Task 3.2. Task 4.2 did not weaken the
validator or create a premature seal; Task 4.3 must restore the contiguous
terminal chain.

## Gates

| Gate | Result |
|---|---|
| Pre-edit Batch03 hashes | PASS: 10/10 matched approved lock |
| Strict notes | PASS: 10/10 exact `[]` |
| Assignment | PASS: 216/10/206/30/176, exact `[]` |
| Focused Task4.2 tests | PASS: 5/5 |
| Complete affected regressions | PASS: 15/15 |
| Deterministic evidence | PASS |
| Fact dispositions | PASS: 94 total, 91 covered, 3 research-needed |
| Unsupported facts | PASS: 0 |
| Content/source/footnote/manual queue | PASS |
| Empty-projection attacks | PASS |
| Batch03 pre-review validation | Expected single `phase2-review-sequence` |
| Scoped build | PASS: selected ten only |
| Second scoped build | PASS: zero writes |
| Nonselected detail bytes/mtime | PASS: exact pre/post digest |
| Generated keyPoints | PASS: 10/10 |
| Corpus coherence | PASS: 980 details = 980 index entries |
| Complete audit/build pytest | PASS: 180 in 230.44s |
| Direct audit smoke | PASS: `NR_SUMMARY_AUDIT_OK` |
| Direct build smoke | PASS: `BUILD_CONCEPTS_TEST_OK` |
| Four-file `py_compile` | PASS: `PY_COMPILE_OK` |
| Latest scoped build | PASS: 0 writes, 980-detail corpus |
| Full lint | Exact inherited 2 errors / 124 warnings |
| Spectra strict validation | PASS |
| Spectra analyze | 0 Critical, 0 Warning, 2 pre-existing Suggestions |
| `git diff --check` | PASS |
| Task4.3/scheduled artifacts | PASS: absent/unchanged |

Full lint remained:

```text
[footnote 未定義] ceap-classification.md 用了 [^*] 但無定義
[json 殘留 ![[...]]] 2022-264
小結：2 errors, 124 warnings
```

Neither inherited error belongs to a selected Batch 03 note or generated
detail.

## Changed files

Production content:

- ten selected `vault/concepts/<slug>.md` Summary spans/addition;
- ten selected `data/concepts/<slug>.json` detail files;
- `docs/reports/nr-summary-rewrite/phase2a/evidence/batch-03-pattern.json`.

Contract enforcement and tests:

- `scripts/nr_summary_audit.py`;
- `scripts/test_nr_summary_audit.py`;
- `tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task4_2_build_evidence.py`.

Report:

- `tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-4-2-report.md`.

No baseline, trusted digest, inventory, assignment, Batch01/02 artifact,
Phase1 artifact, task checkbox, generated manifest, final review record, index,
nonselected source/detail, or scheduled note was changed.

## Concerns for independent review

1. CNS f03/f06/f07 remain legitimately unresolved because existing rendered
   refs do not support the complete compound fungal/exam-answer claims.
2. Dural f04/f05/f06 use the existing rendered Tier-1 `[^1]` citation as a new
   source mapping; the reviewer should confirm its complete category lists.
3. Task 4.3 must independently inspect all 94 facts, seal the genuine two-run
   generated observation, and restore the contiguous Batch01/02/03 generated
   trust chain.
