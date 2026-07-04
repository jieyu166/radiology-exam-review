## Why

網站的概念頁只讀取 data/concepts.json，該檔目前僅含 3 筆概念、且自 2026-04-19 未再更新。與此同時，作者層 vault/concepts/ 已累積 977 個 Note v5 markdown 概念檔（合計約 4.56 MB），涵蓋近期的弱來源補強、淺層深補與 46 個新建卡。兩層之間沒有任何自動同步步驟，導致「題目有上站、概念幾乎都沒上站」。

直接把 977 個概念灌進單一 concepts.json 會產生約 5–6 MB 的單檔，使用者每次進入概念頁都需整包下載，行動裝置體驗差。需重整概念資料架構為「輕量索引 + 單概念懶載入」，讓初始載入維持極小、概念數量可持續成長。

## What Changes

- 新增建置腳本，將 vault/concepts/ 的 977 個 markdown 概念檔解析並對映為網站 schema，產出：
  - data/concepts-index.json：全部概念的輕量索引（slug/name/nameZh/subspecialty），供清單頁一次載入（約 70 KB）。
  - data/concepts/ 目錄下每個概念一個 JSON 檔（完整內容：定義/影像判讀重點/DDx/參考來源/臨床重點/keyPoints/management），供點開時才個別抓取。
- 前端資料載入層改為：清單頁載入索引；點開某概念時才懶載入該概念的 JSON 並快取，保留既有 localStorage 使用者編輯合併行為。
- 概念卡渲染層改為：清單以索引渲染；詳情以懶載入的完整內容渲染，顯示到「判讀重點 + DDx + 參考來源 + 臨床」的完整深度。
- 保留現有 data/concepts.json 作為向後相容 fallback，不移除、不改動題目載入路徑（data/*.json 年份檔）。

## Non-Goals (optional)

- 不改動題目資料模型與題目載入路徑（data/index.json 與年份 JSON 維持原樣）。
- 不引入 node/打包工具或前端框架；維持現有純靜態 + fetch 的 vanilla JS 架構。
- 不在此變更內重寫概念清單頁的 UI 版型或搜尋/篩選功能（僅接上新資料來源；UI 大改另議）。
- 不建立 vault→site 的自動 CI 產生流程（本次為可重跑的本機腳本；CI 自動化另議）。
- 不修改 vault/concepts/ 內的 markdown 內容（本變更只讀取、不改寫作者層）。

## Capabilities

### New Capabilities

- `concept-web-build`: 由 vault/concepts/ markdown 產生網站用的概念索引與單概念 JSON 檔（可重複執行的建置腳本與輸出契約）。
- `concept-lazy-loading`: 前端以索引渲染概念清單、於開啟概念時懶載入單一概念 JSON 並快取渲染的載入行為。

### Modified Capabilities

(none)

## Impact

- Affected specs: concept-web-build, concept-lazy-loading
- Affected code:
  - New:
    - scripts/build_concepts.py
    - data/concepts-index.json
    - data/concepts/ (每概念一個 JSON，共約 977 檔)
  - Modified:
    - js/data-loader.js
    - js/concept-cards.js
  - Removed:
    - (none — data/concepts.json 保留為 fallback)
