## Context

網站是 GitHub Pages 上的純靜態 vanilla JS（`js/vault-app.js` 路由、`js/vault-question-view.js` 題目卡、`js/data-loader.js` 學習進度），內容由 `scripts/vault_site/compiler.py` 從 vault 編譯。學習進度存 localStorage `rex_progress`（schema v2：`seen`、`starred`、`answers[<id>] = {last, correct, ts, sourceSha256}`、`examHistory[]`），只記每題最後一次，無法跨裝置、無法支撐排程與校準。

使用者 2026-10-10 決定：後端用 Cloudflare Workers + D1（已有 Cloudflare 帳號與 img-hosting Worker）；帳號為邀請制給少數同事／住院醫師；登入用帳號密碼即可；題庫為單選 MCQ，部分題目官方答案有誤需獨立旗標；FSRS 等學習功能放在下一個 change `study-scheduler`，本 change 只鋪事件流。

查證結論（2026-10-10）：wrangler 4.149、官方建議 `wrangler.jsonc`；github.io 與 workers.dev 為跨站，Safari 預設封鎖第三方 cookie，HttpOnly cookie session 不可靠；workerd 的 PBKDF2 硬上限 100,000 次，Workers Free 每請求 CPU 10 ms；`ratelimits` binding 2025-09 GA（period 10 或 60 秒，key 建議用帳號）；D1 Free 每日 10 萬列寫入、`batch()` 具交易語意、每查詢 100 個 bound parameters；ts-fsrs 5.4.2 有 UMD bundle（下一個 change 使用）。mcq-bank（MIT）可移植：`attemptOutbox`、`attemptFlusher` 觸發點、`questionTimer`、`clampElapsedMs`、冪等鍵 `${user}:${key}` 模式、`confidence_events` 值域 1–3。

約束：內容（題目、概念）維持純靜態，不經後端；未登入仍可完整離線使用；不新增前端框架或建置步驟；Worker 以 plain JavaScript ES module 撰寫、純函式用 `node --test`；機密只放 wrangler secrets 與 GitHub Actions secrets。

## Goals / Non-Goals

**Goals:**

- 邀請制帳號密碼登入，跨裝置看到同一份學習紀錄。
- 學習紀錄改為 append-only 作答事件（含耗時、信心、來源 sha256），本機離線先寫、上線補送、重送冪等。
- 舊 v2 進度在首次登入時無損轉入事件流。
- 題卡可標記「官方答案有誤、依覆核答案計分」。
- Worker 可由 GitHub Actions 自動部署；本機以 `wrangler dev` 全程可測。

**Non-Goals:**

- FSRS 排程、今日到期、錯題判準改版、信心校準面板、組卷條件、弱點分群（下一個 change）。
- Turnstile、OAuth、Email 驗證、密碼重設信（管理者可直接重發邀請碼並停用舊帳號）。
- 多人協作功能（共筆、留言、聊天）。
- 把前端搬到 Workers Static Assets 或自訂網域（列為日後可改用 cookie 的前提，本 change 不做）。
- 修改任何題卡內容；`2020-013` 等實際標記由醫師日後逐題完成。

## Decisions

### 後端骨架：Worker plain JS、wrangler.jsonc、D1 migrations、純函式可測

- `worker/` 獨立目錄，自有 `package.json`（devDependencies 只有 `wrangler`）、`wrangler.jsonc`（`name: rex-api`、`main: src/index.js`、`compatibility_date` 為實作當日、`d1_databases[0].binding = "DB"`、`migrations_dir = "migrations"`、`ratelimits[0] = {name: "LOGIN_LIMITER", namespace_id: "1001", simple: {limit: 5, period: 60}}`、`vars.ALLOWED_ORIGINS`、`vars.ADMIN_USERNAMES`）。`database_id` 由使用者建立 D1 後填入。
- `src/index.js` 只做路由分派與錯誤轉 JSON；每個模組（`password.js`、`session.js`、`invites.js`、`attempts.js`、`idempotency.js`、`cors.js`、`sync.js`）匯出不依賴 `Request` 的純函式，D1 以參數注入。單元測試 `worker/test/*.test.js` 用 Node 22 內建 `node:test` 與 WebCrypto，不需要 Miniflare。
- 替代方案「TypeScript + Hono」被否決：前端已是零建置 vanilla JS，Worker 同樣零建置可降低維護面；路由數少於 15 條，手寫 `switch` 足夠。

### 帳號、密碼與邀請碼

