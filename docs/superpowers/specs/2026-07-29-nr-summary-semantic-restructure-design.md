# NR Concept Summary 分批語意重組設計

## 背景

本專案以 `vault/concepts/*.md` 為概念內容的主要來源，再由
`scripts/build_concepts.py` 產生網站使用的 `data/concepts-index.json` 與
`data/concepts/*.json`。目前 NR（Neuroradiology）共有 216 篇 concept：

- 212 篇使用精確的 `## Summary` 標題。
- 4 篇使用變體 Summary 標題或其他等價結構。
- 216 篇皆至少有一筆 footnote reference 定義。

現有 Summary 多為完整敘述或長清單，資訊正確但考前掃讀效率不一。本變更將參考使用者
提供的考前重點圖片，以「粗體標籤＋短 bullets」模擬方塊與鑑別矩陣，同時維持
Obsidian、網站 JSON 與來源稽核能力。

## 目標

1. 將 NR concepts 的 Summary 改為可快速掃讀的高密度考前層。
2. 依 concept 類型選用疾病介紹、pattern／鑜別、解剖／分級等不同語意模板。
3. 保留原 Summary 的全部事實單元，不因壓縮而遺漏條件、例外或否定語意。
4. 每個改寫後的事實均可追溯至同一篇筆記既有來源，或本次實際查證並新增的來源。
5. 維持 `scripts/build_concepts.py` 既有輸出契約與網站顯示能力。

## 非目標

- 不重寫 concept 正文、題目、frontmatter、圖片或 Dataview 區塊。
- 不把所有 NR concepts 強制套用同一種疾病模板。
- 不為了補齊固定欄位而推測年齡、症狀、影像、治療或預後。
- 不對全部 216 篇逐篇執行完整五來源查證。
- 不代替使用者登入付費或機構授權平台，也不下載受限 PDF。
- 不在本變更中修改前端 Markdown renderer 或 concept JSON schema。

## 內容分類

每篇 NR concept 在改寫前先歸入一個主要類型。分類只決定 Summary 的資訊排序，不改變
frontmatter 或網站分類。

### 疾病／實體型

適用於以疾病、腫瘤、感染、發炎、先天異常或血管病變為主體的 concept。

可用標籤依原文實際內容選取：

- `**族群／年齡**`
- `**症狀**`
- `**病理／機轉**`
- `**檢查**`
- `**影像**`
- `**治療／追蹤**`
- `**陷阱**`

標籤不是必填欄位。若原筆記沒有可引用的年齡或症狀資料，就省略該 bullet。

### Pattern／鑑別型

適用於以影像 pattern、訊號變化、解剖分布或 differential diagnosis 為主體的 concept。

可用標籤：

- `**第一鑑別軸**`
- `**位置**`
- `**側別／對稱性**`
- `**序列／訊號**`
- `**分布**`
- `**Pattern → diagnosis**`
- `**陷阱**`

### 解剖／量測／分級／處置型

適用於解剖路徑、量測方法、評分系統、分期、處置與技術型 concept。

依原內容選用：

- `**結構／範圍**`
- `**量測**`
- `**門檻**`
- `**分級**`
- `**臨床意義**`
- `**操作順序**`
- `**陷阱**`

## Summary 改寫契約

### 輸入

每篇筆記的：

- 原 Summary（包含 `## Summary` 與語意等價的 Summary 變體）。
- 同篇正文中已有 footnote 支持的必要資訊。
- 同篇 `### 參考來源` 的 footnote definitions。

### 輸出

- 保留原 Summary heading；標題變體可正規化為 `## Summary`，但不得造成章節遺失。
- 原則上產生 4–8 個一階 bullets；內容確有需要時可超出，但不得為追求固定數量刪除事實。
- 每個 bullet 以粗體標籤開始，後接一至兩個短句。
- 同一鑑別軸的多個疾病可以放在同一 bullet，以分號分隔。
- 每個 bullet 末尾或相應事實後保留有效 footnote reference。
- 不將 Obsidian callout、Markdown 表格或 HTML 放進 Summary，以確保網站 renderer 可讀。

### 允許的轉換

- 調整事實順序。
- 合併重複敘述。
- 將長句拆成短句。
- 將列舉改為 `Pattern → diagnosis` 或 `條件：結果`。
- 展開會造成歧義的縮寫一次，之後沿用縮寫。
- 從同篇正文移入已有明確 footnote 的必要鑑別資訊。

### 禁止的轉換

- 新增沒有來源的疾病關聯、數值、門檻、時間範圍或因果關係。
- 把「可能／常見／典型／少見」改成確定敘述。
- 省略否定詞、例外、條件或版本資訊。
- 把相關性改寫為因果性。
- 用較新的指引內容直接覆蓋舊考題所依版本，而不保留雙層版本說明。
- 刪除原 Summary 中無法順利壓縮的事實；此類項目應保留較長 bullet 或標記人工覆核。

