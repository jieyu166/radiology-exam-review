# Task 2.1 independent review — round 1

## Verdict

**APPROVED**

- Reviewed commit:
  `9f1c5be4b4d43c742c04499b7a45818b0db66878`
- Binding scope: Spectra
  `restructure-nr-concept-summaries-phase2a`, Task 2.1 only
- Critical findings: **0**
- Important findings: **0**
- Suggestion findings: **1**

The checked baseline is a lossless, centrally sealed pre-edit record for the
exact ten-note `batch-01-anatomy` assignment. The pending evidence file is
honestly nonterminal. No concept Markdown, generated concept data, inventory,
assignment, Phase 1 artifact, later batch artifact, or scheduled-note artifact
was changed.

## Independent mechanical verification

### Baseline, trust, and source parity

- `validate-baseline --batch batch-01-anatomy` returned exit `0` and `[]`.
- The same CLI returned exit `0` and `[]` when launched from `C:\tmp` with an
  explicit absolute `--repo-root`; no current-working-directory dependency was
  observed.
- Independent canonical JSON recomputation produced
  `1ba97cdc318b16deaf60cc768dc4b7424f01759287c91e43c85bd6c1601b0b64`,
  exactly matching the sole code-owned
  `TRUSTED_PHASE2A_BATCH_LOCK_SHA256["batch-01-anatomy"]` entry.
- Baseline file SHA-256 independently recomputed as
  `6b05caff4e2cbd618a9c15478f914853701b4be2587af58469b013917d0a7934`.
- Membership and order exactly match the ten slugs in the fixed assignment.
- All ten source-file SHA-256 values, accepted Summary headings, and lossless
  `originalSummary` snapshots match the currently loaded source notes.
- The projection contains exactly 72 source statements and 121 stable IDs.
  IDs are gap-free `<slug>-fNN` values in source order.
- Every `sourceStatement` is an exact line in the locked `originalSummary`.
- Every nonempty `sourceRefs` entry resolves to a rendered Obsidian footnote
  definition. Evidence `sourceDefinitions` were independently compared
  character-for-character with those current definitions.
- The only empty mapping is
  `brain-herniation-syndromes-f03`, whose original imaging bullet has no
  footnote. Keeping `sourceRefs: []` is the required conservative behavior.

### Evidence scaffold and attacks

- Root status is `baseline`; sequence is `1`; predecessor is `null`.
- Implementer is `/root/phase2a_task2_1_impl`; reviewer, review snapshot, and
  approval are `null` / `not-started`.
- All ten note statuses and all 121 dispositions are `pending`.
- Every `rewrittenSummary` is the exact pre-edit `originalSummary`.
- No note claims validation, coverage checksum, unsupported-fact count,
  generated verification, manual review, or terminal approval.
- Terminal `validate-batch --check-source-hashes` returned exit `1`, beginning
  with `phase2-evidence-schema`; the scaffold cannot be mistaken for completed
  evidence.
- The coordinated mutable source/inventory/assignment/lock/evidence attack
  still resolves to `phase2-trusted-batch-lock-mismatch`.
- The shadow-checkout parity and pending-scaffold attack regressions passed.
- Focused attack run: `3 passed in 0.39s`.

### Regression and scope gates

- Full audit/build test run: `122 passed in 50.11s`.
- Direct audit smoke: `NR_SUMMARY_AUDIT_OK`.
- Direct build smoke: `BUILD_CONCEPTS_TEST_OK`.
- Four-file `py_compile`: exit `0`.
- `git diff --check`: exit `0`.
- Diff from `12a54e8` contains only the two Task 2.1 artifacts, audit code,
  audit tests, and the implementation report.
- `vault/concepts`, `data/concepts`, `data/concepts-index.json`,
  `inventory.json`, and `phase2-assignment.json` have no diff.
- The only files under the Phase 2A production artifact root are the
  `batch-01-anatomy` baseline and pending evidence scaffold. No batch 02,
  batch 03, generated manifest, or scheduled-note artifact exists.
- Spectra strict validation passed. Artifact analysis has 0 Critical,
  0 Warning, and the same two pre-existing Suggestion-only ambiguities.

