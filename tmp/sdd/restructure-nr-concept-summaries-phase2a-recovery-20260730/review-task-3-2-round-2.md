# Task 3.2 independent review — round 2

## Verdict

`CHANGES_REQUESTED`

- Critical: 0
- Important: 1
- Suggestion: 0
- Reviewed range: `4b6d315..3007b7f`
- Reviewer: `/root/phase2a_task3_2_review`
- Implementer: `/root/phase2a_task3_2_impl`

The round-1 medical-content omissions, long compound bullets, and production
fact mappings are repaired. The remaining blocker is a demonstrated
fail-open coverage-anchor schema: a sufficiently long bold label can be used
as the sole quote for a covered medical fact.

## Important finding

### I1 — A long bold label is accepted as complete fact coverage

The fix report states that label-only coverage anchors are rejected.
`_phase2_coverage_anchor_is_valid()` currently checks:

- exact two-key anchor shape;
- one-based integer bullet index;
- trimmed quote of at least eight non-whitespace characters;
- quote is a substring of the bullet;
- the bullet renders all fact source refs.

It does not require the quote to come from the medical-content portion after
the bullet's bold label and colon.

Independent in-memory attack:

1. Loaded the current production Batch02 evidence.
2. Replaced the complete coverage for
   `2-hydroxyglutarate-idh-mutant-glioma-f06` with:

   ```json
   {
     "bulletIndex": 4,
     "quote": "**IDH-mutant 腫瘤**"
   }
   ```

3. Recomputed the mutable note-local `coverageEvidenceSha256`.
4. Ran `_phase2_coverage_anchor_is_valid()` and full Batch02 validation.

Observed:

```text
_phase2_coverage_anchor_is_valid = True
validate_phase2_batch codes = ["phase2-review-sequence"]
```

There was no `evidence-fact-coverage` finding, although the anchor contains
only the label and does not support the locked f06 facts:

- Diffuse astrocytoma and Anaplastic astrocytoma can show elevated 2-HG;
- the 2021 WHO integration into astrocytoma IDH-mutant grade 2–4.

The existing schema regression uses `**影像**`, which is rejected only because
it is shorter than eight non-whitespace characters. It does not exercise a
long label and therefore gives a false sense that label-only anchors are
generically rejected.

Required correction:

- derive the bold-label prefix from the strict bullet grammar;
- require every coverage quote to be an exact substring of the medical
  content after the closing bold label and colon, not merely anywhere in the
  full bullet;
- add a regression using a label of at least eight non-whitespace characters,
  such as the production `**IDH-mutant 腫瘤**` attack;
- repeat the checksum-reseal attack through full batch validation and require
  `evidence-fact-coverage`;
- retain Batch01's immutable legacy schema without anchors, while keeping
  Batch02 and every future active batch fail-closed.

The current 131 production anchors do not use label-only quotes, so this is a
validator/future-scale integrity defect rather than a new medical-content
loss. It is still Important because the stated purpose of the change is to
make coverage mechanically auditable for the remaining large note corpus.

## Round-1 finding closure

### Semantic fidelity

All five exact round-1 repairs are present and correctly anchored:

- `adrenoleukodystrophy-f08` restores `下行/上行`, 視放射
  (`visual`), 聽放射 (`auditory pathway`), and 皮質脊髓束
  (`projection fibres`).
- `adrenoleukodystrophy-f19` restores the full Loes site list:
  頂枕、額顳、胼胝體、視聽傳導路、投射纖維、基底節、小腦、腦幹.
- `adrenoleukodystrophy-f31` restores `MLD（metachromatic）`.
- `anti-nmda-encephalitis-f05` restores
  `早期切除腫瘤 → 較佳預後`.
- `atypical-teratoid-rhabdoid-tumor-f11` restores
  `< 3 歲預後更差（約 30% 五年存活）`.

No new research claim was introduced. ALD f30 and f33 remain omitted from
Summary and explicitly `research-needed`.

### Short-card structure

The four round-1 compound paragraphs were split correctly:

- 2-HG positive IDH-mutant and negative IDH-wild-type bullets;
- one ALD Schaumburg parent ordering bullet plus ordered central,
  intermediate, and peripheral child-equivalent top-level bullets;
- one Aicardi triad parent bullet plus three member bullets;
- BAO best group, worse groups, intervention requirement, and mRS definition.

The Aicardi triad parent appears once. The ALD center-to-outside parent appears
once. Each parent/member bullet retains applicable defined footnotes.

### Manual anchor audit

All 96 covered facts and all multi-anchor facts were reviewed against the
locked wording and current bullet text:

- 96 covered fact IDs;
- 131 exact clause-level anchors;
- no production label-only quote;
- no unresolved fact anchor;
- Aicardi triad and ALD zone context/order are fully represented;
- compound relationships, including BAO f06 across bullets 5–7, retain their
  comparison, values, and intervention qualifier.

The two unresolved facts have `coverage: null`.

## Mechanical verification

- Evidence: 98 facts = 96 `covered` + 2 `research-needed`.
- Clause anchors: 131.
- `newUnsupportedFacts`: zero for all ten notes.
- Generated keyPoints parity: 10/10.
- Current corpus: 980 detail files and 980 index entries.
- Strict note validation: 10/10 returned exact `[]`.
- Batch02 pre-review validation: only `phase2-review-sequence`.
- Batch01 post-Batch02 pre-seal validation: only
  `generated-manifest-mismatch`.
- Focused regressions:
  `3 passed, 141 deselected`, including forged deletion, schema, and
  deterministic evidence tests.

The forged deletion regression correctly rejects deletion of the 2-HG f05
clause. The focused schema suite nevertheless misses the longer-label attack
described above. A full suite rerun was intentionally not repeated after this
confirmed Important finding; round 3 should rerun it after the schema fix.

## Scope

The reviewed range changes only six selected Summary spans and their six
selected generated details, Batch02 evidence, coverage validator/tests, and
Task3.2 audit/report artifacts. No baseline, trust digest, assignment,
inventory, Batch01 artifact, Batch03 artifact, scheduled note, task checkbox,
or nonselected concept note was modified.
