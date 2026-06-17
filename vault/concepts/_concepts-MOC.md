---
name: 概念索引 MOC（依次專科）
type: MOC
---

# 概念索引 MOC（Map of Content）

> 本 vault **不用資料夾分科**——概念常跨多科（如 rib-tumor=MSK+CH）。改以本 MOC 用既有
> `subspecialty:` frontmatter **自動依科別列出**；一個概念會同時出現在其所有相關科別下。
> 需要時可加裝 **Breadcrumbs** 外掛建立 hub→實體從屬（設定見 [[=Breadcrumbs設定備忘]]，
> 已示範於 [[adrenal-imaging]]↔[[adrenal-adenoma]]）。
> ⚠️ Dataview `FROM` 路徑相對於 **Obsidian vault 根（= 本 `vault/` 資料夾）**，故用 `"concepts"`（非 `vault/concepts`）。

## 依次專科自動分類（Dataview）
```dataview
TABLE WITHOUT ID rows.file.link AS "概念", length(rows) AS "數"
FROM "concepts"
WHERE concepts AND subspecialty
FLATTEN subspecialty AS sub
GROUP BY sub AS "次專科"
SORT sub ASC
```

## 全部概念（依更新日）
```dataview
TABLE name AS "顯示名", subspecialty AS "次專科", dateRev AS "更新"
FROM "concepts"
WHERE concepts AND subspecialty
SORT dateRev DESC
```

## 待補（無 subspecialty 或 stub）
```dataview
LIST
FROM "concepts"
WHERE concepts AND !subspecialty
```

## 建議的組織策略（業界共識）
- **檔案保持扁平**（`concepts/`）；分科靠 **frontmatter `subspecialty` ＋ 本 MOC 的 Dataview**，不搬資料夾。
- **Breadcrumbs**（選用）：同科內的 **hub→實體從屬**用 `up`/`down`（adrenal-imaging→adrenal-adenoma、rib-tumor→各骨腫瘤、acute-stroke-management→aspects-score）；兄弟用 `same`（pulmonary-tb↔septic-pulmonary-emboli）。
- **tags**：用於跨科主題/狀態（如 `#待補圖`），非主結構。
- 與腳本相容：`json_to_vault.py` 只寫被題目引用的 concept slug，本 MOC（無 `concepts` 欄）不受影響。
