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

**化學位移假影來自脂肪與水的共振頻率不同：Type 1 是空間位移（沿頻率編碼方向，各序列皆有）；Type 2 是訊號抵消（只在反相位、且像素內脂肪與水並存才抵消，產生器官邊緣的 India ink 黑線）。** 考試陷阱：「純脂肪區在 out-of-phase 完全失訊號」是錯的——抵消需要脂＋水同時存在，純脂肪沒有水可以抵消。記憶鉤：「抵消要兩個人，純脂肪是獨居，沒人抵消它」。

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

## 考題
```dataview
list from #交換 where contains(concepts, "chemical-shift-artifact")
```
