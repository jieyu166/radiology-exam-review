---
concepts: [gre-hemorrhage-detection]
name: Gradient Echo — Superior Hemorrhage Detection
subspecialty: [NR, Physics]
aliases:
  - gradient echo hemorrhage
  - GE sequence blood sensitivity
  - susceptibility effect hemorrhage
  - 顱內出血MRI波序偵測
dateRev: 2026-07-02
---

# gre-hemorrhage-detection

**梯度回波(Gradient Echo, GE)波序因無180度重聚脈衝，對磁場不均勻性（如出血產物之順磁性代謝物造成的磁化率效應）較敏感，故對顱內出血性病灶之偵測效率優於Spin Echo(SE)或Turbo Spin Echo(TSE)。**

## Summary
- **GE 無重聚脈衝**：GE波序不使用180度重聚脈衝（SE/TSE皆使用），故無法補償局部磁場不均勻性造成的訊號失真(dephasing)。[^1]
- **對出血敏感之機轉**：出血產物（如deoxyhemoglobin、hemosiderin、ferritin）具**順磁性**，會造成局部磁場不均勻(磁化率效應/susceptibility effect)；GE因無重聚脈衝，此不均勻性造成之訊號丟失（blooming）被放大並於影像上呈現為明顯低訊號，故對微出血/出血病灶之偵測**較SE/TSE敏感**。[^1]
- **臨床應用延伸**：此原理亦為SWI(susceptibility weighted imaging)之基礎——SWI即以GRE波序為基礎，進一步利用相位資訊放大磁化率效應，對微出血偵測更為敏感。

> [!note] 考點：何種MR波序對顱內出血性病灶偵測效率較佳？
> **Gradient echo（GE，C）**——GE無180度重聚脈衝，對磁化率效應（出血代謝物之順磁性）較敏感，故偵測出血病灶效率優於SE/TSE。[^1]

### 參考來源
[^1]: 官方2020詳解；Ref: MRI IN PRACTICE, Ch.2, p.34（題目所引）——GE波序無重聚脈衝，對磁場不均勻性（如出血之順磁性代謝物）較敏感，偵測顱內出血效率優於SE/TSE。

## 題目
> [!question]- 在磁振造影中，下列何種波序在針對顱內出血性病灶有較佳的偵測效率? (2020-336)
> **Gradient echo（GE，C）**——GE無重聚脈衝，對磁化率效應較敏感，偵測出血病灶效率優於SE/TSE。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "gre-hemorrhage-detection")
```
