## Why

使用者在本站複習時產生的「作題記錄」（已讀、收藏、答錯、模擬考歷史）目前完全沒有被保存，離開頁面即消失。現有的「匯出 JSON」只匯出題目詳解編輯（供內容併回 repo），並非個人作題記錄。本站為純靜態 GitHub Pages、無後端，需要一個不依賴伺服器、可跨裝置手動搬移的個人記錄機制。

## What Changes

- 新增本機學習記錄資料層（localStorage key `rex_progress`），記錄四類：已讀（seen）、收藏（starred）、最近作答與對錯（answers）、模擬考歷史（examHistory）。
- 卡片模式：開啟卡片即標記已讀；新增「收藏」切換；卡片標頭顯示 已讀／收藏／答錯過 狀態。
- 篩選列（卡片與列表共用）：新增「只顯示收藏」「只顯示答錯過」兩個開關。
- 模擬考：結算時逐題記錄對錯，並寫入一筆考試歷史；模擬考設定頁顯示「近期成績」清單。
- 設定面板新增獨立的「學習記錄」區：匯出學習記錄、匯入學習記錄、清除學習記錄；匯出檔名 rex-progress-YYYY-MM-DD.json。
- 學習記錄與現有「題目編輯」匯出為兩條完全獨立的資料流、各自的檔案，互不混合；現有題目編輯匯出邏輯不變，僅將其按鈕標籤改為可與學習記錄區分的文字。

## Non-Goals

- 不改動題目編輯（rex_edits_*）的匯出邏輯與併回 repo 流程，僅調整其按鈕標籤文字。
- 不引入任何後端、帳號系統或雲端儲存（含 Cloudflare 圖床）；學習記錄一律存本機 localStorage。
- 不做跨裝置自動同步；換裝置以手動匯出／匯入完成。
- 不含概念分科篩選，亦不做概念次專科資料品質清理（別名合併、空值）——皆屬另案。

## Capabilities

### New Capabilities

- `study-progress`: 本機記錄並呈現使用者作題進度（已讀、收藏、答錯、模擬考歷史），並提供以進度為條件的篩選與卡片／模擬考的呈現。
- `progress-backup`: 學習記錄的獨立匯出、匯入與清除，與題目編輯匯出互不混合。

### Modified Capabilities

(none)

## Impact

- Affected specs: study-progress（新）、progress-backup（新）
- Affected code:
  - New: (none)
  - Modified:
    - js/data-loader.js
    - js/card-mode.js
    - js/question-store.js
    - js/app.js
    - js/exam-mode.js
    - js/editor.js
    - index.html
  - Removed: (none)
