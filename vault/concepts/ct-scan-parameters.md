---
concepts: [ct-scan-parameters]
name: CT Scan Parameters — Pitch, Speed, Motion Artifact
subspecialty: [RP]
aliases:
  - CT pitch
  - rotation time
  - detector coverage
  - CT motion artifact
  - CT 掃描參數
dateRev: 2026-07-02
---

# ct-scan-parameters

**CT 掃描關鍵參數：Pitch = 每轉一圈床台移動距離 / beam collimation，僅適用於 helical 模式，axial 模式下不需調整。減少 motion artifact 靠加快掃描速度（縮短 rotation time、增加 pitch）。**

## Summary
- **Pitch**：僅適用於 helical 模式，axial 模式下不適用。[^1]
- **Detector Coverage**：axial 與 helical 皆需設定。[^1]
- **Rotation Time**：兩種模式皆需設定。[^1]
- **Motion Artifact**：加快掃描速度（縮短 rotation time）可減少。[^2]

## 陷阱
- axial 模式下 Pitch & Speed 不需調整。[^1]

### 參考來源
[^1]: 2019 交換考詳解；GE Lightspeed VCT 操作介面。
[^2]: 2019 交換考詳解；GE Lightspeed CT console。

## 考題
```dataview
list from #交換 where contains(concepts, "ct-scan-parameters")
```