- `users(id INTEGER PK, username TEXT UNIQUE, display_name TEXT, password_hash TEXT, role TEXT CHECK(role IN ('member','admin')), created_at, disabled_at)`。username 正規化：trim、小寫、`^[a-z0-9][a-z0-9_.-]{2,31}$`。
- 密碼：`crypto.subtle.deriveBits` PBKDF2-HMAC-SHA256，salt 16 bytes，輸出 32 bytes，迭代數常數 `PBKDF2_ITERATIONS`（預設 100,000），入庫格式 `$pbkdf2-sha256$i=<n>$<salt b64url>$<hash b64url>`；驗證時解析字串內的迭代數，常數調高後下次登入成功即重新雜湊（透明升級）。比對用 `crypto.subtle.timingSafeEqual`。密碼長度 8–128。
- 迭代數與 Free 方案 CPU 10 ms 的關係未知：實作任務必須在 `wrangler dev` 與部署後各量測一次 `/auth/login` 的 CPU 時間（`wrangler tail` 的 `cpuTime`），若超時則把常數降到可通過的最大值並寫進 `docs/account-sync.md`；若使用者升級 Paid 再調回。這是唯一允許的妥協，補償措施是邀請制、rate limit 與鎖定。
- 邀請碼：`invites(id, code_hash TEXT UNIQUE, note, created_by, created_at, expires_at, used_by, used_at, revoked_at)`。碼為 24 字元 base32（`crypto.getRandomValues`），只在簽發回應中出現一次，D1 存 SHA-256。註冊 `POST /auth/register {username, password, inviteCode, displayName?}`：碼有效、未用、未撤銷、未過期才建立 user，同一 `batch()` 內標記 `used_by`。
- 第一位管理者：環境 secret `BOOTSTRAP_INVITE_CODE`，只在 `users` 表為空時被接受，建立的帳號 role 依 `ADMIN_USERNAMES` 判定；之後此 secret 無作用。
- role 判定：`ADMIN_USERNAMES`（逗號分隔）在登入時寫入 `users.role`，與 mcq-bank 的環境變數白名單模式相同。
- 替代方案「Email 為帳號 + 寄信驗證」被否決：使用者指定帳號密碼即可，且 Workers 寄信需另接服務。

### Session：Bearer token，不用跨站 cookie

- `sessions(id, user_id, token_hash TEXT UNIQUE, created_at, expires_at, last_used_at, user_agent)`。登入回傳 `token`（32 bytes base64url）一次；D1 存 SHA-256。到期 30 天固定；`last_used_at` 每 5 分鐘最多更新一次。
- 前端存 localStorage `rex_session = {token, username, displayName, role, expiresAt}`，每個 API 請求帶 `Authorization: Bearer <token>`。登出 `POST /auth/logout` 刪該列並清本機。`GET /auth/me` 回使用者與 session 到期。
- XSS 緩解：`index.html` 加 CSP `default-src 'self'; connect-src 'self' https://*.workers.dev https://img-hosting.jieyu166.workers.dev; img-src 'self' https: data:; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'`；note renderer 既有轉義不變。
- 替代方案「HttpOnly cookie」被否決：跨站在 Safari／iOS 不可用；若日後前端與 API 同站再切換，`session.js` 的 token 產生與驗證不變，只換傳輸層。

### 登入節流與鎖定

- 第一層 `env.LOGIN_LIMITER.limit({key: username})`，超過回 429。
- 第二層 `login_attempts(username PK, failed_count, locked_until, updated_at)`：連續 5 次失敗鎖 15 分鐘，成功即歸零；鎖定中回 423 並附 `retryAfterSeconds`。
- 錯誤訊息一律「帳號或密碼錯誤」，不區分帳號不存在。

### 作答事件流（append-only attempts）與同步協定

