# Task 6.1 Implementation and Verification Report

Date: 2026-07-29
Change: `restructure-nr-concept-summaries`
Scope: independently anchor the reviewed pre-edit `originalSha256` values for
the fixed 10 Phase 1 pilots.

## Outcome

Task 6.1 is implemented. The canonical Phase 1 inventory and batch validators
now bind both mutable evidence files to a code-owned map containing exactly the
10 reviewed pilot hashes. The deterministic inventory comparison no longer
copies its expected pilot hashes from the inventory under validation.

No medical prose, sources, facts, generated concept content, nonpilot output, or
Phase 2 state was changed.

## RED

The regression
`test_coordinated_pilot_hash_replacement_is_rejected_by_trusted_baseline`
loads the real reviewed inventory and batch, replaces
`acute-stroke-management.originalSha256` in both files with the same
syntactically valid value (`"0" * 64`), and runs both canonical validation
paths against temporary copies.

Before the implementation, both validations incorrectly accepted the
coordinated replacement:

```text
inventory exit: 0
NR notes: 216
Duplicate slugs: 0
Unclassified: 0
Batch 00: 10
Unassigned: 206

validate-batch exit: 0
Batch notes: 10
Missing sources: 0
[]
```

This reproduced the final re-review exploit without editing either checked-in
evidence file.

## GREEN

The smallest coherent implementation is:

1. `TRUSTED_PILOT_ORIGINAL_SHA256` stores exactly the 10 reviewed pre-edit
   hashes in `scripts/nr_summary_audit.py`, outside `inventory.json` and
   `batch-00.json`.
2. Canonical `inventory --check` applies those code-owned values to its expected
   deterministic projection. It never derives or preserves the pilot expected
   value from the mutable inventory being checked.
3. `validate_inventory_against_notes()` emits
   `inventory-trusted-baseline-mismatch` when an immutable pilot differs from
   the independent baseline. Nonpilot hashes remain compared with current note
   bytes and still emit `inventory-hash-mismatch` on drift.
4. Canonical batch loading compares both the sibling inventory and batch
   `originalSha256` values with the code-owned map. Any mismatch emits
   `evidence-trusted-baseline-mismatch`.
5. The regression first verifies that the trust map contains exactly the fixed
   10 slugs and that the unchanged reviewed inventory and batch both match all
   10 values. The coordinated replacement then produces nonzero results on both
   validation paths with the stable findings above.

The targeted GREEN run printed:

```text
COORDINATED_REPLACEMENT_GREEN
```

## Verification evidence

The shell did not expose a `python` command, so every Python command below was
executed with the equivalent installed interpreter:
`C:\Users\jai16\AppData\Local\Programs\Python\Python314\python.exe`.

### Audit and compilation

- `scripts/test_nr_summary_audit.py`: exit 0,
  `NR_SUMMARY_AUDIT_OK`.
- `python -m py_compile scripts/nr_summary_audit.py
  scripts/test_nr_summary_audit.py`: exit 0.
- `python -B scripts/test_build_concepts.py`: exit 0,
  `BUILD_CONCEPTS_TEST_OK`.

### Real inventory, batch, and notes

- Real canonical `inventory --check`: exit 0; 216 NR notes, 0 duplicate slugs,
  0 unclassified, 10 batch-00, 206 unassigned.
- Real `validate-batch docs/reports/nr-summary-rewrite/batch-00.json`: exit 0;
  10 notes, 0 missing sources, findings `[]`.
- Strict `validate-note` for each fixed pilot: 10/10 exit 0, each findings
  `[]`.

### Lint and generated outputs

- `scripts/lint_concepts.py --quiet`: expected exit 1; exactly 2 errors and
  124 warnings.
- The only errors remain the undefined `[^*]` in
  `ceap-classification.md` and the `![[...]]` JSON residue in question
  `2022-264`; no pilot error was reported.
- Generated index/detail count: 978/978.
- The real scoped build command was run twice:
  `python scripts/build_concepts.py --batch-file
  docs/reports/nr-summary-rewrite/batch-00.json --quiet`.
- SHA-256, byte length, and UTC mtime snapshots for all 978 detail files plus
  the index were identical before, after run 1, and after run 2.
- Git porcelain status was identical before, after run 1, and after run 2.

### Preserved Phase 1 state

- Root status: `needs-review`.
- Manual queue remains exactly:
  - `acute-stroke-management-f09`
  - `bilateral-subcortical-dwi-hyperintensity-ddx-f08`
  - `bilateral-subcortical-dwi-hyperintensity-ddx-f09`
  - `bilateral-subcortical-dwi-hyperintensity-ddx-f12`
- `phase2Started`: `false`.
- Generated manifest index/detail counts: 978/978.
- Canonical checkout-root enforcement, DOI parsing, all-Summary aggregation,
  generated-manifest validation, and scoped-build idempotence remain covered by
  the passing existing suites and real validation.

### Spectra and repository gates

- `spectra analyze restructure-nr-concept-summaries --json`: Coverage,
  Consistency, and Gaps clean; 7 pre-existing Ambiguity suggestions and no
  critical finding.
- `spectra validate restructure-nr-concept-summaries`: valid.
- `git diff --check`: pass.

## Scope review

The focused implementation changes are limited to:

- the four intentional ingested OpenSpec artifact edits;
- `scripts/nr_summary_audit.py`;
- `scripts/test_nr_summary_audit.py`;
- this report; and
- the Task 6.1 checkbox update performed only after all gates pass.

There are no changes to `vault/concepts`, `data/concepts`,
`data/concepts-index.json`, `docs/reports/nr-summary-rewrite/inventory.json`, or
`docs/reports/nr-summary-rewrite/batch-00.json`. No Phase 2 work was started.

## Concerns

- The repository still intentionally has the fixed lint baseline of 2 errors
  and 124 warnings.
- Spectra analyze still reports 7 non-blocking, pre-existing ambiguity
  suggestions about scenarios without concrete examples.
- The local shell lacks the `python` alias; verification used the installed
  Python 3.14 executable directly.
