# study-scheduler 完成報告

- 日期：2026-10-10
- Change：`study-scheduler`（13 任務）
- 結論：**FSRS 今日複習、最近答錯判準、信心校準與弱點分群、組卷條件與續考已上線；兩裝置排程狀態一致。**

## 上線內容

| 功能 | 位置 | 要點 |
|---|---|---|
| 今日複習 | `#/review`（導覽列／底部導覽） | ts-fsrs 5.4.2（jsDelivr UMD，SRI）前端計算；日界 UTC+8 04:00；learning 優先、每 3 張到期插 1 新、新卡每日上限（預設 20，可調）；四鍵評分含間隔預覽；鍵 1–4、空白鍵揭曉；答錯預設 again；今日完成顯示明日到期 |
| 錯題判準 | 篩選、組卷、弱點分群 | 統一為「最近一次答錯」 |
| 統計與弱點 | `#/stats`（設定面板） | 信心三等級校準表、「有把握卻答錯」最近 20 題、次專科／概念分群（≥2 題、最多 12 群）、「練這一群」跨年交錯（當日固定順序） |
| 概念練習 | 概念頁 | 「練這個概念的題（跨年交錯）」進入卡片模式臨時佇列 |
| 模擬考 | `#/exam` | 狀態 OR × 年份／次專科／概念 AND、即時題數、1–100 題、tutor、計時（逾時記未作答）、`activeExam` 持久化與續考、結果頁 seed 與答錯清單 |
| 同步 | rex-api | `/sync/cards`（LWW）、`/sync/review-logs`（冪等）、`/sync/settings`（LWW）、snapshot 含 cards／reviewLogs／settings；D1 migration 0003 已套用（既有 7 筆 attempts 保留） |

## 驗證

| 檢查 | 結果 |
|---|---|
| `test_scheduler.js`（due-window、queue-mix、wrong-criterion、calibration、weakness、drill；含 spec 例） | 通過 |
| `test_review_view.js`（FSRS 介接、佇列、評分、間隔標籤、統計 view model） | 通過 |
| `test_exam_builder.js`（條件正規化、題池、seeded 抽樣、續考、逾時狀態機） | 通過 |
| `test_study_progress.js`、`test_sync_client.js`、`test_attempt_outbox.js` 擴充 | 通過 |
| Worker `node --test`（含 migration 0003 重建表保留列） | 35/35 |
| 既有前端／Python 測試與 `accept_vault_native_migration.py` | 全過 |
| 本機瀏覽器 | `#/review` 新題→評分→下一題、空白鍵揭曉、outbox 三種項目；`#/stats` 分群與「練這一群」；概念頁練習；設定輸入入 outbox；模擬考條件即時題數、逾時前進、tutor 揭曉、離開後續考第 5 題 |
| 正式環境兩裝置 | 裝置 A（curl，rex-test）上傳 5 張到期卡＋5 筆評分；裝置 B（github.io）登入後「到期 5」，評分一題後「到期 4」、review attempt 即時同步、待同步 0 |
| CI | `deploy-pages.yml`、`deploy-worker.yml` 皆 success（commit 0790a2f0） |

## 留待後續

1. FSRS 參數個人化（optimizer）未做；沿用預設權重。
2. `#/stats` 弱點分群目前以本機 attempts 計算；多裝置下以 snapshot 合併後為準。
3. ts-fsrs 以 CDN 載入；若要離線使用需把 UMD 檔複製進 `js/vendor/`（MIT 允許）。
4. `rex-test` 測試帳號的 5 張種子卡仍在伺服器，可由管理者停用該帳號清理。
