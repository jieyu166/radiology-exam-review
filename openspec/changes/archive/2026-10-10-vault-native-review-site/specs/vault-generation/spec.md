## REMOVED Requirements

### Requirement: Generate SR question cards from question JSON

**Reason**: Vault Markdown is the physician-authored content source for publication, so production website publication cannot depend on JSON-to-vault generation.

**Migration**: Retain `scripts/json_to_vault.py` only as a legacy import or recovery tool. Publish the review website through vault-native-publication.

#### Scenario: Retire JSON-to-vault generation from production publication

- **WHEN** the production website is rebuilt after vault-native migration acceptance
- **THEN** the build SHALL read eligible question Markdown from the vault and SHALL NOT require question JSON to generate those source notes

### Requirement: Mark questions with insufficient explanations

**Reason**: Explanation completeness is reviewed in physician-authored vault notes and medical evidence workflows, not generated from a website JSON source.

**Migration**: Keep evidence and manual-review markers in vault workflows. The vault publication validator only checks structural publication contracts.

#### Scenario: Keep medical completeness review outside the publication compiler

- **WHEN** a question note is eligible for publication
- **THEN** the publication compiler SHALL validate its structural question contract without creating or changing an explanation-completeness marker

### Requirement: Generate concept notes that aggregate their questions

**Reason**: Concept notes are authored in vault and published as raw Markdown; the website does not generate or overwrite concept note content.

**Migration**: Use vault-native-publication records and the relation index to present question relationships without creating concept Markdown.

#### Scenario: Retire generated concept-note aggregation

- **WHEN** the website presents a published question-to-concept relationship
- **THEN** it SHALL use the relation index and SHALL NOT generate or overwrite a concept Markdown note

### Requirement: Idempotent regeneration preserving SR scheduling

**Reason**: Production publication does not regenerate vault cards from JSON.

**Migration**: Preserve existing SR scheduling in vault files. The compiler reads vault content without rewriting it and validates deterministic website output.

#### Scenario: Replace card regeneration with read-only deterministic publication

- **WHEN** the same eligible vault source set is compiled twice without content changes
- **THEN** the compiler SHALL leave vault files and SR scheduling unchanged and produce equivalent publication output

### Requirement: Write SR plugin configuration

**Reason**: Website publication does not configure Obsidian plugins.

**Migration**: Maintain Obsidian plugin configuration outside the website publication workflow.

#### Scenario: Keep Obsidian plugin configuration outside publication

- **WHEN** the vault-native website publication workflow runs
- **THEN** it SHALL NOT write or modify Obsidian plugin configuration
