## ADDED Requirements

### Requirement: Navigation exposes review and statistics routes

The top navigation and the bottom navigation SHALL include `今日複習` (`#/review`); the settings panel SHALL link to `#/stats`; the mock-exam setup route SHALL present the exam builder filters instead of a bare question count; concept pages SHALL offer `練這個概念的題（跨年交錯）`. Existing routes `#/card`, `#/list`, `#/exam`, `#/concepts`, `#/concept/<id>` SHALL keep their behaviour.

#### Scenario: Reach the review route

- **WHEN** the user taps `今日複習` in the bottom navigation on a phone
- **THEN** the hash becomes `#/review` and the review queue renders

#### Scenario: Concept drill entry

- **WHEN** the user opens a concept with 7 related questions across three years and taps the drill entry
- **THEN** card mode starts with an interleaved queue drawn from those 7 questions
