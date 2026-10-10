---
name: exam-explanation-pipeline
description: "為交換考題逐批製作逐選項詳解、補放射來源 reference、補分類，並自評稽核。以官方詳解 PDF 為事實基礎、vault 筆記交叉補強，直接改寫 vault 題卡（`??` 後詳解段與 frontmatter reference），checked 維持 false 交醫師在 Obsidian 覆核。在 agent session（Claude Code／Codex）內依當時 token 剩餘量逐批執行，年份優先 2016→2024。Trigger：製作詳解、補 reference、補分類、跑詳解流水線、explanation pipeline。"
effort: high
license: MIT
metadata:
  author: jieyu166
---

# 交換考題詳解流水線

把「等人手動逐題確認」轉成「機器先審、人覆核」。移植 robust-lit-review 的品質工程骨架，
但查核閘改為放射科來源（期刊/radiopaedia/statdx/教科書/官方詳解），非 DOI/PRISMA。

**唯一權威來源是 vault 題卡 `vault/questions/{year}/{id}.md`**：本流水線直接編輯題卡，
沒有任何中間 JSON、patch 或合併步驟。

## 題卡結構（讀寫前先認清楚）

```
---
id: 2016-001
year:
  - 2016
subspecialty: ABD
correctAnswer: D
concepts:
  - upj-obstruction
checked: false
genHash: 7fbdc8a81043
reference: "Radiopaedia: focal nodular hyperplasia（實際查證 2026-06-17）; AJR 2008;190:1163"
---
#交換 #2016交換 #ABD 題幹……
(A) ……
(B) ……
(C) ……
(D) ……
??
**Ans: D**
(A) **錯誤**：……          ← 詳解段（本流水線唯一改寫的 body 區域）
(B) **正確**：……
概念：[[upj-obstruction]]
<!--SR:!2026-07-21,20,250-->


## 概念
![[upj-obstruction]]
```

- frontmatter 必有：`id`、`year`、`subspecialty`、`correctAnswer`、`concepts`、`checked`；
  可選：`reference`（字串）、`answerStatus`、`answerMode`、`acceptedAnswers`、`reviewStatus`、`genHash`。
- body：`#交換 #YYYY交換 #Sub 題幹` → `(A)`～`(E)` 選項 → `??` → `**Ans: X**` → 詳解段 →
  `概念：[[…]]`／`<!--SR:…-->`／`## 概念` 尾段。
- **詳解段 = `**Ans: X**` 下一行起，到第一個 `概念：`、`<!--SR:` 或 `## 概念` 之前**。
  只改這個區間；`**Ans:**`、SR 註解、`## 概念` 嵌入、`genHash` 一律不動。

## 核心原則（務必遵守）

1. **以官方詳解為事實基礎，不憑空生成**。每題優先採用 `tmp/official-{year}.json` 內對齊到的
   官方 `per_option`（逐選項對錯）與 `citations`（來源）。官方內容不足時才用 vault 筆記補強。
2. **絕不編造 reference**。寫進 frontmatter `reference` 的字串必須通過
   `verify_reference.passes_gate()`。無法歸因到白名單來源時，**不寫進題卡**，改記在
   `tmp/pipeline-progress.json` 該題的 `pending_reference`（來源層級 `llm_suggested`）交人覆核，
   不可假造期刊名/年份。
3. **逐選項格式**。詳解段必須逐一解釋每個選項對/錯（見 Golden Example），非一行排除法。
4. **只改題卡、每題一個最小 diff**。每題只動：詳解段、frontmatter `reference`、
   必要時 `subspecialty`／`concepts`。不重排 frontmatter 鍵序、不改縮排與引號風格、不動其他行；
   `checked` 維持 `false`（覆核是人的職責，醫師在 Obsidian 題卡上覆核後才將 `checked` 改 `true`）。
5. **token 自適應、可續跑**。每題處理完即更新 `tmp/pipeline-progress.json`；接近 token 上限就
   停在乾淨邊界（整題寫完、進度寫好），下次 session 從斷點接續。

## 前置：跑便宜層腳本（每年份一次）

```bash
python scripts/extract_official_explanations.py {year}   # 讀 vault 題卡 → tmp/official-{year}.json（官方詳解切題+對齊）
python scripts/audit_questions.py {year}                 # 讀 vault 題卡 → tmp/audit-{year}.json（修補前基準）
```

兩支腳本皆直接讀 `vault/questions/{year}/*.md`；CLI 參數不變。

## 兩階段（先重構、後生成）

官方詳解由不同人編寫、完成度不一，解析也可能有誤。故分兩階段，**預設只做 Phase A**：

- **Phase A — 重構（預設先做）**：處理 `tmp/audit-{year}.json` 中 `has_official: true` 的題
  （官方有逐選項詳解文字可重構）。事實基礎來自官方，幻覺風險低。
