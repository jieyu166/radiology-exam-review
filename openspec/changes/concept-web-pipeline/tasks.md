## 1. 建置腳本 scripts/build_concepts.py

- [x] 1.1 實作 frontmatter 解析：以 UTF-8 讀取 vault/concepts/*.md（排除底線開頭檔），同時接受 inline concepts 陣列與多行 YAML list 兩種寫法，取出 slug/name/subspecialty 與中文別名，slug 以檔名為準並與 frontmatter 核對。驗證：對 3 個代表檔（含一個被 Obsidian 改成 YAML list 的檔）印出正確 slug 與欄位。
- [x] 1.2 實作 Note v5 章節對映：導讀粗體+Summary→definition、放射科醫師影像判讀重點→imagingFindings、Summary 各 bullet→keyPoints、DDx/鑑別→differentialDiagnosis[]、臨床重點→management、參考來源內 DOI markdown 連結→externalLinks[{label,url}]；缺段給空字串/空陣列且不中斷。驗證：對一個完整檔與一個無臨床段的檔各產出物件，前者各欄非空、後者 management 空且不報錯。（對應需求 Requirement: Markdown sections map to the site concept schema）
- [x] 1.3 實作輸出契約：寫出 data/concepts-index.json（{concepts:[{slug,name,nameZh,subspecialty}]}）與每概念 data/concepts/<slug>.json（design D2 欄位），一律 UTF-8。驗證：json.load 兩類輸出皆成功，且索引筆數 == data/concepts 檔數 == vault 非底線概念檔數。（對應需求 Requirement: Concept build script generates index and per-concept files）
- [x] 1.4 使腳本可重複執行並輸出統計：印出總數、缺影像判讀數、缺參考來源數；相同 vault 重跑產生位元相同輸出。驗證：連續執行兩次後 git diff data/concepts-index.json data/concepts/ 為空。

## 2. 產生資料

- [x] 2.1 執行腳本產生全部概念的索引與單概念檔。驗證：data/concepts 檔數等於當前 vault 非底線概念檔數（約 977）、索引為 KB 級大小、抽查 3 個不同次專科概念檔內容正確對映。

## 3. 前端資料載入層 js/data-loader.js

- [x] 3.1 新增 loadConceptsIndex()：fetch data/concepts-index.json、記憶體快取、回傳概念索引。驗證：於瀏覽器主控台呼叫回傳陣列且長度等於索引筆數。
- [x] 3.2 新增 loadConcept(slug)：fetch data/concepts/<slug>.json、合併 localStorage rex_edits_concepts[slug]、記憶體快取後回傳；當單概念檔 404 時 console.warn 並退回 data/concepts.json 對應項或索引最小物件、不丟例外。驗證：對存在 slug 回傳含 imagingFindings 的完整物件；對不存在 slug 不崩潰且回退。

## 4. 前端渲染層 js/concept-cards.js

- [x] 4.1 概念清單改由 loadConceptsIndex 渲染，不再整包載入概念內容；沿用既有「題目引用但索引無」的空殼收集邏輯（改以索引為基準）。驗證：清單顯示約 977 筆，且初次進入概念頁時 Network 面板無任何 data/concepts/<slug>.json 請求。（對應需求 Requirement: Concept list renders from the lightweight index）
- [x] 4.2 概念詳情改為開啟時呼叫 loadConcept(slug) 後渲染完整深度（definition/imagingFindings/differentialDiagnosis/externalLinks/management），重開同概念不重抓。驗證：點開概念時 Network 出現單次該 slug 請求且四區塊皆有內容；同 session 重開同概念無新請求。（對應需求 Requirement: Concept detail is lazy-loaded and cached）

## 5. 本機驗證與上線

- [x] 5.1 以 preview server 啟動網站，實測概念清單載入、隨機點開 5 個不同次專科概念的完整渲染、懶載入與快取行為。驗證：Network 面板與畫面確認 design 驗收準則①②③（清單來自索引、詳情單次懶載入、重開無重抓）。
- [ ] 5.2 逐檔 git add（scripts/build_concepts.py、js/data-loader.js、js/concept-cards.js、data/concepts-index.json、data/concepts/）→ commit → push，待 GitHub Pages 部署後於正式站確認概念完整上站。驗證：正式站概念頁顯示判讀重點/DDx/來源/臨床、部署 run 綠燈。
