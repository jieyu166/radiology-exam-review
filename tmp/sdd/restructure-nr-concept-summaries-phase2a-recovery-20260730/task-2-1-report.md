# Task 2.1 implementation report

## Result

- Status: DONE_WITH_CONCERNS
- Base: `12a54e8b4c9bde3cb10f9cceac8e9d4aa378e98d`
- Scope: Spectra Task 2.1 only; the Task 2.1 checkbox remains unchanged for
  controller review.
- Batch: `batch-01-anatomy`, exact assignment-order membership of 10 notes.
- No concept Markdown, generated concept JSON, inventory, assignment, Phase 1
  evidence/trust, or generated-observation trust was modified.
- No literature research was performed and no new medical statement was added.

## TDD evidence

Production artifacts were absent when the first Task 2.1 tests ran.

- RED command selected the eight baseline/scaffold tests.
- RED result: `8 failed, 102 deselected in 0.73s`.
- All eight failed for the expected reason: the checked baseline/evidence
  artifacts were missing (`context.baseline` / `context.evidence` were `None`);
  there was no syntax, import, or fixture error.
- Minimal GREEN added the parser-driven lock/scaffold builders, baseline
  validator hardening, one code-owned digest, and the two checked artifacts.
- Initial Task 2.1 GREEN: `8 passed, 102 deselected in 0.47s`.

The first complete audit run then exposed a state-boundary regression:

- RED result: `103 passed, 7 failed in 47.82s`.
- The seven existing later-batch tests demonstrated that
  `validate_baseline_lock` must ground facts in the immutable locked Summary,
  while current source hash/Summary comparison belongs to the explicit
  pre-edit source gate. Comparing the rewrite-era source directly to the lock
  incorrectly blocked valid later-batch generated-chain fixtures.
- The validator now derives fact grounding from `originalSummary` in the lock;
  `validate-baseline` still invokes the explicit pre-edit current-source gate.
- Focused GREEN: `7 passed, 103 deselected in 12.40s`.
- Final complete audit/build GREEN after the coordinated-mutation regression:
  `122 passed in 50.21s`.

## Deterministic source projection

The audited parser is the only content source. It:

1. preserves the complete lossless `originalSummary`;
2. selects factual Summary lines, including nested bullets and factual callout
   answers, while omitting headings and callout labels;
3. preserves exact source order and exact `sourceStatement`;
4. carries explicit footnote refs, or the enclosing top-level bullet refs for
   nested bullets;
5. splits only at top-level `；`, `;`, or `。`, with parentheses/brackets
   protected, so values and qualifiers inside parentheses remain attached;
6. removes only list/quote/bold/footnote markup from fact text and does not
   translate, paraphrase, or synthesize medical content.

The validator recomputes this projection from the immutable locked Summary.
It rejects blank or changed text, changed relationships, missing statements,
out-of-order facts, unstable IDs, malformed/duplicate/non-string refs, and refs
that are absent from the note's rendered definitions.

Two independent builder processes plus the checked-artifact regression produced
identical bytes and digests:

- canonical baseline trust SHA-256:
  `1ba97cdc318b16deaf60cc768dc4b7424f01759287c91e43c85bd6c1601b0b64`;
- baseline file SHA-256:
  `6b05caff4e2cbd618a9c15478f914853701b4be2587af58469b013917d0a7934`;
- baseline bytes: `77,722`;
- evidence scaffold file SHA-256:
  `390a80b5a9e5861c8ae2ea6ccc024e9ef9562812efa54cbf6d4b694834ccded3`;
- evidence scaffold bytes: `51,474`;
- assignment canonical SHA-256 recorded in the lock:
  `b9dfbf5361392c03178928b591c09839fa7f6fc08e7c0072867657bc361a8c0e`.

The code-owned registry contains exactly one entry for this task:
`batch-01-anatomy` mapped to the canonical baseline digest. There are no
per-note trust constants and no batch-02/batch-03 keys.

## Source-statement-to-fact coverage

The baseline contains 72 factual source statements and 121 stable fact units.
Every statement appears in source order in at least one fact's exact
`sourceStatement`. IDs are `<slug>-fNN` without gaps.

| Slug | Statements | Facts | Empty refs | Existing refs used | Source SHA-256 |
|---|---:|---:|---:|---|---|
| `ajcc-8th-head-neck-n-staging` | 4 | 6 | 0 | 1, 2, 3 | `289ee69ba668b560222a068421f905d93c30ad3b52d90be837ff48a44cf09d86` |
| `aneurysm-coiling-recurrence` | 3 | 4 | 0 | 1, 2 | `326a4e68ef668a23fdbaf9862139bace82078abd7bef4f407929bab600e9eb57` |
| `atlantodental-interval` | 15 | 27 | 0 | 1, 2, 3, 4, 5 | `a0f24011fd691d4f932b381834af0f96452f24a37cf6ba1afe5e14891f2dc009` |
| `brachial-plexus-anatomy` | 6 | 9 | 0 | 1, 2 | `001877319ab1cfc2919a6573968ec82ee75dfc84920930ee4d2b3c089dd28163` |
| `brain-herniation-syndromes` | 3 | 3 | 1 | 1 | `aa9d4ad571e5034c4c761bdf895f12691574a77577876f7feb0fac94f0b7e401` |
| `carotid-vertebrobasilar-anastomoses` | 5 | 7 | 0 | 1 | `b44ed155fccbcf9c93de142f7e60ac18a60f671e3836ea4c9123c044aa515922` |
| `cerebral-border-zone-infarct-arteries` | 5 | 11 | 0 | 1, 2 | `489ba2b9c6b725b8b69414fd5c49ca1af5b9535c86f1417c0e99b73964aba122` |
| `cerebral-deep-venous-cortex` | 22 | 40 | 0 | 1–9 | `4d39d46fb1847943f41da42e357c4a94a1c15c3208c343d681eee534f0c3f5c9` |
| `cerebral-herniation-types` | 4 | 7 | 0 | 1 | `1dac0c8e109a0e4c57cf621668982c42d5dfcbaa07f2dae5072337ada195b56e` |
| `cerebral-infarction-evolution` | 5 | 7 | 0 | 1 | `a05a58454d726dcf4e071b2edc4f400faaa15cd260f093b15d354aa615cea7a3` |
| **Total** | **72** | **121** | **1** | — | — |

