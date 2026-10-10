## Why

網站目前的學習進度只存在單一瀏覽器的 localStorage，換裝置或清快取就歸零，也無法讓少數同事／住院醫師各自累積紀錄；進度結構只記每題「最後一次」答案，無法支撐後續的間隔重複排程、錯題判準與信心校準。另外部分題目的官方答案有誤（例：2020-013），目前只能標成 `unresolved` 不計分，無法「依覆核答案計分並揭露官方答案有誤」。本 change 建立邀請制帳號、Cloudflare Workers + D1 後端與 append-only 作答事件流，作為下一個 change `study-scheduler` 的基礎。

## What Changes

- 新增 `worker/`：Cloudflare Worker（plain JavaScript ES module）＋ D1，提供註冊（需邀請碼）、登入、登出、我的帳號、作答事件上傳、進度快照下載、管理者邀請碼管理等 API；wrangler 設定、D1 migrations、純函式單元測試（`node --test`）。
- 新增帳號模型：邀請制（管理者簽發一次性邀請碼）、帳號密碼登入（WebCrypto PBKDF2-HMAC-SHA256，PHC 字串入庫、迭代數可升級）、Bearer session token（32 bytes 隨機、D1 只存 SHA-256、30 天到期；不用跨站 cookie，因 github.io 與 workers.dev 跨站 cookie 在 Safari 會被擋）、admin 由環境變數白名單決定、登入失敗以 Workers `ratelimits` binding ＋ D1 鎖定節流。
- **BREAKING（進度模型）** 學習進度由「每題最後一次答案」改為 append-only 作答事件（attempts：題號、選項、對錯、來源 card/exam、耗時、信心 1–3、來源 sha256、客戶端冪等鍵），`rex_progress` 改為事件流的本機快取＋離線 outbox；舊 v2 進度在首次登入時一次性轉成事件上傳。
- 前端新增登入／登出 UI（設定面板）、同步狀態指示、離線 outbox（localStorage，上線／切回前景／pagehide 時補送、`Idempotency-Key` 冪等）、作答時記錄單題耗時（頁面可見區間累計、10 分鐘截斷）與可略過的答前信心三鍵。
- 未登入仍可離線使用：所有學習狀態先寫本機，登入後合併上傳；內容（題目、概念）維持純靜態，不經後端。
- **BREAKING（內容模型）** 新增題卡答案狀態 `answerStatus: corrected`：frontmatter 以 `officialAnswer` 記錄有誤的官方答案、`correctAnswer`／`acceptedAnswers` 記錄覆核後答案；compiler 投影 `officialAnswer`，題目依覆核答案計分並在揭曉後顯示「官方答案 X 有誤，依覆核採 Y」。
- 部署：Worker 由獨立 GitHub Actions workflow（`wrangler deploy` ＋ `d1 migrations apply`）部署，前端 Pages 流程不變；前端以 `window.REX_API_BASE` 指向 Worker 網址。

## Capabilities

### New Capabilities

- `account-auth`: 邀請制帳號、密碼登入、Bearer session、管理者邀請碼簽發與撤銷、登入節流與鎖定。
- `progress-sync`: append-only 作答事件流的本機 outbox、冪等上傳、伺服器端儲存與快照下載、舊 v2 進度一次性遷移。
- `corrected-answer-state`: 題卡 `answerStatus: corrected` 的 frontmatter 契約、compiler 投影與驗證、前端計分與揭露。

### Modified Capabilities

- `study-progress`: 本機 `rex_progress` 升為 schema v3（新增 `attempts[]`、`outbox[]`、`account`），`answers[<id>]` 改為由事件導出的快取；「最近一次答案」語意不變，但來源改為事件流。
- `progress-backup`: 匯出／匯入改為包含事件流（v3），匯入舊 v2 檔仍可合併。
- `vault-native-publication`: `sr` 投影新增 `officialAnswer`，answerStatus 允許 `corrected`，validation 增加對應硬錯誤。
- `vault-native-review-web`: 揭曉後顯示官方答案有誤的提示；作答結果交給事件流而非直接寫 `answers`。

## Impact

- Affected specs: account-auth（新）、progress-sync（新）、corrected-answer-state（新）、study-progress、progress-backup、vault-native-publication、vault-native-review-web
- Affected code:
  - New: worker/wrangler.jsonc、worker/src/index.js、worker/src/auth.js、worker/src/password.js、worker/src/session.js、worker/src/attempts.js、worker/src/idempotency.js、worker/src/invites.js、worker/src/cors.js、worker/migrations/0001_accounts.sql、worker/migrations/0002_attempts.sql、worker/test/*.test.js、worker/package.json、js/sync-client.js、js/attempt-outbox.js、js/question-timer.js、scripts/test_sync_client.js、scripts/test_attempt_outbox.js、scripts/test_question_timer.js、.github/workflows/deploy-worker.yml、docs/account-sync.md、THIRD_PARTY_NOTICES.md
  - Modified: js/data-loader.js、js/vault-app.js、js/vault-question-view.js、js/content-store.js、index.html、css/main.css、scripts/vault_site/compiler.py、scripts/test_vault_site.py、scripts/test_vault_question_view.js、scripts/test_study_progress.js、scripts/validate_vault_site.py、README.md、.gitignore
  - Removed: 無