- `attempts(id INTEGER PK, user_id, client_id TEXT, question_id, chosen TEXT, is_correct INTEGER, source TEXT CHECK(source IN ('card','exam','legacy')), elapsed_ms INTEGER, confidence INTEGER CHECK(confidence IN (1,2,3)), source_sha256 TEXT, client_ts INTEGER, created_at INTEGER, UNIQUE(user_id, client_id))`；索引 `(user_id, created_at)`、`(user_id, question_id, created_at)`。`client_id` 由前端產生（`crypto.randomUUID()`），`INSERT OR IGNORE` 即為冪等，不另設 request_dedup 表。
- `bookmarks(user_id, question_id, starred INTEGER, updated_at, PRIMARY KEY(user_id, question_id))`：最後寫入為準（`updated_at` 較新者勝）。
- `exam_results(id, user_id, client_id UNIQUE per user, total, correct, wrong, skipped, pct, wrong_ids TEXT(json), source_sha256_by_question TEXT(json), client_ts, created_at)`。
- `seen` 不同步（本機便利資訊，由作答事件亦可導出）。
- API：`POST /sync/attempts {items:[...]}`（每批 ≤ 40 筆，單批 `batch()`；回 `{accepted, ignored}`）、`POST /sync/bookmarks {items:[{questionId, starred, updatedAt}]}`、`POST /sync/exams {items:[...]}`、`GET /sync/snapshot?sinceAttemptId=<n>` 回 `{attempts:[id>since 的全部], bookmarks:[全部], exams:[全部], latestAttemptId}`。所有寫入端點驗證欄位型別、`chosen ∈ A–E 或 null`、`elapsed_ms` 以 `clampElapsedMs` 夾到 0–1,800,000。
- 選擇「客戶端 UUID 唯一鍵」而非 mcq-bank 的 `Idempotency-Key` header＋dedup 表：批次上傳每筆各自冪等，資料表本身即去重，少一張表與一次查詢。

### 前端：progress schema v3、outbox、計時、信心

- `rex_progress` 升 v3：`{schemaVersion: 3, seen, starred, answers, examHistory, attempts: [], outbox: {attempts: [], bookmarks: [], exams: []}, sync: {latestAttemptId, lastSyncAt}}`。`answers[<id>]` 由 `attempts` 的最後一筆導出（`_normalizeProgress` 在讀取時重算），對既有呼叫者（篩選、徽章）介面不變。v2 讀入時：每個 `answers[<id>]` 轉成一筆 `source: 'legacy'` 的 attempt（`client_id = legacy:<id>:<ts>`），`examHistory` 每筆轉成 `client_id = legacy-exam:<ts>`；轉換是確定性的，重複執行不會產生新事件。
- 本機 attempts 上限 5,000 筆（保留最新），伺服器為真相；snapshot 下載後以 `client_id` 合併去重。
- `js/attempt-outbox.js`：移植 mcq-bank `attemptOutbox`（localStorage、`MAX = 300`、同鍵只留一筆、循序 flush、首次失敗即停）＋ `attemptFlusher` 觸發點（啟動、`online`、`visibilitychange` 回前景、`pagehide` 且非空），改以 fetch 與 Bearer header。未登入時 outbox 只累積不送。
- `js/question-timer.js`：移植 `questionTimer`（純函式狀態機、可見區間累計、10 分鐘截斷 `outlier`）。`vault-question-view.js` 在題卡掛載時 `startTimer`，揭曉時 `read` 得 `elapsedMs`。
- 信心：揭曉前於選項下方顯示「猜／普通／有把握」三個可略過的按鈕，選了才寫 `confidence`，模擬考不顯示。
- `js/sync-client.js`：`login/register/logout/me/pushOutbox/pullSnapshot`，`window.REX_API_BASE` 為基底（`index.html` 內 `<script>` 設定，預設 `https://rex-api.<account>.workers.dev`），401 時清本機 session 並顯示「請重新登入」。
- 設定面板新增「帳號」區：未登入顯示登入／註冊表單（註冊需邀請碼），已登入顯示使用者名、同步狀態（待送筆數、上次同步時間）、「立即同步」、「登出」。既有匯出／匯入／清除保留；匯出 v3 含 attempts，匯入 v2 或 v3 皆合併。

### 題卡 `answerStatus: corrected`（官方答案有誤）

- frontmatter 契約：`answerStatus: corrected`、`officialAnswer: <單一 A–E>`、`correctAnswer`／`acceptedAnswers` 為覆核後答案（可為單一或 `any` 多重）。compiler：`ANSWER_STATUSES` 加 `corrected`；`officialAnswer` 必須是單一 A–E 且不在 accepted set，否則 hard error `question_official_answer`；`corrected` 視同 `confirmed` 計分（`scorable: true`）；`sr.officialAnswer` 投影為字串（非 corrected 時 `""`）；`indexes/questions.json` 既有 `answerStatus` 欄位自然帶出。
- 前端：揭曉後在答案徽章旁顯示「官方公布 B 有誤，依覆核答案 D 計分」；模擬考納入；`scoreAnswers` 不變（已依 acceptedAnswers）。
- 替代方案「用 `reviewStatus` 或新 tag」被否決：答案語意與覆核狀態已分離（4.5 決策），`corrected` 落在 answerStatus 維度最一致。

