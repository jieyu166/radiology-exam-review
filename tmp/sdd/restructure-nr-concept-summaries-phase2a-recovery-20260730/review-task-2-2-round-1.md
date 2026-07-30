# Task 2.2 recovery independent review — round 1

## Verdict

`CHANGES_REQUESTED`

- Reviewed commit: `f111990da962ef6b5e3e378c0ba0b8277d343c4d`
- Reviewer: `/root/phase2a_task2_2_review_recovery`
- Critical: 0
- Important: 3
- Suggestion: 0
- Production files edited by reviewer: none

The automated gates are clean apart from the intentionally unapproved
`phase2-review-sequence`, but manual comparison of all 121 sealed facts found
three binding-fidelity gaps. The affected facts are currently recorded as
`covered`; therefore Task 2.2 is not ready to be checked complete.

## Findings

### Important 1 — `atlantodental-interval-f14` loses its locked attribution

Evidence:

- The sealed fact is: `PADI 臨界值 <14 mm（Boden 等）：對神經學缺損的敏感度 97%；`.
- `vault/concepts/atlantodental-interval.md:30` rewrites it as
  `<14 mm 對神經學缺損的敏感度 97%` and omits `（Boden 等）`.
- Evidence still marks `atlantodental-interval-f14` as `covered`
  (`batch-01-anatomy.json` evidence around line 301).

Why Important:

Task 2.2 requires every sealed fact to preserve its qualifiers and source
framing. This is a locked, source-attributed threshold, not a newly optional
label.

Minimal correction:

Restore the attribution in the existing bullet, for example:

`- **PADI 臨界值**：<14 mm（Boden 等）對神經學缺損的敏感度 97%；...[^3]`

Then regenerate the deterministic evidence and selected detail JSON.

### Important 2 — deep-venous anatomy drops locked first-use terminology

Affected facts and current lines:

- `cerebral-deep-venous-cortex-f04`, line 23: drops `三` and the locked
  first-use expansions `internal cerebral veins（ICV，內大腦靜脈）`,
  `basal veins of Rosenthal（BVR，Rosenthal 基底靜脈）`,
  `四疊體池（quadrigeminal cistern）`, and
  `vein of Galen（Galen 大靜脈）`; the rewrite leaves acronyms or
  English-only terms.
- `cerebral-deep-venous-cortex-f06`, line 25: drops the Traditional Chinese
  term `前穿質` while retaining only `anterior perforated substance`.
- `cerebral-deep-venous-cortex-f08`, line 27: drops
  `Sylvian 表淺中大腦靜脈`.
- `cerebral-deep-venous-cortex-f09`, line 28: drops `上吻合靜脈`.
- `cerebral-deep-venous-cortex-f10`, line 29: drops `下吻合靜脈`.
- `cerebral-deep-venous-cortex-f12`, line 31: drops the locked alias
  `insula`.
- `cerebral-deep-venous-cortex-f14`, line 33: drops the locked translation
  `邊緣葉` from `limbic（邊緣葉）`.

Why Important:

The binding brief explicitly says to preserve Traditional Chinese and the
original terminology. In particular, line 23 makes the entire Summary use
`ICV` and `BVR` without retaining their locked anatomical expansions. These
facts are nevertheless all marked `covered`.

Minimal correction:

Restore the missing parenthetical expansions in the same bullets; no new
medical fact or source is needed. Keep the card layout, for example define the
full ICV/BVR/Galen names in the `深部三主幹` bullet and restore the short
bilingual aliases on lines 25 and 27–33. Then regenerate evidence and selected
detail JSON.

### Important 3 — deep-venous rewrite drops a simultaneous CT relationship and a postoperative qualifier

Affected facts:

- `cerebral-deep-venous-cortex-f25`, line 44: the locked source says the
  listed deep veins are hyperattenuating **同時** with the preceding CT
  parenchymal finding. Splitting f24/f25 into separate bullets is acceptable,
  but removing `同時` loses the locked co-occurrence relationship.
- `cerebral-deep-venous-cortex-f30`, line 49: the locked qualifier is
  `神經外科術後（松果體/視丘區手術）尤須警覺`; the rewrite shortens this to
  `松果體或視丘區術後`, dropping that the context is neurosurgical surgery.

Why Important:

The brief explicitly forbids splitting away or dropping a governing
relationship or qualifier. Both facts are marked `covered`, so the evidence
currently overstates complete coverage.

