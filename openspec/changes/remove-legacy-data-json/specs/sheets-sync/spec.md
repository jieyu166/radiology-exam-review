## REMOVED Requirements

### Requirement: JSON to Sheets export
**Reason**: Google Sheets synchronisation operated on `data/<year>.json`, which is retired; physicians now review and edit questions directly in the Obsidian vault.
**Migration**: None. `scripts/json_to_sheets.py` is deleted. Review happens on vault Markdown and the published website.

### Requirement: Sheets to JSON sync
**Reason**: Same as above; the JSON target no longer exists.
**Migration**: None. `scripts/sheets_to_json.py` is deleted.

### Requirement: Schema definition module
**Reason**: `scripts/sheets_schema.py` only served the two deleted sync scripts.
**Migration**: None.

### Requirement: Authentication via service account
**Reason**: No remaining script talks to the Google Sheets API.
**Migration**: None. Any leftover service-account credential file is outside the repository and is not touched by this change.

### Requirement: question_id uniqueness and protected range
**Reason**: Applied only to the retired Sheets workbook.
**Migration**: Question id uniqueness is enforced by the vault compiler (`vault-native-publication`, "Validate source identity and question contracts").
