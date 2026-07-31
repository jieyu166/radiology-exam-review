# Task 5.1 independent final review

## Verdict

`APPROVED`

- Critical: 0
- Important: 0
- Suggestion: 0
- Reviewer: `/root/phase2a_task5_1_final_review`
- Reviewed commit: `2e48db7`
- Correction base: `6a0e019`
- Base commit: `cc9feae`

All three Important findings are closed. `6a0e019` closed noncanonical output
paths and hidden root/nested artifacts. `2e48db7` closes the canonical
hard-link/no-follow gap with a single-link target gate, an exclusively created
same-directory temporary, identity checks, atomic directory-entry replacement,
post-write trust verification, and identity-safe cleanup. No new Critical,
Important, or Suggestion finding remains.

## Round 3 approval evidence

### Canonical writer behavior

Static review confirms:

- an existing canonical target must be regular, non-reparse, and
  `st_nlink == 1`;
- identical current bytes are re-read across stable `(st_dev, st_ino)` checks,
  verified against exact JSON and the code-owned tranche digest, and not
  rewritten;
- a changed or missing report uses `tempfile.mkstemp()` in the already
  validated Phase 2A directory;
- the temporary file is written through its exclusive descriptor,
  flushed/fsynced, and bound to its recorded identity;
- the exact root/section allowlist, temporary identity, and canonical target
  are revalidated immediately before `os.replace`;
- `os.replace` changes the canonical directory entry rather than following the
  old target;
- the resulting report is revalidated for regular/single-link shape, exact
  bytes, valid JSON, and the code-owned canonical digest;
- `finally` removes a temporary pathname only when it still identifies the
  exclusively created single-link file. A replaced path is not followed or
  deleted.

The helper catches only expected `OSError` and `Phase2LoadError` classes. It
adds no CWD/script-location fallback, unsafe glob, broad catch, or external
temporary directory.

### Independent fresh runtime evidence

```text
new atomic/hard-link regressions:
3 passed, 179 deselected in 35.30s

all Task 5.1 regressions:
10 passed, 172 deselected in 250.93s

real CLI upfront canonical hardlink:
exit 1 / phase2-path-invalid
unrelated sentinel SHA-256 and mtime unchanged
canonical path remains the hardlink

real CLI canonical identical two-run:
[] / []
raw SHA-256 f96af355b12523ef0665ba8371a4ab643415e0eb630f0d49a67ccc5b1508b5fa
mtime unchanged on both runs

real CLI missing canonical report:
[] / exit 0
created raw SHA-256 f96af355b12523ef0665ba8371a4ab643415e0eb630f0d49a67ccc5b1508b5fa

py_compile:
exit 0

three validate-batch --check-generated terminals:
[] / [] / []

strict validate-note:
30 checked / 0 failed

spectra strict:
valid

spectra analyze:
Coverage clean / Consistency clean / Gaps clean
2 inherited Suggestion-only artifact-ambiguity findings
0 Critical / 0 Warning

git diff --check cc9feae 2e48db7:
exit 0
```

The controlled post-preflight hard-link swap and injected replace failure
regressions also pass. They prove target-name change is rejected without
changing the sentinel, and replace failure preserves the canonical report and
removes only the owned temporary. The implementation report records a current
full run of `195 passed`; the independent reviewer additionally reran all ten
Task 5.1 high-risk tests and the direct gates above.

The cumulative `cc9feae..2e48db7` scope remains exact: tranche
validator/tests, the checked verification artifact, and implementation report.
There is no diff to concept Markdown, generated detail/index, inventory,
assignment, three batch locks/evidence/manifests, Phase 1, scheduled notes,
Phase 2B, or Spectra tasks.

## Round 2 finding (closed in `2e48db7`)

### Closed I3. Canonical report hard links bypassed the no-follow boundary

**Location:** `scripts/nr_summary_audit.py:3575-3587`,
`scripts/nr_summary_audit.py:7463-7470`

The new `_phase2a_lstat_is()` rejects symlinks and Windows reparse points, but
accepts every regular file without checking `st_nlink`. The final write then
uses `report_file.read_bytes()` and `report_file.write_bytes()`, which follow
an existing hard link. Consequently, enforcing the canonical path does not
ensure that only the canonical artifact inode is changed.

Confirmed with the real CLI in a complete shadow checkout:

```text
README.md initially contained HARDLINK_SENTINEL
verification.json was replaced by a HardLink to README.md

python scripts/nr_summary_audit.py validate-tranche \
  --repo-root <shadow> \
  --assignment docs/reports/nr-summary-rewrite/phase2-assignment.json \
  --report docs/reports/nr-summary-rewrite/phase2a/verification.json \
  --write

output: []
exit: 0
LinkType: HardLink
README sentinel preserved: false
README now begins with the Phase 2A tranche JSON
```

