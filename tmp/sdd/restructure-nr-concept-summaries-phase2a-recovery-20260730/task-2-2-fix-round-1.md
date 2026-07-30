# Task 2.2 scoped fix — review round 1

## Scope

- Base reviewed commit: `f111990da962ef6b5e3e378c0ba0b8277d343c4d`
- Findings fixed: the three Important findings in
  `review-task-2-2-round-1.md`
- No new medical fact, source, footnote, research result, reviewer approval, or
  Task 2.3 artifact was added.

## Exact corrections

1. `atlantodental-interval-f14`
   - restored the locked attribution `（Boden 等）` on the existing PADI
     `<14 mm` threshold bullet.
2. `cerebral-deep-venous-cortex-f04/f06/f08/f09/f10/f12/f14`
   - restored `三`;
   - restored the locked first-use ICV, BVR, quadrigeminal cistern, and vein of
     Galen terminology and Traditional Chinese aliases;
   - restored `前穿質`, `Sylvian 表淺中大腦靜脈`, `上吻合靜脈`,
     `下吻合靜脈`, `insula`, and `邊緣葉`.
3. `cerebral-deep-venous-cortex-f25/f30`
   - restored `同時` to preserve the CT co-occurrence relationship;
   - restored `神經外科術後（松果體或視丘區手術）`.

The existing deterministic rewrite-evidence builder regenerated
`docs/reports/nr-summary-rewrite/phase2a/evidence/batch-01-anatomy.json`.
The existing batch-scoped concept builder then regenerated selected details.
Only the two affected detail files changed:

- `data/concepts/atlantodental-interval.json`
- `data/concepts/cerebral-deep-venous-cortex.json`

## Verification

| Gate | Result |
|---|---|
| Strict `validate-note` | PASS, 10/10; each returned `[]` |
| Focused Task 2.2 pytest | PASS, 4 passed / 123 deselected |
| Complete audit/build pytest | PASS, 127 passed in 59.34 s |
| Non-Summary byte reconstruction | PASS via production regression test, 10/10 |
| Deterministic evidence regeneration | PASS via production regression test |
| Selected detail fresh-parser byte parity | PASS via generated-keyPoints regression test, 10/10 |
| Evidence fact projection | PASS: 121 total, 120 covered, 1 research-needed, 0 manual-review |
| Research/manual queue | PASS: sole entry `brain-herniation-syndromes-f03` with no replacement fact |
| Unsupported facts | PASS, 0 |
| Changed concept Markdown | PASS: exactly the two affected selected notes |
| Changed detail JSON | PASS: exactly the two affected selected details |
| Nonselected Markdown/detail writes | PASS, 0 |
| `data/concepts-index.json` | unchanged |
| Task 2.3 generated manifest | absent |
| Pre-review `validate-batch` | expected sole finding `phase2-review-sequence` |
| `spectra validate ... --strict` | PASS |
| `spectra analyze ... --json` | 0 Critical, 0 Warning; 2 pre-existing Suggestions |
| `git diff --check` | PASS |

Running `validate-batch --check-generated` before Task 2.3 additionally reports
the intentionally absent generated manifest. Therefore the binding Task 2.2
pre-review gate was run without `--check-generated`, matching the prior report;
its sole finding is:

```json
{
  "severity": "error",
  "code": "phase2-review-sequence",
  "message": "Terminal batch status requires approved review of this baseline."
}
```

## Final write scope relative to `f111990`

- `vault/concepts/atlantodental-interval.md`
- `vault/concepts/cerebral-deep-venous-cortex.md`
- `data/concepts/atlantodental-interval.json`
- `data/concepts/cerebral-deep-venous-cortex.json`
- `docs/reports/nr-summary-rewrite/phase2a/evidence/batch-01-anatomy.json`
- this scoped fix report
