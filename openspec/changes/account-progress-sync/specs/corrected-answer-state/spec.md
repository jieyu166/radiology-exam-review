## ADDED Requirements

### Requirement: Corrected answer frontmatter contract

A question card MAY declare `answerStatus: corrected` to record that the officially published answer is wrong. Such a card MUST provide `officialAnswer` as a single letter A–E and MUST provide the reviewed answer through `correctAnswer` or `acceptedAnswers`; `officialAnswer` MUST NOT be a member of the accepted set. The compiler SHALL treat `corrected` as scorable exactly like `confirmed` and SHALL project `sr.officialAnswer` as the letter (empty string for every other status). A `corrected` card that is missing `officialAnswer`, has a multi-letter or non A–E value, or whose `officialAnswer` is in the accepted set SHALL be a hard error `question_official_answer`.

#### Scenario: Publish a corrected question

- **WHEN** a card declares `answerStatus: corrected`, `officialAnswer: B`, `correctAnswer: D`
- **THEN** its projection has `acceptedAnswers: ["D"]`, `officialAnswer: "B"`, `scorable: true`

#### Scenario: Reject an inconsistent correction

- **WHEN** a card declares `answerStatus: corrected`, `officialAnswer: D`, `correctAnswer: D`
- **THEN** the build reports hard error `question_official_answer` for that card

##### Example: Validation matrix

| answerStatus | officialAnswer | correctAnswer | Result |
| --- | --- | --- | --- |
| corrected | B | D | published, scorable, officialAnswer `B` |
| corrected | (missing) | D | `question_official_answer` |
| corrected | BD | A | `question_official_answer` |
| confirmed | B | B | published; officialAnswer projected as `""` and a warning `official_answer_ignored` |

### Requirement: Reveal the official-answer correction

After the answer is revealed, the question view SHALL render, next to the answer badge, the text `官方公布 <officialAnswer> 有誤，依覆核答案 <accepted> 計分` for `corrected` questions and nothing extra for other statuses. Scoring SHALL use the accepted set only. Exam pools SHALL include corrected questions.

#### Scenario: Corrected question in card mode

- **WHEN** a user chooses `B` on a question with `officialAnswer: "B"` and `acceptedAnswers: ["D"]` and reveals
- **THEN** the attempt is marked incorrect and the view shows `官方公布 B 有誤，依覆核答案 D 計分`

#### Scenario: Corrected question in exam scoring

- **WHEN** an exam contains that question and the user chose `D`
- **THEN** the exam counts it correct
