## Context

前置 change `account-progress-sync` 提供：邀請制帳號與 Bearer session、`rex_progress` v3（append-only `attempts` 含 `elapsedMs`、`confidence`、`sourceSha256`、`clientId`）、localStorage outbox 與 `POST /sync/*`／`GET /sync/snapshot` 協定、D1 表 `attempts`、`bookmarks`、`exam_results`。本 change 全部建立在那之上；若前置 change 尚未 archive，本 change 不得 apply。

借鏡來源 mcq-bank（MIT, Hsiehting Lin 2026, https://github.com/htlin222/mcq-bank）的純函式規格已查證：`fsrs.ts`（ts-fsrs 5.4.x，`request_retention 0.9`、`maximum_interval 36500`、`enable_fuzz false`、`enable_short_term true`、`learning_steps ['1m','10m']`、`relearning_steps ['10m']`）、`due-window.ts`（UTC+8、日界 04:00、learning/relearning 須 `due_at <= now`、review 以 `due_at <= dayEnd`）、`queue-mix.ts`（learning 優先、`NEW_EVERY = 4`、新卡每日預設 20 上限 200）、`wrong-criterion.ts`（`times_seen > 0 AND last_correct = 0`）、`calibration.ts`（三等級 bucket）、hypercorrection 候選（`confidence = 3 AND is_correct = 0` 最近 20 題）、`testBuilder.ts`（status 之間 OR、維度之間 AND、count 1–100 預設 20、tutor 需 `=== true`、timed 預設真）、`weakness.ts`（`groupByTopic` min 2、limit 12、anchor 為最近答錯）、`drill.ts`（LCG seeded Fisher–Yates、年份 round-robin）、`examResume.ts`（第一個未作答，全答完回 0）。

ts-fsrs 5.4.2 提供 UMD bundle `https://cdn.jsdelivr.net/npm/ts-fsrs@5.4.2/dist/index.umd.js`，全域 `FSRS`，API：`createEmptyCard(now)`、`fsrs(generatorParameters(params))`、`scheduler.repeat(card, now)` 回四評分預覽、`scheduler.next(card, now, Rating.X)` 回 `{card, log}`、`Rating {Again:1, Hard:2, Good:3, Easy:4}`、`State {New:0, Learning:1, Review:2, Relearning:3}`、`get_retrievability(card, now, false)`。

約束：前端零建置、無框架；排程全部在前端計算，D1 只存狀態；離線可用；每個新模組都是可用 `node --test` 風格腳本測試的純函式；MIT 來源需列入 `THIRD_PARTY_NOTICES.md`。

## Goals / Non-Goals

**Goals:**

- 每題一張 FSRS card，四鍵評分，今日佇列混排，跨裝置一致。
- 錯題判準改為「最近一次答錯」，全站一致。
- 信心校準面板與 hypercorrection 清單。
- 模擬考組卷條件、tutor／timed、續考落點。
- 弱點分群與跨年交錯練習。

**Non-Goals:**

- FSRS 參數個人化訓練（optimizer）；沿用 ts-fsrs 預設權重。
- 伺服器端排程或推播提醒。
- 多人統計、排行榜。
- 修改題卡內容或 compiler（本 change 不碰 vault 與 `scripts/vault_site/`）。
- 離線 service worker 快取（另案）。

## Decisions

### FSRS 介接：ts-fsrs UMD 於前端，card 與 log 走既有同步

