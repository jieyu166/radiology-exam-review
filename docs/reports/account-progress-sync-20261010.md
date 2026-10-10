# account-progress-sync 完成報告

- 日期：2026-10-10
- Change：`account-progress-sync`（16 任務）
- 結論：**邀請制帳號、Cloudflare Worker + D1 後端、append-only 作答事件流與離線同步已上線並通過兩裝置驗證。**

## 上線環境

| 項目 | 值 |
|---|---|
| Worker | `https://rex-api.jieyu166.workers.dev`（Free 方案） |
| D1 | `rex-progress`（APAC），migrations 0001_accounts、0002_attempts 已套用 |
| 前端 | GitHub Pages，`js/config.js` 指向上述 Worker；本機 localhost 自動改指 `127.0.0.1:8787` |
| 第一位管理者 | `jieyu166`（以 `BOOTSTRAP_INVITE_CODE` 註冊，role=admin） |
| 測試帳號 | `rex-test`（member，由直接植入 D1 的測試邀請碼建立，供端對端驗證；可由管理者 API 停用） |
| CI | `deploy-worker.yml`：跑 30 個單元測試；`CLOUDFLARE_API_TOKEN`／`CLOUDFLARE_ACCOUNT_ID` 未設時跳過部署（本次由本機 `wrangler deploy` 部署） |

## 驗證

| 檢查 | 結果 |
|---|---|
| Worker 單元測試（node --test，node:sqlite D1 stub） | 30/30 |
| `worker/test/smoke.sh` 對 `wrangler dev` | 17 項全 PASS（註冊→登入→上傳 3→重送 ignored 3→400 invalid→snapshot→登出→401） |
| 前端測試 7 套＋ Python 4 套 | 全過 |
| `accept_vault_native_migration.py` | passed: true |
| 本機瀏覽器 | 註冊→作答（信心 2、耗時）即時同步→清空後重登取回→Worker 關閉時「待同步 1 筆」→上線後歸零 |
| 正式環境兩裝置 | 裝置 A（curl，rex-test）上傳 2 筆 → 裝置 B（瀏覽器 github.io）登入後 `answers` 含 2020-100（錯）與 2019-521（對），畫面顯示「同步完成：合併 2 筆」 |
| 正式環境登入 CPU（`wrangler tail`） | register 28 ms、login 25–38 ms（PBKDF2 100,000 次），全部 outcome ok |

## 關鍵決策落地

- Bearer token（不用跨站 cookie）；token 只存 SHA-256，30 天到期。
- PBKDF2-HMAC-SHA256 PHC 字串，迭代數可由 `vars.PBKDF2_ITERATIONS` 調整並透明重雜湊。實測 Free 方案未觸發 CPU 限制；若出現 1102 再降到 20,000。
- 登入節流：`ratelimits` binding 5 次／60 秒 ＋ D1 連續 5 次失敗鎖 15 分鐘。
- 作答事件 `UNIQUE(user_id, client_id)` ＋ `INSERT OR IGNORE`，前端 outbox 循序批次補送，首敗即停。
- v2 進度首次登入自動轉成確定性 legacy 事件上傳；重複登入不重送。
- 題卡 `answerStatus: corrected` ＋ `officialAnswer`：依覆核答案計分並揭露官方答案有誤。

## 留待後續

1. GitHub Actions 自動部署 Worker 需使用者建立 API token 並存入 repo secrets（步驟見 `docs/account-sync.md`）；之前改 `worker/` 需本機 `npx wrangler deploy`。
2. 管理者 UI 目前只有「簽發邀請碼」；停用使用者、列邀請碼仍走 API（`docs/account-sync.md`）。
3. `rex-test` 測試帳號保留供日後驗證，可用 `POST /admin/users/2/disable` 停用。
4. 下一個 change `study-scheduler`（FSRS、錯題判準、校準、組卷、弱點）已 park，待本 change archive 後 apply。
