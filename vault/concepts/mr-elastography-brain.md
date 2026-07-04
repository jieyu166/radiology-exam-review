---
concepts: [mr-elastography-brain]
name: MR Elastography of the Brain
subspecialty: [NR, Physics]
nonImaging: true
nonImagingReason: "腦部 MR 彈性成像之技術原理與量化硬度應用主題，重點在成像物理而非單一疾病影像判讀。"
aliases:
  - MRE brain
  - MR elastography
  - 磁振彈性成像
dateRev: 2026-07-04
---

# mr-elastography-brain

**MR Elastography（MRE）為「非侵入性（non-invasive）」MRI 技術：以外部驅動器產生 shear wave、經相位對比編碼波速換算組織硬度（stiffness）；NPH 患者腦部硬度「增加」（尤以 occipital lobe 顯著）——「invasive」為錯誤敘述。**

## Summary
- MRE 為**非侵入性**技術：外部被動驅動器（passive driver）將機械振動傳入腦部產生 **shear wave**，以 phase-contrast（相位對比）序列編碼波速；波速正比於組織剪切模數（shear modulus）／硬度。[^1][^2]
- 可**量化腦組織硬度（stiffness）**，用於評估腫瘤硬度、退化性疾病等。[^1][^2]
- **NPH（normal pressure hydrocephalus）**：MRE 顯示腦部（cerebrum）硬度**顯著增加**，於 **occipital lobe（P<.001）**、parietal、temporal lobe 顯著；frontal lobe、深部灰白質、cerebellum 則無顯著差異。[^1]
- 判讀須將 **edge effects、partial volume、CSF contamination** 之影響降至最低（後處理需抗雜訊與邊緣偽影）。[^1]

## 技術要點
- 原理：機械波（shear wave）以壓電/氣動被動驅動器導入 → MRI 以運動編碼梯度（motion-encoding gradient）記錄位移 → 反演（inversion）演算求得硬度圖（elastogram）；屬 phase-contrast MRI 之一應用。[^2]
- 全程於 MRI 掃描內完成，不需穿刺或注射，故為 **non-invasive**（考點：選項「An invasive MRI exam」為錯誤）。[^1][^2]
- 肝臟 MRE（肝纖維化/脂肪肝分期）為最廣泛的臨床應用；腦部 MRE 為較新且研究性較強的應用。[^2]

## 放射科醫師影像判讀重點
- NPH 之 MRE 判讀重點：腦硬度**增加**且以枕葉最明顯，可作為與其他失智鑑別及分流（shunt）療效研究的潛在指標。[^1]
- 量化硬度時須留意 **edge effect / partial volume / CSF contamination** 造成的誤差，採用抗雜訊與邊緣偽影的後處理。[^1]
- MRE 為非侵入性，不涉穿刺或對比劑注射之侵入性風險。[^1][^2]

> [!note] 考點：關於 MR Elastography，何者為錯誤？
> **An invasive MRI exam** 為錯誤——MRE 為**非侵入性**，以外部振動源產生 shear wave 於 MRI 內量測硬度。其餘正確：可偵測 brain stiffness；須將 edge effects/partial volume/CSF contamination 降至最低；NPH 中 MRE 顯示 cerebrum 硬度增加、尤以 occipital lobe。[^1]

### 參考來源
[^1]: Fattahi N, et al. MR Elastography Demonstrates Increased Brain Stiffness in Normal Pressure Hydrocephalus. AJNR Am J Neuroradiol. 2015;37(3):462-7. 據 PubMed，[DOI](https://doi.org/10.3174/ajnr.A4560)（非侵入性 MRE；NPH 於 cerebrum、occipital/parietal/temporal lobe 硬度顯著增加）。
[^2]: Wymer DT, et al. Phase-Contrast MRI: Physics, Techniques, and Clinical Applications. RadioGraphics. 2020;40(1):122-140. 據 PubMed，[DOI](https://doi.org/10.1148/rg.2020190039)（MRE 屬 phase-contrast MRI：shear wave 波速正比於 shear modulus／硬度之原理）。

> [!question]- About MR Elastography, which one is wrong? (2019-334)
> 正確答案 **B**：An invasive MRI exam（錯誤，MRE 為非侵入性）。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "mr-elastography-brain")
```
