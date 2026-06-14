---
name: exam-explanation-pipeline
description: "為交換考題逐批製作逐選項詳解、補放射來源 reference、補分類，並自評稽核。以官方詳解 PDF 為事實基礎、vault 筆記交叉補強，產出 rex-edits patch 供醫師覆核。在 Codex session 內依當時 token 剩餘量逐批執行，年份優先 2016→2024。Trigger：製作詳解、補 reference、補分類、跑詳解流水線、explanation pipeline。"
effort: high
license: MIT
metadata:
  author: jieyu166
---

# 交換考題詳解流水線

把「等人手動逐題確認」轉成「機器先審、人覆核」。移植 robust-lit-review 的品質工程骨架，
但查核閘改為放射科來源（期刊/radiopaedia/statdx/教科書/官方詳解），非 DOI/PRISMA。

## 核心原則（務必遵守）

1. **以官方詳解為事實基礎，不憑空生成**。每題優先採用 `tmp/official-{year}.json` 內對齊到的
   官方 `per_option`（逐選項對錯）與 `citations`（來源）。官方內容不足時才用 vault 筆記補強。
2. **絕不編造 reference**。reference 必須通過 `verify_reference.passes_gate()`。無法歸因到白名單
   來源時，標 `reference_source: llm_suggested` 並交人覆核，不可假造期刊名/年份。
