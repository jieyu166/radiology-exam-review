## ADDED Requirements

### Requirement: Multi-subspecialty questions match any selected subspecialty

The exam pool, the card/list subspecialty filter and the weakness grouping SHALL treat a question's `subspecialty` as a set: a question matches a subspecialty filter when any of its subspecialties is selected, the filter pills SHALL be derived from the flattened set of all question subspecialties, and the weakness grouping SHALL add one row per subspecialty for a wrong question.

#### Scenario: GI question also counts as ABD

- **WHEN** a question has `subspecialty: ["GI", "ABD"]` and the exam filter selects only `ABD`
- **THEN** the question is in the pool; selecting only `GI` also includes it

#### Scenario: Weakness rows per subspecialty

- **WHEN** two currently-wrong questions have `["GI", "ABD"]` and `["GU", "ABD"]`
- **THEN** the weakness grouping yields an `ABD` group of size 2 (GI and GU each have one question and are omitted)
