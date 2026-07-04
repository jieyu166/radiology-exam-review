## Context

本站為純前端、靜態 GitHub Pages（無後端、無帳號）。目前唯一的使用者持久狀態是 localStorage 的 `rex_edits_*`（題目與概念的內容編輯，含 `checked`），由 `js/data-loader.js` 的 `_getLocalEdits` 系列函式管理，並經 `js/editor.js` 的匯出鈕與 CLI（merge_edits）併回 repo。使用者的「作題記錄」（已讀、收藏、答錯、模擬考成績）完全沒有被保存：模擬考結算只在記憶體，離開即失。

本設計新增一條與「題目編輯」平行、但完全獨立的「學習記錄」資料流，存於本機，可手動匯出／匯入以跨裝置搬移。

## Goals / Non-Goals

**Goals:**

- 以單一 localStorage key `rex_progress` 保存使用者作題記錄：已讀、收藏、最近作答對錯、模擬考歷史。
- 卡片、篩選列、模擬考三處呈現與運用這些記錄（收藏切換、狀態 badge、「只顯示收藏／答錯過」篩選、近期成績）。
- 提供學習記錄的獨立匯出／匯入／清除，檔案與題目編輯匯出互不混合。

**Non-Goals:**

- 不改題目編輯（rex_edits_*）匯出邏輯與併回 repo 流程，僅改其按鈕標籤文字。
- 不引入後端、帳號、雲端儲存；不做跨裝置自動同步。
- 不含概念分科篩選與概念次專科資料品質清理（另案）。

## Decisions

- **獨立 key `rex_progress`（單一 JSON 物件），不併入 `rex_edits_*`。** 理由：兩者語意與生命週期不同——編輯要 commit 回 repo，個人記錄永不回 repo。合併會讓使用者誤把個人記錄當成待提交編輯。替代方案（沿用 rex_edits 命名空間）被否決。
- **匯出／匯入各自獨立檔案。** 題目編輯維持 `rex-edits-*.json`（`exportAllEdits`，不改）；學習記錄用 `rex-progress-*.json`（`exportProgress`）。匯入學習記錄只還原 `rex_progress`，不觸碰 `rex_edits_*`。
- **進度以題目 id 為鍵**（如 `2017-008`），與 `rex_edits_year_*` 相同的穩定 id，跨年份合併題也一致。
- **答錯過（wrongOnly）依 `answers[id].correct === false` 判定**；收藏（starredOnly）依 `starred[id] === true`。篩選在 `QuestionStore.getQuestions` 內以新參數處理，與既有 year／sub／checked 篩選並存。
- **markSeen 在卡片 `_render()` 觸發**（開到即已讀），避免額外互動；收藏為顯式 toggle。
- **匯入採合併（merge）而非覆蓋**：seen／starred／answers 以物件合併，examHistory 陣列以「串接後去重（同 ts）」處理，避免覆蓋掉本機既有記錄。

## Implementation Contract

**資料形狀（`rex_progress`，localStorage）：**

```
{
  seen:    { "<qid>": <epoch_ms>, ... },
  starred: { "<qid>": true, ... },
  answers: { "<qid>": { last: "<choice>", correct: <bool>, ts: <epoch_ms> }, ... },
  examHistory: [ { ts, total, correct, wrong, skipped, pct, wrongIds: ["<qid>", ...] }, ... ]
}
```

**`js/data-loader.js` 新增並匯出的函式（介面）：**

- `getProgress()` → 回傳上述物件（缺漏欄位補預設空值）。
- `markSeen(id)`：寫入 `seen[id] = now`。
- `toggleStar(id)` → 回傳新的布林狀態；`isStarred(id)` → 布林。
- `recordAnswer(id, { chosen, correct })`：寫入 `answers[id]`。
- `addExamRecord(record)`：`examHistory` 前插一筆。
- `exportProgress()` → 回傳僅含 `rex_progress` 的物件（供下載）。
- `importProgress(obj)`：合併還原，回傳統計 `{ seen, starred, answers, examHistory }` 各新增數。
- `clearProgress()`：移除 `rex_progress`（不動 `rex_edits_*`）。
- 既有 `exportAllEdits()` 不變。

**`js/question-store.js`：** `getQuestions({ years, subspecialties, checkedOnly, starredOnly, wrongOnly })`；新增兩旗標讀 `getProgress()`，與既有篩選串接，維持 `_dedupeById`。

**UI 可觀察行為：**

- 卡片標頭出現 已讀／收藏／答錯過 狀態；動作列有「收藏」toggle，點擊即時反映並持久化。
- 篩選列（卡片與列表）有「只顯示收藏」「只顯示答錯過」開關；切換後清單即時縮放。
- 模擬考結算後，`examHistory` 多一筆、答錯題進 `answers`；模擬考設定頁顯示「近期成績」清單（日期／百分比／對錯數）。
- 設定面板：題目編輯區按鈕標籤可與學習記錄區分；學習記錄區有匯出／匯入／清除三鈕，匯出下載 `rex-progress-YYYY-MM-DD.json`。

**失敗模式：** localStorage 讀寫以 try/catch 包覆，解析失敗回傳空進度並 console.warn（比照 `_getLocalEdits`）；匯入非法 JSON 顯示錯誤 toast、不改動本機資料。

**驗收：** 依 tasks 的驗證段以 preview MCP 端到端確認（收藏／已讀／答錯／考試歷史／兩條匯出流獨立／回歸）。

**In scope：** `js/data-loader.js`、`js/card-mode.js`、`js/question-store.js`、`js/app.js`、`js/exam-mode.js`、`js/editor.js`、`index.html`。
**Out of scope：** 題目編輯匯出邏輯、概念分科篩選、概念資料品質清理、任何後端。

## Risks / Trade-offs

- [使用者清瀏覽器資料會遺失記錄] → 提供匯出／匯入手動備份；文件與 UI 標示記錄存本機。
- [localStorage 容量上限（~5MB）] → 進度為輕量鍵值與精簡歷史；examHistory 僅存必要欄位（不存整份題目）。
- [瀏覽器對靜態 JS 頑強快取，改版後使用者可能跑到舊碼] → 屬既有問題；本案不處理，但驗證時須以 `fetch(f,{cache:'reload'})` 後 reload 確認新碼。
- [已讀在「開到即標記」下可能過度標記] → 可接受；已讀僅為輔助提示，非評分依據。

## Migration Plan

- 無資料遷移：`rex_progress` 首次讀取不存在時回傳空預設，向後相容既有使用者（其 `rex_edits_*` 不受影響）。
- 匯出檔為新格式 `rex-progress-*.json`，與既有 `rex-edits-*.json` 不衝突；匯入只認 `rex_progress`。
