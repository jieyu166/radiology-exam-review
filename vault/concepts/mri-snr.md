---
concepts: [mri-snr]
name: MRI Signal-to-Noise Ratio (Bandwidth & Parameters)
subspecialty: [Physics]
aliases:
  - MRI SNR
  - receiver bandwidth
  - signal-to-noise ratio
  - 磁振訊雜比
dateRev: 2026-07-03
nonImaging: true
nonImagingReason: "純 MRI 物理（SNR 公式/參數權衡），無可判讀影像特徵"
---

# mri-snr

**Bandwidth 與 SNR 的關係是「反平方根」——頻寬窄，雜訊取樣少，SNR 上升，但代價是最短 TE 延長與化學位移偽影加重。** 判讀分水嶺一：**SNR ∝ 1/√BW——頻寬減半，SNR 升為 √2 倍（≈1.41×），非 2 倍**；判讀分水嶺二：**SNR 同時受 voxel volume、√(NEX)、√(相位步數) 影響**，頻寬只是其中一個旋鈕。

## Summary
- **Bandwidth 與 SNR**：**SNR 與接收頻寬的平方根成反比（SNR ∝ 1/√BW）**。[^1]
  - **頻寬減半 → SNR 變為原來 √2 倍**（≈1.41×）。
- **代價**：較窄頻寬雖增 SNR,但**延長最短 TE、加重化學位移偽影**。[^1]
- 其他影響 SNR：**SNR ∝ voxel volume、√(NEX/averages)、√(phase-encoding steps)**、線圈、場強;3D volume 取像較 2D 增 SNR。[^1][^3]
- **成像鏈與 SNR（Plewes）**：MRI 訊號源自淨磁化被 RF 激發、以接收線圈偵測橫向磁化之進動；**SNR 取決於體素內自旋數（voxel 大小/質子密度）、B₀、線圈與取樣（頻寬/平均次數）**；影像對比與 SNR 之取捨受 TR/TE/翻轉角與序列設計影響。[^4]
- **場強(field strength)與SNR**：理論上訊號強度與靜磁場強度(B0)**平方**成正比，雜訊則與場強成**線性**正比——完美系統下**SNR與B0成正比**，故**3T系統之SNR理論上為1.5T之2倍**。[^2]

> [!note] 考點：bandwidth 減半,SNR 如何變化?
> **變為原來的 √2 倍**（SNR ∝ 1/√BW）。非 2 倍、非 1/2、非不變。[^1]

> [!note] 考點：3T MRI的SNR是1.5T的幾倍？
> **2倍（B）**——SNR理論上與場強(B0)成正比。[^2]

### 參考來源
[^1]: MRI SNR 與 bandwidth（官方 2016 詳解；Hashemi, MRI: The Basics 2nd ed. p.168）：**SNR ∝ 1/√(bandwidth)**;頻寬減半 SNR 增 √2 倍;窄頻寬延長 TE、加重化學位移偽影。
[^2]: 官方2020詳解；Ref: Walter Huda, Review of radiologic physics. 4th Ed., 2016. P.206, 231（題目所引）——訊號強度與B0平方成正比、雜訊與B0線性成正比，故SNR理論上與B0成正比，3T之SNR為1.5T之2倍。
[^3]: Gaillard F, et al. *Signal-to-noise ratio (MRI)*. Radiopaedia, rID-14045, DOI 10.53347/rID-14045（輔助來源）——**MRI SNR ∝ voxel 體積、√(averages) 與 √(phase steps)**（固定 voxel），故與取像時間密切相關；3D volume 取像較 2D 增 SNR——佐證 SNR 之參數依存（頻寬亦為其中一旋鈕）。
[^4]: **Tier 1** Plewes DB, Kucharczyk W. *Physics of MRI: a primer*. J Magn Reson Imaging 2012;35(5):1038-54（據 PubMed，DOI [10.1002/jmri.23642](https://doi.org/10.1002/jmri.23642)；Review；基於 ISMRM「MR Physics for Clinicians」課程；實際查證 accessed 2026-07-04）——闡述 MR 訊號如何在掃描儀中產生與偵測、NMR 弛豫、Fourier transform 與影像形成、梯度空間編碼、脈衝序列與對比之因素；**SNR 取決於體素內自旋數（voxel 大小/質子密度）、B₀、線圈與取樣（頻寬/平均），對比與 SNR 之取捨受 TR/TE/翻轉角與序列設計影響**——佐證 SNR 之物理參數依存。原「官方/Radiopaedia」弱來源已由本次 JMRI DOI Tier 1 查核升級。

## 題目
> [!question]- 3T MRI 的訊雜比(SNR)是1.5T MRI的幾倍？ (2020-417)
> **2倍（B）**——SNR理論上與靜磁場強度(B0)成正比。[^2]

## 考題
```dataview
list from #交換 where contains(concepts, "mri-snr")
```
