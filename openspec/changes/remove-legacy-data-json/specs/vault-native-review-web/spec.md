## MODIFIED Requirements

### Requirement: Provide question review and examination from SR projections

The website SHALL render a question front from the published SR projection, reveal the projected back on answer review, record selected answers against the current question source hash, and show linked concepts through the relation index. After reveal, when `sr.reference` is non-empty, the website SHALL render a `vault-question-reference` block after the answer badge with the HTML-escaped reference text; when empty it SHALL render no such block. Exam scoring SHALL use the projected correct answer and SHALL not mutate published question content. The website MUST NOT fetch any path under `data/`.

#### Scenario: Review a question answer

- **WHEN** a user chooses option `C` for a question whose projected correct answer is `B`
- **THEN** the website marks the attempt incorrect, records the current source hash with the attempt, and can reveal the source back content

#### Scenario: Show the reference after reveal

- **WHEN** a user reveals the answer of a question whose `sr.reference` is `AJR 2008;190:S18-S22`
- **THEN** the back content includes a `vault-question-reference` block reading `參考來源：AJR 2008;190:S18-S22`

#### Scenario: Omit the reference block when empty

- **WHEN** a user reveals the answer of a question whose `sr.reference` is the empty string
- **THEN** no `vault-question-reference` block is rendered
