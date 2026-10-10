# question-reference Specification

## Purpose

TBD - created by archiving change 'remove-legacy-data-json'. Update Purpose after archive.

## Requirements

### Requirement: Question reference lives in vault frontmatter

The vault question card frontmatter SHALL be the only storage location for a question's bibliographic reference, using the optional string key `reference`. No JSON file under `data/` SHALL exist as a source for question references. A one-time migration SHALL copy every non-empty `reference` string from the legacy `data/<year>.json` records into the matching vault card, inserting exactly one `reference:` line at the end of the frontmatter block without altering any byte of the card body. When the vault card already carries a `reference` value, the migration MUST NOT overwrite it and MUST report the pair as a conflict.

#### Scenario: Migrate a reference into a card without one

- **WHEN** the migration runs against a card whose frontmatter has no `reference` key and whose legacy record has `reference` equal to `Agrawal R, et al. RadioGraphics 2020;40(3):656-666.`
- **THEN** the card frontmatter gains the line `reference: Agrawal R, et al. RadioGraphics 2020;40(3):656-666.` immediately before the closing `---`, the body bytes are unchanged, and the migration output counts the card under `updated`

#### Scenario: Preserve an existing vault reference

- **WHEN** the migration finds a card whose frontmatter already has `reference` and the legacy value differs
- **THEN** the card is left unchanged and its id is listed under `conflicts` in the migration output

#### Scenario: Report a card that cannot be parsed

- **WHEN** the legacy record's id matches no vault card, or the matching card has no parseable frontmatter block
- **THEN** nothing is written for that id, the id is listed under `missingCards`, and the migration exits non-zero

##### Example: Migration summary output

| Legacy records with reference | Cards already holding same value | Cards already holding different value | Cards missing | stdout JSON |
| --- | --- | --- | --- | --- |
| 2007 | 0 | 0 | 0 | `{"updated": 2007, "alreadyPresent": 0, "conflicts": [], "missingCards": []}` |
| 3 | 1 | 1 | 1 | `{"updated": 1, "alreadyPresent": 1, "conflicts": ["2020-100"], "missingCards": ["2019-521"]}` |


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

---
### Requirement: Compiler projects the reference into question records and indexes

The vault compiler SHALL copy the frontmatter `reference` string into the question record's `sr.reference` field and into the matching entry of `indexes/questions.json`. When the key is absent the value SHALL be the empty string. When the value is not a string the compiler SHALL emit a warning with code `reference_not_string`, SHALL project the empty string, and SHALL NOT treat the note as a hard error. The compiler MUST NOT include `reference` text in `indexes/search.json`.

#### Scenario: Project a string reference

- **WHEN** an eligible question card has `reference: Radiology Review Manual P.466`
- **THEN** its question record has `sr.reference` equal to `Radiology Review Manual P.466` and the `indexes/questions.json` entry carries the same `reference` value

#### Scenario: Project an absent reference

- **WHEN** an eligible question card has no `reference` key
- **THEN** `sr.reference` and the index entry `reference` are both the empty string and no warning is emitted

#### Scenario: Degrade a non-string reference

- **WHEN** an eligible question card has `reference` set to a YAML list
- **THEN** the build report contains a `reference_not_string` warning for that card, the projected value is the empty string, and the build still succeeds


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

---
### Requirement: Website shows the reference after the answer is revealed

The question view SHALL render a block with class `vault-question-reference` containing the text `參考來源：` followed by the HTML-escaped `sr.reference` string, placed after the answer badge, only once the answer has been revealed. When `sr.reference` is empty the view MUST NOT render the block.

#### Scenario: Show reference on reveal

- **WHEN** a user reveals the answer of a question whose `sr.reference` is `AJR 2008;190:S18-S22`
- **THEN** the rendered back contains a `vault-question-reference` element whose text is `參考來源：AJR 2008;190:S18-S22`

#### Scenario: Hide reference before reveal and when empty

- **WHEN** the answer is not yet revealed, or `sr.reference` is the empty string
- **THEN** no `vault-question-reference` element is rendered

#### Scenario: Escape markup in a reference

- **WHEN** `sr.reference` contains `<b>bold</b> & more`
- **THEN** the rendered text shows the literal characters `<b>bold</b> & more` and no `b` element is created

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