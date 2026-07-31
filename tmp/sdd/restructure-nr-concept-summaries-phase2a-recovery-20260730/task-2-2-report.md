# Task 2.2 implementation report — batch-01 anatomy Summary rewrite

## Outcome

`DONE_WITH_CONCERNS`

- Base: `efbc291`
- Batch: `batch-01-anatomy`
- Scope: ten selected NR anatomy concept notes only
- Implementer: `/root/phase2a_task2_2_impl`
- Intended reviewer: `/root/phase2a_task2_3_review`
- Evidence workflow: `reviewStatus=not-started`,
  `reviewedBaselineSha256=null`
- Spectra Task 2.2 and Task 2.3 checkboxes were not changed.
- Task 2.3 generated manifest, approval, observation, and lint-acceptance
  artifacts were not created.

The ten Summary spans were rewritten into flat, single-line
`- **粗體標籤**：短內容。[^n]` cards. Of 121 sealed facts, 120 are covered and
one remains `research-needed`. No unsupported fact was added.

The canonical exact before/after pairs are stored without report-time
retranscription in:

- before: `docs/reports/nr-summary-rewrite/phase2a/baselines/batch-01-anatomy.json`
  → each note's `originalSummary`
- after: `docs/reports/nr-summary-rewrite/phase2a/evidence/batch-01-anatomy.json`
  → each note's `rewrittenSummary`

The baseline lock remains
`1ba97cdc318b16deaf60cc768dc4b7424f01759287c91e43c85bd6c1601b0b64`.

## RED/GREEN evidence

Tests were added before production rewrites.

Initial audit-focused RED run:

- result: `3 failed, 1 passed, 111 deselected`
- failures demonstrated that:
  1. a non-covered fact with empty refs was incorrectly rejected as an
     `evidence-source-definition` error;
  2. the deterministic Task 2.2 rewrite-evidence builder did not exist;
  3. the pending scaffold did not contain derived `summaryBulletEvidence`.
- the byte-scope reconstruction test already passed, proving the test could
  distinguish Summary bytes from all other note bytes.

The generated-output test was then added before the scoped build and failed
because the checked-in selected `keyPoints` still reflected the old Summary.

GREEN:

- Task 2.2 focused audit/build tests: `5 passed, 122 deselected`
- complete audit/build pytest: `127 passed in 51.19s`
- direct audit smoke: `NR_SUMMARY_AUDIT_OK`
- direct build smoke: `BUILD_CONCEPTS_TEST_OK`
- four-file `py_compile`: exit `0`

The new production tests cover:

- non-covered empty refs are allowed only with a non-covered disposition and
  derived queue membership;
- covered empty refs fail;
- exact non-Summary byte reconstruction;
- deterministic evidence construction and pre-review workflow state;
- all selected summaries use sourced flat-card grammar and preserve the 121
  stable facts;
- all ten generated detail files are byte-identical to current parser output,
  selected `keyPoints` equal accepted Summary bullets, and the 978-file
  detail/index corpus is coherent.

## Per-note before/after and coverage

“Before” counts are distinct locked source statements in `originalSummary`.
“After” counts are accepted top-level bold-label bullets in
`rewrittenSummary`. The fact counts and dispositions come from the sealed fact
units and deterministic evidence.

| Note | Before statements | Locked facts | After bullets | Covered | Research-needed | Source definitions | After labels |
|---|---:|---:|---:|---:|---:|---:|---|
| `ajcc-8th-head-neck-n-staging` | 4 | 6 | 5 | 6 | 0 | 3 | 版本變革；ENE 適用；cN3b；臨床 vs 病理；部位例外 |
| `aneurysm-coiling-recurrence` | 3 | 4 | 4 | 4 | 0 | 2 | 復發相關軸；Huang 2017 風險因子；復發率；復發機轉 |
| `atlantodental-interval` | 15 | 27 | 25 | 27 | 0 | 5 | AADI/PADI 量法與意義；X 光/CT 年齡正常值；橫韌帶與 PADI 閾值；病因、動態量測、MRI、兒童與量測陷阱、DDx |
| `brachial-plexus-anatomy` | 6 | 9 | 8 | 9 | 0 | 2 | 常見起源；位置；Trunks；Divisions；Cords；變異；MR neurography；外傷提示 |
| `brain-herniation-syndromes` | 3 | 3 | 2 | 2 | 1 | 1 | 受壓結構；臨床警訊 |
| `carotid-vertebrobasilar-anastomoses` | 5 | 7 | 5 | 7 | 0 | 1 | Persistent trigeminal/hypoglossal/proatlantal/otic arteries；考題辨析 |
| `cerebral-border-zone-infarct-arteries` | 5 | 11 | 11 | 11 | 0 | 2 | 本質、比例、好發條件；external/internal 部位、影像、供應與機轉；非供應者 |
| `cerebral-deep-venous-cortex` | 22 | 40 | 40 | 40 | 0 | 9 | 40 個一事實一卡標籤，依 f01→f40 原順序涵蓋解剖、引流領域、變異、DCVT 影像與 DDx/陷阱 |
| `cerebral-herniation-types` | 4 | 7 | 7 | 7 | 0 | 1 | Subfalcine、descending、ascending、tonsillar 的血管/循環/併發症 |
| `cerebral-infarction-evolution` | 5 | 7 | 7 | 7 | 0 | 1 | Fogging effect 定義、時機與比例、機轉、漏診、策略、考題定義、錯誤選項 |
| **Total** | **72** | **121** | **114** | **120** | **1** | **27** | |

