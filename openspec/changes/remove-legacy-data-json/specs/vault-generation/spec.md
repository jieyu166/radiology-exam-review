## ADDED Requirements

### Requirement: Vault is the sole authoritative source

The repository SHALL NOT contain any generator that writes vault Markdown from JSON, nor any script that writes question or concept JSON under `data/`. The directory `data/` MUST NOT exist in the tracked tree and SHALL be listed in `.gitignore`. The cutover audit SHALL report `legacyToolsAbsent: true` only when `data/` is absent and none of the retired scripts (`build_concepts.py`, `vault_to_json.py`, `json_to_vault.py`, `merge_edits.py`, `nr_summary_audit.py`, `sheets_to_json.py`, `json_to_sheets.py`, `import_obsidian_sr.py`) exist under `scripts/`; otherwise it SHALL report `legacyToolsAbsent: false`, list every residual path under `legacyResidue`, and exit with status 1.

#### Scenario: Audit passes on a clean tree

- **WHEN** the cutover audit runs on a checkout with no `data/` directory and none of the retired scripts
- **THEN** the report has `legacyToolsAbsent: true`, an empty `legacyResidue`, and the process exits 0

#### Scenario: Audit fails on residue

- **WHEN** a checkout contains `scripts/merge_edits.py` or a `data/` directory
- **THEN** the report has `legacyToolsAbsent: false`, `legacyResidue` names each residual path, and the process exits 1

##### Example: Residue listing

| Residual paths present | legacyResidue |
| --- | --- |
| `data/` | `["data"]` |
| `scripts/merge_edits.py`, `scripts/build_concepts.py` | `["scripts/build_concepts.py", "scripts/merge_edits.py"]` |

## REMOVED Requirements

### Requirement: Publish verified 100-note Phase 2B concept summaries from the vault
**Reason**: The Phase 2B publication target (`data/concepts/*.json` and `data/concepts-index.json`) is retired together with `data/`. The 100-note Summary rewrite is complete and its evidence is preserved under `docs/reports/nr-summary-rewrite/phase2b/`; the audit chain (`scripts/nr_summary_audit.py`, `scripts/build_concepts.py`) is removed.
**Migration**: Concept content is published only through the vault compiler (`vault-native-publication`). Summary quality checks run through compiler warnings and `scripts/find_weak_concepts.py` / `scripts/find_shallow_concepts.py`.

### Requirement: Preserve sub-batch publication isolation
**Reason**: Sub-batch isolation governed scoped writes into `data/concepts/`, which no longer exists.
**Migration**: None required; the sealed Phase 2B artifacts are archived in git history by the preservation commit of this change.
