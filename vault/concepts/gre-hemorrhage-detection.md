---
concepts: [gre-hemorrhage-detection]
name: Gradient Echo — Superior Hemorrhage Detection
subspecialty: [NR, Physics]
aliases:
  - gradient echo hemorrhage
  - GRE blooming
  - susceptibility weighted imaging
  - SWI
  - 顱內出血MRI波序偵測
dateRev: 2026-07-03
---

# gre-hemorrhage-detection

**梯度回波（Gradient Echo, GRE）以「梯度反轉」而非「180° 重聚脈衝」形成回波，故不補償靜態磁場不均勻——出血產物之順磁性代謝物造成的磁化率效應（susceptibility）被完整表現為訊號丟失/blooming，因此偵測顱內出血優於 Spin Echo（SE）/Turbo Spin Echo（TSE）。SWI 更以 GRE 為基礎、加用相位資訊，對微出血最敏感。** 判讀分水嶺：**GRE/SWI 上的低訊號 blooming ＝順磁性血產物（deoxyHb/methemoglobin/hemosiderin/ferritin）；SE/TSE 的 180° 重聚會把靜態不均勻「補回去」，故對出血較不敏感。**

## Summary
- **GRE 無 180° 重聚**：GRE 僅用梯度反轉形成回波（SE/TSE 用 180° RF 重聚），**無法補償局部靜態磁場不均勻**，影像權重帶 **T2\*** 特性。[^1]
- **對出血敏感之機轉**：血產物（**deoxyhemoglobin、ferritin、hemosiderin**、細胞內 methemoglobin）具**順磁性**，造成局部磁化率（susceptibility）不均 → GRE 無重聚，dephasing 不被補償 → 呈明顯低訊號並 **blooming（放大）**，故偵測微出血/出血較 SE/TSE 敏感。[^1][^2]
- **SWI 延伸**：SWI ＝**以 GRE 為基礎之 3D 高解析、速度校正序列**，同時利用**相位 + 強度**並經 high-pass filter 後處理放大磁化率效應，對**微出血最敏感**；相位資訊亦可**區分鈣化（反磁性）與血產物（順磁性）**。[^2][^3]
- **T2\* 加權參數與其他應用**：**GRE 以「低翻轉角、長 TE、長 TR」使影像偏 T2\* 加權**；T2\*-based 對比為多種應用之基礎——**SWI、灌注 MR（gadolinium 通過微血管致訊號下降）、功能性 MR（BOLD 效應）、鐵過載影像**。[^3]

## 放射科醫師影像判讀重點
- **blooming 徵象**：小出血在 GRE/SWI 上因 dephasing 而看起來比實際大 → 提高偵測率，但**會高估病灶大小**。[^1][^2]
- **序列選擇**：懷疑微出血（CAA、高血壓、DAI）、海綿狀血管瘤、出血性轉移 → 加做 GRE 或 SWI。[^2]
- **SE/TSE 為何較不敏感**：180° 重聚脈衝把靜態磁場不均勻重新相位化，抑制了磁化率效應，故對慢性血產物（hemosiderin）較不顯。[^1]
- **鈣 vs 血**：兩者於 GRE 皆可低訊號 blooming；**SWI 相位圖**可分辨（鈣化反磁性、血產物順磁性，相位方向相反，惟依製造商相位慣例）。[^2]
- **陷阱**：GRE/SWI 對磁化率極敏，顱底/氣骨界面之偽影亦明顯，勿誤判為出血。[^2]

## 臨床重點（5 句）
1. **一句話**：要找出血/微出血，選 GRE 或 SWI（T2\* 加權），別只靠 SE/TSE。[^1][^2]
2. **機轉核心**：GRE 無 180° 重聚 → 磁化率效應不被補償 → 順磁性血產物 blooming。[^1]
3. **SWI 最敏感**：GRE 基礎 + 相位資訊，偵測微出血優於一般 GRE。[^2]
4. **臨床用途**：CAA/高血壓微出血、DAI、海綿狀血管瘤、出血性轉移之偵測與分佈評估。[^2]
5. **判讀提醒**：blooming 會放大病灶、且鈣血需靠相位分辨，界面偽影勿誤判。[^2]

> [!note] 考點：何種MR波序對顱內出血性病灶偵測效率較佳？
> **Gradient echo（GRE，C）**——GRE 無 180° 重聚脈衝，對磁化率效應（出血代謝物之順磁性）較敏感，偵測出血病灶效率優於 SE/TSE（SWI 以 GRE 為基礎更敏感）。[^1][^2]

### 參考來源
[^1]: 官方 2020 詳解；Ref: MRI in Practice, Ch.2, p.34（題目所引）——GRE 波序無 180° 重聚脈衝、對磁場不均勻（出血之順磁性代謝物）較敏感，偵測顱內出血優於 SE/TSE。此物理原理與下述一手來源一致。
[^2]: *Susceptibility weighted imaging*. Radiopaedia.org, rID-13858, DOI 10.53347/rID-13858（輔助來源）——SWI 為對「扭曲局部磁場之化合物」特別敏感之 MRI 序列，利於偵測**血產物、鈣化**；為 **3D 高解析、velocity-corrected gradient-echo** 序列，利用**相位 + 強度** + 後處理；順磁性化合物含 **deoxyhemoglobin、ferritin、hemosiderin**。
[^3]: **Tier 1（開放取用）** Chavhan GB, Babyn PS, Thomas B, Shroff MM, Haacke EM. *Principles, techniques, and applications of T2\*-based MR imaging and its special applications*. RadioGraphics 2009;29(5):1433-1449（據 PubMed，DOI [10.1148/rg.295095034](https://doi.org/10.1148/rg.295095034)，PMC2799958，實際查證 accessed 2026-07-03）——**T2\* relaxation ＝自旋-自旋弛豫＋磁場不均勻所致橫向磁化衰減，「僅見於 GRE」，因 SE 之 180° 脈衝消除磁場不均勻造成的橫向弛豫**；GRE 以低翻轉角/長 TE/長 TR 使影像偏 T2\* 加權；**T2\*-weighted GRE 用以顯示出血、鈣化、鐵沉積**；**SWI 利用相位＋T2\* 對比開發血/鐵/鈣之磁化率差異**；T2\* 基礎另用於灌注 MR、BOLD 功能性 MR、鐵過載影像。原「官方 2020 詳解（題目所引）」弱來源已由本 Tier 1 RadioGraphics 全文查核升級。

## 題目
> [!question]- 在磁振造影中，下列何種波序在針對顱內出血性病灶有較佳的偵測效率? (2020-336)
> **Gradient echo（GRE，C）**——GRE 無重聚脈衝、對磁化率效應較敏感，偵測出血病灶效率優於 SE/TSE。[^1][^2]

## 考題
```dataview
list from #交換 where contains(concepts, "gre-hemorrhage-detection")
```
