## REMOVED Requirements

### Requirement: Concept build script generates index and per-concept files

**Reason**: A fixed JSON detail schema duplicates physician-authored Markdown and omits source sections that do not map to the legacy website fields.

**Migration**: Use the vault-native-publication compiler to emit raw Markdown assets, minimal records, indexes, and manifest entries. Retain the legacy builder until vault-native migration acceptance completes.

#### Scenario: Retire legacy concept JSON generation after migration acceptance

- **WHEN** the vault-native publication acceptance suite passes for all eligible concept notes
- **THEN** the production review-site build SHALL use vault-native records and raw Markdown assets instead of requiring the legacy per-concept JSON files

### Requirement: Markdown sections map to the site concept schema

**Reason**: Mapping clinical Markdown sections into `definition`, `imagingFindings`, `keyPoints`, and `management` makes website fields an implicit authoring schema.

**Migration**: Render raw Markdown sections generically through vault-native-review-web. Use records only for outline, links, assets, relations, and question interaction metadata.

#### Scenario: Retire fixed semantic field mapping after migration acceptance

- **WHEN** a published concept contains a supported Markdown section that has no legacy JSON field
- **THEN** the vault-native renderer SHALL render that section from its raw Markdown source without mapping it into the retired fixed concept schema