Minimal correction:

- Begin the line-44 finding with `同時，...` or otherwise explicitly link it
  to the CT parenchymal finding.
- Restore `神經外科術後（松果體或視丘區手術）` on line 49.

Regenerate evidence and selected detail JSON after the text changes.

## Full 121-fact review

I manually compared, in sealed order, every baseline `factUnits[].text` and
`sourceStatement` against the ten rewritten Summary spans and their evidence
dispositions:

| Note | Sealed facts | Manual result |
|---|---:|---|
| `ajcc-8th-head-neck-n-staging` | 6 | otherwise faithful |
| `aneurysm-coiling-recurrence` | 4 | faithful |
| `atlantodental-interval` | 27 | f14 finding above |
| `brachial-plexus-anatomy` | 9 | faithful |
| `brain-herniation-syndromes` | 3 | f01–f02 covered; f03 correctly unresolved |
| `carotid-vertebrobasilar-anastomoses` | 7 | faithful |
| `cerebral-border-zone-infarct-arteries` | 11 | faithful |
| `cerebral-deep-venous-cortex` | 40 | findings above |
| `cerebral-herniation-types` | 7 | faithful |
| `cerebral-infarction-evolution` | 7 | faithful |
| **Total** | **121** | **120 declared covered, 1 research-needed** |

`brain-herniation-syndromes-f03` is handled exactly as required:

- absent from the rewritten Summary;
- `disposition=research-needed`;
- `sourceRefs=[]`;
- note/root status remains non-verified as applicable;
- the only `manualReviewFactIds` entry.

No unsupported replacement was smuggled into another bullet.

## Independent verification

### Content, source, and workflow

- 10/10 `validate-note`: exit 0, `[]`.
- Pre-review `validate-batch`: exactly one finding,
  `phase2-review-sequence` with message
  `Terminal batch status requires approved review of this baseline.`
- Evidence projection: 121 facts; 120 `covered`; 1 `research-needed`;
  0 `manual-review`; 27 existing-footnote definitions;
  `newUnsupportedFacts=0`; queue exactly
  `brain-herniation-syndromes-f03`.
- All rewritten lines satisfy flat bold-label + inline defined-footnote
  grammar. The Important findings above are semantic coverage defects that the
  marker-based automated test does not detect.

### Tests

- Focused Task 2.2 tests: `5 passed, 122 deselected`.
- Complete audit/build suite: `127 passed in 76.98s`.

### Byte and write scope

- Replacing each current rewritten Summary with its sealed
  `originalSummary` reconstructs the sealed whole-file SHA-256 for all 10
  notes: 10/10.
- The commit changes no nonselected concept Markdown and no nonselected detail
  JSON.
- `data/concepts-index.json` is unchanged from the Task 2.2 base.
- No batch-02, batch-03, scheduled, or generated Task 2.3 artifact exists.
- `git diff --check` passes and the worktree was clean before this review
  report was added.

### Generated output

- Selected evidence bullets equal selected generated `keyPoints`: 10/10.
- Per-note counts match exactly:
  `5, 4, 25, 8, 2, 5, 11, 40, 7, 7`.
- Detail/index corpus is coherent: 978 detail files, 978 index entries, exact
  slug-set parity.
- Eight selected JSON files contain deterministic parser normalization beyond
  `keyPoints`, all within the permitted selected paths:
  - AJCC: `externalLinks`
  - aneurysm recurrence: `externalLinks`
  - atlantodental interval: `differentialDiagnosis`
  - brachial plexus: `externalLinks`, `imagingFindings`, `management`
  - carotid-vertebrobasilar anastomoses: `externalLinks`
  - border-zone infarct: `externalLinks`
  - deep venous cortex: `differentialDiagnosis`, `externalLinks`
  - cerebral herniation types: `externalLinks`

The checked-in selected detail bytes equal fresh parser output, so this
normalization is reproducible and is not itself a review finding.

## Re-review requirements

1. Correct the exact affected bullets without adding new medical content.
2. Regenerate `batch-01-anatomy` evidence and the affected selected detail
   JSON.
3. Re-run 10 strict notes, focused/full tests, byte-scope reconstruction,
   selected keyPoints parity, nonselected scope, and pre-review batch
   validation.
4. The only remaining machine finding may again be
   `phase2-review-sequence`; request scoped re-review of the three findings
   above before Task 2.2 is marked complete.
