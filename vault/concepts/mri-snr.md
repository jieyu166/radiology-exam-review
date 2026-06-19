---
concepts: [mri-snr]
name: MRI Signal-to-Noise Ratio (Bandwidth & Parameters)
subspecialty: [Physics]
aliases:
  - MRI SNR
  - receiver bandwidth
  - signal-to-noise ratio
  - 磁振訊雜比
dateRev: 2026-06-19
---

# mri-snr

**MRI 的 SNR 與多個掃描參數相關;receiver bandwidth 與 SNR 成『反平方根』關係。** 判讀分水嶺一：**SNR ∝ 1/√(bandwidth)**——頻寬減半 → SNR 變為原來的 **√2 倍**;判讀分水嶺二：**SNR 亦正比於 voxel volume、√(NEX)、√(相位編碼數);較窄頻寬增 SNR 但延長 echo time/加重化學位移偽影**。

## Summary
- **Bandwidth 與 SNR**：**SNR 與接收頻寬的平方根成反比（SNR ∝ 1/√BW）**。[^1]
  - **頻寬減半 → SNR 變為原來 √2 倍**（≈1.41×）。
- **代價**：較窄頻寬雖增 SNR,但**延長最短 TE、加重化學位移偽影**。[^1]
- 其他影響 SNR：voxel volume、√(NEX/averages)、√(phase-encoding steps)、線圈、場強。[^1]

> [!note] 考點：bandwidth 減半,SNR 如何變化?
> **變為原來的 √2 倍**（SNR ∝ 1/√BW）。非 2 倍、非 1/2、非不變。[^1]

### 參考來源
[^1]: MRI SNR 與 bandwidth（官方 2016 詳解；Hashemi, MRI: The Basics 2nd ed. p.168）：**SNR ∝ 1/√(bandwidth)**;頻寬減半 SNR 增 √2 倍;窄頻寬延長 TE、加重化學位移偽影。

## 題目
> [!question]- MRI bandwidth 調整為原來的一半,對 SNR 的影響為何? (2016-259)
> **變為原來的 √2 倍**（SNR 與 √bandwidth 成反比）。非 2 倍、非 1/2、非不變。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "mri-snr")
```
