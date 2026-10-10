## MODIFIED Requirements

### Requirement: Render answer states without false scoring

The question view SHALL render `answerMode: single` and `answerMode: any` as single-choice controls, `answerMode: all` as multi-select controls, and `answerMode: none` as a review-only question. Exam pools SHALL exclude questions with `scorable: false` and SHALL include `corrected` questions; card and concept routes MAY display unscorable questions with an explicit unresolved/no-valid-answer badge. Scoring SHALL compare the selected set with `acceptedAnswers` according to `answerMode`. For `corrected` questions the revealed back SHALL show the official-answer correction text. Every revealed answer in card mode SHALL be recorded as an attempt event carrying the elapsed time and the optional confidence rating; exam answers SHALL be recorded as `exam` attempts when the exam is submitted.

#### Scenario: Do not score an unresolved question

- **WHEN** a question record has `scorable: false` and `answerStatus: unresolved`
- **THEN** the exam pool excludes it and the card view shows that it is pending review rather than marking a guessed option correct

#### Scenario: Corrected question is scored by the reviewed answer

- **WHEN** a question record has `answerStatus: corrected`, `officialAnswer: "B"`, `acceptedAnswers: ["D"]` and the user chooses `D`
- **THEN** the attempt is correct and the revealed back shows `官方公布 B 有誤，依覆核答案 D 計分`

#### Scenario: Confidence control only in card mode

- **WHEN** a question is rendered in card mode before reveal
- **THEN** three optional confidence buttons (猜／普通／有把握) are shown; in exam mode they are not rendered
