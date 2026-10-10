# 帳號與學習進度同步（rex-api）

Spectra change：`account-progress-sync`（2026-10-10）。內容（題目、概念）仍由 vault 編譯成靜態檔；後端只存帳號與學習狀態。

## 架構

```
GitHub Pages（index.html + js/，零建置）
  ├─ js/data-loader.js   rex_progress v3：attempts（append-only）、bookmarks、examHistory、outbox、sync
  ├─ js/attempt-outbox.js 離線佇列：啟動／online／回前景／pagehide 觸發，循序分批（≤40）補送，首敗即停
  ├─ js/question-timer.js 單題計時（只算可見區間，10 分鐘 outlier）
  └─ js/sync-client.js    fetch 包裝：Bearer token、login/register/logout/me/pushOutbox/pullSnapshot
          │  Authorization: Bearer <token>（不用 cookie：github.io ↔ workers.dev 跨站，Safari 擋第三方 cookie）
          ▼
Cloudflare Worker rex-api（worker/，plain JS ES module，wrangler.jsonc）
  ├─ /auth/*   邀請制註冊、登入（ratelimits binding + D1 鎖定）、登出、me
  ├─ /admin/*  邀請碼簽發／列表／撤銷、使用者列表／停用（role=admin）
  ├─ /sync/*   attempts／bookmarks／exams 上傳、snapshot 下載
  └─ D1 rex-progress：users、invites、sessions、login_attempts、attempts、bookmarks、exam_results
```

## 資料模型

- `attempts`：`UNIQUE(user_id, client_id)`，`INSERT OR IGNORE` → 重送冪等；欄位 chosen A–E／null、is_correct、source card|exam|legacy、elapsed_ms 0–1,800,000、confidence 1–3、source_sha256、client_ts。API 永不更新或刪除。
- `bookmarks`：`(user_id, question_id)` 主鍵，`updated_at` 新者勝。
- `exam_results`：`UNIQUE(user_id, client_id)` append-only。
- `sessions`：只存 token 的 SHA-256，30 天到期，`last_used_at` 每 5 分鐘最多更新一次。
- `users.password_hash`：`$pbkdf2-sha256$i=<n>$<salt>$<hash>`（PHC，base64url）。登入時若 `<n>` 低於目前設定會透明重雜湊。

## API 契約

| 方法 | 路徑 | 說明 | 成功 | 失敗 |
|---|---|---|---|---|
| POST | /auth/register | `{username, password, inviteCode, displayName?}` | 201 `{token, expiresAt, user, bootstrap}` | 400 invalid_username／invalid_password／invite_invalid、409 username_taken |
| POST | /auth/login | `{username, password}` | 200 `{token, expiresAt, user}` | 401 auth_failed、423 locked `{retryAfterSeconds}`、429 rate_limited |
| POST | /auth/logout | Bearer | 200 | — |
| GET | /auth/me | Bearer | 200 `{user, session}` | 401 |
| POST | /sync/attempts | `{items[≤40]}` | 200 `{accepted, ignored, acceptedIds}` | 400 invalid_items `{errors:[{index, reason}]}`、401 |
| POST | /sync/bookmarks | `{items:[{questionId, starred, updatedAt}]}` | 同上 | 同上 |
| POST | /sync/exams | `{items:[exam result]}` | 同上 | 同上 |
| GET | /sync/snapshot?sinceAttemptId=n | Bearer | 200 `{attempts, bookmarks, exams, latestAttemptId}` | 401 |
| POST | /admin/invites | `{note?, expiresInDays?}` | 201 `{id, code, expiresAt}`（code 只出現一次） | 403 |
| GET | /admin/invites | | 200 `{invites:[{id, note, status, …}]}` | 403 |
| DELETE | /admin/invites/:id | | 200 | 404 |
| GET | /admin/users | | 200 `{users}` | 403 |
| POST | /admin/users/:id/disable | | 200（該使用者所有 session 失效） | 400 cannot_disable_self、404 |
| GET | /health | | 200 | |

所有錯誤格式：`{error: <code>, message, …}`。CORS 只對 `ALLOWED_ORIGINS` 內的 Origin 回 allow headers，`Access-Control-Max-Age: 7200`。

## 密碼雜湊與 CPU 預算

- workerd 對 PBKDF2 的硬上限是 100,000 次；程式預設 `PBKDF2_ITERATIONS = 100000`，可用環境變數 `PBKDF2_ITERATIONS`（≥1000）覆寫，PHC 字串記錄實際迭代數，調高後下次登入自動重雜湊。
- 量測（2026-10-10）：Node 22 WebCrypto 100k ≈ 22 ms、50k ≈ 11 ms、20k ≈ 4 ms、10k ≈ 2 ms（wall）；`wrangler dev` 本機 `/auth/login` 整個請求約 85 ms wall。
- Workers Free 每請求 CPU 10 ms。正式部署後以 `npx wrangler tail --format json` 觀察 `/auth/login` 的 `cpuTime`；若超過限制，於 `wrangler.jsonc` `vars.PBKDF2_ITERATIONS` 設為可通過的最大值（預估 20,000–50,000），並把數值記在下方；升級 Paid（cpu_ms 可到 30,000）後移除覆寫即回到 100,000。
- 補償措施：邀請制、`ratelimits` 每帳號 5 次／60 秒、D1 連續 5 次失敗鎖 15 分鐘、密碼 8–128 字元。