### 部署與機密

- `.github/workflows/deploy-worker.yml`：push main 且 `worker/**` 變動時，`npm ci` → `wrangler d1 migrations apply rex-progress --remote` → `wrangler deploy`，secrets `CLOUDFLARE_API_TOKEN`、`CLOUDFLARE_ACCOUNT_ID`。Worker secrets（`BOOTSTRAP_INVITE_CODE`）由使用者以 `wrangler secret put` 設定一次。
- 使用者需手動完成（實作時會明確停下來請使用者做）：建立 D1 資料庫並把 `database_id` 填入 `wrangler.jsonc`、建立 Cloudflare API token（Workers Scripts:Edit、D1:Edit）並存入 GitHub secrets、設定 `BOOTSTRAP_INVITE_CODE`。
- `THIRD_PARTY_NOTICES.md` 記錄自 mcq-bank（MIT, Hsiehting Lin 2026）移植的 outbox／timer／clamp 邏輯與完整授權文字。

## Implementation Contract

**Behavior**

- 未登入：網站行為與現況相同，作答仍寫本機；設定面板顯示登入／註冊。
- 註冊：有效邀請碼 → 201 並直接登入（回 token）；無效、已用、過期、撤銷 → 400 `invite_invalid`；`users` 為空且碼等於 `BOOTSTRAP_INVITE_CODE` → 視為有效。
- 登入：正確 → 200 `{token, user:{username, displayName, role}, expiresAt}`；錯誤 → 401 `auth_failed`；連續 5 次失敗 → 423 `locked` 附 `retryAfterSeconds`；超過 rate limit → 429。
- 已登入作答：每題揭曉時本機立即新增 attempt 與 outbox 項目，畫面不等待網路；flush 成功後 outbox 清空、`sync.lastSyncAt` 更新；同一 `client_id` 重送 → 伺服器 `ignored` 計數 +1、資料不重複。
- 換裝置登入：`pullSnapshot` 後 `answers`、`starred`、`examHistory` 與原裝置一致（以事件流重算）。
- 首次登入時本機有 v2 進度：轉成 legacy attempts 上傳；重新整理再登入不會再產生新事件。
- `answerStatus: corrected` 題目：揭曉顯示官方答案有誤提示；選覆核答案得分；`officialAnswer` 不合法時 build 失敗。
- 停用帳號（`disabled_at` 非空）的 token 一律 401。

**Interface / data shape**

- Worker 路由：`POST /auth/register`、`POST /auth/login`、`POST /auth/logout`、`GET /auth/me`、`POST /sync/attempts`、`POST /sync/bookmarks`、`POST /sync/exams`、`GET /sync/snapshot`、`POST /admin/invites`、`GET /admin/invites`、`DELETE /admin/invites/:id`、`GET /admin/users`、`POST /admin/users/:id/disable`、`OPTIONS *`、`GET /health`。所有錯誤回 `{error: <code>, message}`。
- attempt 物件：`{clientId: string(uuid), questionId: string, chosen: 'A'|'B'|'C'|'D'|'E'|null, isCorrect: boolean|null, source: 'card'|'exam'|'legacy', elapsedMs: number|null, confidence: 1|2|3|null, sourceSha256: string|null, clientTs: number}`。
- `rex_progress` v3 如上；`rex_session` 如上。
- `DataLoader` 新增：`recordAttempt(attempt)`、`getAttempts()`、`getOutbox()`、`markSynced(clientIds)`、`mergeSnapshot(snapshot)`、`getSession()`／`setSession()`／`clearSession()`；既有 `getProgress`、`markSeen`、`toggleStar`、`recordAnswer`（內部改為產生 attempt）、`addExamRecord`、`exportProgress`、`importProgress`、`clearProgress` 簽名不變。
- `password.js`：`hashPassword(password) -> Promise<string>`、`verifyPassword(password, phc) -> Promise<{ok, needsRehash}>`、`parsePhc(string)`；`session.js`：`newToken() -> {token, tokenHash}`、`hashToken(token)`；`attempts.js`：`validateAttempt(obj) -> {ok, value|errors}`、`clampElapsedMs`；`cors.js`：`corsHeaders(origin, allowedOrigins)`。
- compiler `sr` 新增 `officialAnswer: string`；錯誤碼 `question_official_answer`。

**Failure modes**

