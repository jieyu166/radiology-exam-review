## Why

`account-progress-sync` 之後，每位使用者的作答都是帶耗時與信心的 append-only 事件，但網站仍只有「隨機翻卡／模擬考」兩種學習方式：沒有排程告訴使用者今天該複習哪些題、錯題清單用「曾經答錯」永遠不會縮小、無法知道自己哪類題目高信心卻答錯、模擬考不能只抽未做過或答錯的題、也看不出弱點集中在哪些次專科與概念。本 change 借鏡 mcq-bank（MIT）的純函式，在事件流之上補齊這些學習功能。

## What Changes

- 新增 FSRS 間隔重複排程：前端以 ts-fsrs 5.4.2（UMD，jsDelivr）計算，每題一張 FSRS card（stability、difficulty、due、state、reps、lapses、learning_steps、last_review），作答揭曉後以 again／hard／good／easy 四鍵評分；日界台灣時間凌晨 4 點；今日佇列依「learning 優先 → 每 3 張到期插 1 張新卡 → 新卡每日上限（預設 20，可設 0–200）」混排；card 與 review log 經既有同步協定存到 D1（新表 `fsrs_cards`、`fsrs_review_logs`），跨裝置一致。
- 新增「今日複習」路由：顯示到期／學習中／新卡剩餘數，逐題作答並評分；提供四鍵的下次到期預覽。
- **BREAKING（語意）** 錯題判準改為「最近一次作答答錯」（`last_correct = 0`），取代「曾經答錯」；「只顯示答錯過」篩選與模擬考的 `wrong` 條件同步採用。
- 新增信心校準面板（設定或統計頁）：三個信心等級的作答數與正確率、最近 20 題「有把握卻答錯」清單並可直接開啟題目。
- 模擬考組卷條件：狀態（未做過／最近答錯／答對過／已收藏，彼此 OR）× 年份 × 次專科 × 概念（AND），題數 1–100，tutor（作答即揭曉）與 timed（倒數）切換；續考落點為第一個未作答題。
- 弱點分群：依次專科與概念把最近答錯的題分群（每群 ≥ 2 題、最多 12 群、anchor 為最近答錯），可一鍵「練這一群」（跨年份交錯、seeded 洗牌、確定性）。
- 概念頁新增「練這個概念的題（跨年交錯）」。
- 所有新函式皆為無框架純函式（`js/scheduler/*.js`），以 `node --test` 風格的 `scripts/test_*.js` 測試；D1 僅新增表與同步端點，排程計算不在伺服器。

## Capabilities

### New Capabilities

- `spaced-repetition-scheduling`: FSRS card 狀態、評分、日界、今日佇列混排、新卡上限、跨裝置同步。
- `review-queue-ui`: 今日複習路由、四鍵評分與預覽、佇列計數。
- `answer-analytics`: 錯題判準、信心校準、弱點分群、交錯練習。
- `exam-builder`: 組卷條件、tutor／timed、續考落點。

### Modified Capabilities

- `study-progress`: `rex_progress` 新增 `cards`、`reviewLogs`、`settings.newPerDay`、`settings.dayStartHour`；「只顯示答錯過」改用最近一次判準。
- `progress-sync`: outbox 與 snapshot 新增 cards（last-write-wins by `updatedAt`）與 reviewLogs（append-only by `clientId`）。
- `vault-native-review-web`: 導覽新增「今日複習」；模擬考設定頁改為組卷條件；概念頁新增交錯練習入口。

## Impact

- Affected specs: spaced-repetition-scheduling（新）、review-queue-ui（新）、answer-analytics（新）、exam-builder（新）、study-progress、progress-sync、vault-native-review-web
- Affected code:
  - New: js/scheduler/fsrs-adapter.js, js/scheduler/due-window.js, js/scheduler/queue-mix.js, js/scheduler/wrong-criterion.js, js/scheduler/calibration.js, js/scheduler/test-builder.js, js/scheduler/weakness.js, js/scheduler/drill.js, js/scheduler/exam-resume.js, js/review-view.js, js/analytics-view.js, scripts/test_scheduler.js, scripts/test_review_view.js, scripts/test_exam_builder.js, worker/migrations/0003_fsrs.sql, worker/src/fsrs-sync.js, worker/test/fsrs-sync.test.js
  - Modified: index.html, css/main.css, js/vault-app.js, js/vault-question-view.js, js/data-loader.js, js/sync-client.js, js/attempt-outbox.js, worker/src/index.js, worker/src/sync.js, scripts/test_study_progress.js, scripts/test_vault_question_view.js, README.md, docs/account-sync.md, THIRD_PARTY_NOTICES.md
  - Removed: 無
