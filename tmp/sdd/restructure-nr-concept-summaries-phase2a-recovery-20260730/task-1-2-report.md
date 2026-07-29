# Task 1.2 implementation report

## Result

- Status: DONE_WITH_CONCERNS
- Base: `5c3256e4c0e4db18e06657e1d8eb9245a0dba9a1`
- Scope: Spectra Task 1.2 only; the Task 1.2 checkbox remains unchanged for controller review.
- Production assignment: `docs/reports/nr-summary-rewrite/phase2-assignment.json`
- Synchronized inventory: `docs/reports/nr-summary-rewrite/inventory.json`

## TDD evidence

RED was established before production JSON was written:

1. Inventory batch/status synchronization:
   - RED: `test_phase2_assignment_rejects_inventory_batch_status_sync_mismatch`
   - Result: `1 failed, 96 deselected in 0.24s`
   - Expected `phase2-assignment-inventory-mismatch`; actual findings were empty.
   - GREEN: `1 passed, 96 deselected in 0.08s`.
2. Deterministic production APIs, exact arithmetic, and pilot preservation:
   - RED: three tests failed because synchronization, canonical assignment bytes,
     and exact count APIs did not exist.
   - Result: `3 failed, 97 deselected in 0.31s`.
   - GREEN: `3 passed, 97 deselected in 0.10s`.
3. CLI count reporting:
   - RED: relocated checked-production CLI returned only `[]`.
   - Result: `1 failed, 99 deselected in 0.29s`.
   - GREEN: `1 passed, 99 deselected in 0.15s`.
4. Closed synchronized-inventory schema:
   - RED: production inventory yielded 413 legacy Phase 1-only findings.
   - Result: `1 failed, 101 deselected in 0.24s`.
   - GREEN with legacy controls: `3 passed, 99 deselected in 0.09s`.
5. Production integration:
   - First post-write complete suite exposed that `inventory --check` still
     compared the synchronized inventory directly with pre-synchronization
     generation input.
   - Result: `112 passed, 1 failed in 48.94s`.
   - The check path now explicitly builds source inventory, derives assignment,
     synchronizes expected inventory, and validates the checked assignment.
   - Focused GREEN: `1 passed, 101 deselected in 0.62s`.

The fixed-active substitution control and duplicate/missing/type-drift controls
run against synchronized production fixtures. Their focused result was
`2 passed, 99 deselected in 0.17s`. The consolidated Task 1.2 deterministic
and mutation gate was `10 passed, 92 deselected in 0.09s`.

## Deterministic generation

Generation used the checked public APIs:

```python
assignment = build_phase2_assignment(source_inventory)
assignment_bytes = build_phase2_assignment_bytes(source_inventory)
synchronized = synchronize_phase2_inventory(source_inventory, assignment)
```

The production writer loaded the existing inventory, built two independent
assignment objects/byte sequences, required equality, synchronized a deep copy,
verified the pilot projection, and only then wrote canonical UTF-8 JSON with a
final newline.

Two additional independent Python processes regenerated the checked assignment:

- process 1: SHA-256
  `15e3aa72a77aa017423680186d0cb31c96a28cb4a978c4d7a8e712a0ccec59df`,
  10,864 bytes;
- process 2: the same SHA-256 and byte count, with `CHECKED_IDENTICAL` against
  the checked file.

Other production digests:

- `sourceInventorySha256`:
  `9a343b0184256033228ce42aa5ba9507e37a9dc4c8843b76c0cdf14030eadd9b`;
- synchronized `inventory.json` SHA-256:
  `b4289d4a25c225f4083a1ee4a0bbf2a83ec4baabdf4c8eee0f453a3321923131`.

## Production arithmetic and invariants

Final `validate-assignment` output:

```text
NR total: 216
Phase 1 pilots: 10
Phase 2 non-pilots: 206
Phase 2A active: 30
Scheduled: 176
[]
```

- 3 fixed active batches and 19 scheduled batches.
- Type totals remain 49 anatomy/measurement/management, 122 disease, and
  35 pattern-ddx.
- Only each type's final scheduled batch is short:
  `scheduled-anatomy-04` has 9, `scheduled-disease-12` has 2, and
  `scheduled-pattern-03` has 5.
- All other scheduled batches contain exactly 10 members.
- Every non-pilot occurs exactly once.
- All paths remain safe repository-relative POSIX paths.

## Phase 1 pilot and inventory proof

Canonical SHA-256 of the ten complete pilot objects:

- before:
  `b51f89e87fe63136b656fec5c51cff924b84d91704476f56afba9abe08c0348b`;
- after:
  `b51f89e87fe63136b656fec5c51cff924b84d91704476f56afba9abe08c0348b`.

The field-level comparison against base `5c3256e` proved:

- pilot objects changed: 0;
- non-pilot objects changed: 206;
- changed keys for every non-pilot: exactly `batch` and `status`;
- slug, path, type, sourceStatus, originalSha256, summaryHeadings, and all
  other content remained unchanged.

## Verification gates

- Production `inventory --check`: exit 0; 216 notes, 0 duplicates,
  0 unclassified, 10 `batch-00`, 0 unassigned.
- Production `validate-assignment`: exit 0; exact 216/10/206/30/176 counts;
  findings `[]`.
- Task 1.2 mutation/determinism regressions:
  `10 passed, 92 deselected in 0.09s`.
- Complete audit/build pytest:
  `113 passed in 50.26s`.
- Consolidated Phase 2, scoped-build, and explicit-root attacks:
  `41 passed, 72 deselected in 26.08s`.
- Direct Phase 1 audit smoke: `NR_SUMMARY_AUDIT_OK`.
- Direct Phase 1 build smoke: `BUILD_CONCEPTS_TEST_OK`.
- Four-file `py_compile`: exit 0.
- Spectra strict validation: valid, 0 errors, 0 warnings.
- Spectra artifact analysis: 0 Critical, 0 Warning; two pre-existing
  Suggestion-level ambiguity findings for later Summary/research scenarios.
- `git diff --check`: exit 0.
- `git diff --exit-code 5c3256e -- vault/concepts`: exit 0.
- `git diff --exit-code 5c3256e -- data/concepts data/concepts-index.json`:
  exit 0.
- Task 1.2 checkbox diff: none.
- No Phase 2A baseline, evidence, or generated production directories/files
  were created.

## Changed files

- `scripts/nr_summary_audit.py`
- `scripts/test_nr_summary_audit.py`
- `docs/reports/nr-summary-rewrite/inventory.json`
- `docs/reports/nr-summary-rewrite/phase2-assignment.json`
- `tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-1-2-report.md`

## Concerns

- Spectra analysis still reports two Suggestion-only ambiguity findings in
  later-task scenarios (`Invalid Summary grammar is rejected` and
  `Research supplies a permitted new fact`). They are outside Task 1.2 and are
  neither Critical nor Warning.
- Git emits an environment warning that the user-level
  `C:\Users\jai16\.config\git\ignore` is unreadable in the managed sandbox.
  Repository diff/status commands still completed successfully.
