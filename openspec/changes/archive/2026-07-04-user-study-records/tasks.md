## 1. 學習記錄資料層（js/data-loader.js）

- [x] 1.1 新增 `rex_progress` 讀寫與細粒度 helper：`getProgress()`、`markSeen(id)`、`toggleStar(id)`、`isStarred(id)`、`recordAnswer(id,{chosen,correct})`、`addExamRecord(record)`，並全部加入 module `return`。對應需求：Local study-progress store。行為：呼叫後 localStorage `rex_progress` 反映對應變更，`getProgress()` 對缺漏欄位補 `seen/starred/answers/examHistory` 空預設，讀取失敗以 try/catch 回空進度並 console.warn。驗證：preview MCP 於 console 依序呼叫各函式，檢查 `getProgress()` 結果正確且 `location.reload()` 後持久。
- [x] 1.2 新增 `exportProgress()`、`importProgress(obj)`（合併：seen/starred/answers 依鍵合併、examHistory 串接後依 ts 去重，回傳新增統計）、`clearProgress()`；`exportAllEdits()` 維持不動。此為 backup 三動作（Export study progress independently／Import study progress by merge／Clear study progress only）的底層實作。行為：`exportProgress()` 僅回傳 `rex_progress`；`importProgress` 不觸碰 `rex_edits_*`；`clearProgress` 只移除 `rex_progress`。驗證：preview 呼叫後檢查 localStorage 兩命名空間（`rex_progress` 與 `rex_edits_*`）互不影響。

## 2. 進度篩選（js/question-store.js）

- [x] 2.1 `getQuestions` 新增 `starredOnly`、`wrongOnly` 參數，讀 `DataLoader.getProgress()`，與既有 year/subspecialties/checkedOnly 串接並保留 `_dedupeById`。對應需求：Filter questions by progress state。行為：`starredOnly` 回傳 starred 為 true 的題；`wrongOnly` 回傳 `answers[id].correct===false` 的題。驗證：preview 呼叫 `QuestionStore.getQuestions({starredOnly:true})` 與 `{wrongOnly:true}`，比對集合與 `getProgress()` 一致。

## 3. 卡片呈現與收藏（js/card-mode.js、index.html #card-view）

- [x] 3.1 `_render()` 觸發 `markSeen`；動作列（`標記已確認` 旁）新增「收藏」toggle（呼叫 `toggleStar` 即時更新按鈕狀態）。對應需求：Mark question as seen；Bookmark a question。行為：開到卡片即記已讀、點收藏即時切換且持久。驗證：preview 開卡片後 `getProgress().seen` 有值、點收藏後 `starred` 有值且按鈕反映、reload 後持久。
- [x] 3.2 卡片標頭顯示 已讀／收藏／答錯過 badge。對應需求：Surface progress in the interface（卡片 badge 部分）。行為：badge 反映 seen／starred／`answers[id].correct===false` 三種狀態。驗證：preview 對一題設為已讀+收藏+答錯後開卡片，確認三個指示同時顯示。

## 4. 篩選列 UI（index.html #filter-bar、js/app.js）

- [x] 4.1 篩選列新增「只顯示收藏」「只顯示答錯過」兩個 toggle，接到 `_renderCardView`／`_renderListView`（傳入 `starredOnly`／`wrongOnly`），並在 `_syncFilterControls` 同步狀態，套用到卡片與列表。對應需求：Filter questions by progress state（UI 套用部分）。行為：切換後卡片與列表的可見題集即時縮放且兩視圖一致。驗證：preview 收藏數題、切「只顯示收藏」→ 卡片與列表題數等於收藏數；答錯數題後切「只顯示答錯過」同理。

## 5. 模擬考記錄（js/exam-mode.js、index.html #exam-setup）

- [x] 5.1 `_showResult` 結算時對每題呼叫 `recordAnswer`，並 `addExamRecord` 寫入一筆歷史（total/correct/wrong/skipped/pct/wrongIds）。對應需求：Record answers and exam history。行為：考完後 `answers` 更新、`examHistory` 前插一筆。驗證：preview 跑一次模擬考作答後檢查 `getProgress().answers` 與 `examHistory` 各新增。
- [x] 5.2 exam setup（#exam-setup）新增「近期成績」清單，來源 `getProgress().examHistory`，顯示日期／百分比／對錯數、新到舊。對應需求：Surface progress in the interface（近期成績部分）。行為：有歷史時列出、無歷史時顯示空狀態。驗證：preview 考完一場後開模擬考設定頁，確認該筆成績出現在最上方。

## 6. 設定面板匯出匯入（index.html #settings-panel、js/editor.js）

- [x] 6.1 將現有題目編輯匯出鈕標籤改為可與學習記錄區分的文字（如「匯出題目編輯（詳解）」），底層仍呼叫 `exportAllEdits()`、邏輯不變。對應需求：Question-edit export stays separate。行為：按鈕文字可區分、匯出檔仍只含 `rex_edits_*`。驗證：preview 觸發後檢查下載內容只含 `rex_edits_*`、不含 `rex_progress`。
- [x] 6.2 設定面板新增獨立「學習記錄」區三鈕：匯出（`exportProgress()` → 下載 `rex-progress-YYYY-MM-DD.json`）、匯入（隱藏 `<input type="file" accept="application/json">` → `JSON.parse` → `DataLoader.importProgress()` → toast 統計 → 重繪目前視圖；非法 JSON 顯示錯誤 toast 且不改本機）、清除（`clearProgress()`）。對應需求：Export study progress independently；Import study progress by merge；Clear study progress only。行為：三鈕各自正確、與題目編輯匯出互不混合。驗證：preview 匯出檔只含 `rex_progress`；`clearProgress` 後匯入同檔還原且 `countPendingEdits()` 不變；匯入壞檔顯示錯誤且進度不變。

## 7. 端到端驗證與回歸

- [x] 7.1 以 preview MCP 跑完整驗證：收藏／已讀／答錯／模擬考歷史／兩條匯出流獨立，並回歸（一般卡片上一題/下一題、既有年份/次專科/已確認篩選、concept→card `qid` 連結）。行為：design 之驗收條件全數通過。驗證：因靜態 JS 快取頑強，先對改動檔逐一 `fetch(f,{cache:'reload'})` 再 `location.reload()` 確保跑新碼，逐項確認並截圖佐證。
