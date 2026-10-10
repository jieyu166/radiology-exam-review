## MODIFIED Requirements

### Requirement: Emit explicit answer-state projections

For every eligible question, the `sr` projection SHALL contain `answerStatus`, `answerMode`, `acceptedAnswers`, `scorable` and `officialAnswer`. `acceptedAnswers` SHALL contain normalized option letters only. A `confirmed` or `corrected` question SHALL have a non-empty accepted set and a scoring mode other than `none`; an `unresolved` or `no_valid_answer` question SHALL have an empty accepted set and `scorable: false`. `officialAnswer` SHALL be the declared letter for `corrected` questions and the empty string otherwise.

#### Scenario: Publish a question where either of two answers is acceptable

- **WHEN** a question declares `answerStatus: confirmed`, `answerMode: any`, and `acceptedAnswers: [B, D]`
- **THEN** its projection preserves both letters, renders single-choice interaction, and scores either `B` or `D` as correct

#### Scenario: Publish an unresolved question without a scored answer

- **WHEN** a question declares `answerStatus: unresolved`, `answerMode: none`, and `acceptedAnswers: []`
- **THEN** its raw note and record are published with `scorable: false`, and the projection does not invent a correct answer

#### Scenario: Publish a corrected question

- **WHEN** a question declares `answerStatus: corrected`, `officialAnswer: B`, `correctAnswer: D`
- **THEN** its projection has `acceptedAnswers: ["D"]`, `officialAnswer: "B"`, `answerMode: "single"`, `scorable: true`
