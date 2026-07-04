## Why

概念頁（#/concepts）目前把 977 個概念平鋪成單一大清單，無法依次專科縮小範圍（issue #1）。考題的卡片與列表模式早有次專科 pill 篩選，概念頁應補上對等能力，讓使用者能快速聚焦某一科的概念。

## What Changes

- 概念列表頁在標題下方新增一列次專科藥丸（pill）篩選，第一顆為「全部」，其後每個次專科各一顆並附該科概念數。
- 藥丸選項由已載入的 data/concepts-index.json 動態去重產生（非沿用考題寫死的 13 個 pill），以涵蓋概念特有的次專科值（GU/GI/PE/Neuro/HN/RP/MRI/GYN 等）；subspecialty 為空者歸為「未分類」。
- 藥丸排序：先照考題既定順序（ABD/CV/CH/NR/MSK/H&N/PED/IR/Physics/Breast/US），其餘概念特有值接於其後。
- 點選藥丸即以純前端方式過濾概念 grid（不重新 fetch），並更新藥丸 active 狀態；「全部」還原。相關題數與「待建立概念」區塊行為不變。

## Non-Goals (optional)

- 不改動概念詳情頁、概念資料模型或 data/concepts-index.json 的產生流程（build_concepts.py）。
- 不做概念次專科的資料品質清理（HN vs H&N、Neuro vs NR、空值合併）——另案處理；本案僅忠實呈現現有值。
- 不動考題（卡片/列表/模擬考）既有的次專科 pill。
- 不新增後端或額外網路請求；篩選純用已載入的索引資料。

## Capabilities

### New Capabilities

- `concept-subspecialty-filter`: 概念列表頁依次專科（由概念索引動態產生的藥丸）做純前端篩選。

### Modified Capabilities

(none)

## Impact

- Affected specs: concept-subspecialty-filter（新）
- Affected code:
  - New: (none)
  - Modified:
    - js/concept-cards.js
  - Removed: (none)