- `index.html` 以 `<script src="https://cdn.jsdelivr.net/npm/ts-fsrs@5.4.2/dist/index.umd.js" integrity="<sha384>" crossorigin="anonymous">` 載入，CSP `script-src` 已含 `https://cdn.jsdelivr.net`。`js/scheduler/fsrs-adapter.js` 包裝：`createCard(now)`、`rate(cardRow, now, rating) -> {cardRow, log}`、`preview(cardRow, now) -> {again, hard, good, easy}`（各含 `dueAt`、`scheduledDays`、`state`）、`retrievability(cardRow, now)`。cardRow 欄位全為 epoch 毫秒與數字：`{questionId, dueAt, stability, difficulty, elapsedDays, scheduledDays, learningSteps, reps, lapses, state, lastReviewAt, updatedAt}`，與 mcq-bank `FsrsCardRow` 對齊。若全域 `FSRS` 不存在（CDN 失敗），今日複習路由顯示「排程模組載入失敗，可繼續用卡片模式」而不中斷其他功能。
- 參數：`request_retention 0.9`、`maximum_interval 36500`、`enable_fuzz false`、`enable_short_term true`、`learning_steps ['1m','10m']`、`relearning_steps ['10m']`、`w` 用 ts-fsrs 預設。
- 本機：`rex_progress.cards[<questionId>] = cardRow`、`rex_progress.reviewLogs[]`（`{clientId, questionId, rating, state, dueAt, stability, difficulty, elapsedDays, lastElapsedDays, scheduledDays, learningSteps, reviewedAt}`，上限 5,000）。同步：cards 為 last-write-wins by `updatedAt`（outbox `cards` 佇列、`POST /sync/cards`）、reviewLogs 為 append-only by `clientId`（`POST /sync/review-logs`）；`GET /sync/snapshot` 新增 `cards` 與 `reviewLogs`（`sinceReviewLogId`）。D1 `fsrs_cards(user_id, question_id, …, updated_at, PRIMARY KEY(user_id, question_id))`、`fsrs_review_logs(id, user_id, client_id, …, UNIQUE(user_id, client_id))`。
- 替代方案「Worker 端計算排程」被否決：離線必須能評分，且 ts-fsrs 在瀏覽器可直接用；伺服器只做儲存，與事件流一致。

### 日界、佇列混排與新卡上限

- `js/scheduler/due-window.js`：移植 `dayWindow(now, {dayStartHour})`（固定 UTC+8、預設 4 點、`clampHour`）、`isDueToday(card, now, window)`（新卡與無卡為 true；Learning／Relearning 須 `dueAt <= now`；Review 以 `dueAt <= dayEnd`）。
- `js/scheduler/queue-mix.js`：移植 `pickNextKind({served, learning, dueReview, newAvailable, newRemaining})`、`remainingNewToday(introducedToday, limit)`、`parseNewLimit(raw)`（預設 20、上限 200）。「今日已引入新卡數」＝ `reviewLogs` 中 `reviewedAt` 落在今日 window 且該 log 的前一狀態為 New（以 log 的 `state` 欄位記錄評分前狀態 New=0）的題數。
- 設定面板新增「每日新卡上限」（0–200）與「日界時刻」（0–23，預設 4），存 `rex_progress.settings`，隨 snapshot 同步（last-write-wins）。
- 佇列候選：`learning` ＝ cards 中 state 1/3 且 `dueAt <= now`；`dueReview` ＝ state 2 且 `dueAt <= dayEnd`；`newAvailable` ＝ 目前篩選（年份／次專科）下 scorable 且無 card 的題；佇列排序：learning 依 dueAt、due 依 dueAt、new 依題號。
- 替代方案「依使用者時區」被否決：使用者群在台灣，固定 UTC+8 與 mcq-bank 相同，少一個設定。

### 今日複習路由與四鍵評分

- 新路由 `#/review`，導覽列與底部導覽新增「今日複習」。畫面：頂部計數「學習中 L／到期 D／新卡 N（剩餘 R）」，中央為既有 `VaultQuestionView` 題目卡（card 模式，含信心三鍵），揭曉後顯示四鍵 again／hard／good／easy，每鍵附 `preview` 的下次間隔（「<1 分」「10 分」「3 天」格式）。評分即：寫 card、寫 reviewLog、產生 attempt（`source: 'review'`，attempts 的 source CHECK 需放寬加入 `review`）、三者入 outbox、取下一題。
- 鍵盤：1–4 對應四鍵，空白鍵揭曉。
- 佇列為空時顯示「今日完成」與明日到期數。
- 替代方案「把評分做成答對自動 good／答錯自動 again」被否決：FSRS 需要主觀難度；但提供預設焦點（答對預設 good、答錯預設 again）加速操作。

### 錯題判準改為最近一次答錯

- `js/scheduler/wrong-criterion.js`：`isWrong(answerEntry)` ＝ `answerEntry && answerEntry.correct === false`（`answers[<id>]` 已由最新 attempt 導出，即「最近一次」）；提供 `wrongIds(progress)`。「只顯示答錯過」篩選、組卷 `wrong` 狀態、弱點分群輸入三處統一使用。
- 弱點分群不採 mcq-bank `/weakness-map` 的寬鬆判準（`last_correct = 0 OR times_correct*2 < times_seen`），全站只有一種定義。
- 文案改為「最近答錯」。