正式環境：Worker 網址 `https://rex-api.jieyu166.workers.dev`（2026-10-10 部署，D1 `rex-progress` 於 APAC）。登入 CPU 量測結果（2026-10-10，`wrangler tail --format json`，PBKDF2 100,000 次）：`/auth/register` cpuTime 28 ms、`/auth/login` 25–38 ms（三次成功登入與一次錯密碼皆 outcome ok、未被截斷）。雖高於 Free 方案標示的 10 ms，實測未觸發限制；若日後出現 Cloudflare 1102（CPU 超限）錯誤，先在 `wrangler.jsonc` 的 `vars` 設 `PBKDF2_ITERATIONS: "20000"`（約 6 ms）並重新部署，既有帳號下次登入會自動改用新迭代數。

## 本機開發

```bash
cd worker
npm install
npx wrangler d1 migrations apply rex-progress --local
npx wrangler dev --port 8787        # 或在 Claude Code 用 .claude/launch.json 的 rex-api
npm test                            # node --test test/*.test.js（30 tests，含 node:sqlite D1 stub）
BASE=http://127.0.0.1:8787 bash test/smoke.sh   # 需 worker/.dev.vars 的 BOOTSTRAP_INVITE_CODE
```

`worker/.dev.vars`（gitignored）放本機 secrets；`.wrangler/` 為本機 D1 狀態。

## 正式部署：使用者需手動做一次

1. 建立 D1：`cd worker && npx wrangler d1 create rex-progress`，把回傳的 `database_id` 填進 `wrangler.jsonc`。
2. 設定 bootstrap 邀請碼（只在 users 表為空時有效）：`npx wrangler secret put BOOTSTRAP_INVITE_CODE`（24 個 A–Z2–7 字元）。
3. 建立 Cloudflare API token（權限 Workers Scripts:Edit、D1:Edit、Account Settings:Read），存到 GitHub repo secrets `CLOUDFLARE_API_TOKEN` 與 `CLOUDFLARE_ACCOUNT_ID`。
4. 推 main：`.github/workflows/deploy-worker.yml` 會 `wrangler d1 migrations apply rex-progress --remote` 再 `wrangler deploy`。
5. 把正式 Worker 網址填進 `index.html` 的 `window.REX_API_BASE`，推 main 部署 Pages。
6. 用 bootstrap 碼註冊第一個帳號（username 須在 `ADMIN_USERNAMES` 內才是 admin），之後在設定面板簽發邀請碼給同事。

## 前端行為

- 未登入：一切如常，作答寫本機；設定面板顯示登入／註冊表單。
- 登入後：首次把本機 v2 進度轉成的 legacy attempts 上傳（`sync.migratedLegacy`），再 `pullSnapshot` 合併；之後每次作答即時入 outbox，啟動／上線／回前景／pagehide 自動補送；設定面板顯示待同步筆數與上次同步時間。
- 401：清除本機 session、保留 outbox、提示重新登入。
- 題卡 `answerStatus: corrected`：frontmatter `officialAnswer` 記錄有誤的官方答案，`correctAnswer` 為覆核答案；揭曉後顯示「官方公布 X 有誤，依覆核答案 Y 計分」。

## 學習排程（study-scheduler，2026-10-10）

- 前端 `js/scheduler/`（全部純函式，掛在 `window.RexScheduler`）：`fsrs-adapter`（ts-fsrs UMD 包裝；retention 0.9、max 36500、fuzz off、short-term on、learning 1m/10m、relearning 10m）、`due-window`（UTC+8、日界 4 點）、`queue-mix`（learning 優先、每 4 張 1 新、每日新卡上限）、`wrong-criterion`、`calibration`、`test-builder`、`exam-resume`、`weakness`、`drill`。`js/review-view.js`、`js/analytics-view.js`、`js/exam-session.js` 為 view／session 層。
- `rex_progress` v3 新增：`cards{questionId → cardRow}`、`reviewLogs[]`（≤5000）、`settings{newPerDay, dayStartHour, examSecondsPerQuestion, updatedAt}`、`activeExam`、outbox 佇列 `cards`／`reviewLogs`／`settings`、`sync.latestReviewLogId`；attempts `source` 新增 `review`。
- 同步順序：attempts → cards → reviewLogs → bookmarks → exams → settings。

| 方法 | 路徑 | 語意 |
|---|---|---|
| POST | /sync/cards | `{items:[cardRow]}`，`updated_at` 新者勝 |
| POST | /sync/review-logs | `{items:[log]}`，`UNIQUE(user_id, client_id)` + `INSERT OR IGNORE` |
| POST | /sync/settings | `{items:[settings]}`，`updated_at` 新者勝 |
| GET | /sync/snapshot?sinceAttemptId&sinceReviewLogId | 回傳另含 `cards`、`reviewLogs`（id > since）、`settings`、`latestReviewLogId` |

D1 migration `0003_fsrs.sql`：新增 `fsrs_cards`、`fsrs_review_logs`、`user_settings`，並重建 `attempts` 讓 `source` CHECK 含 `review`（既有列與 id 保留）。