- **Phase B — 生成（最後才執行，需使用者明確指定）**：處理 `has_official: false`/`null` 的題
  （無官方詳解或官方完成度低）。改用 vault 筆記 + 放射知識**生成**詳解。
  - 詳解段第一行加標記 `（AI 生成草稿，待覆核）`，進度檔該題 `generated: true`、
    `reference_source: llm_suggested`。一律強制人覆核，且 Phase B 應在 Phase A 全數覆核後再啟動。

## Phase A 逐題流程（8 步）

對該年 `has_official: true` 且 `missing` 非空的題，依題號順序處理：

1. **取官方詳解**：從 `tmp/official-{year}.json` 找該 qid 的 match。
   - `matched:false` 或 `answer_agree:false` → **直接讀官方 PDF 該題**（Read 工具可視覺讀 PDF）核對，
     不要盲信錯配的區塊。答案不一致時**不改 `correctAnswer`**，記進度檔 `_answer_check` 交人裁決。
2. **重構詳解段**：把官方 `per_option` 整理成逐選項格式（繁體中文、台灣用語），
   整段取代 `**Ans: X**` 之後、尾段之前的詳解段。
   - 正解標 **正確**、錯誤選項標 **錯誤** 並說明為何錯（**bold** 用 `**…**`）。
   - 關鍵診斷/概念用 `[[concept-id]]` wikilink（必須對應 `vault/concepts/{slug}.md` 既有檔；
     新概念先提給使用者，不自行建檔）。
3. **補 reference**：優先用官方 `citations`；不足時用 vault 筆記補。
   - 官方 PDF 轉錄的引用直接採信（含跨專科期刊如 Urol Clin North Am，不受白名單限制），
     但寫入時字串尾端加 `（交換考 {year} 官方詳解）`，使其以 `official_pdf` 層級通過閘門並保留出處。
   - 其他來源經 `verify_reference.best_source()` 標層級。**白名單已涵蓋多本放射期刊**
     （非只有 Radiology，見下），不屬白名單者不寫進題卡、記 `pending_reference` 交人覆核，**絕不編造**。
   - **寫入規則**：`reference` 是單一字串，多來源以 `; ` 分隔；題卡已有 `reference` 時只在尾端追加，
     不刪既有內容。字串含 `: `、`#`、引號或以特殊字元開頭時依 YAML 規則加雙引號
     （內部雙引號以 `\"` 跳脫）。沒有 `reference` 鍵時加在 frontmatter 最後一行（`---` 之前）。
   - **原文可得性檢查**：reference 指向期刊論文時，在 vault 論文庫
     `3. Resources/論文s/`（含子資料夾）用 Grep 找檔名/DOI 是否有原文 PDF。
     - 有 → 可在 reference 附 `[[檔名]]` wikilink。
     - 無 → 進度檔該題 `needs_download: true`，並在 reference 保留完整書目資訊
       （期刊+年+卷頁/DOI），供使用者自行下載原文。不要因為沒有原文就略過或改寫該 reference。
4. **補分類**：`subspecialty == Unknown` 時依題幹判定（白名單見下），直接改 frontmatter
   `subspecialty`；同時把 body 首行 `#Sub` 標籤改成一致。概念歸屬有誤時修 frontmatter `concepts`
   （YAML list，slug 必須存在於 `vault/concepts/`）與尾段 `概念：[[…]]`／`![[…]]`。
   低信心 → 進度檔 `low_confidence_subspecialty: true` 走覆核。
5. **圖片**：官方 PDF 該題若含圖且題卡未嵌圖 → 進度檔該題 `_needs_image: true`，本流水線不搬圖
   （圖片走 Cloudflare 圖床 `/img-hosting` 流程另行處理），僅標記待補。
6. **自評稽核**：對產出的題跑 5 項清單（answer / 逐選項 / 分類 / reference / image），記 `audit_score`。
7. **寫入題卡**：用 Edit 工具做最小替換（詳解段整段、`reference` 一行、必要時 `subspecialty`／`concepts`），
   寫完 `git diff -- vault/questions/{year}/{qid}.md` 確認只有預期行變動，**不要**設 `checked:true`。
8. **更新進度**：寫 `tmp/pipeline-progress.json`（格式見下）。

## 進度／稽核檔格式（`tmp/pipeline-progress.json`）

所有流水線附帶欄位都放這裡，**不寫進題卡**（題卡只放醫師與前端需要的欄位）。

```json
{
  "year": 2016,
  "phase": "A",
  "last_qid": "2016-011",
  "ts": "2026-10-10T14:30:00+08:00",
  "done": ["2016-002", "2016-011"],
  "remaining": ["2016-013", "2016-017"],
  "items": {
    "2016-011": {
      "reference_source": "journal",
      "pending_reference": null,
      "needs_download": false,
      "generated": false,
      "audit_score": 4,
      "low_confidence_subspecialty": false,
      "_needs_image": false,
      "_answer_check": "official=B card=B agree"
    }
  }
}
```

