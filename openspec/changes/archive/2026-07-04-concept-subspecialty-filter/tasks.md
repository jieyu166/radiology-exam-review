## 1. 概念列表次專科篩選（js/concept-cards.js）

- [x] 1.1 在 `renderAll()` 中，載入 `DataLoader.loadConceptsIndex()` 後，對所有概念的 `subspecialty` 去重並依規則排序，產生藥丸清單資料：先按考題既定順序（ABD/CV/CH/NR/MSK/H&N/PED/IR/Physics/Breast/US），其餘概念特有值接於後，空值歸為「未分類」置於最後；每項附該科概念數。對應需求：Subspecialty filter on the concept list；Filter control ordering。行為：藥丸來源純由已載入索引去重、不發額外請求，排序與空值分組符合上表。驗證：preview MCP 開 `#/concepts`，讀 DOM 確認「全部」＋各次專科藥丸、順序（canonical 在前、GU/GI 等在後、未分類最後）、每顆計數正確，且 network 無新增請求。
- [x] 1.2 以模組變數 `_conceptSubFilter`（預設 `''`＝全部）記住選取；渲染 `.pills-row` > `.pill`（沿用既有 CSS）於標題下方，點藥丸 → 設 `_conceptSubFilter` → 只重繪 `.concept-grid` 與藥丸 active 狀態（不重新 fetch）；grid 依 `_conceptSubFilter` 過濾（`''` 全部、`未分類` 顯示 subspecialty 為空者、否則相符者）。「全部」還原。`relCount` 與「待建立概念」區塊不受影響。對應需求：Selecting a subspecialty filters the grid。行為：點某科只剩該科概念、該藥丸 active、無網路請求；點「全部」還原全部。驗證：preview 點「Breast」→ grid 只剩 Breast 概念且藥丸 active；點某概念特有值（如 GU）亦可篩到；點「全部」還原；全程 network 無新增請求。

## 2. 驗證

- [x] 2.1 以 preview MCP 端到端驗證篩選並回歸概念頁其他功能（概念卡片點入、待建立概念連結、上一輪 concept→card `qid` 連結）。行為：篩選正確且既有概念頁行為不變。驗證：因靜態 JS 快取頑強，先 `fetch('js/concept-cards.js',{cache:'reload'})` 再 `location.reload()` 確保跑新碼，逐項確認並截圖佐證。
