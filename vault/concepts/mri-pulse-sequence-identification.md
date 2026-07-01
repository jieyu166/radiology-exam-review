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
dateRev: 2026-07-01
---

# mri-pulse-sequence-identification

**依RF脈衝圖形辨識MRI序列的關鍵：只用「小於90度的可變翻轉角(α°)」重複激發、無180度重聚脈衝者為Gradient echo；每個TR週期以「90度激發+一個或多個180度重聚」脈衝組成者為Spin echo（多個180度重聚脈衝＝Fast/Turbo spin echo變化型）。** 判讀分水嶺：**Gradient echo僅用梯度反轉造成回訊、無RF重聚脈衝，翻轉角可調（常<90度）以縮短TR、加快掃描;Spin echo必有180度RF重聚脈衝以抵消磁場不均勻造成的去相位，經典型為單一90度+單一180度，Fast Spin Echo則在同一TR內接續多個180度脈衝、產生多個回訊填入k空間不同列以加速掃描。**

## Summary
- **Gradient echo（GRE）辨識特徵**：RF脈衝圖僅顯示重複的**α°（可變、常小於90度）**激發脈衝，**無180度重聚脈衝**；回訊靠梯度反轉（非RF重聚）產生，翻轉角越小可縮短TR、加快掃描速度但訊噪比較低。[^1]
- **Spin echo（SE）辨識特徵**：每個TR週期內可見**90度激發脈衝**接續一個或多個**180度重聚脈衝**；180度脈衝用以抵消靜磁場不均勻造成的自旋去相位，產生回訊(echo)。[^2]
- **Fast/Turbo spin echo（FSE/TSE）**：在單一90度激發脈衝後，接續**多個180度重聚脈衝**（如圖示90°-180°-180°-180°...），每個180度脈衝產生一個回訊、分別填入k空間不同相位編碼列，大幅縮短掃描時間。[^2]

> [!note] 考點：依RF脈衝圖形判讀MRI序列
> - 僅見重複**α°小翻轉角**脈衝、無180度重聚 → **Gradient echo**。[^1]
> - 見**90度+多個180度**重聚脈衝序列 → **Spin echo（Fast Spin Echo型態）**。[^2]

### 參考來源
[^1]: 官方 2017 詳解；IMAIOS, MRI Sequences: Gradient Echo (https://www.imaios.com/en/e-Courses/e-MRI/MRI-Sequences/gradient-echo)：Gradient echo以重複可變小翻轉角(α°)脈衝激發、無RF重聚脈衝，靠梯度反轉產生回訊。
[^2]: 官方 2017 詳解；IMAIOS, MRI Sequences: Fast Spin Echo (https://www.imaios.com/en/e-Courses/e-MRI/MRI-Sequences/Fast-Spin-Echo)：Spin echo以90度激發+180度重聚脈衝產生回訊，Fast/Turbo Spin Echo於同一TR內接續多個180度脈衝產生多個回訊加速掃描。

## 題目
> [!question]- 請問下圖RF pulse給予方式屬於何種MRI sequence? (α°重複脈衝、無180度重聚) (2017-089)
> **Gradient echo（B）**——僅見重複可變小翻轉角(α°)脈衝、無180度重聚脈衝，回訊靠梯度反轉產生。[^1]

> [!question]- 請問下圖RF pulse給予方式屬於何種MRI sequence? (90°+多個180°脈衝序列) (2017-090)
> **Spin echo（A，Fast Spin Echo型態）**——90度激發後接續多個180度重聚脈衝，各自產生回訊填入k空間不同列。[^2]

## 考題
```dataview
list from #交換 where contains(concepts, "mri-pulse-sequence-identification")
```
