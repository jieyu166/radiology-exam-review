## 1. 轉檔骨架與 SR 卡片

- [x] 1.1 建立 scripts/json_to_vault.py 入口：CLI 接受 year 位置參數與 --force 旗標，讀 data/{year}.json 並輸出至 vault/questions/{year}/。行為：執行 `python scripts/json_to_vault.py 2016` 在 vault/questions/2016/ 產生每題一檔。驗證：產出檔數等於 data/2016.json 的 questions 數（197）。
- [x] 1.2 實作 "Generate SR question cards from question JSON"：每題卡片依序輸出 YAML frontmatter（id/year/subspecialty/correctAnswer/concepts/checked）、tag 行 `#交換 #{year}交換 #{subspecialty}`、題幹與選項、`??`、`**Ans: {correctAnswer}**`、explanation、以及每個 concept 的 `[[{concept-id}]]` 內文連結。驗證：抽查 2016-001 卡片各欄位對應符合 spec 的「2016-001 field mapping」範例表，`??` 前為題幹選項、後為答案詳解。

## 2. 詳解不足標記

- [x] 2.1 實作 "Mark questions with insufficient explanations"：重用 scripts/audit_questions.py 的逐選項判定，explanation 為空或未逐選項者，卡片背面在 `**Ans:**` 後加 `> [!todo] 待補詳解` callout；足夠者原樣寫入。驗證：取一題空 explanation 確認出現 callout，取一題通過逐選項檢查確認無 callout。

## 3. 概念筆記

- [x] 3.1 實作 "Generate concept notes that aggregate their questions"：為被任一題引用的 concept 產出 vault/concepts/{concept-id}.md，含 frontmatter（concept/name/subspecialty）、概念說明（取自 data/concepts.json，缺則留空白說明區）、以及篩選 concepts 含該 id 的 Dataview list 區塊。驗證：upj-obstruction.md 存在且含 Dataview list；對 concepts.json 無此 id 者仍建立並有空說明區。

## 4. 冪等與 SR 排程保留

- [x] 4.1 實作 "Idempotent regeneration preserving SR scheduling"：預設不覆寫既有卡片/概念檔並回報 skip；--force 時覆寫但保留原檔所有以 `<!--SR:` 開頭的排程註解行。驗證：對既有 vault 重跑（無 --force）不變更且報 skip；手動於某卡片加一行 `<!--SR:!2026-...-->` 後以 --force 重跑，該行仍保留。

## 5. SR 外掛設定

- [x] 5.1 實作 "Write SR plugin configuration"：產生最小 vault/.obsidian/ 設定，將 Spaced Repetition 外掛 flashcard tag 設為 `#交換`；不嘗試安裝任何社群外掛。驗證：vault/.obsidian/ 下 SR 外掛 data 檔宣告 `#交換` 為 flashcard tag。

## 6. 端到端驗證與文件

- [x] 6.1 端到端驗證並補文件：跑轉檔後用 Obsidian 開 vault/ 確認 SR 外掛辨識 `#交換` 牌組（197 張）、抽查 5 張卡格式正確、概念筆記經 backlink/Dataview 列出相關題；README.md 增補 vault 產生與使用說明。驗證：Obsidian 牌組張數=197、抽查 5 卡通過、README 含 vault 段落。
