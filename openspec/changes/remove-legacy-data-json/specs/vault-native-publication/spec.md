## MODIFIED Requirements

### Requirement: Emit minimal question interaction projections

For an eligible question note, the compiler SHALL emit an `sr` projection containing front and back source line ranges, option line ranges, the parsed correct answer, linked concept ids, and the frontmatter `reference` string (empty string when absent). The projection SHALL reference the raw Markdown and SHALL NOT become an editable content source. The `reference` value SHALL also appear on the matching entry of `indexes/questions.json` and SHALL NOT be indexed in `indexes/search.json`.

#### Scenario: Build a question projection

- **WHEN** an eligible question contains one SR front/back boundary, options A through E, `Ans: B`, `[[brain-abscess]]`, and frontmatter `reference: Radiology Review Manual P.466`
- **THEN** its question record contains the front and back line ranges, five option ranges, correct answer `B`, concept id `brain-abscess`, and `reference` equal to `Radiology Review Manual P.466`

#### Scenario: Build a projection without reference

- **WHEN** an eligible question has no `reference` frontmatter key
- **THEN** `sr.reference` is the empty string and the build emits no warning for that field