## 分批流程

### 第 0 批：規則校準

選取 8–12 篇代表性筆記，至少包含：

- 3 篇疾病／實體型。
- 3 篇 pattern／鑑別型。
- 2 篇解剖／分級／處置型。
- 1 篇 Summary heading 變體。
- 1 篇既有 Summary 超過 10 個 bullets 的長篇筆記。

第 0 批完成後檢查語氣、壓縮程度、來源追蹤與網站輸出；若規則需調整，先更新設計與
驗證器，再處理後續批次。

### 正式批次

- 每批 15–25 篇。
- 優先按語意類型分批，而非單純依檔名排序，以便套用一致模板。
- 每批保留一份清單，記錄 `rewritten`、`unchanged`、`research-needed`、
  `manual-review` 與 `build-failed` 狀態。
- 任何來源待查項目不阻塞同批其他可安全改寫的筆記。

## 額外文獻查證

只有以下情況啟用 `radiology-topic-research`：

1. Summary 的事實找不到對應 footnote definition。
2. Summary、正文或不同來源互相矛盾。
3. 涉及可能更新的診斷準則、分期、治療門檻或處置建議。
4. 現有依據僅為考題詳解或其他弱來源，且壓縮時需要判斷限制條件。
5. 原文措辭過度簡略，無法在不推測的情況下重寫。

查證順序依技能規範，以 STATdx、Radiopaedia、ClinicalKey、RadioGraphics、AJR
及適用之最新版／題目當時版學會指引交叉核對。公開來源優先；需要受限平台時，請使用者
自行登入並將分頁停在可閱讀狀態。不得處理帳密、規避存取控制或下載受限 PDF。

新增事實必須同時新增 article／chapter 級 footnote。若文獻不一致，並列差異並採保守措辭；
查不到可靠來源就保持原文或標記 `manual-review`。

## 事實覆蓋驗證

每篇改寫前建立原 Summary 的「事實單元」清單。事實單元至少包含：

- 主體或疾病。
- 影像／臨床／病理關係。
- 方向與極性，例如高／低、增加／減少、有／無。
- 限定詞，例如典型、少見、可能、相對保留。
- 數值、門檻、時間與版本。
- 否定、例外及鑑別條件。
- 對應 footnote reference。

改寫後逐項對照：

- 每個原事實單元必須在新 Summary 中有對應。
- 新 Summary 不得出現無對應來源的新事實單元。
- 所有引用的 footnote 必須在同檔案中有定義。
- 被移入 Summary 的正文事實必須保留原 footnote。

無法自動確定的語意對應標記為 `manual-review`，不得自動視為通過。

## 技術驗證

每批至少執行：

1. YAML/frontmatter 與 Markdown 基本結構檢查。
2. Summary heading 唯一性及存在性檢查。
3. Summary bullets 格式檢查：粗體標籤、短句、無表格／callout。
4. footnote reference 與 definition 完整性檢查。
5. 原 Summary 事實覆蓋報告。
6. `scripts/build_concepts.py` 建置。
7. `scripts/lint_concepts.py`。
8. 確認產生的 `data/concepts-index.json` 與 NR concept JSON 可解析。
9. 抽樣檢視網站 JSON 中的 `keyPoints`，確保粗體與短 bullets 正確輸出。

建置產物只在該批 Markdown 通過內容驗證後才保留。若建置器會更新全部 concept JSON，
提交前必須隔離並核對非 NR 產物是否只有可重現的機械性差異。

## 錯誤與中止條件

- 找不到來源：保持原文並標記 `research-needed` 或 `manual-review`。
- 來源衝突：停止該篇自動改寫，完成交叉查證後再處理。
- 舊考題與新指引衝突：採題目當時版／最新版雙層寫法，各自引用。
- 事實覆蓋失敗：還原該篇 Summary 改寫，不影響同批其他筆記。
- footnote 或 build 失敗：該批不得標記完成。
- 偵測到使用者在處理期間修改同一檔案：停止覆寫該檔並人工合併。

## 驗收標準

- 216 篇 NR concept 均有明確批次狀態。
- 所有安全完成的 NR Summary 均符合其語意類型模板。
- 原 Summary 事實覆蓋無已知遺失；未能確定者均列入人工覆核，不偽裝為通過。
- 新增或改寫的事實全部有有效 footnote。
- 沒有新增無來源的數字、疾病關聯、診斷門檻或處置建議。
- Concept build 與 lint 通過。
- 網站生成 JSON 可解析，抽樣 `keyPoints` 與 vault Summary 一致。
- 非 NR concept 正文不因本變更被修改。
