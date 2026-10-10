## ADDED Requirements

### Requirement: Publish every eligible vault note as raw Markdown

The publication compiler SHALL discover every Markdown file under `vault/questions/` and `vault/concepts/` whose basename does not start with `_` and whose frontmatter does not set `publish: false`. For every eligible source, the compiler SHALL emit one raw Markdown asset below `dist/notes/` at the same vault-relative path, one manifest entry, and one typed record. The raw asset SHA-256 SHALL equal the SHA-256 of the source bytes.

#### Scenario: Publish an eligible concept note

- **WHEN** `vault/concepts/brain-abscess.md` has no `publish: false` frontmatter
- **THEN** the package contains `notes/concepts/brain-abscess.md`, one `concept` record, and one manifest entry with the source path and matching SHA-256

#### Scenario: Exclude an explicit draft

- **WHEN** `vault/concepts/draft-topic.md` has frontmatter `publish: false`
- **THEN** no raw asset, record, manifest entry, search entry, or relation entry is emitted for that note

### Requirement: Emit lossless publication records and indexes

The compiler SHALL emit one schema-versioned record per eligible note and schema-versioned manifest, concept index, question index, relation index, search index, and build report. Every record SHALL contain `id`, `kind`, `sourcePath`, `sourceSha256`, `rawPath`, `frontmatter`, `outline`, `links`, `embeds`, and `diagnostics`. Records SHALL NOT define medical-content fields such as `definition`, `imagingFindings`, `keyPoints`, or `management`.

#### Scenario: Preserve an unknown concept section

- **WHEN** an eligible concept contains a level-two heading named `Teaching Pearls` that has no website-specific mapping
- **THEN** the raw Markdown contains that heading and body unchanged, the record outline lists the heading, and no semantic content field is created for it

##### Example: generic outline entry

- **GIVEN** source line 21 is `## Teaching Pearls`
- **WHEN** the compiler emits the concept record
- **THEN** the outline contains an entry with `level` equal to 2, `heading` equal to `Teaching Pearls`, and `startLine` equal to 21

### Requirement: Emit minimal question interaction projections

For an eligible question note, the compiler SHALL emit an `sr` projection containing front and back source line ranges, option line ranges, the parsed correct answer, and linked concept ids. The projection SHALL reference the raw Markdown and SHALL NOT become an editable content source.

#### Scenario: Build a question projection

- **WHEN** an eligible question contains one SR front/back boundary, options A through E, `Ans: B`, and `[[brain-abscess]]`
- **THEN** its question record contains the front and back line ranges, five option ranges, correct answer `B`, and concept id `brain-abscess`

### Requirement: Publish resolved static assets

The compiler SHALL resolve every supported published Markdown embed to one content-addressed asset path below `dist/assets/` and record the resolved path in the owning record. A supported required embed that is missing or has more than one valid source candidate SHALL be reported as a hard validation error.

#### Scenario: Publish an image embed

- **WHEN** an eligible note embeds `![[brain-abscess.png]]` and exactly one supported source asset resolves
- **THEN** the package contains one content-addressed asset and the note record maps the embed to that asset path
### Requirement: Emit explicit answer-state projections

For every eligible question, the `sr` projection SHALL contain `answerStatus`, `answerMode`, `acceptedAnswers`, and `scorable`. `acceptedAnswers` SHALL contain normalized option letters only. A `confirmed` question SHALL have a non-empty accepted set and a scoring mode other than `none`; an `unresolved` or `no_valid_answer` question SHALL have an empty accepted set and `scorable: false`.

#### Scenario: Publish a question where either of two answers is acceptable

- **WHEN** a question declares `answerStatus: confirmed`, `answerMode: any`, and `acceptedAnswers: [B, D]`
- **THEN** its projection preserves both letters, renders single-choice interaction, and scores either `B` or `D` as correct

#### Scenario: Publish an unresolved question without a scored answer

- **WHEN** a question declares `answerStatus: unresolved`, `answerMode: none`, and `acceptedAnswers: []`
- **THEN** its raw note and record are published with `scorable: false`, and the projection does not invent a correct answer
