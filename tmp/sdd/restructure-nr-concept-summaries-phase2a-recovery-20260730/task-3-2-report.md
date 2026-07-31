# Task 3.2 implementation report — batch-02 disease Summary rewrite

## Outcome

- Status: `DONE_WITH_CONCERNS`
- Approved Task 3.1 base: `0a3f73f`
- Implementation dispatch HEAD: `035cc8a`
- Batch: `batch-02-disease`
- Implementer: `/root/phase2a_task3_2_impl`
- Intended independent reviewer: `/root/phase2a_task3_3_review`
- Task 3.2 checkbox was not changed.
- Task 3.3 approval, generated manifest, and generated-observation seal were
  not created or claimed.
- No Batch 03 or scheduled work was started.

The ten disease summaries were rewritten as sourced bold-label, short,
top-level bullets. The approved lock still contains 60 source statements and
98 immutable facts. Final pre-review dispositions are 96 `covered` and two
`research-needed`; `newUnsupportedFacts=0`.

## TDD evidence

Production tests were added before production edits.

- Pre-edit baseline gate:
  `validate-baseline --batch batch-02-disease` returned exact `[]`.
- Initial RED:
  `1 passed, 3 failed`.
  - the non-Summary byte test already passed against the untouched notes;
  - strict disease-card validation failed on the original nested ALD Summary;
  - deterministic final evidence failed because the checked file was still a
    pending scaffold;
  - generated parity failed because two selected details did not yet exist.
- The ALD source definitions exposed one narrow validator gap: Obsidian
  footnote definitions and four-space/tab continuations under
  `### 參考來源` were being treated as prose. A focused regression now treats
  only that reference-subsection metadata as non-content; a footnote
  definition elsewhere in Summary remains `summary-content-line`.
- Focused validator GREEN: `3 passed`.
- Task 3.2 production GREEN plus Batch 01 corpus regression: `5 passed`.
- State-transition regressions after the scoped build: `7 passed`.
- Complete audit/build suite:
  `155 passed in 105.10s`.

The production tests bind:

- all 98 stable fact IDs and their exact final disposition;
- sourced bold-label grammar;
- optional disease axes without synthesized categories;
- Aicardi triad preservation;
- ALD Schaumburg center-to-outside preservation;
- omission and derivation of unresolved ALD f30/f33;
- exact non-Summary byte reconstruction;
- evidence determinism;
- selected generated `keyPoints` and full index/detail coherence;
- honest pre-review workflow state.

## Per-note rewrite and coverage

| Slug | Locked statements | Rewritten bullets | Facts | Covered | Research-needed | Source definitions |
|---|---:|---:|---:|---:|---:|---:|
| `2-hydroxyglutarate-idh-mutant-glioma` | 4 | 4 | 7 | 7 | 0 | 3 |
| `adrenoleukodystrophy` | 18 | 13 | 36 | 34 | 2 | 11 |
| `aicardi-syndrome` | 7 | 4 | 8 | 8 | 0 | 2 |
| `als-imaging` | 3 | 3 | 4 | 4 | 0 | 1 |
| `angioinvasive-aspergillosis` | 5 | 5 | 6 | 6 | 0 | 1 |
| `anti-nmda-encephalitis` | 4 | 4 | 7 | 7 | 0 | 2 |
| `arterial-dissection-mri` | 5 | 5 | 7 | 7 | 0 | 2 |
| `atypical-teratoid-rhabdoid-tumor` | 5 | 5 | 12 | 12 | 0 | 2 |
| `autoimmune-encephalitis` | 4 | 4 | 4 | 4 | 0 | 1 |
| `basilar-artery-occlusion` | 5 | 5 | 7 | 7 | 0 | 4 |
| **Total** | **60** | **52** | **98** | **96** | **2** | — |

