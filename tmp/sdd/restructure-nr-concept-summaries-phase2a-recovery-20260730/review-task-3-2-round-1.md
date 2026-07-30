# Task 3.2 independent review — round 1

## Verdict

`CHANGES_REQUESTED`

- Critical: 0
- Important: 3
- Suggestion: 0
- Reviewed range: `035cc8a..4b6d315`
- Reviewer: `/root/phase2a_task3_2_review`
- Implementer: `/root/phase2a_task3_2_impl`

The mechanical shape is largely correct: only the ten selected Markdown files
appear in the source diff, the evidence contains 98 facts with 96 `covered`
and exactly `adrenoleukodystrophy-f30` / `adrenoleukodystrophy-f33` marked
`research-needed`, all `newUnsupportedFacts` values are zero, all ten current
`validate-note` runs return `[]`, and current Batch02 validation has only the
expected pre-review `phase2-review-sequence` finding. Batch01 post-build
validation has only the expected pre-seal `generated-manifest-mismatch`.

The batch is not approvable because the rewritten text loses or weakens locked
semantic content, several bullets do not meet the requested short-card style,
and the new tests do not fail when a locked fact is deleted from the Summary.

## Important findings

### I1 — Five locked semantic details are omitted or weakened

Task 3.2 requires preservation of every locked subject, relationship,
qualifier, comparison, and terminology. The following facts are marked
`covered`, but their current bullets do not fully preserve the locked text.

1. `adrenoleukodystrophy-f08`

   - Locked:
     `可沿下行/上行纖維束累及視放射（visual）與聽放射（auditory pathway）、皮質脊髓束（projection fibres）。`
   - Current:
     `可沿纖維束累及 visual、auditory pathway 與 projection fibres。`
   - Lost:
     the `下行/上行` direction qualifier and the explicit structure
     terminology `視放射` / `聽放射` / `皮質脊髓束`.
   - Required:
     restore the direction qualifier and all three structure names while
     retaining their English terminology.

2. `adrenoleukodystrophy-f19`

   - Locked:
     `Loes score（嚴重度量化）：腦 MRI 評分系統,最高 34 分,評估白質受累位置／範圍＋局部或瀰漫性腦萎縮（含頂枕、額顳、胼胝體、視聽傳導路、投射纖維、基底節、小腦、腦幹）。`
   - Current:
     `腦 MRI 評分最高 34 分，涵蓋白質受累位置／範圍與局部或瀰漫性萎縮`
   - Lost:
     the complete locked site list: `頂枕、額顳、胼胝體、視聽傳導路、投射纖維、基底節、小腦、腦幹`.
   - Required:
     restore the complete list; it cannot remain marked `covered` while these
     locked details are absent.

3. `anti-nmda-encephalitis-f05`

   - Locked:
     `早期切除腫瘤 → 較佳預後。`
   - Current:
     `早期切除腫瘤可有較佳預後。`
   - Changed:
     the locked directional relationship is weakened to a possibility.
   - Required:
     preserve the locked relationship without adding a stronger causal claim
     than the source wording supports.

4. `atypical-teratoid-rhabdoid-tumor-f11`

   - Locked:
     `< 3 歲預後更差（約 30% 五年存活）；`
   - Current:
     `< 3 歲約 30% 五年存活`
   - Lost:
     the comparison `預後更差`.
   - Required:
     restore the comparison together with the approximately 30% five-year
     survival value.

5. `adrenoleukodystrophy-f31`

   - Locked:
     `Krabbe 與 MLD（metachromatic）`
   - Current:
     `Krabbe 與 MLD`
   - Lost:
     the locked English terminology `metachromatic`.
   - Required:
     restore the terminology; the user explicitly requires preserving
     original English medical terms.

These are direct fact-fidelity failures, not optional wording preferences.
After repair, regenerate evidence and generated output from the corrected
Summaries.

### I2 — Phase 2 coverage remains mechanically fail-open

`build_phase2_rewrite_evidence()` assigns every locked fact not named in
`research_needed_fact_ids` to `covered` and copies the locked source refs. It
does not bind each fact ID to a specific rewritten bullet or otherwise verify
that the locked semantic content remains in that bullet.

