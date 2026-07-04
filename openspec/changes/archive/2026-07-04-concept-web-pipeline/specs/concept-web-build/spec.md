## ADDED Requirements

### Requirement: Concept build script generates index and per-concept files

The system SHALL provide a re-runnable build script (scripts/build_concepts.py) that reads every concept markdown file under vault/concepts/ (excluding files whose basename starts with an underscore) and emits two outputs: a single lightweight index file data/concepts-index.json and one per-concept content file data/concepts/<slug>.json. Running the script again SHALL fully regenerate both outputs from the current vault contents (idempotent for identical input).

#### Scenario: Generating outputs from the vault

- **WHEN** the build script runs against a vault/concepts/ directory containing N concept markdown files (excluding underscore-prefixed files)
- **THEN** data/concepts-index.json is written containing exactly N entries, and data/concepts/ contains exactly N files named <slug>.json

#### Scenario: Slug is derived from filename and matches frontmatter

- **WHEN** a concept file vault/concepts/<slug>.md declares an inline `concepts: [<slug>]` frontmatter field
- **THEN** the emitted per-concept file is data/concepts/<slug>.json and its slug field equals the filename slug

##### Example: index entry shape

- **GIVEN** a file vault/concepts/adrenal-adenoma.md with frontmatter name "Adrenal Adenoma", subspecialty [ABD], and a Chinese alias "腎上腺腺瘤"
- **WHEN** the build script runs
- **THEN** the index entry is `{"slug":"adrenal-adenoma","name":"Adrenal Adenoma","nameZh":"腎上腺腺瘤","subspecialty":"ABD"}`

### Requirement: Markdown sections map to the site concept schema

Each per-concept JSON file SHALL populate the website concept schema fields from the Note v5 markdown sections: name and subspecialty from frontmatter; a Chinese display name from a Chinese alias when present; a definition from the lead bold summary and the Summary section; imaging-reading content from the "放射科醫師影像判讀重點" section; keyPoints from the Summary bullet list; differentialDiagnosis from any DDx/鑑別 content; clinical points from the "臨床重點" section; and externalLinks from DOI links in the "參考來源" section. When a source section is absent, the corresponding field SHALL be an empty string or empty array rather than omitted.

#### Scenario: Missing section yields empty field, not a crash

- **WHEN** a concept markdown file has no "臨床重點" section
- **THEN** the per-concept JSON still validates as JSON and its clinical field is an empty array (or empty string), and the build script does not error on that file

#### Scenario: Full-depth content is preserved

- **WHEN** a concept file contains 放射科醫師影像判讀重點, DDx, 參考來源 with DOI links, and 臨床重點
- **THEN** the per-concept JSON contains non-empty imagingFindings, differentialDiagnosis, externalLinks, and clinical fields reflecting those sections
