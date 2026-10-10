# vault-generation Specification

## Purpose

TBD - created by archiving change 'obsidian-exam-vault'. Update Purpose after archive.

## Requirements

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

<!-- @trace
source: remove-legacy-data-json
updated: 2026-10-10
code:
  - scripts/image_asset_manager.js
  - output/imagegen/adrenoleukodystrophy-background-draft.png
  - scripts/image_asset_manager.py
  - scripts/start_image_asset_manager.ps1
  - start-image-manager.cmd
  - docs/image-asset-manager.md
  - scripts/image_asset_manager.html
  - docs/concept-summary-review-publication.md
tests:
  - scripts/test_image_asset_manager.py
  - scripts/test_image_asset_manager.js
-->