---
name: Breadcrumbs 外掛設定備忘
type: meta
---

# Breadcrumbs 外掛設定備忘

> 用 frontmatter `up`/`down`/`same` 建立筆記從屬（hub→實體、兄弟），Breadcrumbs 把它畫成可走的有向圖。
> 本 vault 已在概念筆記埋好欄位（見最下方清單），裝外掛＋下列設定即可顯示。

## 1. 安裝
設定 → 第三方外掛 → 瀏覽 → 搜尋 **Breadcrumbs** → 安裝 → 啟用。

## 2. Edge Sources（邊來源）→ 開啟「Frontmatter」
- **關鍵**：讓 Breadcrumbs 把 frontmatter 中**值為 `[[wikilink]]` 的欄位**當作 typed edge。
- 我筆記用的 `up` / `down` / `same` 就會被讀取。

## 3. Fields / Edge fields（欄位 ↔ 方向對應）
確認下列三欄存在且方向正確（v4 預設多半已有 up/down；**`same` 可能要手動新增**）：

| 欄位名 | 方向 direction |
| --- | --- |
| `up` | **up**（parent ↑） |
| `down` | **down**（child ↓） |
| `same` | **same**（sibling ↔） |

（若想改用 `parent`/`child` 等欄名，在此改對應即可；但本 vault 一律用 `up`/`down`/`same`。）

## 4. Implied relations（隱含關係）→ 建議開啟「opposite / 反向」
- 開啟後**只需寫單向**（子寫 `up: [[hub]]`），Breadcrumbs 自動推得 hub 的 `down`。
- 本 vault 目前**兩邊都顯式寫**，開不開都正常；開啟可讓日後只寫一邊。

## 5. Views（顯示）→ 依喜好開啟
- **Trail**：筆記頂端麵包屑路徑（看祖先 / 回 hub）。
- **Tree view**（側欄）：展開目前筆記之下的階層。
- **Matrix view**：依關係類型分組顯示進 / 出連結。

## 6.（選用）視覺化 codeblock
在任一筆記插入：

    ```breadcrumbs
    type: tree
    ```

即可把該節點鄰域畫成 tree / Mermaid 圖。

## 注意
- Obsidian Properties UI 可能把 `down`/`same` 顯示為 Text；**不影響** Breadcrumbs 解析，欲整齊可手動把屬性型別設為 **List**。
- 已裝 **Dataview**（[[_concepts-MOC]] 用）；若想讓 inline field（`up:: [[..]]`）也成邊，Dataview 開著即可。

## 目前已埋從屬的概念群
| 群組 | 結構 |
| --- | --- |
| 腎上腺 | [[adrenal-imaging]]（hub）↕ [[adrenal-adenoma]] |
| 骨腫瘤 | [[rib-tumor]]（hub）↓ [[hcc-bone-metastasis]] / [[fibrous-dysplasia]] / [[aneurysmal-bone-cyst]] / [[langerhans-cell-histiocytosis]] |
| Stroke | [[acute-stroke-management]]（hub）↓ [[aspects-score]] |
| 肺感染 | [[pulmonary-tb]] ↔ [[septic-pulmonary-emboli]]（same） |

> 日後新增實體概念時，於其 frontmatter 加 `up: "[[<hub>]]"` 即可掛入對應 hub。

## 參考
- Breadcrumbs（GitHub）：https://github.com/SkepticMystic/breadcrumbs （現維護 michaelpporter/breadcrumbs）
- Quickstart（Obsidian Hub）：https://publish.obsidian.md/hub/04+-+Guides,+Workflows,+&+Courses/Guides/Breadcrumbs+Quickstart+Guide
