## ADDED Requirements

### Requirement: Question index entries publish subspecialty as a list

The compiler SHALL publish `subspecialty` on every `indexes/questions.json` entry as a de-duplicated list of strings: a frontmatter string becomes a one-item list, a frontmatter list is kept in order, and a missing value becomes an empty list. The question record SHALL keep the frontmatter value unchanged.

#### Scenario: Single string frontmatter

- **WHEN** a question card declares `subspecialty: NR`
- **THEN** its index entry has `subspecialty: ["NR"]`

#### Scenario: Multi-subspecialty frontmatter

- **WHEN** a question card declares `subspecialty: [GI, ABD]`
- **THEN** its index entry has `subspecialty: ["GI", "ABD"]` and the question appears under both the GI and ABD filters

##### Example: Normalization

| frontmatter | index entry |
| --- | --- |
| `subspecialty: NR` | `["NR"]` |
| `subspecialty: [GI, ABD]` | `["GI", "ABD"]` |
| (missing) | `[]` |
