# Independent review — Task 4.2, round 1

Verdict: **APPROVED**

Reviewer: `/root/phase2a_task4_2_review`

Reviewed range: `89fa3d8..b55c195`

This was a read-only review of production code, tests, evidence, source
Markdown, and generated JSON. The reviewer did not participate in Task 4.2
implementation and did not modify or commit any production/test/artifact
file.

## Findings

### Critical

None.

### Important

None.

### Suggestions

None.

## Binding material reviewed

Read in full:

- Task 4.2 implementation brief and report;
- approved Task 4.1 baseline brief/report and round-2 independent review;
- Spectra proposal, design, implementation contract, tasks, and both delta
  specs;
- Obsidian Markdown skill;
- radiology-topic-research skill;
- Batch 03 baseline and current evidence;
- all ten source Markdown diffs and all ten selected generated JSON diffs;
- complete Task 4.2 production-code diff, evidence builder, and affected test
  changes.

## Medical and fact/source review

The approved lock remains 69 source statements and 94 immutable fact units.
I reviewed every locked fact against the rewritten Summary, evidence
disposition, sourceRefs, clause-level coverage anchor, governing medical
subject, and source definition.

Observed terminal content projection:

| slug | facts | covered | research-needed | rewritten bullets |
| --- | ---: | ---: | ---: | ---: |
| `brain-tumor-imaging` | 7 | 7 | 0 | 5 |
| `cerebral-infarction-fogging` | 5 | 5 | 0 | 5 |
| `cerebral-microbleeds` | 11 | 11 | 0 | 6 |
| `cerebrovascular-malformations` | 0 | 0 | 0 | 3 |
| `chemical-shift-artifact` | 34 | 34 | 0 | 19 |
| `cns-opportunistic-infection` | 7 | 4 | 3 | 2 |
| `cranial-nerve-muscle-atrophy` | 6 | 6 | 0 | 4 |
| `dural-based-masses-aids` | 7 | 7 | 0 | 5 |
| `facial-fracture-complications` | 14 | 14 | 0 | 4 |
| `gbm-vs-pcnsl` | 3 | 3 | 0 | 3 |
| **Total** | **94** | **91** | **3** | **56** |

All 91 covered facts:

- preserve the original subject and relationship;
- retain the applicable polarity, qualifier, number/unit, time/version,
  exception, comparison, sequence/signal, distribution, clinical context,
  DDx, and exam-answer context;
- have nonempty defined sourceRefs;
- have a medical-body clause anchor in the correct bullet;
- remain in source order without changing a one-way comparison into an
  equivalence or rule;
- do not introduce a new medical conclusion.

High-risk checks passed:

- Fogging retains CT 2–3 weeks, MRI T2 6–36 days/median 10 days, approximately
  50%, contrast delineation, and all three negative timing/mimic clauses.
- Microbleeds keeps lobar/posterior/deep-sparing CAA distinct from deep
  hypertensive distribution, DAI, Zabramski IV cavernoma, other mimics, and
  NF1 noncausality.
- Chemical shift preserves all 34 facts, including 3.5 ppm, 1.5T/3T
  frequencies, 32 kHz/256/125 Hz and 1.8-pixel example, first-versus-second
  type directionality, in/opposed-phase distinctions, pure-fat and
  hemosiderosis reversals, Dixon pitfalls, and the 2016-092 polarity.
- Cranial-nerve denervation preserves the complete motor/sensory lists and
  `<1 month` -> `1–20 months` -> `>20 months` ordering.
- Facial fracture bullets retain each location as the governing context before
  nerve injury and symptom consequences.
- GBM-versus-PCNSL retains `PCNSL ADC < GBM` and the original morphology and
  incidence directions.

### CNS unresolved queue

The following are honestly unresolved:

```text
cns-opportunistic-infection-f03
cns-opportunistic-infection-f06
cns-opportunistic-infection-f07
```

Each has:

- `disposition=research-needed`;
- `sourceRefs=[]`;
- `coverage=null`;
- no corresponding unsupported Summary wording;
- membership in the sorted derived root queue.

Ref `[^1]` supports the abscess DWI claim but not the complete fungal-host
claim. Ref `[^2]` supports the toxoplasmosis claim but cannot cover the
compound fungal/answer-D statement. The implementation therefore did not
use partial support to bypass the queue. Only the CNS note is
`research-needed`; the other nine notes are mechanically eligible as
`verified`, and the root correctly remains `needs-review`.

### Dural empty-ref resolution

The existing rendered `[^1]` source definition explicitly enumerates the
complete tumor, granulomatous, and lymphoproliferative lists represented by:

- `dural-based-masses-aids-f04`;
- `dural-based-masses-aids-f05`;
- `dural-based-masses-aids-f06`.

The three rewritten bullets reproduce those lists without expansion or
omission. Mapping them to existing rendered ref `1` is therefore auditable
and does not require new literature or a new footnote.

## Exact empty-projection migration

`cerebrovascular-malformations` retains the trusted lock:

```text
summaryHeadings=[]
originalSummary=""
factUnits=[]
```

The range diff adds only one accepted canonical `## Summary` containing three
source-backed bullets. The pre-existing parenthesized legacy sections remain
once each and byte-identical:

- `## Summary（有無AV分流之分類）`;
- `## Summary（硬腦膜動靜脈瘻，Dural AV Fistula）`;
- `## Summary（軟膜動靜脈瘻，Pial AV Fistula）`.

The new bullets are direct conservative compression of rendered `[^1]`,
`[^2]`, and `[^3]`. In particular, the Pial AVF bullet preserves both
`higher hemorrhage risk than AVM` and the qualifying statement that only a
smaller proportion of PAVF presents with symptomatic hemorrhage. It also
retains 1.6%, absence of a nidus, and possible spontaneous occlusion in a
small low-flow lesion.

Removing only the inserted accepted Summary reconstructs the locked full-file
SHA-256. The evidence has no invented fact ID and derives exactly source
definitions `1,2,3` from the actual bullets.

## Structure, source definitions, and generated parity

- Strict `validate-note` returned exact `[]` for 10/10 notes.
- Every accepted Summary line is a permitted `###` heading or a top-level
  bold-label bullet with a colon and one or more defined Obsidian footnotes.
- There are no tables, callouts, nested bullets, plain prose, undefined refs,
  or unsourced matrix cells in accepted Summary spans.
- All ten evidence `summaryBulletEvidence` arrays equal their current
  generated `keyPoints` arrays in source order, with counts
  `5,5,6,3,19,2,4,5,4,3`.
- Every note has `newUnsupportedFacts=0`.
- The detail corpus is coherent at 980 unique detail files. The checked index
  hash remains
  `ae01c3105477a18c170238df777eed62556fdc199b80a60256d00a9cb3d9e35f`.
- The only selected generated field outside `keyPoints` that changed is
  `cerebral-microbleeds.externalLinks`, where the scoped deterministic rebuild
  removed malformed punctuation from the already-declared DOI URL. It is an
  allowed selected-detail rebuild, not a source-note or index scope expansion.

## Code and trust-boundary review

The empty-projection exception is fail-closed:

- batch must be exactly `batch-03-pattern`;
- slug must be exactly `cerebrovascular-malformations`;
- trusted lock projection must be exactly empty headings, empty Summary, and
  empty facts;
- baseline validation occurs before evidence construction;
- current note must contain a nonempty accepted Summary with strict sourced
  bullets;
- removal of that exact accepted Summary must reconstruct the trusted original
  full-file hash;
- source definitions are derived from current bullet refs and must equal
  rendered definitions;
- an invented fact ID, altered definition, additional accepted Summary,
  changed non-Summary byte, unsourced bullet, or a different batch/slug/lock
  is rejected.