- 網路失敗或 5xx：outbox 保留，下次觸發再送；畫面顯示「待同步 N 筆」。
- 401：清 `rex_session`，outbox 保留，提示重新登入。
- 批次中某筆欄位不合法：整批 400 並回 `errors[{index, reason}]`，前端把該筆標記 `invalid` 移出 outbox 並記錄 console warning，其餘重送。
- D1 寫入額度用盡（錯誤訊息含 `limit`）：Worker 回 503 `quota`，前端保留 outbox 並延後。
- localStorage 不可用：所有寫入 try/catch 吞掉並 console.warn，網站仍可瀏覽。

**Acceptance criteria**

- `node --test worker/test/`：password（PHC 格式、驗證、needsRehash）、session token、invite 碼驗證、attempt 驗證與 clamp、CORS、snapshot 合併，全部通過。
- `node scripts/test_study_progress.js`：v2 → v3 遷移確定性、attempts 導出 answers、outbox 入列／去重／flush 順序、snapshot 合併去重。
- `node scripts/test_attempt_outbox.js`、`node scripts/test_question_timer.js`：移植函式案例（含 10 分鐘 outlier、hide/show 冪等）。
- `node scripts/test_vault_question_view.js`：corrected 題目揭曉文字、信心三鍵只在 card 模式出現。
- `python scripts/test_vault_site.py`：corrected 合法／`officialAnswer` 缺少／等於 accepted 三案。
- `wrangler dev` 本機：以 curl 腳本 `worker/test/smoke.sh` 走完 bootstrap 註冊 → 登入 → 上傳 3 筆 attempts → 重送同批（ignored=3）→ snapshot → 登出 → 401；全部回應碼符合契約。
- 部署後：瀏覽器 A 登入作答 2 題，瀏覽器 B（或無痕）登入後 `answers` 含該 2 題；`wrangler tail` 顯示登入請求的 cpuTime 與迭代數記錄於 `docs/account-sync.md`。
- 既有 7 套測試與 `accept_vault_native_migration.py` 仍通過。

**Scope boundaries**

- In：上述 Decisions；`index.html` 設定面板帳號區與 CSP；題卡 `corrected` 契約與渲染；文件。
- Out：FSRS 與任何排程 UI；Turnstile；Email；自訂網域；修改題卡內容；清理 `index.html` 其他舊殼層。

## Risks / Trade-offs

- [PBKDF2 100k 在 Free 10 ms CPU 內可能超時] → 任務內實測並調整常數；PHC 字串記錄迭代數，升級後透明重雜湊；同時有邀請制、rate limit、鎖定三層補償。
- [Bearer token 可被 XSS 竊取] → CSP 限制 script 來源；note renderer 既有轉義；token 30 天到期、可由管理者停用帳號使所有 session 失效。
- [D1 Free 每日 10 萬列寫入] → 每筆 attempt 含 2 個索引約算 3 列；少數使用者每日數百題遠低於上限；超額時回 503 且 outbox 保留。
- [v2 遷移重複上傳] → legacy `client_id` 由題號與時間戳確定性組成，伺服器 `INSERT OR IGNORE`。
- [outbox 與多分頁同時寫 localStorage 競態] → flush 前重讀、同鍵去重；接受偶發重送，由伺服器冪等吸收。
- [使用者尚未建立 D1 與 token 時 CI 部署會失敗] → workflow 僅在 `worker/**` 變動觸發；實作時先完成本機 `wrangler dev` 驗證，部署任務明確停下來等使用者提供 database_id 與 secrets。

## Migration Plan

1. 先合併不影響現況的部分：compiler `corrected`、前端 v3 schema（讀 v2 自動轉）、outbox／timer 模組與測試；此時未登入行為不變。
2. Worker 本機開發與 smoke 測試通過後，請使用者建立 D1、填 `database_id`、設定 GitHub secrets 與 `BOOTSTRAP_INVITE_CODE`；推 main 觸發 `deploy-worker.yml`。
3. 前端 `REX_API_BASE` 指向正式 Worker，推 main 部署 Pages；使用者以 bootstrap 碼註冊管理者，簽發邀請碼給同事。
4. 回滾：前端 revert 即回到純本機模式（v3 檔案仍可讀）；Worker 可 `wrangler rollback`；D1 資料保留。

## Open Questions

- Free 方案下 PBKDF2 可行的最高迭代數（實作時量測，不阻塞設計）。
- `REX_API_BASE` 的正式網址（Worker 名稱 `rex-api`，實際子網域取決於使用者帳號，部署後填入）。