All covered facts retain their applicable locked refs. Every retained ref is
rendered inline and has an exact rendered `sourceDefinitions` entry. The
evidence builder derives `summaryBulletEvidence`, validation counters, note
status, source status, root status, manual queue, and
`coverageEvidenceSha256` from the lock and current notes.

### High-risk relationship preservation

- Aicardi `典型三主徵` appears exactly once and retains all three members:
  corpus callosal dysgenesis/agenesis, chorioretinal lacunae, and infantile
  spasms/early seizure.
- ALD `三區帶（Schaumburg zones,由中央向外）` appears exactly once and retains
  the ordered central, intermediate, and peripheral zones with their
  pathology, T1/T2/DWI/ADC, enhancement, and leading-edge relationships.
- Numeric and qualified facts remain attached to their governing subject,
  including 2-HG ppm/false-positive values, ALD ages/Loes thresholds,
  anti-NMDAR percentages, AT/RT distribution/survival, and BAO recanalization
  and mRS definitions.

## Exception-only literature research

Research was limited to:

- `adrenoleukodystrophy-f30`
- `adrenoleukodystrophy-f33`

Queries were restricted to Radiopaedia, RadioGraphics, and Radiology/RSNA.
No credential was handled, no access control was bypassed, and no restricted
PDF was downloaded.

### f30 — PML comparison

Readable results supported parts of the locked compound claim:

- a Radiopaedia PML case (DOI `10.53347/rID-22071`) showed an
  immunocompromised host, subcortical U-fiber involvement, and no abnormal
  enhancement;
- Hodel et al., *Radiology* 2016,
  DOI `10.1148/radiol.2015150673`, supported U-fiber involvement as a
  predictive PML feature.

They did not verify the complete locked compound comparison, especially the
general IRIS exception and absence of an adrenal association at
article/chapter level. No partial source was used to claim complete coverage.

### f33 — PRES comparison

A readable RadioGraphics review, *Imaging Patterns of Toxic and Metabolic
Brain Disorders*, DOI `10.1148/rg.2019190016`, supported posterior
parieto-occipital subcortical vasogenic edema, reversibility, hypertension,
and immunosuppressive/cytotoxic medication associations.

It did not verify the complete locked negative comparison that PRES
`通常不沿壓部呈進展性強化前緣`. The compound fact was not weakened or split
merely to claim coverage.

### Derived unresolved queue

```text
adrenoleukodystrophy-f30
adrenoleukodystrophy-f33
```

Both facts:

- are absent from the rewritten Summary;
- have `sourceRefs=[]`;
- retain `disposition=research-needed`;
- make only the ALD note `research-needed`;
- make the batch root `needs-review`;
- do not downgrade the nine verified sibling notes.

## Evidence and validation

- Evidence SHA-256:
  `7ec047f7188c5b8b1d07cf4bfa6aaa4cbecc7617a9b8fd71b8c5bab82c917289`.
- Trusted baseline file SHA-256 remains:
  `334c132f12d60c8f5eb51373a11fe97ea228d14d9c7729ee9953f1972c03e5d9`.
- Workflow remains:
  - sequence `2`;
  - predecessor `batch-01-anatomy`;
  - implementer `/root/phase2a_task3_2_impl`;
  - reviewer `/root/phase2a_task3_3_review`;
  - `reviewStatus=not-started`;
  - `reviewedBaselineSha256=null`.
- Batch root status: `needs-review`.
- Note statuses: 9 `verified`, 1 `research-needed`.
- Final dispositions: 98 = 96 covered + 2 research-needed.
- `newUnsupportedFacts=0` for all ten notes.
- Batch02 pre-review validator has exactly one finding:
  `phase2-review-sequence`, because terminal evidence awaits independent
  review. There are no content, source, structure, footnote, unsupported-fact,
  baseline, membership, predecessor, or manual-queue findings.

## Byte scope and generated output

For every selected Markdown file, replacing the current accepted Summary with
the locked `originalSummary` reconstructs the exact locked full-file SHA-256.
This proves all bytes outside the accepted Summary span are unchanged.