### 信心校準與 hypercorrection

- `js/scheduler/calibration.js`：移植 `calibration(events) -> [{confidence, n, correct, accuracy}]`（三等級固定輸出，`accuracy` 在 n=0 時為 null）；`hypercorrectionCandidates(attempts, limit=20)` ＝ `confidence === 3 && isCorrect === false` 依 `clientTs` 遞減。
- 新路由 `#/stats`（設定面板加入口）：校準表、hypercorrection 清單（題號、年份、次專科、連結到 `#/card?qid=`）、弱點分群區塊（見下）。

### 組卷條件、tutor／timed 與續考

- `js/scheduler/test-builder.js`：`normalizeFilters(raw) -> {status[], years[], subspecialties[], concepts[], count, tutor, timed}`（status 只接受 unseen／wrong／correct／bookmarked，去重保序；count 夾 1–100 預設 20；tutor 需 `=== true`；timed 非 `=== false` 即真；空陣列代表不限）、`buildPool(entries, progress, filters) -> entryIds`（status 之間 OR、維度之間 AND，unseen＝無 attempt、wrong＝最近答錯、correct＝最近答對、bookmarked＝starred；排除 `scorable: false`）、`sample(pool, count, seed)`（seeded Fisher–Yates，seed 預設 `Date.now()`，結果記錄在 examHistory 供重現）。
- 模擬考設定頁改為條件表單；`tutor` 模式作答即揭曉、`timed` 模式顯示每題倒數（預設 90 秒／題，可關）。進行中考試狀態 `rex_progress.activeExam = {entryIds, answers, index, startedAt, filters, seed}` 持久化，重新整理後以 `js/scheduler/exam-resume.js` 的 `resumeIndex(entries, answers)`（第一個未作答，全答完回 0）續考。
- 替代方案「保留原本只有題數的設定」被否決：使用者明確要組卷條件。

### 弱點分群與交錯練習

- `js/scheduler/weakness.js`：移植 `groupByTopic(rows, order, {min: 2, limit: 12})`：rows 由最近答錯題展開為 `{slug, label, questionId}`，第一層 slug 為次專科，第二層為 `conceptIds`；order 為依 `clientTs` 遞減的答錯題號；size 遞減、同 size 以 label `localeCompare`；anchor 為排名最小者。
- `js/scheduler/drill.js`：移植 `seededShuffle(arr, seed)`（LCG 1664525／1013904223）、`pickInterleaved(hits, {anchor, n, seed})`（去重、排除 anchor、依年份分桶、各桶 seeded 洗牌、round-robin）。
- 入口：`#/stats` 每群「練這一群」→ 以該群題號為 hits、anchor 為群 anchor、n 預設 10、seed 為當日 `dayKey` 雜湊，進入卡片模式的臨時佇列（不寫入 FSRS card，作答仍產生 `card` attempt）；概念頁「練這個概念的題（跨年交錯）」用 `relations` 的題號為 hits。

## Implementation Contract

**Behavior**

- `#/review`：顯示三個計數；取題順序符合 `pickNextKind`；評分後 card 更新、下一題立即出現；佇列空時顯示完成訊息；離線評分可用，上線後 cards／reviewLogs／attempts 自動同步。
- 四鍵預覽文字與實際評分後的 `dueAt` 一致。
- 「只顯示答錯過」只列最近一次答錯的題；答對一次即離開清單。
- `#/stats`：校準表三列；hypercorrection 最多 20 筆、最新在前；弱點分群最多 12 群、每群 ≥ 2 題。
- 模擬考：條件改變時即時顯示符合題數；開始後重新整理可續考到第一個未作答題；tutor 模式作答即揭曉並計分；timed 模式倒數歸零自動進下一題（記為未作答）。
- 兩裝置：A 評分 5 題後 B 登入，B 的 `#/review` 計數與 A 相同。

**Interface / data shape**