All labels are only retrieval aids. They do not add independent propositions.
Where one bullet represents more than one locked fact, the evidence mapping
still preserves each stable fact ID and source-ref set in source order.

## Final dispositions and derived queue

- `covered`: 120
- `research-needed`: 1
- `manual-review`: 0
- `newUnsupportedFacts`: 0 for every note and 0 in total
- root status: `needs-review`
- derived `manualReviewFactIds`:
  - `brain-herniation-syndromes-f03`

The unresolved fact is the original unreferenced imaging sentence:

> CT/MRI 見顳葉鉤回內移、環池（ambient/perimesencephalic cistern）不對稱變窄或消失、中腦受壓變形。

It was omitted from the rewritten Summary. Its disposition is
`research-needed`, its `sourceRefs` is exactly `[]`, and it is the only queue
item. It was not silently converted to `covered`.

## Source-definition and footnote parity

- All 120 covered facts have nonempty `sourceRefs`.
- Every covered ref resolves to a rendered definition in the same note.
- Evidence `sourceDefinitions` is the exact ordered projection of the refs
  used by each note.
- All 27 definitions are `kind=existing-footnote`; no new definition was
  invented.
- Existing locators and citation strings match the rendered note definitions
  exactly.
- All ten evidence validation blocks report:
  - `hashMatches=true`
  - `losslessSummaryMatches=true`
  - `allSourceRefsDefined=true`
  - zero structure errors
  - zero footnote errors

The validator now also fails covered facts with empty refs and fails altered
existing-footnote locators/citations, while allowing empty refs only for
non-covered dispositions that feed the derived queue.

## Exception research

Research was restricted to `brain-herniation-syndromes-f03`, as required.

