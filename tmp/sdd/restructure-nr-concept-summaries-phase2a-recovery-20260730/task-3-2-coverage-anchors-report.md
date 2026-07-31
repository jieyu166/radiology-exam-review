# Task 3.2 coverage-anchor audit

- Result: `DONE`
- Covered fact IDs mapped: `96/96`
- Clause-level anchors: `131`
- Contract failures from `_phase2_fact_coverage_is_valid`: `0`
- Fact/bullet semantic disagreements: `0`
- Impossible mappings: `0`

## Per-note fact counts

| Note | Covered facts mapped |
|---|---:|
| `2-hydroxyglutarate-idh-mutant-glioma` | 7 |
| `adrenoleukodystrophy` | 34 |
| `aicardi-syndrome` | 8 |
| `als-imaging` | 4 |
| `angioinvasive-aspergillosis` | 6 |
| `anti-nmda-encephalitis` | 7 |
| `arterial-dissection-mri` | 7 |
| `atypical-teratoid-rhabdoid-tumor` | 12 |
| `autoimmune-encephalitis` | 4 |
| `basilar-artery-occlusion` | 7 |

## Unresolved exclusions

- `adrenoleukodystrophy-f30`: excluded from anchors; remains `research-needed`.
- `adrenoleukodystrophy-f33`: excluded from anchors; remains `research-needed`.

## Audit notes

- JSON keys follow approved baseline note/fact order.
- Every anchor is an exact substring of its 1-based current Summary bullet.
- Every quote has at least eight non-whitespace characters and is not label-only.
- Every selected bullet renders all `sourceRefs` required by its mapped fact.
- Compound facts use multiple clause anchors where needed.
- `basilar-artery-occlusion-f06` is explicitly bound across bullets 5, 6, and 7.
- Aicardi triad parent and three members are independently bound in source order.
- ALD Schaumburg center-to-outside parent and central/intermediate/peripheral children are independently bound in source order.
- The five round-1 fidelity repairs are directly anchored: ALD f08, f19, f31; anti-NMDA f05; AT/RT f11.
