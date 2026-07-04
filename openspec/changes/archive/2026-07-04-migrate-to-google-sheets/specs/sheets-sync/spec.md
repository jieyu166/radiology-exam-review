## ADDED Requirements

### Requirement: JSON to Sheets export

The `json_to_sheets.py` script SHALL read all `data/2016.json` through `data/2024.json` and `data/concepts.json`, deduplicate cross-year questions (one row per `question_id`), and write all rows to a Google Sheets spreadsheet via the Sheets API v4 `batchUpdate` method.

The script SHALL detect questions appearing in multiple year JSON files (i.e., same `id` field) and merge them into a single row, setting the `years` column to a comma-separated list of all years (e.g., `2018,2019,2022`). When multiple JSON files contain conflicting content for the same `question_id`, the script SHALL use the version from the file whose year matches the first segment of the `question_id` (the primary year) and SHALL write the list of conflicting IDs to `scripts/conflicts.json`.

The script SHALL create or overwrite three sheets in the target spreadsheet: `questions`, `concepts`, and `_metadata`. The `questions` sheet SHALL have the following columns in order: `question_id`, `primary_year`, `number`, `years`, `subspecialty`, `question_text`, `option_A`, `option_B`, `option_C`, `option_D`, `option_E`, `correct_answer`, `reference`, `explanation`, `concepts`, `checked`. The `subspecialty_confidence` field SHALL NOT be included in the sheet or in any generated JSON output.

#### Scenario: Normal export with no conflicts

- **WHEN** all year JSON files contain no duplicate `question_id` values
- **THEN** the script writes one row per question to the `questions` sheet, with `years` equal to the single year in the question's `years` array, and does not create `scripts/conflicts.json`

#### Scenario: Export with cross-year duplicates

- **WHEN** the same `question_id` (e.g., `2018-019`) appears in `data/2018.json`, `data/2019.json`, and `data/2022.json` with identical content
- **THEN** the script writes exactly one row for `2018-019` with `years` = `2018,2019,2022` and `primary_year` = `2018`

#### Scenario: Export with conflicting cross-year content

- **WHEN** the same `question_id` appears in two year files with different `explanation` text
- **THEN** the script uses the version from the primary year file, writes the conflicting IDs to `scripts/conflicts.json`, and prints a warning to stderr listing the conflicting IDs

#### Scenario: Explanation exceeds cell character limit

- **WHEN** any question's `explanation` field exceeds 49,000 characters
- **THEN** the script truncates the value to 49,000 characters, appends `[TRUNCATED]` at the end, prints a warning to stderr with the affected `question_id`, and continues processing remaining questions

### Requirement: Sheets to JSON sync

The `sheets_to_json.py` script SHALL read the `questions` and `concepts` sheets from the Google Sheets spreadsheet and regenerate `data/2016.json` through `data/2024.json` and `data/concepts.json`.

For each question row, the script SHALL parse the `years` column (comma-separated integers) and write the question object into the JSON file for each listed year. Each year JSON file SHALL contain only the questions whose `years` column includes that year. The output JSON schema SHALL include the following fields: `id`, `year`, `number`, `subspecialty`, `questionText`, `options`, `correctAnswer`, `reference`, `explanation`, `images`, `concepts`, `checked`, `years`. The `subspecialty_confidence` field SHALL NOT be written to any generated JSON file.

The script SHALL validate every row before writing: `correct_answer` MUST be one of `A`, `B`, `C`, `D`, `E`; `subspecialty` MUST be one of `ABD`, `CV`, `CH`, `Breast`, `H&N`, `MSK`, `NR`, `PED`, `US`, `IR`, `Physics`, `Unknown`; `question_text` MUST NOT be empty; at least `option_A`, `option_B`, `option_C` MUST be non-empty. Rows failing validation SHALL be skipped and reported to stderr; they SHALL NOT be written to any JSON file.

The script SHALL write output files atomically: each file MUST be written to a `.tmp` file first, then renamed to the final path, so a partial failure leaves existing JSON intact.

The script SHALL print a summary diff to stdout comparing the new JSON with the current git HEAD version of each file (line counts added/removed per file).

#### Scenario: Normal sync from clean Sheet

