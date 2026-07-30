# Task 4.1 implementation brief — batch-03 pattern baseline

## Binding task and prerequisite

Implement only Spectra Task 4.1 for `batch-03-pattern`, starting from
`04fa65e` (with the approved Batch 02 seal at `0a68194`).

The controller independently confirmed both predecessors:

- `batch-01-anatomy validate-batch --check-generated` → exact `[]`;
- `batch-02-disease validate-batch --check-generated` → exact `[]`.

Canonical implementer identity:

`/root/phase2a_task4_1_impl`

Do not mark the Spectra checkbox. A different subagent must independently
review Task 4.1.

## Fixed pre-edit membership

Create a lossless pre-edit baseline only for these ten `pattern-ddx` notes, in
exact assignment order:

1. `brain-tumor-imaging`
2. `cerebral-infarction-fogging`
3. `cerebral-microbleeds`
4. `cerebrovascular-malformations`
5. `chemical-shift-artifact`
6. `cns-opportunistic-infection`
7. `cranial-nerve-muscle-atrophy`
8. `dural-based-masses-aids`
9. `facial-fracture-complications`
10. `gbm-vs-pcnsl`

Create:

- `docs/reports/nr-summary-rewrite/phase2a/baselines/batch-03-pattern.json`
- `docs/reports/nr-summary-rewrite/phase2a/evidence/batch-03-pattern.json`

Update only the central baseline trust registry with one Batch 03 digest,
strictly necessary builder/validator/tests, and the Task 4.1 report.

Do not edit concept Markdown, detail/index JSON, inventory, assignment,
Phase 1, Batch 01/02 artifacts or seals, scheduled notes, or any generated
manifest.

## Baseline lock requirements

Use the audited builder, not hand-copied medical text. Preserve:

- exact assignment digest, ordered membership/path/type, source SHA-256,
  accepted Summary headings, and lossless `originalSummary`;
- every factual Summary statement from bullets, numbered/nested content,
  factual callouts, comparisons, matrices, and multi-part DDx statements;
- stable `<slug>-fNN` IDs in source order;
- exact `sourceStatement` and applicable explicit/enclosing footnote refs.

Fact units must retain every subject, relationship, polarity, qualifier,
number/unit, age, date/version, negation, exception, sequence/signal,
location, distribution, symmetry, enhancement, clinical discriminator,
pitfall, and DDx contrast. Do not translate, correct, research, infer, or add
facts during baseline creation.

Footnote definitions and continuation lines are sources, not facts. Pure
semantic parents followed by nested children must appear exactly once as
context facts; ordered and unordered children inherit only applicable refs.
Headings/callout labels alone are not facts.

## Central trust and sequencing

`TRUSTED_PHASE2A_BATCH_LOCK_SHA256` must contain exactly the contiguous prefix:

1. existing `batch-01-anatomy` digest unchanged;
2. existing `batch-02-disease` digest unchanged;
3. new `batch-03-pattern` digest.

Do not add per-note constants or a mutable trust registry. Preserve both
generated-observation seals and all Batch 01/02 artifact bytes.

Baseline creation may proceed only after verifying both predecessor terminal
chains, but the Batch 03 scaffold remains pre-edit and nonterminal.

## Pending evidence scaffold

Create an honest scaffold:

- root `status=baseline`;
- workflow sequence `3`, predecessor `batch-02-disease`;
- implementer `/root/phase2a_task4_1_impl`;
- reviewer `null`, `reviewStatus=not-started`,
  `reviewedBaselineSha256=null`;
- rewritten Summary equals locked original;
- every locked fact copied with `pending` disposition;
- actual source definitions only;
- note status pending, queue empty;
- no coverage anchors yet, because no fact is covered before rewrite;
- no approval, coverage claim, generated observation, or tranche state.

It must pass `validate-baseline` but must not be accepted as terminal evidence.

## TDD and attacks

Add RED production regressions for:

1. exact Batch 03 membership/order/path/type/hash/Summary snapshot;
2. complete stable fact/sourceStatement/sourceRefs projection;
3. tables, callouts, nested ordered/unordered children, semantic parents, and
   footnote definitions/continuations handled without phantom or lost facts;
4. missing/extra/duplicate/out-of-order note/fact and malformed refs;
5. registry accepts only the exact three-batch active prefix;
6. coordinated source/inventory/assignment/lock/evidence replacement fails;
7. missing/wrong predecessor baseline or generated seal prevents later
   workflow writes;
8. canonical and relocated checkout parity;
9. pending scaffold cannot pass final content/review/generated gates.

Parameterize existing attacks where possible. If a production note reveals a
new parser boundary, first create a focused RED fixture, then implement the
smallest general fix; do not special-case a slug.

## Required gates

- ten current source hashes equal inventory before generation;
- Batch 01 and Batch 02 terminal validations remain exact `[]`;
- `validate-baseline --batch batch-03-pattern` returns exact `[]`;
- lock/assignment/inventory/source/headings/lossless Summary all agree;
- regeneration is byte-identical and digest matches the code-owned trust;
- explicit per-note source-statement/fact/ref/empty-ref counts are reported;
- no footnote-definition facts or lost semantic parents;
- registry/coordinated/predecessor/relocation attacks fail with stable codes;
- scaffold is honest and nonterminal;
- full audit/build pytest, direct smokes, four-file `py_compile`,
  assignment/inventory, Spectra strict/analyze, and `git diff --check` pass;
- no diff to `vault/concepts`, `data/concepts`, index, Batch 01/02 artifacts,
  or scheduled artifacts.

## Report and commit

Write:

`tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-4-1-report.md`

Include RED/GREEN evidence, per-note statement/fact/ref/empty counts,
source-hash and lossless parity, canonical bytes/digests, registry shape,
pending-scaffold state, predecessor terminal proof, mutation/relocation
results, all gates, scope, and concerns.

Make one focused commit and return DONE, DONE_WITH_CONCERNS, or BLOCKED with
the SHA. Do not mark Task 4.1 complete.
