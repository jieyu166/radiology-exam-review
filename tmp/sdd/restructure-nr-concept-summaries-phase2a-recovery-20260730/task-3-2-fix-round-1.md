# Task 3.2 review round 1 fixes

## Result

`DONE_WITH_CONCERNS`

All three Important findings in
`review-task-3-2-round-1.md` were addressed. Mechanical, semantic, coverage,
generation, and Spectra gates pass. The two previously retained ALD facts
remain `research-needed`; independent Task 3.3 review is still required.

## Finding closure

### 1. Locked semantic fidelity

- ALD f08 now explicitly preserves the descending/ascending tract direction
  and the visual, auditory, and corticospinal tract aliases.
- ALD f19 restores the full Loes site list: parieto-occipital,
  frontotemporal, corpus callosum, visual/auditory pathways, projection
  fibres, basal ganglia, cerebellum, and brainstem.
- ALD f31 restores `MLD (metachromatic)`.
- Anti-NMDAR f05 restores `early tumour removal -> better prognosis`.
- AT/RT f11 restores the worse prognosis below age 3 with the qualified
  approximately 30% five-year survival figure.

### 2. Fail-closed covered-fact evidence

For Batch02 and later evidence:

- every covered fact requires a nonempty, duplicate-free `coverage` array;
- every anchor has exactly `bulletIndex` and `quote`;
- indexes are one-based integers and Boolean values are rejected;
- quotes must be exact current-bullet substrings with at least eight
  non-whitespace characters;
- the selected bullet must render every source reference required by that
  fact;
- unresolved facts must explicitly store `coverage: null`;
- missing, stale, malformed, short, label-only, source-incomplete, duplicate,
  or extra-key anchors emit `evidence-fact-coverage`;
- Batch01 remains byte/checksum compatible and rejects the new field.

The independent mapping artifact covers all 96 covered facts with 131
clause-level anchors. ALD f30/f33 are the only exclusions and remain
`research-needed`. The formal production validator reports zero mapping
failures and zero fact/bullet semantic disagreements.

The forged-checksum deletion attack removes the locked 2HG f05 clause while
resealing the mutable snapshot. With otherwise valid production evidence, the
attack is rejected as `evidence-fact-coverage`.

### 3. Short-card structure

- 2HG tumour-type content is split into positive IDH-mutant and negative
  IDH-wild-type bullets.
- ALD Schaumburg zones are split into a parent ordering bullet and
  central/intermediate/peripheral child bullets.
- Aicardi triad is split into one parent and three member bullets.
- BAO outcome content is split into best group, worse groups, intervention
  need, and mRS definition.

All child and parent bullets retain the applicable Obsidian footnotes.

## Production evidence

- Covered facts: `96`
- Research-needed facts: `2`
- Clause anchors: `131`
- Unresolved coverage values: exactly two `null`
- `newUnsupportedFacts`: `0` for all ten notes
- Evidence file SHA-256:
  `8a083f8fe0943a4cad73c757715697e16a5e2621bdb982df47dc6584d6478eaf`
- Batch02 base validation: exactly one expected
  `phase2-review-sequence`; no coverage, structure, source, footnote, manual
  queue, unsupported-fact, or baseline finding.

## Verification

| Gate | Result |
|---|---|
| Strict note validation | PASS: 10/10 exact `[]` |
| Independent anchor audit | PASS: 96/96 facts, 131 anchors, 0 failures |
| Builder with audited mapping | PASS |
| Deterministic evidence | PASS |
| Semantic fidelity regressions | PASS |
| Forged-checksum deletion attack | PASS |
| Coverage schema attacks | PASS |
| Scoped build | PASS |
| Second scoped build | PASS: 13 detail/index targets with zero hash/mtime drift |
| Full pytest | PASS: `157 passed in 108.94s` |
| Direct audit smoke | PASS: `NR_SUMMARY_AUDIT_OK` |
| Direct build smoke | PASS: `BUILD_CONCEPTS_TEST_OK` |
| Four-file `py_compile` | PASS |
| Full lint | Exact inherited `2 errors, 124 warnings` |
| Spectra strict validation | PASS |
| Spectra analyze | 0 Critical, 0 Warning, 2 pre-existing Suggestions |
| `git diff --check` | PASS |

The inherited lint errors remain only:

```text
[footnote 未定義] ceap-classification.md 用了 [^*] 但無定義
[json 殘留 ![[...]]] 2022-264
```

## Scope

The round-1 fix changes:

- six Batch02 Summary spans and their six generated detail JSON files;
- the Batch02 evidence artifact;
- the fail-closed coverage implementation and tests;
- the review, mapping, mapping-audit, executable helper, and this fix report.

No baseline lock, trust digest, inventory, assignment, Batch01 artifact,
Batch03 artifact, scheduled note, nonselected concept note, or task checkbox
was modified.

## Remaining concerns

1. `adrenoleukodystrophy-f30` and `adrenoleukodystrophy-f33` remain explicitly
   `research-needed`; they are not represented as covered.
2. Task 3.3 must independently review the repaired content, source mapping,
   generated observation, and the two-item manual queue before Batch02 can be
   approved or Batch03 can start.
