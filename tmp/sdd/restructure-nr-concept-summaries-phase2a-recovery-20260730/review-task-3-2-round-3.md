# Task 3.2 independent review — round 3

## Verdict

`APPROVED`

- Critical: 0
- Important: 0
- Suggestion: 0
- Reviewed range: `3007b7f..605f5fc`
- Reviewer: `/root/phase2a_task3_2_review`
- Implementer: `/root/phase2a_task3_2_impl`

The round-2 label-only coverage defect is fixed without changing medical
content, production evidence, generated output, or the Batch01 legacy schema.
All round-1 and round-2 findings are closed.

## Core attack results

### Production long-label checksum reseal

The production Batch02 evidence was copied in memory and
`2-hydroxyglutarate-idh-mutant-glioma-f06` was forged to use only:

```json
{
  "bulletIndex": 4,
  "quote": "**IDH-mutant 腫瘤**"
}
```

After recomputing the mutable `coverageEvidenceSha256`, full Batch02
validation returned:

```text
evidence-fact-coverage
phase2-review-sequence
```

The required coverage error is now present. The remaining sequence finding is
the expected pre-review workflow gate.

### Long-label boundary cases

Using:

```text
- **ABCDEFGH**：ABCDEFGH。[^1][^3]
```

independent direct results were:

| Quote | Expected | Result |
|---|---:|---:|
| `**ABCDEFGH**` | reject | reject |
| `**ABCDEFGH**：A` | reject | reject |
| `ABCDEFGH` | accept | accept |
| `**ABCDEFGH**：ABCDEFGH` | accept | accept |

The validator now requires at least eight non-whitespace characters from the
medical body after the bold label and colon. Footnote-reference characters do
not count toward that body intersection. A long label can no longer subsidize
an otherwise empty or one-character body quote.

## Production evidence

- Covered facts: 96.
- Research-needed facts: 2.
- Clause anchors: 131.
- All 131 production anchors pass
  `_phase2_fact_coverage_is_valid()`.
- Production label-only anchors: 0.
- Unresolved non-null coverage values: 0.
- ALD f30 and f33 remain `research-needed` with `coverage: null`.
- `newUnsupportedFacts`: 0 for all ten notes.

No production anchor or checksum changed in this round.

## Prior finding closure retained

- The five locked semantic repairs remain present:
  ALD f08, f19, f31; anti-NMDAR f05; AT/RT f11.
- The 2-HG, ALD, Aicardi, and BAO long compound bullets remain split into
  short top-level sourced bullets.
- Aicardi triad context appears once with three sourced member bullets.
- ALD Schaumburg center-to-outside context appears once with ordered sourced
  zone bullets.
- The 96 covered facts retain reviewer-audited clause-level anchors.
- The two unresolved ALD facts remain omitted rather than partially promoted
  from the exception-research results.

## Mechanical verification

- Focused round3 regressions:
  `6 passed, 139 deselected`.
- The focused set covered:
  - forged long-label checksum reseal;
  - long-label boundary schema cases;
  - locked-clause deletion;
  - Batch02 deterministic evidence;
  - Batch01 deterministic reviewed evidence;
  - Batch01 legacy projection compatibility.
- Batch02 base validation:
  only `phase2-review-sequence`.
- Batch01 post-Batch02 pre-seal validation:
  only `generated-manifest-mismatch`.
- `git diff --check 3007b7f..605f5fc`: pass.
- Implementer-reported complete audit/build suite:
  `158 passed in 111.96s`.

The complete suite was not redundantly rerun because the round3 request
allowed focused verification and the independent core attacks exercised the
changed validator path directly.

## Diff and scope

The reviewed range changes only:

- `scripts/nr_summary_audit.py`;
- `scripts/test_nr_summary_audit.py`;
- the round-2 independent review report;
- the round-2 fix report.

Unchanged:

- all vault concept Markdown;
- Batch02 evidence and all 131 anchors;
- generated concept details and index;
- baseline locks and trust registries;
- assignment and inventory;
- Batch01 and Batch03 artifacts;
- scheduled notes and task checkbox.

Task 3.2 is ready for the controller to mark complete and proceed to the
separate Task 3.3 independent generated-output/review seal.