## Manual statement-to-fact review

All ten notes were reviewed statement by statement, including every split fact,
qualifier, number, unit, date/version, polarity, negation, exception,
relationship, DDx clause, source reference, nested-bullet inheritance, and
factual callout answer.

| Note | Statements → facts | Independent review result |
|---|---:|---|
| `ajcc-8th-head-neck-n-staging` | 4 → 6 | ENE version distinction, cN3b/pN2a nuance, sizes, polarity, and site exceptions retained; refs 1/2/3 remain attached only to their original statements. |
| `aneurysm-coiling-recurrence` | 3 → 4 | Risk factors, VER threshold, 12.6% (83/658), stent polarity, and mechanisms retained without a new causal claim. |
| `atlantodental-interval` | 15 → 27 | All AADI/PADI definitions, modality-specific adult/child thresholds, 97%/94%, 5/7/14 mm rules, causes, dynamic-view caveats, DDx, and the factual callout answer are present. No value, unit, exception, or negation was lost. |
| `brachial-plexus-anatomy` | 6 → 9 | C5–T1, uncommon C4, trunk/division/cord relations, variants, imaging, and trauma statements retained. Nested Trunks/Divisions/Cords correctly inherit only enclosing ref 1. |
| `brain-herniation-syndromes` | 3 → 3 | CN III mechanism, clinical laterality/Kernohan exception, and imaging relationship retained. The unsupported imaging line remains deliberately source-empty. |
| `carotid-vertebrobasilar-anastomoses` | 5 → 7 | Relative frequency, controversy, origins/canals, exam conclusion, and factual callout answer retained under ref 1. |
| `cerebral-border-zone-infarct-arteries` | 5 → 11 | External/internal territories, mechanisms, 5–10%, ≥3/≥3 mm criteria, arteries, string-of-pearls, and negative superior-hypophyseal relationship retained. |
| `cerebral-deep-venous-cortex` | 22 → 40 | All anatomy, drainage routes/territories, variants, modality signs, unilateral exception, bilateral-thalamic DDx, negations, and pitfalls retained in order. Refs 1–9 remain on the source statements that carried them; no new source was inferred. |
| `cerebral-herniation-types` | 4 → 7 | Each herniation type remains paired with its compressed vessel, infarct territory, neurologic effect, circulation exception, or hydrocephalus relationship. |
| `cerebral-infarction-evolution` | 5 → 7 | Definition, 6–36 days/median 10 days, ~50%, mechanism, diagnostic limitation, and all callout-answer negations retained under ref 1. |

No statement omission, invented medical claim, qualifier/negation loss,
incorrect threshold association, source-order drift, or incorrect inherited
reference was found.

## Findings

### Suggestion — make split `text` fields more self-contained before wider-scale reuse

`_phase2_fact_segments` currently splits every top-level semicolon or full stop
mechanically (`scripts/nr_summary_audit.py:1067-1081`). A few resulting `text`
fields depend on the preceding clause for their subject, for example:

- `atlantodental-interval-f13` at
  `docs/reports/nr-summary-rewrite/phase2a/baselines/batch-01-anatomy.json:232`
  is `≥7 mm 強烈提示...`; its exact `sourceStatement` supplies `AADI`.
- `cerebral-border-zone-infarct-arteries-f02` at the same file's line 572 is
  `占腦梗塞 5-10%；`; its exact `sourceStatement` supplies the border-zone
  infarct subject.
- `cerebral-herniation-types-f06` at the same file's line 1078 is
  `可致阻塞性水腦。`; its exact `sourceStatement` supplies ascending
  transtentorial herniation.

This is **not Important for this lock**: every affected record retains the full
exact `sourceStatement`, source order, shared refs, and lossless
`originalSummary`; validator regeneration restores that context, so no
baseline fact, relationship, qualifier, or citation is lost. It is therefore a
readability and future-review ergonomics issue, not a fidelity failure.

Before scaling the same projection across substantially larger batches,
consider retaining a dependent clause with its prior segment or conservatively
carrying the original label/subject into the fact text, with regressions for
threshold and causal clauses. Such a change would require deliberate baseline
regeneration and digest review; it should not be applied silently to this
approved lock.