The scoped build selected exactly the ten assignment slugs.

- First run: 10 selected, 11 writes
  (10 selected detail paths plus `data/concepts-index.json`).
- Two selected details were newly created:
  - `data/concepts/2-hydroxyglutarate-idh-mutant-glioma.json`
  - `data/concepts/atypical-teratoid-rhabdoid-tumor.json`
- The other eight selected details and the index changed deterministically.
- No nonselected source or detail path appears in Git diff.
- Second identical scoped build: `實際寫入：0`.
- Current coherent corpus: 980 detail files and 980 index entries.
- All ten generated `keyPoints` arrays equal current accepted Summary bullets.
- Batch 03 baseline/evidence/generated paths are absent.

The approved Batch 01 artifacts remain byte-identical. Before Batch02 scoped
generation, Batch01 terminal `validate-batch --check-generated` was exact
`[]`. After the intentionally unsealed Batch02 writes, it has exactly one
expected `generated-manifest-mismatch` for the incomplete later generated
chain. Task 3.2 did not weaken that trust rule or create a premature seal.
Task 3.3 must create and independently seal the Batch02 generated observation,
after which Batch01 terminal validation must return exact `[]` again.

## Gates

| Gate | Result |
|---|---|
| Pre-edit Batch02 baseline | PASS: exact `[]` |
| Strict notes | PASS: 10/10 exact `[]` |
| Deterministic evidence | PASS |
| Fact dispositions | PASS: 98 total, 96 covered, 2 research-needed |
| Unsupported facts | PASS: 0 |
| Content/source/footnote/manual queue | PASS |
| Batch02 pre-review validation | Expected single `phase2-review-sequence` |
| Scoped build | PASS: selected ten only |
| Second scoped build | PASS: zero writes |
| Generated keyPoints | PASS: 10/10 |
| Corpus coherence | PASS: 980 details = 980 index entries |
| Full pytest | PASS: 155 |
| Direct audit smoke | PASS: `NR_SUMMARY_AUDIT_OK` |
| Direct build smoke | PASS: `BUILD_CONCEPTS_TEST_OK` |
| Four-file `py_compile` | PASS |
| Full lint | Exact inherited 2 errors / 124 warnings |
| Spectra strict validation | PASS |
| Spectra analyze | 0 Critical, 0 Warning, 2 pre-existing Suggestions |
| `git diff --check` | PASS |
| Batch03/scheduled artifacts | PASS: absent/unchanged |

Full lint remained:

```text
[footnote 未定義] ceap-classification.md 用了 [^*] 但無定義
[json 殘留 ![[...]]] 2022-264
小結：2 errors, 124 warnings
```

Neither inherited error belongs to a selected note.

## Changed files

Production content:

- ten selected `vault/concepts/<slug>.md` Summary spans;
- ten selected `data/concepts/<slug>.json` detail files;
- `data/concepts-index.json`;
- `docs/reports/nr-summary-rewrite/phase2a/evidence/batch-02-disease.json`.

Contract enforcement and tests:

- `scripts/nr_summary_audit.py`;
- `scripts/test_nr_summary_audit.py`;
- `scripts/test_build_concepts.py`.

Report:

- `tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-3-2-report.md`.

No baseline, trust digest, inventory, assignment, Batch 01 artifact, Batch 03
artifact, Phase 1 artifact, task checkbox, or scheduled note was changed.

## Concerns for independent review

1. ALD f30/f33 remain legitimately unresolved because readable allowed
   sources did not support the complete compound claims.
2. The generated corpus grew from the Batch01 historical 978 to 980 because
   two selected Batch02 details did not previously exist. Current index/detail
   coherence is exact; Task3.3 must seal the new 980-entry observation and
   re-establish the complete contiguous historical chain.
3. Until Task3.3 seals the later generated observation, Batch01 terminal
   generated validation intentionally reports the single fail-closed chain
   mismatch described above.