This is the same forbidden unrelated-file overwrite as round-1 I1, now through
the canonical pathname. It violates the single-artifact allowed-write scope,
preflight-zero-write safety, and requested no-follow/TOCTOU boundary.

**Minimal fix:** never update the checked report with an in-place path-following
write. Write deterministic bytes to a newly created regular temporary file in
the already validated Phase 2A directory, fsync/close as appropriate, then
atomically replace the canonical directory entry. Reject a present canonical
report with `st_nlink != 1`, and revalidate the parent/target immediately before
replacement. For the missing-report path, use exclusive creation or the same
atomic replacement flow. Add a real hard-link regression that asserts nonzero
or safe link replacement while the unrelated target's bytes and mtime remain
unchanged.

## Round 2 defense (closed in `2e48db7`)

The confirmed hard-link bypass does not require a race. Separately, there is
still a time window between the early artifact-tree `lstat` checks and the
final write. A symlink/reparse swap during the long preflight was not
independently reproduced in this environment, but the corrected atomic
replacement flow should explicitly close this window and receive a regression
that swaps the canonical entry after preflight begins.

**Round 3 closure evidence:** the writer now revalidates the target immediately
before an atomic directory-entry replacement. The controlled post-preflight
hard-link swap returns `phase2-path-invalid` and preserves the unrelated
sentinel. A real Windows symlink could not be created under the execution
identity; the static reparse checks and the same atomic replacement boundary
cover that path without an unsupported success claim.

## Round 1 findings (closed in `6a0e019`)

### Closed I1. Noncanonical `--report` overwrite

**Location:** `scripts/nr_summary_audit.py:7086`, `:7334`, `:7358`

`--report` accepts any repository-relative safe path. In write mode the code
sets `candidate = expected`, so it never reads or validates the existing target
as the canonical Phase 2A artifact. After a successful preflight it writes the
verification payload to that arbitrary path.

Independent minimal reproduction in a complete shadow checkout:

```text
README.md initially contained TASK51_SENTINEL

python scripts/nr_summary_audit.py validate-tranche \
  --repo-root <shadow> \
  --assignment docs/reports/nr-summary-rewrite/phase2-assignment.json \
  --report README.md \
  --write

output: []
exit: 0
README sentinel preserved: false
README now begins with the Phase 2A tranche JSON
```

This violates the Task 5.1 allowed-write scope, the single deterministic
checked-artifact contract, and the preflight-zero-write safety requirement. A
typo can destroy an unrelated tracked file even though every acceptance gate
passes.

**Minimal fix:** define one canonical report path constant,
`docs/reports/nr-summary-rewrite/phase2a/verification.json`, and reject every
other `--report` value with `phase2-path-invalid` (or a narrower stable report
path code) before lint or any write. Add RED/GREEN tests for an arbitrary safe
path, an existing unrelated file, and a non-existing unrelated path; all must
return nonzero with zero bytes/mtime drift.

**Round 2 closure evidence:** real subprocess calls for existing `README.md`
and absent `docs/not-the-tranche.json` both return exit 1 with
`phase2-path-invalid`. README content/mtime and the canonical report
SHA-256/mtime remain unchanged; the absent target is not created. Removing the
canonical report and invoking the canonical `--write` path succeeds only after
full preflight and recreates raw SHA-256
`f96af355b12523ef0665ba8371a4ab643415e0eb630f0d49a67ccc5b1508b5fa`.

### Closed I2. Nested/root scheduled or later-phase artifacts

**Location:** `scripts/nr_summary_audit.py:3571-3593`, `:4032`

`_phase2a_validate_artifact_scope()` examines only immediate files in the
three `baselines`, `evidence`, and `generated` directories:

```python
{path.name for path in section_root.iterdir() if path.is_file()}
```

It does not reject subdirectories or recursively discovered files, and it does
not inspect unexpected files/directories directly under the Phase 2A root.
Meanwhile `phase2BStarted` is emitted as the literal `False`, rather than being
supported by a complete absence check.

Independent minimal reproduction in a complete shadow checkout:

```text
added:
docs/reports/nr-summary-rewrite/phase2a/evidence/later/
  scheduled-disease-01.json

payload names /root/phase2b_impl and /root/phase2b_review

python scripts/nr_summary_audit.py validate-tranche \
  --repo-root <shadow> \
  --assignment docs/reports/nr-summary-rewrite/phase2-assignment.json \
  --report docs/reports/nr-summary-rewrite/phase2a/verification.json

output: []
exit: 0
```

This contradicts the tranche requirements that the 176 scheduled notes have
no Phase 2A lock/evidence/implementation/reviewer record and that later work
has not started. The existing regression covers only a direct extra JSON file,
so this bypass is not detected.