- `rex_progress` 新增：`cards: {<questionId>: cardRow}`、`reviewLogs: []`、`settings: {newPerDay: 20, dayStartHour: 4, examSecondsPerQuestion: 90}`、`activeExam | null`；`outbox` 新增 `cards`、`reviewLogs` 佇列；`sync` 新增 `latestReviewLogId`。
- attempts `source` 新增 `review`（前端與 D1 CHECK 同步放寬）。
- Worker：`POST /sync/cards {items:[cardRow]}`（last-write-wins by `updatedAt`）、`POST /sync/review-logs {items:[log]}`（`INSERT OR IGNORE` by `clientId`）、`GET /sync/snapshot?sinceAttemptId&sinceReviewLogId` 回傳新增 `cards`、`reviewLogs`、`latestReviewLogId`、`settings`。
- 純函式簽名如 Decisions；全部放 `js/scheduler/`，以 IIFE 掛到 `window.RexScheduler` 命名空間（`RexScheduler.dueWindow`、`RexScheduler.queueMix`…），測試腳本以 `vm` 載入。

**Failure modes**

- ts-fsrs 未載入：`#/review` 顯示降級訊息；其他路由不受影響；評分鍵不出現。
- card 與伺服器衝突（兩裝置離線各評同題）：`updatedAt` 新者勝，舊裝置下次 snapshot 覆蓋本機；reviewLogs 兩筆都保留。
- 佇列候選為空但有未來到期：顯示明日到期數與最早到期時間。
- `activeExam` 內題號已不存在於目前 index（內容更新）：跳過該題並在結果頁註明。

**Acceptance criteria**

- `node scripts/test_scheduler.js`：due-window（4 點日界、UTC+8、三種 state 判定）、queue-mix（spec 例：served 0..7 的 kind 序列、limit 解析）、wrong-criterion、calibration（n=0 為 null）、hypercorrection 排序與上限、test-builder（normalize 規則、OR/AND 池、seeded sample 可重現）、weakness（min/limit/anchor/排序）、drill（round-robin、確定性、排除 anchor）、exam-resume（全答完回 0）全部通過。
- `node scripts/test_review_view.js`：以 fixture cards 驗證計數、取題順序、評分後 card 欄位變化（用 ts-fsrs UMD 檔於 vm 載入）、四鍵預覽格式。
- `node scripts/test_exam_builder.js`：條件表單→池→抽樣→續考落點。
- `node --test worker/test/fsrs-sync.test.js`：cards last-write-wins、review-logs 冪等、snapshot since 過濾。
- `node scripts/test_study_progress.js` 擴充：v3 無 cards 時自動補空結構；outbox 新佇列 flush 順序。
- 瀏覽器（本機 wrangler dev）：兩 profile 一致性；離線評分 3 題後上線 outbox 歸零。
- 既有全部測試與 `accept_vault_native_migration.py` 通過；`deploy-pages.yml` 與 `deploy-worker.yml` 綠燈。

**Scope boundaries**

- In：上述 Decisions、`#/review` 與 `#/stats` 路由、模擬考設定頁改版、概念頁入口、D1 `0003_fsrs.sql`、兩個同步端點、文件與 MIT 聲明。
- Out：FSRS optimizer、提醒通知、service worker、題卡內容、compiler。

## Risks / Trade-offs

- [CDN 不可用導致排程不可用] → UMD 檔以 SRI 固定版本；失敗時降級訊息；可日後改為把 UMD 檔複製進 `js/vendor/`（需確認授權 MIT，可行）。
- [多裝置同題離線評分衝突] → cards last-write-wins、logs 全保留；衝突機率低（單人多裝置）。
- [新卡上限與篩選交互造成「今日沒新卡」誤解] → 計數列顯示「新卡剩餘 R／篩選內可用 N」。
- [reviewLogs 本機 5,000 上限] → 伺服器為真相；「今日已引入新卡數」只需當日 log。
- [attempts source 放寬需改 D1 CHECK] → 以 migration `0003` 重建約束（SQLite 需建新表搬資料），在 `node --test` 以 schema fixture 驗證。

## Migration Plan

1. 前置 change archive 後開始。先合併純函式模組與測試（無 UI 變更）。
2. 合併 D1 migration 與兩個同步端點，部署 Worker。
3. 合併前端路由與 UI，部署 Pages；舊 v3 進度自動補 `cards`／`reviewLogs` 空結構，無資料遷移。
4. 回滾：前端 revert 即回到無排程版本；D1 新表保留無害。

## Open Questions

- 無。參數（retention 0.9、日界 4 點、新卡 20）沿用 mcq-bank 預設，使用者可在設定面板調整新卡與日界。