- **WHEN** the `questions` sheet contains valid rows covering years 2016–2024 and no validation errors
- **THEN** the script writes 9 JSON files and 1 concepts JSON, prints a diff summary, and exits with code 0

#### Scenario: Sync with validation error

- **WHEN** one row has `correct_answer` = `X` (invalid value)
- **THEN** the script skips that row, prints `SKIP: <question_id> — invalid correct_answer 'X'` to stderr, writes all other questions normally, and exits with code 1

#### Scenario: Atomic write on partial failure

- **WHEN** the script encounters an OS write error while writing `data/2022.json`
- **THEN** the partially written `.tmp` file is deleted, `data/2022.json` remains unchanged at its previous state, and the script exits with code 1

#### Scenario: Cross-year expansion

- **WHEN** one row has `question_id` = `2018-019` and `years` = `2018,2019,2022`
- **THEN** the question object appears in `data/2018.json`, `data/2019.json`, and `data/2022.json`, each with the `years` field set to `[2018, 2019, 2022]`

### Requirement: Schema definition module

The `sheets_schema.py` module SHALL define all column names for the `questions` and `concepts` sheets as named constants, the ordered list of column names (used to set sheet headers and map row positions), the list of valid `subspecialty` values, and the validation function `validate_question_row(row: dict) -> list[str]` that returns a list of error strings (empty list if valid).

#### Scenario: Import by both scripts

- **WHEN** either `json_to_sheets.py` or `sheets_to_json.py` imports `sheets_schema`
- **THEN** both scripts reference the same column-name constants and call the same `validate_question_row` function without duplicating validation logic

#### Scenario: Invalid subspecialty detected

- **WHEN** `validate_question_row` is called with a row where `subspecialty` = `"Cardio"` (not in allowed list)
- **THEN** the function returns a list containing the string `"invalid subspecialty: Cardio"`

### Requirement: Authentication via service account

The sync scripts SHALL authenticate to the Google Sheets API using a service account JSON key file. The path to the key file SHALL be read from the `GOOGLE_KEY_PATH` environment variable, falling back to `~/.config/radiology-sheets-key.json` if the variable is not set. The `SHEET_ID` of the target spreadsheet SHALL be read from the `SHEET_ID` environment variable; if absent, the script SHALL exit with code 1 and print `Error: SHEET_ID environment variable not set`.

#### Scenario: Key file found via environment variable

- **WHEN** `GOOGLE_KEY_PATH=/path/to/key.json` is set and the file exists
- **THEN** the script authenticates successfully and proceeds to read/write the spreadsheet

#### Scenario: Missing SHEET_ID

- **WHEN** `SHEET_ID` environment variable is not set
- **THEN** the script prints `Error: SHEET_ID environment variable not set` to stderr and exits with code 1 without making any API calls

#### Scenario: Key file not found

- **WHEN** `GOOGLE_KEY_PATH` points to a non-existent file and `~/.config/radiology-sheets-key.json` does not exist
- **THEN** the script prints an error message indicating the missing key file path and exits with code 1

### Requirement: question_id uniqueness and protected range

The `json_to_sheets.py` script SHALL validate that all `question_id` values across all source JSON files are unique before writing anything to the spreadsheet. If any duplicate `question_id` is found, the script SHALL print each duplicate ID to stderr, exit with code 1, and make no API calls.

After writing all rows, the script SHALL call the Sheets API `addProtectedRange` to set the `question_id` column (column A of the `questions` sheet) as a WARNING-level protected range, so that any edit to that column triggers a confirmation dialog in the Google Sheets UI.

#### Scenario: Duplicate question_id detected before export

- **WHEN** two source JSON files both contain a question with `id` = `"2018-019"` and the values are different (conflict)
- **THEN** the script prints `DUPLICATE: 2018-019` to stderr and exits with code 1 without writing any data to the spreadsheet

#### Scenario: question_id column protected after export

- **WHEN** `json_to_sheets.py` completes writing all rows successfully
- **THEN** the script calls `addProtectedRange` on column A of the `questions` sheet with `warningOnly: true`, so a user editing that column sees a confirmation dialog

#### Scenario: All question_ids unique — export proceeds

- **WHEN** all question_ids across all source JSON files are unique (no two questions share the same `id` value)
- **THEN** the script proceeds to write all rows to the spreadsheet without error
