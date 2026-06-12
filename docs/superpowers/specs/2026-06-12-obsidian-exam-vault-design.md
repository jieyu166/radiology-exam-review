# 交換考題 Obsidian SR Vault — 設計 spec

日期：2026-06-12
狀態：已核准設計，待寫實作計畫

## Context（為什麼做）

先前方向（線上網站 + Google Sheets + 稽核流水線）對目前需求過於複雜。改以**純 Obsidian
vault** 形式整理交換考題：以 spaced repetition（SR）卡片複習、以 concept 筆記組織知識。
舊放射 vault 太複雜，故在 `radiology-exam-review` repo 內**新開一個獨立、乾淨的 vault**。

先做 2016、先做 vault（不碰網站）。資料源用 repo 既有的 `data/2016.json`（197 題，多數已含
詳解、subspecialty、concepts），詳解不足者交給既有 `exam-explanation-pipeline` skill 補。

## 範圍

- ✅ 只做 2016；只產出 Obsidian vault（SR 卡片 + concept 筆記）
- ✅ 重用 `data/2016.json`、`data/concepts.json`、`scripts/verify_reference.py`、
  `scripts/audit_questions.py`、`.claude/skills/exam-explanation-pipeline`
- ❌ 不動既有 `data/*.json`（除 Step 2 補詳解外）、`js/`、`index.html`、Google Sheets
- ❌ 不做網站整合、不做其他年份（之後比照）

## Vault 結構

在 repo 內新開獨立 vault `vault/`（含自己的 `.obsidian/` 設定，與網站程式碼分離）：

```
radiology-exam-review/
└── vault/
    ├── .obsidian/                      # SR 外掛設定（flashcard tag）
    ├── questions/2016/2016-001.md …    # 一題一檔（SR 卡片）
    ├── concepts/upj-obstruction.md …   # 一概念一檔
    └── _index/=NR.md …                 # （選用）各科 Dataview 索引頁
```

## 題目卡片格式（一題一檔 `questions/2016/{id}.md`）

```markdown
---
id: 2016-001
year: 2016
subspecialty: NR
correctAnswer: D
concepts: [upj-obstruction]
checked: false
---
#交換 #2016交換 #NR

Concerning congenital ureteropelvic junction (UPJ) obstruction, which one is TRUE?
(A) It is an uncommon cause of hydronephrosis in children.
(B) Urinary tract infection is the most common presentation.
(C) Females and males are affected equally.
(D) The presence of crossing vessels decreases the success rate of pyeloplasty.
??
**Ans: D**
(A) 錯：UPJ obstruction 是兒童水腎最常見原因…
(D) 正確：Crossing vessel 會降低 pyeloplasty 成功率…

概念：[[upj-obstruction]]
```

規則：
- **YAML**：`id/year/subspecialty/correctAnswer/concepts/checked` → 供 Dataview 查詢。
- **Tag 行**：`#交換`（SR 牌組總標籤）+ `#2016交換`（年）+ `#{subspecialty}`（科）。
- **`??`**：Obsidian SR 多行卡片分隔，前=題幹+選項，後=答案+逐選項詳解。
- **概念連結**：內文 `[[concept-id]]`（題目→概念，產生反向連結；概念筆記據此自動匯整）。
  YAML `concepts:` 與內文 `[[ ]]` 並存：前者給 Dataview、後者給 backlinks。
- **`<!--SR:!...-->`**：SR 外掛排程註解，初次產生時無；**腳本重跑時絕不刪改**（見冪等性）。
- 詳解不足的題：背面仍寫 `**Ans: X**`，詳解區放 `> [!todo] 待補詳解` 佔位，待 Step 2 補。

## 概念筆記格式（一概念一檔 `concepts/{concept-id}.md`）

```markdown
---
concept: upj-obstruction
name: UPJ Obstruction
subspecialty: NR
---
# UPJ Obstruction

（概念說明：定義、影像特徵、鑑別診斷、重點、處置）

## 相關交換考題
\`\`\`dataview
list from #交換 where contains(concepts, "upj-obstruction")
\`\`\`
```

