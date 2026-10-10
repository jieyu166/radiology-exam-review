## Summary

題卡 frontmatter `subspecialty` 由單一字串改為可多值的清單，索引一律發佈清單，前端篩選、組卷、弱點分群改以「任一包含」比對；同時把 GI／GU／OBGYN 題目同時歸入 ABD，概念側 ENT→H&N、MR→MRI。

## Motivation

使用者 2026-10-11 要求：題目可跨次專科（GI、GU、OBGYN 的題目也屬 ABD），概念卡早已是清單，題卡卻只能一個值，造成次專科篩選與組卷漏題。

## Proposed Solution

- compiler：`indexes/questions.json` 的 `subspecialty` 一律為去重字串清單（字串→單元素清單、缺→空清單）；record 的 frontmatter 原樣保留。
- 前端：`_subs(entry)` 容忍字串或清單；年份／次專科 pill 由展平集合產生；篩選、組卷 `subspecialties`、弱點分群（每個次專科一列）、統計標籤（以 `/` 串接）皆改用清單語意。
- 資料：104 張 GI／GU／OBGYN 題卡改為 `[X, ABD]` 並在題幹 tag 加 `#ABD`；2 張概念卡 ENT→H&N、MR→MRI。
- `scripts/vault_questions.py` 既已以 `, ` 串接清單，不需改。

## Non-Goals

- 不改概念卡模型（已是清單）。
- 不處理 CM、MRI、Unknown、CT、ER、General 等其餘值。

## Impact

- Affected specs: vault-native-publication, concept-subspecialty-filter, exam-builder, answer-analytics
- Affected code:
  - Modified: scripts/vault_site/compiler.py, js/vault-app.js, js/scheduler/test-builder.js, js/scheduler/weakness.js, js/analytics-view.js, scripts/test_vault_site.py, scripts/test_exam_builder.js, scripts/test_scheduler.js, 104 張 vault/questions 題卡, 2 張 vault/concepts 概念卡
  - New: 無
  - Removed: 無