Source-ref overrides are restricted to Batch 03 and may apply only to locked
empty-ref facts that are covered rather than unresolved. The current helper
uses them only for the three reviewed dural facts. Batch 01 and Batch 02
cannot use the mechanism.

Inventory accepted-state handling also requires:

- the exact slug and inventory empty-heading state;
- exactly one currently accepted canonical Summary;
- current note bytes matching the parsed hash;
- the trusted Batch 03 lock and original hash;
- reconstructed original full-file hash equality;
- otherwise-clean current evidence validation, allowing only the expected
  pre-review sequence finding.

The production exception does not expand the accepted Summary heading regex,
change assignment/inventory bytes, trust a mutable self-attestation, or
authorize a general zero-fact note.

## Historical tests and generated chain

The 14 post-transition test repairs do not delete a trust assertion and add no
`skip` or `xfail`.

- Task 4.1 production-baseline tests now reconstruct an authenticated pre-edit
  shadow from the trusted lock before comparing fact templates and canonical
  bytes.
- The generic three-batch two-run, relocation, historical-authorization, and
  drift-attack suites remain present.
- Current Batch 01/02 production tests accept exactly one fail-closed finding:
  the deliberately unsealed later Batch 03 contiguous generated-observation
  chain.
- No test treats that mismatch as success for generated acceptance, changes a
  trust digest, or permits a premature Batch 03 seal.
- First/second-run byte and mtime attacks remain executable through an
  authenticated predecessor state.

This is the correct Task 4.2 pre-seal state. Task 4.3 must independently
produce and seal the Batch 03 generated observation before the complete
Batch 01/02/03 terminal chain can return exact `[]`.

## Scope and immutable predecessor proof

The range contains exactly:

- ten selected source Markdown Summary replacements/addition;
- ten selected detail JSON rebuilds;
- Batch 03 evidence;
- narrowly related audit code/tests;
- the deterministic evidence helper and Task 4.2 report.

Unchanged:

- `data/concepts-index.json`;
- Batch 03 baseline and baseline trust digest;
- assignment and inventory;
- all Batch 01/02 baseline, evidence, generated manifests, and trust values;
- Phase 1 artifacts;
- nonselected source notes and 970 nonselected detail JSON files;
- Task 4.2 checkbox;
- Batch 03 generated manifest and generated-observation trust registry;
- all scheduled/Phase 2B artifacts.

Independent hash checks reproduced the report values for the Batch 03
baseline/evidence and all Batch 01/02 approved artifacts. For each of the ten
notes, restoring the locked Summary (or removing the sole inserted canonical
Summary for the zero-fact note) reconstructs its exact locked original
SHA-256.

`git diff --check 89fa3d8..b55c195` is clean.

## Independent command evidence

Re-run in this review:

```text
10 x validate-note
  -> 10 exact []

validate-assignment
  -> 216 NR / 10 Phase 1 / 206 non-pilot / 30 active / 176 scheduled / []

pytest -q scripts/test_nr_summary_audit.py -k batch03_task42
  -> 5 passed, 162 deselected

task4_2_build_evidence.py (dry-run)
  -> evidence SHA de931f6fcbdf35ca9f455b024c6d6ea5b8ac7b0f08ca0d187395bc7087c94b8c
  -> 10 notes / 94 facts / 91 covered
  -> queue f03/f06/f07
  -> findingCodes = [phase2-review-sequence]

validate-batch batch-03-pattern (post-edit, no pre-edit hash flag)
  -> exactly phase2-review-sequence

validate-batch batch-01-anatomy --check-generated
validate-batch batch-02-disease --check-generated
  -> each exactly generated-manifest-mismatch:
     Complete contiguous generated-observation chain is invalid.
```

The controller separately reported the complete suite as
`180 passed in 230.44s`; this independent review did not needlessly rerun the
four-minute full suite after reproducing the Task 4.2-specific gates.

Task 4.2 is approved for controller completion. The three CNS facts must remain
in the manual research queue through Task 4.3 unless separately verified from
an accessible article/chapter source.