- 概念說明來源：`data/concepts.json` 既有欄位（definition / imagingFindings /
  differentialDiagnosis / keyPoints / management）；不足由 skill 補。
- 相關題目透過 backlinks + Dataview 自動匯整，無需手動維護清單。

## 工作流（分兩步）

### Step 1 — 轉檔（先做，一次性、可重跑）
新腳本 `scripts/json_to_vault.py`：
1. 讀 `data/2016.json` 的 `questions[]`，每題輸出 `vault/questions/2016/{id}.md`（上述格式）。
2. 讀 `data/concepts.json`，為被引用到的 concept 輸出 `vault/concepts/{id}.md`（概念說明 stub +
   Dataview 匯整區）。
3. 產出 `vault/.obsidian/` 最小設定，將 SR 外掛 flashcard tag 設為 `#交換`。
4. **冪等性**：預設**不覆寫**已存在的 `.md`（保護使用者編輯與 SR 排程）；`--force` 才覆寫，且
   覆寫時保留檔內所有 `<!--SR:!...-->` 行。

### Step 2 — 補詳解 + 建概念筆記（後做）
1. 跑 `python scripts/audit_questions.py 2016` 找「詳解不足」題（逐選項未通過 / explanation 過短）。
2. 對這些題呼叫 `exam-explanation-pipeline` skill：官方詳解優先重構（Phase A），無官方者最後生成
   （Phase B，標 `generated`）。產出寫回 `data/2016.json`（沿用既有 merge_edits 流程）。
3. 重跑 `json_to_vault.py --force` 僅針對受影響題重生卡片（保留 SR 排程）。
4. 為涉及的概念補 `concepts/*.md` 內容（同樣由 skill 依 vault 知識/官方來源生成）。

> 單一內容真實來源仍是 `data/2016.json`；vault 由其產生。SR 排程只存在於 vault 且永遠保留。

## SR 外掛設定

- flashcard tag = `#交換`（外掛掃描帶此 tag 的筆記中的 `??` 卡片）。
- 題目同時帶 `#2016交換 #{subspecialty}` 供篩選與分牌組複習。
- **前提**：使用者需在 Obsidian 安裝社群外掛 **Spaced Repetition** 與 **Dataview**。
  `json_to_vault.py` 只能寫入外掛設定（`.obsidian/plugins/.../data.json`），無法代為安裝外掛；
  首次開 vault 時需手動啟用這兩個外掛。

## 重用與新增

| 動作 | 項目 |
|---|---|
| 新增 | `scripts/json_to_vault.py`、`vault/`（含 `.obsidian/`） |
| 重用 | `data/2016.json`、`data/concepts.json`、`verify_reference.py`、`audit_questions.py`、`exam-explanation-pipeline` skill |
| 不動 | `data/*.json`（除 Step 2）、`js/`、`index.html`、`sheets_*` |

## 已確認的預設

1. SR flashcard tag 用 `#交換`（總牌組）。
2. vault 放 `radiology-exam-review/vault/`（同 repo、獨立子資料夾）。
3. 概念連結：題目內文用 `[[concept-id]]`（非 `![[]]` embed，非單純 `#tag`）。

## 驗證

1. `python scripts/json_to_vault.py`（dry-run / 預設）→ 檢查 `vault/questions/2016/` 出 197 檔、
   `vault/concepts/` 出被引用概念數。
2. 用 Obsidian 開 `vault/`，SR 外掛能辨識 `??` 卡片、`#交換` 牌組數=197。
3. 抽查 5 張卡：YAML 正確、`??` 前後切分正確、`[[concept]]` 在概念筆記產生 backlink、Dataview 匯整有結果。
4. 冪等性：再跑一次（無 `--force`）→ 不覆寫、不報錯；手動加一條 `<!--SR:-->` 後 `--force` → 該行保留。
5. Step 2：對一題詳解不足者跑 skill → 卡片背面詳解補上、概念筆記生成。
```