The official RSNA RadioGraphics page for
[*Brain Herniation and Intracranial Hypertension*](https://pubs.rsna.org/doi/full/10.1148/rg.2019190018)
was reachable only as an abstract/figure-caption view and displayed a
full-access requirement. The accessible material did not fully establish the
entire locked three-part CT/MRI claim with an allowed readable source.

Conservative result:

- no research-derived bullet;
- no new footnote;
- `sourceStatus=research-needed`;
- f03 remains unresolved and queued.

## Byte scope and nonselected-write proof

The pre-edit gate confirmed all ten whole-file SHA-256 values matched the
sealed baseline before the first production edit. `validate-baseline` returned
exit `0` with `[]`.

Independent range-diff audit against `efbc291` found:

- 10/10 selected Markdown files have byte-identical prefix and suffix around
  the accepted `## Summary` span;
- no research footnote was appended;
- no nonselected Markdown file changed;
- no nonselected generated detail changed;
- `data/concepts-index.json` is byte-identical to the base;
- no Task checkbox changed;
- no batch-02, batch-03, scheduled, or Task 2.3 generated artifact exists;
- `git diff --check` passes.

The tracked diff before adding this report was exactly 24 files:

- 10 selected `vault/concepts/<slug>.md`;
- 10 selected `data/concepts/<slug>.json`;
- `docs/reports/nr-summary-rewrite/phase2a/evidence/batch-01-anatomy.json`;
- `scripts/nr_summary_audit.py`;
- `scripts/test_nr_summary_audit.py`;
- `scripts/test_build_concepts.py`.

`scripts/build_concepts.py` itself did not need a production change.

## Scoped build and generated parity

The batch-scoped command used the evidence batch file:

```text
python scripts/build_concepts.py --repo-root . --batch-file docs/reports/nr-summary-rewrite/phase2a/evidence/batch-01-anatomy.json --quiet
```

Final accepted write scope:

- `data/concepts/ajcc-8th-head-neck-n-staging.json`
- `data/concepts/aneurysm-coiling-recurrence.json`
- `data/concepts/atlantodental-interval.json`
- `data/concepts/brachial-plexus-anatomy.json`
- `data/concepts/brain-herniation-syndromes.json`
- `data/concepts/carotid-vertebrobasilar-anastomoses.json`
- `data/concepts/cerebral-border-zone-infarct-arteries.json`
- `data/concepts/cerebral-deep-venous-cortex.json`
- `data/concepts/cerebral-herniation-types.json`
- `data/concepts/cerebral-infarction-evolution.json`

Observed scope:

- selected details changed: 10
- nonselected details changed: 0
- nonselected Markdown changed: 0
- index changed: 0
- selected `keyPoints` parity: 10/10
- checked-in selected detail bytes equal fresh parser output: 10/10
- detail files: 978
- index slugs exactly equal detail slugs: 978

Because the scoped builder serializes the complete selected detail object,
8/10 selected details also received deterministic normalization of stale
parser-derived fields (for example `externalLinks`, and in a few selected
notes `differentialDiagnosis`, `imagingFindings`, or `management`). Those
changes are reproducible from the current selected Markdown and remain inside
the explicitly permitted ten detail paths.

An initial scoped synchronization was followed by a final same-batch
resynchronization after semantic qualifier corrections. No invocation wrote
outside the selected batch. This extra same-scope invocation is recorded as a
process concern even though final scope and byte-idempotence gates pass.

## Validation gates

| Gate | Result |
|---|---|
| Pre-edit 10/10 hashes equal sealed baseline | PASS |
| `validate-baseline --batch batch-01-anatomy` | PASS, `[]` |
| Strict `validate-note` | PASS, 10/10, each `[]` |
| 121 stable facts/final dispositions | PASS, 120 covered + 1 research-needed |
| Content/source/footnote/manual-queue findings | PASS, none |
| Pre-review `validate-batch` | Expected sole finding: `phase2-review-sequence` |
| Unsupported facts | PASS, 0 |
| Scoped generated `keyPoints` parity | PASS, 10/10 |
| Complete detail/index corpus | PASS, 978/978 |
| Nonselected source/detail writes | PASS, 0 |
| Focused Task 2.2 tests | PASS, 5 |
| Complete audit/build pytest | PASS, 127 |
| Direct audit smoke | PASS, `NR_SUMMARY_AUDIT_OK` |
| Direct build smoke | PASS, `BUILD_CONCEPTS_TEST_OK` |
| Four-file `py_compile` | PASS |
| Inventory check | PASS: NR 216, duplicate 0, unclassified 0, batch 00 10, unassigned 0 |
| `spectra validate restructure-nr-concept-summaries-phase2a --strict` | PASS |
| `spectra analyze ... --json` | 0 Critical, 0 Warning, 2 pre-existing Suggestions |
| `git diff --check` | PASS |
| Task 2.3 approval/manifest absent | PASS |

The exact remaining pre-review batch finding is:

```json
{
  "severity": "error",
  "code": "phase2-review-sequence",
  "message": "Terminal batch status requires approved review of this baseline."
}
```

This is intentionally not suppressed: independent Task 2.3 review has not
started.

The two Spectra suggestions are unchanged proposal-quality notes:

1. “Invalid Summary grammar is rejected” lacks a concrete example.
2. “Research supplies a permitted new fact” lacks a concrete example.

Neither is a Task 2.2 implementation failure.

## Concerns handed to the reviewer

1. `brain-herniation-syndromes-f03` remains research-needed because the
   permitted official source was not fully readable and accessible content did
   not cover the complete claim.
2. The final batch status cannot pass terminal validation until the independent
   Task 2.3 reviewer approves this exact baseline/evidence state.
3. The final scoped generated files are correct and isolated, but a second
   same-batch synchronization was required after semantic qualifier
   corrections.
4. Selected detail JSON includes deterministic normalization beyond
   `keyPoints`; reviewer should judge the complete parser-derived selected
   outputs, not assume each JSON diff is keyPoints-only.
