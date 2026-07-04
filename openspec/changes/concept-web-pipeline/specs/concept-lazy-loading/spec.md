## ADDED Requirements

### Requirement: Concept list renders from the lightweight index

The concept list view SHALL be populated by fetching data/concepts-index.json once, without fetching any per-concept content file. The initial payload required to render the full concept list SHALL NOT include the body content (definition, imaging findings, differential diagnosis, sources, clinical points) of the concepts.

#### Scenario: Opening the concept list

- **WHEN** the user navigates to the concepts view
- **THEN** the app fetches data/concepts-index.json and renders one list entry per index entry
- **AND** the app does NOT fetch data/concepts/<slug>.json for any concept until one is opened

### Requirement: Concept detail is lazy-loaded and cached

When the user opens a specific concept, the app SHALL fetch that concept's data/concepts/<slug>.json on demand, render its full-depth content (definition, imaging-reading points, differential diagnosis, external links, clinical points), and cache the fetched content so that reopening the same concept in the same session does not refetch it. User edits stored in localStorage SHALL continue to be merged onto the loaded concept object.

#### Scenario: Opening a concept the first time

- **WHEN** the user opens concept <slug> that has not been opened this session
- **THEN** the app fetches data/concepts/<slug>.json and renders its imagingFindings, differentialDiagnosis, externalLinks, and clinical content

#### Scenario: Reopening a cached concept

- **WHEN** the user opens concept <slug> that was already fetched earlier in the same session
- **THEN** the app renders it from cache without issuing a new network fetch for data/concepts/<slug>.json

#### Scenario: Local edits are preserved

- **GIVEN** the user has a localStorage edit patch for concept <slug>
- **WHEN** the concept is lazy-loaded
- **THEN** the rendered concept reflects the base content merged with the localStorage patch
