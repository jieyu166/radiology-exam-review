## Context

網站為純靜態 SPA（無 package.json、無打包工具），以 fetch 載入 JSON。題目路徑健全：data/index.json 指向 data/<year>.json，前端 DataLoader.loadYear 逐年載入。概念路徑則斷裂：DataLoader.loadConcepts 只 fetch 單一 data/concepts.json（現況僅 3 筆、2026-04-19 後未更新），而作者層 vault/concepts/ 已有 977 個 Note v5 markdown（合計 4.56 MB、平均 4.8 KB、最大 16 KB）。兩層無同步步驟。題目共引用 965 個不同概念 slug，故清單本質由題目驅動、幾乎每個概念都有對應題目。

約束：維持 vanilla JS + 靜態 fetch；GitHub Pages 服務；Windows 端 Python 需以 UTF-8 明確讀寫（cp950 預設會對 ≈ 等字元報錯）；Obsidian 會把 frontmatter 的 inline `concepts: [x]` 改寫成多行 YAML list，解析器須同時接受兩種寫法。

## Goals / Non-Goals

**Goals:**

- 讓全部 977 個 vault 概念以「完整深度（判讀重點 + DDx + 參考來源 + 臨床）」呈現於網站。
- 概念頁初始載入維持極小（索引 ~70 KB），不隨概念數成長而變慢。
- 提供可重複執行的建置腳本，日後改 vault 只需重跑一次即同步。
- 沿用現有概念欄位渲染，前端改動集中在「資料來源與載入時機」，降低風險。

**Non-Goals:**

- 不改題目資料模型與載入路徑（data/index.json 與年份 JSON 不動）。
- 不引入 node/打包工具或框架。
- 不重寫概念清單 UI 版型、搜尋/篩選（僅接上新資料源）。
- 不建 CI 自動產生流程（本次為本機腳本）。
- 不改寫 vault/concepts/ 內容（只讀）。

## Decisions

**D1：索引 + 單概念檔（採用），而非單一大檔或按次專科分片。** 單一 concepts.json 全量約 5–6 MB，行動端每次進頁整包下載，不可接受。按次專科分片雖較小仍需整片載入且切分僵硬。索引 + 單概念懶載入使初始只需 ~70 KB、開啟才抓 5–20 KB 單檔、快取後零重抓，且概念數可無限成長；純靜態檔最契合 GitHub Pages。代價是 git 內新增約 977 個小檔（可接受）。

**D2：沿用既有 concepts.json 的欄位 schema（採用）。** 每個單概念檔沿用現有欄位（name/nameZh/subspecialty/definition/imagingFindings/differentialDiagnosis/externalLinks/keyPoints/management/checked）並加上 slug。如此 concept-cards.js 既有的欄位渲染可重用，前端只改「載入路徑」而非「渲染」。臨床重點（5句）對映至既有的 management 欄位（渲染器已會顯示），不新增欄位以免擴大前端改動面。

**D3：Note v5 章節 → schema 對映（section-based 解析）。** 以標題切段對映：導讀粗體 + Summary → definition；`## 放射科醫師影像判讀重點` → imagingFindings；Summary 各 bullet → keyPoints；DDx/鑑別段落 → differentialDiagnosis[]；`## 臨床重點` → management；`### 參考來源` 內的 DOI markdown 連結 → externalLinks[{label,url}]。缺段一律給空字串/空陣列，不省略欄位、不讓腳本中斷。

**D4：frontmatter 解析同時接受 inline 與 YAML list 兩種 concepts 寫法**（因 Obsidian 會改寫），slug 以檔名為準並與 frontmatter 核對。

**D5：保留 data/concepts.json 作 fallback**，不移除；單概念檔 404 時前端退回舊檔對應項或以索引最小資訊呈現，不崩潰。

## Implementation Contract

**行為（使用者可觀察）：** 進入概念頁 → 立即看到全部約 977 筆清單（來自索引，一次 fetch）；點開任一概念 → 該概念的完整內容（定義、影像判讀重點、DDx、參考來源連結、臨床）出現，並僅在此時 fetch 該單一概念檔；同一 session 再開同概念不重抓。

**資料形狀（契約）：**

- data/concepts-index.json：
  ```json
  { "concepts": [ { "slug": "adrenal-adenoma", "name": "Adrenal Adenoma", "nameZh": "腎上腺腺瘤", "subspecialty": "ABD" } ] }
  ```
- data/concepts/<slug>.json：
  ```json
  { "slug":"...", "name":"...", "nameZh":"...", "subspecialty":"...",
    "definition":"...", "imagingFindings":"...",
    "differentialDiagnosis":[], "externalLinks":[{"label":"...","url":"..."}],
    "keyPoints":[], "management":"...", "checked":false }
  ```

**介面（前端 DataLoader）：** 新增 loadConceptsIndex() 回傳索引物件；新增 loadConcept(slug) 以 fetch data/concepts/<slug>.json、合併 localStorage rex_edits_concepts[slug]、記憶體快取後回傳。concept-cards 清單改呼叫 loadConceptsIndex，詳情改呼叫 loadConcept(slug)。

**建置腳本（scripts/build_concepts.py）：** 掃 vault/concepts/*.md（排除底線開頭）→ UTF-8 讀取 → 解析 frontmatter（接受 inline 與 list 兩式）與章節 → 依 D3 對映 → UTF-8 寫出 data/concepts-index.json 與 data/concepts/<slug>.json。相同輸入重跑產生相同輸出。

**失敗模式：** 概念檔缺某段 → 對應欄位空、腳本繼續（僅 warn）；無法解析 slug 的檔 → 跳過並 warn；前端單概念檔 404 → console.warn + 退回舊 concepts.json 對應項或索引最小呈現，不丟例外。

**驗收準則：** ①本機 preview server 開概念頁見約 977 筆清單；②點開概念時 Network 面板顯示對該 slug 檔的單次請求並正確渲染影像判讀/DDx/來源/臨床；③重開同概念無新請求；④重跑腳本對相同 vault 產生位元相同輸出；⑤data/concepts/ 檔數等於 vault 非底線概念檔數、索引筆數相同；⑥既有題目頁不受影響。

**範圍邊界：** 範圍內＝建置腳本、索引與單概念輸出、data-loader 與 concept-cards 的載入路徑改動、保留 fallback。範圍外＝概念頁 UI 改版、搜尋/篩選、CI 自動化、題目路徑、vault 內容改寫。

## Risks / Trade-offs

- **git 檔數增加（約 977 個小檔）**：倉庫檔案數上升、Pages 部署 artifact 略增（總量仍僅數 MB）；換取初始載入極小與可擴充性，取捨可接受。
- **markdown→schema 對映為啟發式**：章節命名不一致可能使某欄位偏空；以 section-based 解析 + 缺段給空值緩解，並在腳本輸出統計（幾檔缺影像判讀/缺來源）供覆核。
- **Windows 編碼**：Python 一律以 encoding="utf-8" 讀寫，避免 cp950 例外。
- **內容重複真相來源**：vault 為真相源、data/concepts 為衍生產物；須靠重跑腳本保持同步（本次不做 CI，屬已知取捨）。