All ten current file hashes, accepted headings, and lossless Summary snapshots
equal the lock and inventory. The single empty source mapping is
`brain-herniation-syndromes-f03`, whose original imaging bullet had no
footnote. The lock intentionally preserves `sourceRefs: []`; it does not guess,
research, or upgrade the source.

## Pending evidence scaffold

The checked scaffold is intentionally nonterminal:

- root status: `baseline`;
- sequence: `1`; predecessor: `null`;
- implementer: `/root/phase2a_task2_1_impl`;
- reviewer: `null`;
- review status: `not-started`;
- reviewed baseline SHA: `null`;
- all 10 note statuses: `pending`;
- all 121 dispositions: `pending`;
- rewritten Summary: exact pre-edit `originalSummary`;
- source definitions: only existing definitions referenced by locked facts;
- manual review fact IDs: `[]`;
- generated field: future manifest path only;
- no validation block, coverage checksum, generated verification, independent
  approval, or terminal claim.

The terminal `validate-batch --check-source-hashes` gate returned exit `1` and
started with `phase2-evidence-schema`, proving that the pending scaffold cannot
be accepted as completed evidence.

## Mutation and parity results

- ungrounded inserted relationship -> `phase2-baseline-schema`;
- blank fact text -> `phase2-baseline-schema`;
- removed source statement with IDs renumbered -> `phase2-baseline-schema`;
- non-list, non-string, duplicate, or undefined source refs ->
  `phase2-baseline-schema`;
- missing, extra, or duplicate note -> `phase2-baseline-inventory-mismatch`;
- missing/wrong/early/unknown central registry entry ->
  `phase2-trusted-batch-lock-mismatch`;
- coordinated shadow mutation of source bytes, inventory hash, regenerated
  assignment, baseline hash/digest reference, and evidence lock reference ->
  exactly `phase2-trusted-batch-lock-mismatch`;
- canonical and relocated shadow checkout baseline validation produced the
  same finding-code list and exit state: no findings / success.

## Verification gates

- Production `validate-baseline --batch batch-01-anatomy`: exit 0, findings
  `[]`.
- Task 2.1 targeted baseline/scaffold tests: 8/8 passed before the added
  coordinated-mutation test; the final complete suite includes that ninth
  production attack regression.
- Complete audit/build pytest: `122 passed in 50.21s`.
- Direct Phase 1 audit smoke: `NR_SUMMARY_AUDIT_OK`.
- Direct Phase 1 build smoke: `BUILD_CONCEPTS_TEST_OK`.
- Four-file `py_compile`: exit 0.
- Spectra strict validation: valid.
- Spectra artifact analysis: 0 Critical, 0 Warning; two pre-existing
  Suggestion-only ambiguity findings remain.
- `git diff --check`: exit 0.
- Working-tree scope diff for `vault/concepts`, `data/concepts`,
  `data/concepts-index.json`, `inventory.json`, and
  `phase2-assignment.json`: exit 0.
- All 10 selected current SHA-256 values match the lock; mismatches `[]`.
- The only Phase 2A production files are the batch-01 baseline and pending
  evidence scaffold. No batch-02, batch-03, generated manifest, or scheduled
  note artifact exists.
- Task 2.1 checkbox diff: none.

## Changed files

- `scripts/nr_summary_audit.py`
- `scripts/test_nr_summary_audit.py`
- `docs/reports/nr-summary-rewrite/phase2a/baselines/batch-01-anatomy.json`
- `docs/reports/nr-summary-rewrite/phase2a/evidence/batch-01-anatomy.json`
- `tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-2-1-report.md`

## Concerns

- The original unsupported imaging sentence in
  `brain-herniation-syndromes` remains source-empty by design. Task 2.2 must
  either leave it in the derived manual/research queue or use the permitted
  exception-research workflow; Task 2.1 makes no coverage claim.
- The parser-driven split is mechanically complete and source-exact, but
  semantic granularity remains an independent-review concern. This report and
  each fact's exact `sourceStatement` provide the requested explicit
  statement-to-fact audit trail.
- Spectra still reports the two unrelated Suggestion-level ambiguities for
  later Summary grammar/research scenarios. They are not Critical or Warning.
- Git emits a managed-sandbox warning that the user-level
  `C:\Users\jai16\.config\git\ignore` cannot be read. Repository
  status/diff/check commands still complete successfully.
