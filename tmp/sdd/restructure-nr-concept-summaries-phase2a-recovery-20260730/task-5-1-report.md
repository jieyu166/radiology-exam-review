# Task 5.1 implementation report — Phase 2A tranche acceptance

## Outcome

- Status: `DONE_WITH_CONCERNS`.
- Implementer: `/root/phase2a_task5_1_impl`.
- Starting commit: `cc9feae`.
- Spectra Task 5.1 checkbox was not changed.
- No concept Markdown, detail JSON, corpus index, assignment, inventory,
  baseline, Phase 1 evidence, batch evidence/manifest, scheduled note, or
  Phase 2B artifact was changed.
- The only concern is the exact six-fact derived research queue. Mechanical,
  source-integrity, generated, lint, scope, and relocation gates pass.

## Interface and checked artifact

Added public interfaces:

```text
build_phase2a_tranche_verification(
    repo_root: Path,
    assignment_path: Path,
    lint_output: str,
    lint_exit_code: int,
    *,
    allow_missing_verification: bool = False,
) -> dict

validate_phase2a_tranche(
    repo_root: Path,
    assignment_path: Path,
    reviewed_report: object,
    lint_output: str,
    lint_exit_code: int,
    *,
    allow_missing_verification: bool = False,
) -> list[Finding]
```

Added CLI:

```text
python scripts/nr_summary_audit.py validate-tranche \
  --repo-root <repo-root> \
  --assignment docs/reports/nr-summary-rewrite/phase2-assignment.json \
  --report docs/reports/nr-summary-rewrite/phase2a/verification.json \
  [--write]
```

`--write` runs live lint and every assignment, scope, Phase 1, batch,
generated, and tranche trust preflight before writing. It uses deterministic
write-if-different behavior; a failing preflight writes nothing.

Checked artifact:

`docs/reports/nr-summary-rewrite/phase2a/verification.json`

- raw file SHA-256:
  `f96af355b12523ef0665ba8371a4ab643415e0eb630f0d49a67ccc5b1508b5fa`;
- canonical report observation SHA-256:
  `b53ea1fd1edfc2779c3f64ad25268883033b9d9227d34f601c66326397ecebd0`;
- bytes: 11,783;
- report shape is exact; missing and extra keys are rejected;
- one code-owned tranche observation digest authenticates the complete fresh
  projection. The mutable report cannot authenticate itself.

The projection contains:

- exact assignment digest and three active batches;
- each trusted baseline digest, approved reviewer, evidence-file digest,
  authenticated batch observation digest, and ten selected-detail hashes;
- current complete index hash/count, detail count/tree digest, and all 30
  selected-detail hashes;
- exact live lint projection and zero warning delta;
- trusted Phase 1 evidence path and exact active artifact paths;
- exact 216/10/206/30/176 scope arithmetic;
- `phase2BStarted=false`.

No `Path.cwd()`, script-location root fallback, canonical absolute-path
comparison, or broad exception catch was added. All persisted paths and
finding paths are repository-relative POSIX paths.

## Exact accepted tranche truth

- Inventory: 216 NR notes.
- Phase 1 pilots: 10.
- Phase 2 non-pilots: 206.
- Phase 2A active: 30 unique notes in the exact three fixed batches.
- Scheduled-not-started: 176.
- Trusted locks/evidence/reviews/generated observations: 3/3/3/3.
- Strict active notes: 30.
- Verified notes: 27.
- Research-needed notes: 3.
- Generated details/index: 980/980.
- Tranche status:
  `phase2a-complete-with-manual-queue`.
- `phase2BStarted=false`.

Exact derived sorted queue:

```text
adrenoleukodystrophy-f30
adrenoleukodystrophy-f33
brain-herniation-syndromes-f03
cns-opportunistic-infection-f03
cns-opportunistic-infection-f06
cns-opportunistic-infection-f07
```

The queue is derived from the three independently reviewed evidence reports.
It cannot be hidden by promoting the tranche to `verified`, changing a note
status, changing a disposition, or resealing only mutable JSON.

## Generated corpus binding

- Batch 01 manifest SHA:
  `bd1d2be10b9045c17b3f7ff540414623b8ecee4b6f2dd38f576aa3d118fbbbdb`
- Batch 01 observation SHA:
  `7adfa693cf5a178e1a393c250b1322f4e7ea4de990fdac16c0afae26f6f9cefd`
- Batch 02 manifest SHA:
  `e2f069c345410b018ac33b84fa7bfea98c4d0157e307973bf4d30dc8dea55c0e`
- Batch 02 observation SHA:
  `2011c04c8c9c0b681c2fd46faede583c39ed7e1a9a8299c2e354b3f904d47538`
