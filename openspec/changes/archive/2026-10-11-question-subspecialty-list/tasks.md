## 1. 模型與程式

- [x] 1.1 compiler 將題目索引的 `subspecialty` 一律發佈為去重清單（字串→單元素、缺→空），滿足 **Question index entries publish subspecialty as a list**。驗證：`python scripts/test_vault_site.py` 新增三列正規化案通過；重建索引後所有 entry 的 `subspecialty` 皆為 list。
- [x] 1.2 前端以清單語意比對：`vault-app.js` 的 `_subs(entry)`（篩選、pill、列表顯示、組卷表單）、`test-builder.js` 任一包含、`weakness.js` 每個次專科一列、`analytics-view.js` 以 `/` 串接，滿足 **Multi-subspecialty questions match any selected subspecialty**。驗證：`node scripts/test_exam_builder.js`（`["GI","ABD"]` 題在 ABD 或 GI 篩選下皆入池）、`node scripts/test_scheduler.js`（兩題 `[GI,ABD]`／`[GU,ABD]` 產生 ABD:2 群）通過；瀏覽器點 ABD pill 時 GI 題出現。

## 2. 資料與上線

- [x] 2.1 104 張 GI／GU／OBGYN 題卡 frontmatter 改為 `[X, ABD]` 並在題幹 tag 補 `#ABD`；2 張概念卡 ENT→H&N、MR→MRI；只提交別名變更，不帶入其他 session 的未提交修改。驗證：`git show --numstat HEAD -- vault` 每檔皆為 2/2（題卡）或 1/1（概念卡）；重建索引後題目次專科集合不含 OB／GYN／ENT／MR，ABD 計數增加 104。
- [x] 2.2 推送 main，`deploy-pages.yml` success；線上 `indexes/questions.json` 所有 entry 的 `subspecialty` 為 list，GI 題在 ABD 篩選下可見。驗證：`gh run list --workflow deploy-pages.yml --limit 1` success；curl 線上索引統計；瀏覽器 read_page 確認。