> `pending_reference`：未過閘的候選來源字串（`llm_suggested`），醫師決定後再手動寫入題卡。
> 其他稽核輸出（如重跑 `audit_questions.py` 的比較）也一律落在 `tmp/`，不進 repo 其他目錄。

## 放射來源辨識閘（白名單，與 verify_reference.py 同步）

- 期刊：`Radiology / RadioGraphics / AJR / AJNR / JVIR` + 年份
- 線上：`radiopaedia`、`statdx`
- 教科書：`Osborn's Brain` / `Core Radiology` / `The Requisites` / `Fundamentals of CT/MRI/Skeletal Radiology` / `BI-RADS 2013`
- 官方：`交換考 {year} 官方詳解`（保底）
- vault：`[[筆記名]]`（可回溯實體 PDF）

不屬上述 → `llm_suggested`，不寫進題卡、強制人覆核。寫完一批可用
`python scripts/audit_questions.py {year}` 重跑，量化 reference/逐選項覆蓋率提升。

## subspecialty 白名單

`ABD, CV, CH, Breast, H&N, MSK, NR, PED, US, IR, Physics, Unknown`

## 品質清單（自評 5 項，每項 0/1）

1. 有合法 correctAnswer 且與官方詳解一致
2. 詳解段逐選項解釋
3. subspecialty 非 Unknown
4. reference 過來源辨識閘
5. 圖片題已嵌圖（無法判定 → NA 不扣分）

## Golden Example（逐選項詳解，2016-002 Adrenal adenoma）

題卡 `??` 之後應長這樣（`**Ans:**` 與尾段原樣保留）：

```
??
**Ans: A**
(A) **正確**：Adrenal adenoma 佔腎上腺 incidentaloma 約 75%，遠比 metastasis 常見。
(B) **錯誤**：腺瘤在非顯影 CT 上密度 **≤10 HU**（非 >20 HU）即可確診。
(C) **錯誤**：腺瘤在 opposed-phase MRI 上**訊號明顯下降**（含脂），這是其特徵。
(D) **錯誤**：腺瘤特性是 contrast **快速 washout**（>60% absolute / >40% relative），非滯留 90%。
概念：[[adrenal-adenoma]]
```

對應 frontmatter：

```yaml
reference: "AJR 2008;190:1163 adrenal adenoma washout; 見 [[Adrenal adenoma]]"
```

## Phase B 逐題流程（生成，最後執行）

僅在使用者明確要求、且 Phase A 已覆核完成後啟動。對 `has_official: false`/`null` 的題：

1. **核對題目**：先讀官方 PDF 該題（若有殘缺官方內容）確認題幹/答案無誤。
2. **蒐證**：在 `2. Areas/{科}相關知識/` 與 `vault/concepts/` 用 Grep/omnisearch 找對應主題筆記，
   讀其內容與 `### 參考來源`。無對應筆記時才用一般放射知識。
3. **生成逐選項詳解**：格式同 Golden Example，但詳解段第一行為
   `（AI 生成草稿，待覆核）`。寧可保守、標明不確定處，不得杜撰數據。
4. **reference**：能對到 vault 筆記/白名單期刊就寫進 frontmatter；否則記 `pending_reference`
   （`reference_source: llm_suggested`），並依需要標 `needs_download: true`。
5. **寫入題卡**：同 Phase A 第 7 步；進度檔該題 `generated: true`，**絕不設 checked**。
6. **稽核 + 進度**：同 Phase A。

> Phase B 是「沒有官方詳解時的補救」，品質本質低於 Phase A，務必讓使用者知道哪些題是生成的
> （詳解段首行標記 + 進度檔 `generated: true`，醫師可在 Obsidian 搜尋 `AI 生成草稿` 優先覆核）。

## 人覆核迴圈（流水線外，醫師執行）

1. 醫師在 Obsidian 開題卡逐題覆核：確認詳解、reference、分類；有疑義直接改題卡。
2. 覆核通過後將 frontmatter `checked` 改為 `true`；Phase B 題同時刪掉首行 `（AI 生成草稿，待覆核）`。
3. 進度檔 `pending_reference` 有值的題，醫師決定採用與否；採用則手動寫入 `reference`。

## Commit 規範（agent 執行）

- 一批處理完（或 token 邊界停下）就 commit，**只列明確路徑**，不用 `git add -A`／`git add .`：

```bash
git add vault/questions/2016/2016-011.md vault/questions/2016/2016-013.md
git commit -m "pipeline(2016): 2016-011、2016-013 逐選項詳解＋reference 草稿（checked:false）"
```

- `tmp/` 不進 commit。推 main 前依多代理推送規則先 `git fetch` 做祖先檢查；被拒絕不 `--force`。
