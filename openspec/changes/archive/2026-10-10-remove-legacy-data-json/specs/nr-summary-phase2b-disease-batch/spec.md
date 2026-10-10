## MODIFIED Requirements

### Requirement: Verifiable 100-note batch acceptance

A Phase 2B note MUST NOT be marked verified unless its source hash, lossless pre-edit Summary lock, Summary structure, footnotes, and fact coverage all pass with `newUnsupportedFacts` equal to zero. The 100-note tranche MUST NOT be accepted unless every sub-batch has an independent approved review and the derived manual queue matches every unresolved fact ID. Acceptance evidence SHALL be recorded under `docs/reports/nr-summary-rewrite/phase2b/` and SHALL remain byte-for-byte unchanged after the audit tooling is retired. Acceptance MUST NOT depend on any generated JSON under `data/`; the vault Summary section is the final published form of each note.

#### Scenario: Block publication when a fact lacks coverage

- **WHEN** any locked fact unit has no covered, research-needed, or manual-review disposition
- **THEN** validation fails and the note and its sub-batch remain unverified

##### Example: Missing disposition

- **GIVEN** `brain-abscess-f03` is present in the baseline lock and absent from every evidence disposition
- **WHEN** batch validation runs
- **THEN** validation reports fact-coverage failure and does not mark `brain-abscess` verified

#### Scenario: Preserve sealed evidence after tooling retirement

- **WHEN** the audit scripts are deleted from `scripts/`
- **THEN** every file under `docs/reports/nr-summary-rewrite/phase2b/` keeps the same SHA-256 as in the preservation commit, and the vault Summary sections of the 100 notes are unchanged