- Batch 03 manifest SHA:
  `8de399a3c8a73c01479a2dc2a97a52675ee056312924331c3c8c1fde7b364c6d`
- Batch 03 observation SHA:
  `fa0bca4f69a2bcc8ee914aac4ce364e86dc260d272e65697b672f0481f49dec9`
- Final index SHA:
  `ae01c3105477a18c170238df777eed62556fdc199b80a60256d00a9cb3d9e35f`
- Final index entries: 980.
- Final detail files: 980.
- Final detail-tree SHA:
  `5d53aa489719c43f585c0fead74faf484e62fe9c30c6a6b14f1b10378d4f4ad9`
- Aggregate batch-manifest projection SHA:
  `0e3100ad088094d1e10781439ac174796845ed8ee68fe10dd7c3a1ee8464e86f`

All 30 generated `keyPoints` arrays are checked by the existing batch
validator against all accepted `## Summary` and
`## Summary — <nonblank suffix>` sections in source order. Non-Summary
sections remain excluded.

## TDD RED → GREEN

RED was observed before production code or the final artifact existed:

```text
5 failed, 172 deselected in 2.67s
```

Four failures were the absent public tranche function. The fifth was the
absent checked verification artifact.

Focused GREEN after implementation, direct attacks, relocation, CWD change,
and failed-write coverage:

```text
5 passed, 172 deselected in 167.86s
```

The focused tests exercise the real checked artifacts and complete relocated
216-note validation surface rather than mock batch state. The only mocked
boundary is live lint execution in the deliberately failed `--write` shadow
test; the linter's exact real output is tested separately and in production
CLI runs.

## Fail-closed attacks

Stable failures cover:

| Attack | Stable result |
|---|---|
| extra/missing/changed checked report field | `phase2a-tranche-manifest-mismatch` |
| wrong code-owned tranche digest | `phase2a-tranche-untrusted` |
| hidden queue or false root `verified` | `phase2a-tranche-manifest-mismatch` |
| true/missing/ambiguous Phase 2B flag | `phase2a-tranche-manifest-mismatch` |
| duplicate/wrong active membership | `phase2-assignment-membership` |
| forged reviewer identity | `phase2-reviewer-conflict` |
| forged derived batch queue | `phase2-manual-queue-mismatch` plus generated-chain finding |
| selected detail missing/changed | `generated-manifest-mismatch` |
| selected keyPoints mismatch | `generated-keypoints-mismatch` |
| selected manifest hash/reseal drift | `generated-manifest-mismatch` / `generated-observation-untrusted` |
| duplicate/missing/incoherent index | `generated-manifest-mismatch` |
| wrong final 980/980 count/tree | `generated-manifest-mismatch` |
| scheduled source byte drift | `phase2a-scheduled-drift` |
| extra scheduled evidence/lock/manifest | `phase2a-scheduled-drift` |
| Phase 1 evidence or pilot drift | existing code-owned Phase 1 trust finding |
| changed/missing/new lint error | `lint-baseline-mismatch` |
| unexplained warning delta | `lint-baseline-mismatch` |
| unsafe/absolute/escaping assignment/report path | `phase2-path-invalid` |
| incomplete relocated checkout | `phase2a-scheduled-drift` or owning missing-artifact finding |
| failed `--write` preflight | nonzero and checked report bytes unchanged |

Batch findings are collected in two phases: content/review/queue findings
first, generated-chain findings second. All unique findings are retained, so a
precise owning queue failure is not hidden by an earlier batch's generic
historical-chain failure.

## Verification evidence

### Full tests and direct gates

```text
python -m pytest scripts/test_nr_summary_audit.py
  scripts/test_build_concepts.py -q
190 passed in 435.31s

python scripts/test_nr_summary_audit.py
NR_SUMMARY_AUDIT_OK

python scripts/test_build_concepts.py
BUILD_CONCEPTS_TEST_OK

python -m py_compile scripts/nr_summary_audit.py
  scripts/test_nr_summary_audit.py scripts/build_concepts.py
  scripts/test_build_concepts.py
exit 0
```

### Assignment, inventory, batch, and strict-note gates

```text
validate-assignment:
216 total / 10 pilots / 206 non-pilots / 30 active / 176 scheduled
[]

validate-batch --check-generated:
batch-01-anatomy []
batch-02-disease []
batch-03-pattern []

inventory --check:
216 notes / 0 duplicate / 0 unclassified / batch-00 10 / unassigned 0

validate-note:
30/30 exact []
```

### Lint

Live full lint retains exactly:

```text
[footnote 未定義] ceap-classification.md 用了 [^*] 但無定義
[json 殘留 ![[...]]] 2022-264
```

Warnings remain exactly 124:

- missing `correctAnswer`: 65;
- missing question Dataview: 37;
- unreferenced footnote: 22.

The linter exits 1 because the two inherited errors intentionally remain; the
tranche parser requires that exact exit code and exact messages.

### Two-run write proof

Each of the three batch-scoped builds ran twice, followed by two
`validate-tranche --write` runs.

```text
SCOPED_AND_TRANCHE_TWO_RUN_OK
files = 982
byte drift = 0
mtime drift = 0
Git status drift = 0
```

The 982 paths are 980 detail JSON files, the complete index, and the final
verification artifact.

### Relocation and CWD independence

Two complete 216-note checkouts at different absolute depths produced:

- byte-identical verification JSON;
- identical canonical report digest;
- identical empty finding lists;
- identical selected/index/tree hashes;
- identical exit behavior.

Changing process CWD outside both checkouts did not change the relocated
result. An incomplete checkout and unsafe assignment paths fail closed.

### Spectra and diff

```text
spectra validate restructure-nr-concept-summaries-phase2a --strict
valid

spectra analyze restructure-nr-concept-summaries-phase2a --json
Coverage clean
Consistency clean
Gaps clean
2 inherited Suggestion-only Ambiguity findings
0 Critical / 0 Warning

git diff --check
pass
```

## Changed-file scope

Allowed changes only:

- `scripts/nr_summary_audit.py`;
- `scripts/test_nr_summary_audit.py`;
- `docs/reports/nr-summary-rewrite/phase2a/verification.json`;
- this implementation report.

There is no Task 5.1 diff to:

- `vault/concepts/*.md`;
- `data/concepts/*.json`;
- `data/concepts-index.json`;
- assignment or inventory;
- any baseline, batch evidence, or batch generated manifest;
- Phase 1 artifacts;
- the 176 scheduled notes;
- Spectra task checkboxes;
- Phase 2B or later-tranche artifacts.

## Concern

Six facts remain intentionally unresolved in the derived queue. The tranche
therefore cannot be called `verified`; its only honest terminal status is
`phase2a-complete-with-manual-queue`. This is a content limitation, not a
mechanical or integrity failure.

## Correction round 1 — independent review findings I1 and I2

The independent final review requested two Important corrections. Both were
first reproduced with exact RED regressions against commit `34e8b51`:

```text
pytest -k "task51_write_rejects_noncanonical or task51_recursive_scope"
2 failed, 177 deselected in 34.80s
```

- I1 reproduced an exit-0 overwrite of an existing unrelated `README.md`
  when passed as `validate-tranche --write --report`.
- I2 reproduced exit 0 for a nested later-phase artifact under
  `phase2a/evidence/later/`; the prior immediate-file scan did not see it.

Minimal fixes:

- `--write` now accepts exactly
  `docs/reports/nr-summary-rewrite/phase2a/verification.json`. Any other path
  fails before lint with stable code `phase2-path-invalid`, whether the target
  exists or not.
- The `phase2a` artifact tree now has an exact `lstat`-based allowlist. The
  root permits only `baselines/`, `evidence/`, `generated/`, and the canonical
  `verification.json`. Each section permits exactly the three active batch
  JSON regular files. Unknown root entries, nested entries, directories,
  symlinks, and Windows reparse points fail with
  `phase2a-scheduled-drift` before unknown entry contents are read.
- Only canonical write mode may temporarily omit `verification.json`, so an
  initial checked report can be created. The parent tree must still exactly
  match the allowlist. Read-only custom reports do not enter the Phase 2A
  artifact allowlist and still must exactly equal the fresh trusted
  projection.

Fresh GREEN evidence:

```text
new exact regressions:
2 passed, 177 deselected in 22.26s

original Task 5.1 regressions:
5 passed, 174 deselected in 175.89s

all Task 5.1 regressions:
7 passed, 172 deselected in 185.42s

full repository suite:
192 passed in 448.91s
```

Actual CLI attack and immutability evidence:

```text
--write --report README.md:
exit 1 / phase2-path-invalid
README bytes preserved: true
README mtime preserved: true

shadow nested artifact:
exit 1 / phase2a-scheduled-drift / report preserved: true

shadow root phase2b-review artifact:
exit 1 / phase2a-scheduled-drift / report preserved: true

canonical two-run write:
982 files / byte drift 0 / mtime drift 0 / Git status drift 0
```

Final gates:

