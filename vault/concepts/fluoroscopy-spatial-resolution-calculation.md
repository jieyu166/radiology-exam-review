---
concepts: [fluoroscopy-spatial-resolution-calculation]
name: Digital Imaging Spatial Resolution Calculation (FOV/Matrix)
subspecialty: [Physics]
aliases:
  - field of view matrix resolution
  - pixel size calculation
  - limiting spatial resolution
  - 照野矩陣解析度計算
dateRev: 2026-07-02
nonImaging: true
nonImagingReason: "純物理計算題（FOV/矩陣推算像素大小與極限解析度），無可判讀影像特徵"
---

# fluoroscopy-spatial-resolution-calculation

**數位影像極限空間解析度(lp/mm)之計算：先由照野(FOV)除以矩陣(matrix)大小求出pixel size，再取其倒數的一半——因分辨一組line pair需要至少2個pixel寬度（一亮一暗）。**

## Summary
- **Pixel size公式**：**Pixel size = FOV ÷ Matrix大小**（例如FOV 30cm、matrix 1024x1024時，pixel size = 300mm/1024 ≈ 0.293mm）。[^1]
- **極限空間解析度公式**：**極限解析度(lp/mm) = 1 ÷ (2 × pixel size)**——因分辨一組line pair（一亮線一暗線）至少需2個pixel寬度。[^1]
- **常見誤區**：勿誤用「1/pixel size」（少除以2）或誤用其他倍數關係，需先確認每組line pair所需之pixel數。[^1]

> [!note] 考點：FOV 30cm、matrix 1024x1024，系統理論上解析度不超過多少lp/mm？
> **約1.72 lp/mm（D）**——pixel size = 300mm/1024 ≈ 0.293mm；極限解析度 = 1/(2×0.293mm) ≈ 1.706 lp/mm。[^1]

### 參考來源
[^1]: 官方2020詳解；Ref: Bushberg JT et al., The Essential Physics of Medical Imaging, 3rd Ed., 2011, p.299（題目所引）——pixel size = FOV/matrix；極限空間解析度(lp/mm) = 1/(2×pixel size)，因分辨一組line pair需2個pixel寬度。

## 題目
> [!question]- 若一透視攝影設備設定的可視照野大小(FOV)為30cm，且影像成像矩陣(imaging matrix)為1024x1024，則該系統理論上解析度不超過多少lp/mm？ (2020-415)
> **約1.72 lp/mm（D）**——pixel size≈0.293mm，極限解析度=1/(2×0.293mm)≈1.706 lp/mm。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "fluoroscopy-spatial-resolution-calculation")
```