**Minimal fix:** validate the complete Phase 2A artifact tree. Require the
three known section directories to contain exactly the three expected regular
files and no nested entries, and require the Phase 2A root itself to contain
only the expected directories plus the canonical verification artifact.
Reject every unexpected file, directory, symlink/reparse target, or recursive
entry with `phase2a-scheduled-drift`. Add root-level and nested scheduled/later
artifact attacks and assert nonzero findings and no report write.

**Round 2 closure evidence:** the exact root allowlist and exact section
allowlists reject unknown root files, nested directories/files, non-regular
section entries, symlinks, and Windows reparse points with
`phase2a-scheduled-drift` before unknown entry contents are read. The two new
root/nested RED regressions are GREEN, and the canonical exact tree continues
to pass.

## Verified requirements that passed

- Commit scope is exact: only the tranche validator/tests, final verification
  artifact, and Task 5.1 implementation report changed. There is no diff to
  concept Markdown, detail JSON, corpus index, inventory, assignment,
  baselines, batch evidence/manifests, Phase 1 artifact, Spectra tasks, or
  Phase 2B content.
- Assignment/inventory gates report exactly
  `216 / 10 / 206 / 30 / 176`, inventory duplicates `0`, unclassified `0`,
  batch-00 `10`, unassigned `0`.
- All three `validate-batch --check-generated` commands return exact `[]`.
- All 30 active notes return exact `[]` under strict `validate-note`.
- The checked report derives 27 verified notes, 3 research-needed notes, and
  the exact sorted six-fact queue. Its root is honestly
  `phase2a-complete-with-manual-queue`, never `verified`.
- The three baseline/evidence/reviewer/generated-observation chains and all 30
  selected detail hashes validate; the current generated corpus is coherent at
  980 detail files and 980 index entries.
- The code-owned tranche digest rejects report extra keys, queue/status
  forgery, mutable generated resealing, selected-detail drift, and changed
  lint input. Phase 1 evidence and pilot hashes remain code-anchored.
- Live lint remains the exact two named inherited errors and 124 warnings with
  delta `{before: 124, after: 124, delta: 0, explanations: []}`.
- Relocated complete checkouts and changed CWD produce equal projections;
  unsafe assignment paths and incomplete checkouts fail closed.
- Tests contain no new skip, xfail, broad exception catch, or extra-key
  tolerance.

## Fresh verification evidence

```text
python -m pytest scripts/test_nr_summary_audit.py -q -k phase2a_task51
5 passed, 172 deselected in 165.80s

python -m pytest scripts/test_nr_summary_audit.py scripts/test_build_concepts.py -q
190 passed in 444.60s

python -m py_compile scripts/nr_summary_audit.py
  scripts/test_nr_summary_audit.py scripts/build_concepts.py
  scripts/test_build_concepts.py
exit 0

validate-assignment
216 total / 10 pilot / 206 non-pilot / 30 active / 176 scheduled / []

inventory --check
216 notes / 0 duplicate / 0 unclassified / batch-00 10 / unassigned 0

validate-batch --check-generated
batch-01-anatomy []
batch-02-disease []
batch-03-pattern []

validate-note
30 checked / 0 failed

spectra validate restructure-nr-concept-summaries-phase2a --strict
valid

spectra analyze restructure-nr-concept-summaries-phase2a --json
Coverage clean / Consistency clean / Gaps clean
2 inherited Suggestion-only Ambiguity findings
0 Critical / 0 Warning

git diff --check cc9feae 34e8b51
exit 0
```

## Round 2 fresh verification evidence

```text
new round-2 regressions:
2 passed, 177 deselected in 18.00s

all Task 5.1 regressions:
7 passed, 172 deselected in 183.31s

real CLI noncanonical existing/absent targets:
exit 1 / phase2-path-invalid
target bytes and mtime unchanged
canonical report bytes and mtime unchanged

real CLI missing canonical report:
[] / exit 0
created SHA-256 f96af355b12523ef0665ba8371a4ab643415e0eb630f0d49a67ccc5b1508b5fa

real CLI canonical hard-link attack:
[] / exit 0
unrelated README overwritten

three validate-batch --check-generated terminals:
[] / [] / []

strict validate-note:
30 checked / 0 failed

spectra strict:
valid

spectra analyze:
Coverage clean / Consistency clean / Gaps clean
2 inherited Suggestion-only Ambiguity findings
0 Critical / 0 Warning

git diff --check cc9feae 6a0e019:
exit 0
```

The full round-2 suite was not claimed as fresh reviewer evidence because it
was stopped after the confirmed hard-link blocker; the seven high-risk Task
5.1 tests and all direct gates above completed.

## Approval

Task 5.1 satisfies the implementation contract and is approved at `2e48db7`.
The exact six-fact manual queue remains an honest content concern, not a
mechanical or integrity failure; the root correctly remains
`phase2a-complete-with-manual-queue`.