```text
py_compile: exit 0
lint: exact 2 inherited errors / 124 warnings / exit 1
assignment: 216 / 10 / 206 / 30 / 176 / []
inventory: 216 / duplicates 0 / unclassified 0 / batch-00 10 /
  unassigned 0 / []
three validate-batch --check-generated terminals: [] / [] / []
strict validate-note: 30 checked / 0 failed
canonical validate-tranche --write: []
spectra strict: valid
spectra analyze: Coverage, Consistency, and Gaps clean; two inherited
  Suggestion-only Ambiguity findings; zero Critical or Warning
git diff --check: pass
```

Correction-round scope remains exactly:

- `scripts/nr_summary_audit.py`;
- `scripts/test_nr_summary_audit.py`;
- this Task 5.1 implementation report.

The checked verification artifact remained byte-identical, and there is still
no correction-round diff to concept Markdown, generated JSON/index, inventory,
assignment, baselines, evidence/manifests, Phase 1, scheduled notes, Phase 2B,
or Spectra task checkboxes.

## Correction round 2 — hardlink-safe atomic report replacement

Independent review I3 confirmed that a canonical `verification.json` hardlink
still reached the old in-place `Path.write_bytes()` call and overwrote its
unrelated link peer. Three exact RED regressions reproduced the write-boundary
failure before production code changed:

```text
round-2 RED:
3 failed, 179 deselected in 53.36s
```

- an upfront canonical hardlink overwrote a README sentinel;
- a controlled hardlink swap after tranche preflight overwrote a second
  sentinel;
- an injected `os.replace` failure had no effect because the old path still
  used in-place `write_bytes`, so the canonical file drifted.

The final write boundary now:

- rejects a present canonical target unless `lstat` identifies a regular,
  non-reparse, single-link file; failures return stable
  `phase2-path-invalid` before lint or mutation;
- permits a missing canonical report only for the exact canonical write path;
- creates one exclusive temporary regular file in the already validated
  Phase 2A parent;
- writes through its file descriptor, then flushes and `fsync`s it;
- records the exclusive file identity and revalidates the complete exact
  parent tree, the temporary identity, and the canonical target immediately
  before replacement;
- uses `os.replace` to atomically replace the canonical directory entry,
  without truncating or following the prior entry;
- revalidates the resulting target as regular/single-link and checks exact
  bytes plus the code-owned canonical tranche digest;
- cleans up a temporary path only if it still has the exact identity of the
  exclusively created file. A swapped or attacker-owned path is never
  followed or removed.

Fresh GREEN evidence:

```text
round-2 new regressions:
3 passed, 179 deselected in 33.98s

all Task 5.1 regressions:
10 passed, 172 deselected in 219.57s

full repository suite:
195 passed in 483.62s
```

Real complete-shadow subprocess evidence:

```text
upfront canonical hardlink:
exit 1 / phase2-path-invalid
README sentinel bytes and mtime preserved: true
canonical path remains the hardlink: true

controlled post-preflight hardlink swap:
exit 1 / phase2-path-invalid
README sentinel bytes and mtime preserved: true
canonical path remains the hardlink: true

missing canonical report:
[] / exit 0
created raw SHA-256:
f96af355b12523ef0665ba8371a4ab643415e0eb630f0d49a67ccc5b1508b5fa

canonical two-run write:
[] / []
982 files / byte drift 0 / mtime drift 0 / Git status drift 0
```

A real Windows symlink attack was attempted but could not be created because
the execution identity lacks symlink privilege (`WinError 1314`). The same
no-follow boundary rejects the Windows reparse attribute before any read or
write; the independently reproducible hardlink attacks exercise the confirmed
I3 vulnerability and the post-preflight write window without relying on
symlink privilege.

Final gates:

```text
py_compile: exit 0
lint: exact 2 inherited errors / 124 warnings / exit 1
assignment: 216 / 10 / 206 / 30 / 176 / []
inventory: 216 / duplicates 0 / unclassified 0 / batch-00 10 /
  unassigned 0 / []
three validate-batch --check-generated terminals: [] / [] / []
strict validate-note: 30 checked / 0 failed
spectra strict: valid
spectra analyze: Coverage, Consistency, and Gaps clean; two inherited
  Suggestion-only Ambiguity findings; zero Critical or Warning
git diff --check: pass
```

Correction-round scope remains exactly:

- `scripts/nr_summary_audit.py`;
- `scripts/test_nr_summary_audit.py`;
- this Task 5.1 implementation report.

The checked verification artifact remains byte-identical. No artifact,
concept content, generated JSON/index, inventory, assignment, batch evidence,
Phase 1 data, scheduled note, Phase 2B file, or Spectra task checkbox changed.
