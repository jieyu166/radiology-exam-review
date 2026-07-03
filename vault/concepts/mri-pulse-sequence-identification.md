---
concepts: [mri-pulse-sequence-identification]
name: MRI Pulse Sequence Identification — RF Pulse Diagrams
subspecialty: [Physics]
aliases:
  - gradient echo sequence
  - spin echo sequence
  - fast spin echo
  - flip angle alpha
  - RF pulse diagram
  - 脈衝序列判讀
dateRev: 2026-07-03
---

# mri-pulse-sequence-identification

**依 RF 脈衝圖辨識 MRI 序列：只用「<90° 的可變翻轉角（α°）」重複激發、無 180° 重聚脈衝者＝Gradient echo；每個 TR 以「90° 激發 + 一個或多個 180° 重聚」組成者＝Spin echo（多個 180° 重聚＝Fast/Turbo spin echo）。** 判讀分水嶺：**GRE＝梯度反轉造回訊、無 RF 重聚、翻轉角 α 常 10-80°（<90°）以縮短 TR；SE＝必有 180° RF 重聚抵消靜磁場不均勻（T2 非 T2\*）；FSE＝同一 TR 內接續多個 180° 產多回訊填 k-space 不同列加速。**

## Summary
- **Gradient echo（GRE）**：RF 圖僅見重複之 **α°（可變、常 10-80°、<90°）**激發、**無 180° 重聚脈衝**；回訊靠**梯度反轉**產生；短 TR、快、但 **T2\* 加權**（對磁化率敏感）、SNR 較低。[^1][^2]
- **Spin echo（SE）**：每 TR 見 **90° 激發 + 一個 180° 重聚脈衝**；180° 抵消靜磁場不均勻造成之去相位 → 產生 echo（T2 加權）。[^1]
- **Fast/Turbo spin echo（FSE/TSE）**：單一 90° 後接續**多個 180° 重聚脈衝**（90°-180°-180°-180°…，echo train），各產一 echo 填 k-space 不同相位編碼列 → 大幅加速。[^1]

## 放射科醫師影像判讀重點
- **辨圖法**：只見重複 α 小翻轉角、無 180° → GRE；見 90° + 180°(s) → SE/FSE。[^1][^2]
- **GRE 物理**：無 180° 補償 → 保留 T2\*（磁化率）→ 對出血/鈣化敏感（見 [[gre-hemorrhage-detection]]）、但氣骨界面偽影多。[^2]
- **SE/FSE 物理**：**180° 重聚脈衝重新聚相、抵消靜磁場不均勻造成之去相位 → 真 T2（非 T2\*）**；FSE echo train 長度（ETL/turbo factor）越大越快但模糊/T2 blur。[^1][^3]
- **翻轉角意義**：GRE 大 α → 較 T1 權重、小 α → 較 PD/T2\* 權重；SE 固定 90°/180°。[^2][^3]
- **應用**：GRE 用於動態/血管/SWI；FSE 用於高解析 T2（省時）。[^1][^2]

## 臨床重點（5 句）
1. **GRE**：α<90°、無 180°、梯度回訊、T2\*。[^1][^2]
2. **SE**：90°+180°、真 T2。[^1]
3. **FSE**：90°+多個 180°（echo train）加速。[^1]
4. **辨圖**：有無 180° 重聚是關鍵。[^1]
5. **權重**：GRE 翻轉角調權重；SE 固定。[^2]

> [!note] 考點：依RF脈衝圖形判讀MRI序列
> - 僅見重複 **α° 小翻轉角**脈衝、無 180° 重聚 → **Gradient echo**。[^1][^2]
> - 見 **90° + 多個 180°** 重聚脈衝序列 → **Spin echo（Fast Spin Echo 型態）**。[^1]

### 參考來源
[^1]: 官方 2017 詳解；Ref: IMAIOS e-MRI, MRI Sequences: Gradient Echo / Fast Spin Echo（題目所引；accessed 2026-07-03）——GRE 以重複可變小翻轉角(α°)激發、無 RF 重聚、靠梯度反轉產生回訊；SE 以 90°+180° 重聚產生回訊，FSE 於同一 TR 接續多個 180° 產多回訊加速。
[^2]: Gaillard F, et al. *Gradient echo sequences*. Radiopaedia, rID-18339, DOI 10.53347/rID-18339（輔助來源）——GRE 與 spin-echo 之兩大差異：**用梯度場產生橫向磁化**、**翻轉角 <90°**（SE 約 90°，GRE 常 10-80°，以 α 表示）；佐證以「翻轉角 + 有無 180° 重聚」辨識序列。
[^3]: **Tier 1** Plewes DB, Kucharczyk W. *Physics of MRI: a primer*. J Magn Reson Imaging 2012;35(5):1038-54（據 PubMed，DOI [10.1002/jmri.23642](https://doi.org/10.1002/jmri.23642)；Review；基於 ISMRM「MR Physics for Clinicians」課程；實際查證 accessed 2026-07-04）——闡述基本脈衝序列與影像對比之形成：**spin echo 以 90° 激發 + 180° 重聚脈衝重新聚相、抵消靜磁場不均勻之去相位而得真 T2（非 T2\*）；gradient echo 以梯度反轉重聚、可用 <90° 翻轉角縮短 TR 但保留 T2\* 敏感度**；並涵蓋 NMR 弛豫、Fourier transform、梯度空間編碼與 TR/TE/翻轉角對對比之影響。佐證以「有無 180° RF 重聚 + 翻轉角」辨識序列與 T2 vs T2\* 之差異。原「官方/Radiopaedia」弱來源已由本次 PubMed DOI Tier 1 查核升級。

## 題目
> [!question]- 請問下圖RF pulse給予方式屬於何種MRI sequence? (α°重複脈衝、無180度重聚) (2017-089)
> **Gradient echo（B）**——僅見重複可變小翻轉角(α°)脈衝、無 180° 重聚脈衝，回訊靠梯度反轉產生。[^1][^2]

> [!question]- 請問下圖RF pulse給予方式屬於何種MRI sequence? (90°+多個180°脈衝序列) (2017-090)
> **Spin echo（A，Fast Spin Echo 型態）**——90° 激發後接續多個 180° 重聚脈衝，各自產生回訊填入 k-space 不同列。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "mri-pulse-sequence-identification")
```