An independent shadow-checkout mutation deleted the complete content of
`2-hydroxyglutarate-idh-mutant-glioma-f05` from the Summary while leaving a
strict, sourced bullet. The builder still emitted:

```json
{
  "deletedLockedFact": "2-hydroxyglutarate-idh-mutant-glioma-f05",
  "forgedDisposition": "covered",
  "newUnsupportedFacts": 0
}
```

Batch validation produced only workflow review-sequence findings and no
fact-coverage or unsupported-fact finding. Therefore the new tests' assertions
that all 98 IDs/dispositions exist do not prove that all 98 locked facts are
actually represented.

This task does not require general-purpose semantic NLP. It does require a
deterministic, reviewer-auditable fact-to-bullet binding sufficient for this
production workflow. Add explicit fact IDs to per-bullet evidence (or an
equivalent deterministic mapping), enforce that:

- every `covered` fact appears exactly once;
- unresolved facts appear zero times;
- no fact is duplicated;
- bullet refs include the applicable refs for every mapped fact;
- mutation deletion of a mapped fact cannot regenerate as `covered` without a
  failing gate.

The implementation may still rely on independent human review for semantic
paraphrase quality, but the machine record must expose and enforce the mapping
instead of silently auto-covering every non-queued fact.

### I3 — Four compound bullets do not meet the short-bullet card contract

The brief requires short, retrieval-friendly top-level bullets. The following
current bullets remain slide-paragraph length:

- ALD `三區帶`: 328 characters;
- BAO `取栓後預後分層`: 229 characters;
- 2-HG `腫瘤類型`: 200 characters;
- Aicardi `典型三主徵`: 195 characters.

Split them into short bold-label bullets while preserving the locked grouping
and comparison semantics:

- ALD: state `三區帶（Schaumburg zones，由中央向外）` exactly once, then
  use separate sourced child-equivalent top-level bullets for `中央帶`,
  `中間帶`, and `周邊帶`, in that order.
- Aicardi: state `典型三主徵` exactly once, then use separate sourced
  child-equivalent top-level bullets for the three members.
- BAO: separate the best-prognosis group, the two worse comparison groups,
  intervention qualifier, and mRS definition, while keeping the comparative
  relationship explicit.
- 2-HG: separate IDH-mutant positive tumor types from the IDH-wild-type
  negative statement, preserving the 2021 WHO qualifier.

Every resulting top-level bullet must retain a bold label, defined inline
footnotes, and exact fact-to-bullet evidence. Do not duplicate the parent
context merely to satisfy coverage.

## Other verification evidence

- `git diff --name-status 035cc8a..4b6d315` shows only the ten selected concept
  Markdown files, their ten selected generated details, the corpus index,
  Batch02 evidence, audit/build tests, validator logic, and the Task3.2 report.
- The current evidence root is honestly `needs-review`.
- Counts independently inspected:
  - 60 locked source statements;
  - 98 locked facts;
  - 96 `covered`;
  - 2 `research-needed`;
  - 0 `newUnsupportedFacts`.
- Aicardi triad parent context appears once and the three members remain in
  order.
- ALD Schaumburg parent context appears once and the central/intermediate/
  peripheral order remains intact.
- Exception research did not promote partial PML/PRES sources to full
  coverage; no new research citation was added to claim support.
- Ten current `validate-note` commands returned exact `[]`.
- Current Batch02 `validate-batch` returned only
  `phase2-review-sequence`.
- Current Batch01 `validate-batch --check-generated` returned only
  `generated-manifest-mismatch`, consistent with the absent Task3.3 seal.
- `git diff --check 035cc8a..4b6d315` passed.

Full test-suite success reported by the implementer does not override the
confirmed semantic omissions or the demonstrated coverage mutation blind
spot. Round 2 should rerun the focused deletion mutation, strict notes,
evidence validation, scoped-build idempotency, generated parity, complete
tests, and Batch01/Batch02 chain checks after the fixes.
