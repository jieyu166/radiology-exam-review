# Independent review — Task 4.1, round 1

Verdict: **CHANGES_REQUESTED**

Reviewer: `/root/phase2a_task4_1_review`

Reviewed range: `f2b8153..290667d`

## Findings

### Critical

None.

### Important

1. **The required `git diff --check` gate does not pass.**

   Independent execution of:

   ```text
   git diff --check f2b8153..290667d
   ```

   returned:

   ```text
   tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-4-1-report.md:184: new blank line at EOF.
   ```

   This contradicts the implementation report's claim that the gate passed.
   Remove only the extra terminal blank line, rerun `git diff --check`, and
   submit the focused fix for re-review.

### Suggestions / downstream concern

1. `cerebrovascular-malformations` has three source headings of the form
   `## Summary（...）`, which are outside the accepted Summary-heading grammar.
   The locked empty projection is therefore an accurate representation of the
   current parser contract, not lost data within an accepted Summary span.
   However, Task 4.2 must not count this note as 10/10 covered or synthesize a
   Summary from zero locked facts. Resolve the heading contract through a
   separate source-preserving decision before rewriting this note, or keep the
   note explicitly blocked/unresolved.

2. The four empty-reference facts are correctly preserved rather than
   over-claimed:

   - `cns-opportunistic-infection-f06`
   - `dural-based-masses-aids-f04`
   - `dural-based-masses-aids-f05`
   - `dural-based-masses-aids-f06`

   Task 4.2 must not mark them covered without auditable source mapping.

## Independent fact-projection review

All ten source projections and all 69 statements / 94 fact units were
inspected in source order.

| Note | Statements | Facts | Review |
| --- | ---: | ---: | --- |
| `brain-tumor-imaging` | 5 | 7 | Four bullets plus factual callout body retained; callout label excluded. |
| `cerebral-infarction-fogging` | 5 | 5 | Numbers, timing, modality contrast, negations, and qualifier sequence retained. |
| `cerebral-microbleeds` | 8 | 11 | Distribution parent retained exactly once; all four nested causes inherit only the enclosing refs. |
| `cerebrovascular-malformations` | 0 | 0 | Exact current accepted projection: `headings=[]`, `originalSummary=""`, `facts=[]`. |
| `chemical-shift-artifact` | 19 | 34 | All 34 facts inspected; field strength/frequency/voxel/sequence distinctions, numbers, polarity, pitfalls, and factual callout body retained. |
| `cns-opportunistic-infection` | 5 | 7 | Factual callout retained; f06 is genuinely uncited in the source and remains empty-ref. |
| `cranial-nerve-muscle-atrophy` | 4 | 6 | Nerve list, sensory exclusions, and all temporal thresholds/signals retained. |
| `dural-based-masses-aids` | 6 | 7 | Semantic DDx parent retained exactly once with the child-ref union; f04–f06 correctly do not inherit a trailing sibling citation. |
| `facial-fracture-complications` | 14 | 14 | Four semantic syndrome/nerve parents and ten nested children retained in exact order with applicable enclosing ref. |
| `gbm-vs-pcnsl` | 3 | 3 | Comparison direction and listed discriminators retained. |

No footnote-definition or continuation line became a fact. No factual callout
body, semantic parent, ordered/unordered child, polarity, number, sequence,
location, distribution, or DDx contrast was lost.

## Empty-projection review

The new exception is fail-closed at both construction and validation:

- construction permits no facts only when there is no accepted Summary span,
  `originalSummary == ""`, and the derived templates are empty;
- validation additionally requires the exact triple
  `summaryHeadings=[]`, `originalSummary=""`, `factUnits=[]`;
- an accepted Summary with zero fact content and a forged empty lock hiding an
  accepted Summary are rejected.

Independent parser probes confirmed:

```text
accepted_summary 1 1
parenthesized_summary 0 0
```

This is sufficient for Task 4.1's pre-edit lock, but it creates the explicit
Task 4.2 concern above.

## Trust, sequencing, and mutation review

Independent targeted suite:

```text
12 passed, 150 deselected in 12.75s
```

It covered Batch 03 production projection, membership/fact/ref attacks,
registry shape, pending scaffold, coordinated replacement, predecessor
artifacts, zero-write sequencing, and relocated parity.

Additional exact registry probes confirmed:

```text
batch1_wrong_later_digest []
batch2_wrong_later_digest []
batch3_wrong_own_digest ['phase2-trusted-batch-lock-mismatch']
```

Thus the central registry is the exact three-batch active prefix, while Batch
01/02 validation does not incorrectly depend on the Batch 03 digest value.
Batch 03 still fails on its own wrong digest.

The two predecessor terminal validations and the current baseline validation
each returned exact `[]`:

```text
batch-01-anatomy validate-batch --check-generated []
batch-02-disease validate-batch --check-generated []
batch-03-pattern validate-baseline []
```

Approved predecessor artifact byte SHA-256 values match the report:

- Batch 01 baseline/evidence/generated:
  `6b05caff...a7934`, `0225a5e6...7f70b`, `bd1d2be1...bbbdb`
- Batch 02 baseline/evidence/generated:
  `334c132f...e5d9`, `0d58513e...51614`, `e2f069c3...55c0e`

No diff exists under concept Markdown, generated concept details/index, or any
Batch 01/02 baseline/evidence/generated artifact.

## Scaffold and canonical artifact review

- Batch 03 baseline byte SHA-256:
  `2c4de39b3d410f33009fb0613faeaa8d112080e4e5dcdbbcbae8e6b58fe2a3ae`
- Batch 03 canonical lock SHA-256:
  `3a93bfbe332067f06b5dda7ac47c6484107f52afd152059701f44ea3d7394e98`
- Batch 03 evidence byte SHA-256:
  `2a474f66730af8f541b2fd7024553132b548a3f1d83620fda920022bbf6104c4`

The pending evidence is honest and nonterminal: status `baseline`, sequence 3,
Batch 02 predecessor, null reviewer/reviewed digest, all facts pending, no
coverage anchors, no generated observation, and no terminal approval claim.

## Re-review scope

Re-review can be limited to the report EOF fix, `git diff --check`, and
confirmation that no production/test/artifact byte changed.
