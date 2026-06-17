---
concepts: [chemical-shift-artifact]
name: MRI Chemical Shift Artifact
subspecialty: [NR, ABD]
aliases:
  - chemical shift artifact
  - India ink artifact
  - 化學位移假影
dateRev: 2026-06-17
---

# chemical-shift-artifact

**化學位移假影源自脂肪與水的共振頻率差。Type 1(misregistration)在頻率編碼方向、所有序列皆有；Type 2(cancellation/India ink)只在反相位(out-of-phase)、且需『同一像素內同時有脂肪與水』才抵消——『純脂肪』在反相位『不會』完全失去訊號。** 判讀分水嶺一：**Type1=空間位移(頻率編碼軸)、Type2=訊號抵消(反相位)**；判讀分水嶺二：**India ink 黑線=器官四周(脂水界面)**。

## Summary
- **Type 1（misregistration）**：沿**頻率編碼方向**的空間位移；**所有序列**或多或少皆有（常不明顯）。[^1]
- **Type 2（cancellation / India ink）**：僅見於**反相位(out-of-phase)**，**像素內同時含脂肪與水**時訊號抵消 → 器官四周黑線(India ink)。[^1]
- **純脂肪區在反相位『不會』完全失訊號**——抵消需脂＋水並存；故「純脂肪在 out-of-phase 完全失去強度」**錯誤**（2016-092 正解 B）。[^1]
- **India ink**：完整環繞器官各邊的黑線，可與只沿頻率編碼軸的 type 1 區分。[^1]
- **Hemosiderosis**：肝脾在 out-of-phase 反而較亮（in-phase TE 較長、T2* 效應使 in-phase 變暗）。[^1]

> [!note] 考點：何者「為非」？
> 「**純脂肪區在 out-of-phase 完全失去強度**」為非——抵消需**脂＋水同一像素**並存；純脂肪不抵消。其餘(type2 反相位、India ink 環繞、hemosiderosis out-of-phase 較亮)正確。[^1]

### 參考來源
[^1]: MRI 化學位移假影經實際查證（accessed 2026-06-17，Radiopaedia *chemical shift artifact*）：脂水頻率差；type1 頻率編碼方向位移(各序列)、type2 反相位抵消(需脂+水)；India ink 環繞器官；hemosiderosis out-of-phase 較亮(in-phase T2*)。

## 題目
> [!question]- 關於 MRI 化學位移假影，何者「為非」？
> 「**純脂肪區在 out-of-phase 完全失去訊號**」為非——抵消需脂＋水同一像素並存。type2 反相位、India ink 環繞器官、hemosiderosis out-of-phase 較亮皆正確。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "chemical-shift-artifact")
```
