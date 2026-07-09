---
concepts: [dce-mri-perfusion]
name: Dynamic Contrast-Enhanced (DCE) MR Perfusion
subspecialty: [Physics]
aliases:
  - DCE-MRI
  - dynamic contrast enhanced MRI
  - permeability MRI
  - time-signal intensity curve
  - 動態顯影劑加強磁振造影
dateRev: 2026-07-06
---

# dce-mri-perfusion

**DCE-MRI 的時間-訊號強度曲線（time–signal intensity curve）反映的是「組織灌流／血管通透性（perfusion / permeability）」，而非氧合、代謝或細胞密度——它利用釓對比劑通過組織所造成的 T1 縮短效應，連續取像後以曲線描繪對比劑進出組織的速率。判讀分水嶺：DCE＝T1-based，量的是「血流＋血管通透」；氧合看 BOLD、代謝看 FDG-PET/MRS、細胞密度看 DWI/ADC。**

## Summary
- **DCE-MRI 曲線＝組織灌流／通透**：以 3D T1 加權快速梯度回波序列在釓對比劑注射前後連續重複取像，量測每個像素隨時間的訊號變化，形成 time–signal intensity curve；此曲線反映對比劑經血流進入並外滲至組織間隙的過程，即**灌流（perfusion）與血管通透性（permeability）**。[^1][^2]
- **原理為 T1 縮短**：釓對比劑通過組織時造成 T1 縮短，訊號上升；曲線的上升斜率、達峰時間、洗出型態即代表對比劑動力學。[^1]
- **藥物動力學參數**：以 compartmental model 擬合曲線可導出 **K^trans（容積轉移常數，反映血流＋通透）**、v_e、v_p、以及 wash-in/wash-out 半定量指標。[^1]
- **本題辨析**：**氧合 → BOLD/fMRI；代謝活性 → FDG-PET 或 MRS；細胞密度 → DWI/ADC**；只有**灌流（B）**才是 DCE-MRI 時間-訊號曲線所代表的參數。[^1][^2]

## 放射科醫師影像判讀重點
- **惡性曲線型態**：初期快速強化（rapid wash-in）＋隨後 washout（type 3）較偏惡性；plateau（type 2）中間；persistent 漸升（type 1）偏良性——常用於乳房、攝護腺 mpMRI 判讀。[^1][^2]
- **與 DSC 區別**：DCE 為 **T1-based**（量灌流＋通透，時間解析度較低、可做定量藥動模型）；DSC（dynamic susceptibility contrast）為 **T2\*-based**（量腦部 CBV/CBF，適合腦腫瘤／缺血）。[^1]
- **臨床應用**：攝護腺 PI-RADS DCE 分項、乳房病灶動力學、腦腫瘤血管通透性（K^trans）、以及腫瘤抗血管治療反應評估。[^1][^2]
- **陷阱**：DCE 需高時間解析度與可靠 AIF（arterial input function）；定量 K^trans 受序列、模型與後處理影響，跨中心比較須謹慎。[^1]

### 參考來源
[^1]: *Dynamic contrast enhanced (DCE) MR perfusion*. Radiopaedia.org（實際查證 accessed 2026-07-06）：DCE 依賴釓對比劑之 T1 縮短效應，於注射前後連續 3D T1 加權取像產生時間-訊號強度曲線，反映對比劑通過組織之灌流／通透；藥動模型可導出 K^trans、v_e、v_p 等區域性參數。另 *Breast MRI*．Radiopaedia.org（accessed 2026-07-06）：DCE-MRI 提供病灶形態與功能（動力學）資訊、乳房 MRI 敏感度 >90%。
[^2]: **Tier 1** Mann RM, Kuhl CK, Moy L. *Breast MRI: State of the Art*. Radiology 2019;292(3):520-536, DOI 10.1148/radiol.2019182947（實際查證 accessed 2026-07-06）：DCE-MRI 為乳房 MRI 判讀核心，動態強化曲線（wash-in/wash-out）反映腫瘤血管灌流與通透性，用以區分良惡性；氧合（BOLD）、代謝（MRS/PET）、細胞密度（DWI）為不同對比機轉。

## 題目
> [!question]- Which of the following is represented by the time-signal intensity curve in dynamic contrast-enhanced magnetic resonance imaging (DCE-MRI)? A:Tissue Oxygenation B:Tissue perfusion C:Tissue metabolic activity D:Tissue cellularity (2022-424)
> **B（關鍵）Tissue perfusion（組織灌流／血管通透）**——DCE-MRI 利用釓對比劑之 T1 縮短效應連續取像，時間-訊號強度曲線描繪對比劑經血流進入並外滲至組織的動力學，代表灌流與通透性（可導出 K^trans）。氧合以 BOLD/fMRI 評估、代謝活性以 FDG-PET/MRS 評估、細胞密度以 DWI/ADC 評估，皆非此曲線所代表。[^1][^2]

## 考題
```dataview
list from #交換 where contains(concepts, "dce-mri-perfusion")
```