3. **逐選項格式**。explanation 必須逐一解釋每個選項對/錯（見 Golden Example），非一行排除法。
4. **不直接改 data/*.json**。一律輸出 `data/rex-edits-pipeline-{year}-{date}.json` patch，
   由 `merge_edits.py` 合併、醫師在網頁覆核後才 `checked:true`。
5. **token 自適應、可續跑**。每題處理完即更新 `tmp/pipeline-progress.json`；接近 token 上限就
   停在乾淨邊界、寫好進度，下次 session 從斷點接續。

## 前置：跑便宜層腳本（每年份一次）

```bash
python scripts/extract_official_explanations.py {year}   # → tmp/official-{year}.json（官方詳解切題+對齊）
python scripts/audit_questions.py {year}                 # → tmp/audit-{year}.json（修補前基準）
```

## 兩階段（先重構、後生成）

官方詳解由不同人編寫、完成度不一，解析也可能有誤。故分兩階段，**預設只做 Phase A**：

- **Phase A — 重構（預設先做）**：處理 `tmp/audit-{year}.json` 中 `has_official: true` 的題
  （官方有逐選項詳解文字可重構）。事實基礎來自官方，幻覺風險低。
- **Phase B — 生成（最後才執行，需使用者明確指定）**：處理 `has_official: false`/`null` 的題
  （無官方詳解或官方完成度低）。改用 vault 筆記 + 放射知識**生成**詳解。
  - explanation 開頭加標記 `（AI 生成草稿，待覆核）`，`reference_source` 必為 `llm_suggested`，
    patch 加 `generated: true`。一律強制人覆核，且 Phase B 應在 Phase A 全數覆核後再啟動。

## Phase A 逐題流程（8 步）

對該年 `has_official: true` 且 `missing` 非空的題，依題號順序處理：

1. **取官方詳解**：從 `tmp/official-{year}.json` 找該 qid 的 match。
   - `matched:false` 或 `answer_agree:false` → **直接讀官方 PDF 該題**（Read 工具可視覺讀 PDF）核對，
     不要盲信錯配的區塊。
2. **重構 explanation**：把官方 `per_option` 整理成逐選項格式（繁體中文、台灣用語）。
   - 正解標 **正確**、錯誤選項標 **錯誤** 並說明為何錯（**bold** 用 `**…**`）。
   - 關鍵診斷/概念用 `[[concept-id]]` wikilink（對應 concepts.json；新概念可順手提出）。
3. **補 reference**：優先用官方 `citations`；不足時用 vault 筆記補。
   - 官方 PDF 轉錄的引用一律標 `reference_source: official_pdf` 直接採信（含跨專科期刊如
     Urol Clin North Am，不受白名單限制）。
   - 其他來源經 `verify_reference.best_source()` 標層級。**白名單已涵蓋多本放射期刊**
     （非只有 Radiology，見下），不屬白名單者標 `llm_suggested` 交人覆核，**絕不編造**。
   - **原文可得性檢查**：reference 指向期刊論文時，在 vault 論文庫
     `3. Resources/論文s/`（含子資料夾）用 Grep 找檔名/DOI 是否有原文 PDF。
     - 有 → 可在 reference 附 `[[檔名]]` wikilink。
     - 無 → patch 該題加 `needs_download: true`，並在 reference 保留完整書目資訊
       （期刊+年+卷頁/DOI），供使用者自行下載原文。不要因為沒有原文就略過或改寫該 reference。
4. **補分類**：`subspecialty == Unknown` 時依題幹判定（白名單見下）。低信心 → `reference_source` 仍走覆核。
5. **圖片**：官方 PDF 該題若含圖且 data 未連結 → 記在 patch 的 `_needs_image` 註記，本流水線不搬圖
   （圖片改由 import_obsidian_sr.py 處理），僅標記待補。
6. **自評稽核**：對產出的題跑 5 項清單（answer / 逐選項 / 分類 / reference / image），記 `audit_score`。
7. **寫入 patch**：累加到 `data/rex-edits-pipeline-{year}-{今日日期}.json`（格式見下），**不要**設 `checked:true`
   （覆核是人的職責）。
8. **更新進度**：寫 `tmp/pipeline-progress.json`：`{year, done:[qid...], remaining:[qid...], last_qid, ts}`。

## Patch 格式（沿用 rex-edits，相容 merge_edits.py）

```json
{
  "rex_edits_year_2016": {
    "2016-011": {
      "subspecialty": "CH",
      "explanation": "(A) **錯誤**：……\n(B) **正確**：……",
      "reference": "Eur Radiol 2009;19:1937. bronchiectasis. 見 [[Bronchiectasis]]",
      "reference_source": "journal",
      "needs_download": false,
      "generated": false,
      "audit_score": 4,
      "_needs_image": false,
      "_answer_check": "official=B json=B agree"
    }
  }
}
```

> 註：`reference_source` / `audit_score` / `_*` 為流水線附帶欄位，向後相容（舊前端忽略未知欄位）。
> `checked` 一律不在此設定。

## 放射來源辨識閘（白名單，與 verify_reference.py 同步）

- 期刊：`Radiology / RadioGraphics / AJR / AJNR / JVIR` + 年份
- 線上：`radiopaedia`、`statdx`
- 教科書：`Osborn's Brain` / `Core Radiology` / `The Requisites` / `Fundamentals of CT/MRI/Skeletal Radiology` / `BI-RADS 2013`
- 官方：`交換考 {year} 官方詳解`（保底）
- vault：`[[筆記名]]`（可回溯實體 PDF）

不屬上述 → `llm_suggested`，強制人覆核。寫完一批可用
`python scripts/audit_questions.py {year}` 重跑，量化 reference/逐選項覆蓋率提升。

## subspecialty 白名單

`ABD, CV, CH, Breast, H&N, MSK, NR, PED, US, IR, Physics, Unknown`

## 品質清單（自評 5 項，每項 0/1）

1. 有合法 correctAnswer 且與官方詳解一致
2. explanation 逐選項解釋
3. subspecialty 非 Unknown
4. reference 過來源辨識閘
5. 圖片題已連結（無法判定 → NA 不扣分）

## Golden Example（逐選項詳解，2016-002 Adrenal adenoma）

```
(A) **正確**：Adrenal adenoma 佔腎上腺 incidentaloma 約 75%，遠比 metastasis 常見。
(B) **錯誤**：腺瘤在非顯影 CT 上密度 **≤10 HU**（非 >20 HU）即可確診。
(C) **錯誤**：腺瘤在 opposed-phase MRI 上**訊號明顯下降**（含脂），這是其特徵。
(D) **錯誤**：腺瘤特性是 contrast **快速 washout**（>60% absolute / >40% relative），非滯留 90%。

reference: AJR 2008; adrenal adenoma washout. 見 [[Adrenal adenoma]]
```

## Phase B 逐題流程（生成，最後執行）

僅在使用者明確要求、且 Phase A 已覆核完成後啟動。對 `has_official: false`/`null` 的題：

1. **核對題目**：先讀官方 PDF 該題（若有殘缺官方內容）確認題幹/答案無誤。
2. **蒐證**：在 `2. Areas/{科}相關知識/` 用 Grep/omnisearch 找對應主題筆記，
   讀其內容與 `### 參考來源`。無對應筆記時才用一般放射知識。
3. **生成逐選項詳解**：格式同 Golden Example，但 explanation 開頭標
   `（AI 生成草稿，待覆核）`。寧可保守、標明不確定處，不得杜撰數據。
4. **reference**：能對到 vault 筆記/白名單期刊就標；否則 `reference_source: llm_suggested`，
   並依需要標 `needs_download: true`。
5. **patch**：加 `generated: true`、`reference_source: llm_suggested`，**絕不設 checked**。
6. **稽核 + 進度**：同 Phase A。

> Phase B 是「沒有官方詳解時的補救」，品質本質低於 Phase A，務必讓使用者知道哪些題是生成的
> （`generated: true` 可在網頁 editor 篩選優先覆核）。

## 人覆核迴圈（流水線外，醫師執行）

```bash
python scripts/merge_edits.py data/rex-edits-pipeline-{year}-{date}.json   # 併入 data/{year}.json
git diff data/{year}.json                                                 # 確認只動目標欄位
python -m http.server 8080                                                # 開網頁 editor 覆核、設 checked、匯出
git add data/ && git commit -m "pipeline: {year} 詳解+reference 草稿" && git push
```
