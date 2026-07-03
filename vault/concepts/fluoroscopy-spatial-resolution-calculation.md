---
concepts: [fluoroscopy-spatial-resolution-calculation]
name: Digital Imaging Spatial Resolution Calculation (FOV/Matrix)
subspecialty: [Physics]
aliases:
  - field of view matrix resolution
  - pixel size calculation
  - Nyquist limiting resolution
  - 照野矩陣解析度計算
nonImaging: true
nonImagingReason: "純物理計算題（FOV/矩陣推算像素大小與極限解析度），無可判讀影像特徵"
dateRev: 2026-07-03
---

# fluoroscopy-spatial-resolution-calculation

**數位影像極限空間解析度（lp/mm）計算兩步：①pixel size = FOV ÷ matrix；②極限解析度 = 1 ÷ (2 × pixel size)——依 Nyquist 抽樣定理，分辨一組 line pair（一亮一暗）至少需 2 個 pixel 寬度，故要「除以 2」。** 判讀分水嶺：**別忘了「÷2」（Nyquist）——只取 1/pixel size 會高估一倍；且這是「取樣/顯示」上限，實際解析度還受焦點大小、幾何放大等限制。**

## Summary
- **Pixel size 公式**：**pixel size = FOV ÷ matrix**（例：FOV 30 cm、matrix 1024×1024 → 300 mm/1024 ≈ 0.293 mm）。[^1]
- **極限空間解析度公式（Nyquist）**：**極限解析度(lp/mm) = 1 ÷ (2 × pixel size)**——分辨一組 line pair（一亮線一暗線）至少需 **2 個 pixel** 寬度。[^1]
- **範例計算**：0.293 mm → 1 ÷ (2 × 0.293 mm) ≈ **1.71 lp/mm**。[^1]
- **常見誤區**：勿誤用「1/pixel size」（漏除以 2 → 高估一倍）或其他倍數；先確認每組 line pair 所需 pixel 數（=2）。[^1]

## 放射科醫師影像判讀重點
- **兩步驟固定**：先 FOV/matrix 得 pixel、再 1/(2×pixel) 得 lp/mm。[^1]
- **單位一致**：FOV 換成 mm 再除，避免 cm/mm 混用。[^1]
- **Nyquist 概念**：取樣頻率須 ≥ 2 倍最高空間頻率，才不失真（aliasing）；影像上即「2 pixel/line pair」。[^1]
- **上限非實測**：此為「取樣/顯示」理論上限，實際受焦點大小、幾何放大、散射、偵測器 MTF 等進一步限制而更低。[^1]
- **縮小 FOV/增矩陣**：pixel 變小 → 極限解析度上升（但雜訊/劑量/計算負擔隨之變化）。[^1]

## 臨床重點（5 句）
1. **公式**：pixel = FOV/matrix；極限 = 1/(2×pixel)。[^1]
2. **除以 2**：Nyquist——1 line pair 需 2 pixel。[^1]
3. **範例**：30 cm/1024 → 0.293 mm → ~1.71 lp/mm。[^1]
4. **上限**：理論值，實際受焦點/幾何/MTF 限制更低。[^1]
5. **調整**：縮 FOV 或增 matrix 可提高極限解析度。[^1]

> [!note] 考點：FOV 30cm、matrix 1024x1024，系統理論上解析度不超過多少lp/mm？
> **約 1.72 lp/mm（D）**——pixel size = 300 mm/1024 ≈ 0.293 mm；極限解析度 = 1/(2×0.293 mm) ≈ 1.71 lp/mm（Nyquist：1 line pair 需 2 pixel）。[^1]

### 參考來源
[^1]: 官方 2020 詳解；Ref: Bushberg JT, et al. *The Essential Physics of Medical Imaging*, 3rd ed., 2011, p.299（題目所引；accessed 2026-07-03）——**pixel size = FOV/matrix**；**極限空間解析度(lp/mm) = 1/(2×pixel size)**（Nyquist 抽樣定理：分辨一組 line pair 需 2 個 pixel 寬度）。範例 FOV 30 cm、matrix 1024 → 0.293 mm → ~1.71 lp/mm，計算經逐步覆核無誤。

## 題目
> [!question]- 若一透視攝影設備設定的可視照野大小(FOV)為30cm，且影像成像矩陣(imaging matrix)為1024x1024，則該系統理論上解析度不超過多少lp/mm？ (2020-415)
> **約 1.72 lp/mm（D）**——pixel size ≈ 0.293 mm，極限解析度 = 1/(2×0.293 mm) ≈ 1.71 lp/mm。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "fluoroscopy-spatial-resolution-calculation")
```
