---
concepts: [dbt-artifact]
name: Digital Breast Tomosynthesis (DBT) Artifacts
subspecialty: [Breast, Physics]
nonImaging: true
nonImagingReason: "數位乳房斷層攝影之成像物理與偽影主題，重點在技術原理而非單一疾病影像判讀。"
aliases:
  - DBT 偽影
  - tomosynthesis artifact
  - 乳房斷層攝影偽影
dateRev: 2026-07-04
---

# dbt-artifact

**DBT 四大偽影中，motion artifact 因固有的 out-of-plane blurring 具「遮蔽效應（masking effect）」而最不易被察覺；blurring-ripple、truncation、loss of skin and superficial tissue resolution 則相對可辨識。**

## Summary
- **Blurring-ripple artifact**：高對比物體（如金屬、緻密鈣化）沿 z 軸方向於相鄰重建切面殘留漣漪狀影，源自有限角度取樣與重建。[^1][^2]
- **Truncation artifact**：因有限掃描角度／偵測器邊界，視野邊緣組織資訊被截斷。[^1][^2]
- **Loss of skin and superficial tissue resolution**：淺層（皮膚/皮下）組織在斷層重建中解析度下降。[^1]
- **Motion artifact**：因 DBT 固有的 out-of-plane blurring 之遮蔽效應，動作模糊**難以辨識（rarely appreciated）**——即考點所在。[^1]

## 技術要點
- DBT 以有限角度（limited sweep angle）掃描並重建三維切面：**sweep angle 越寬 → out-of-plane（z 軸）解析度越佳**（利於腫塊與結構扭曲）；**投影張數越多 → in-plane（x-y）解析度越佳**（利於微鈣化）。[^1]
- **連續管球運動（continuous tube motion）**縮短取像時間但造成 focal spot blurring；step-and-shoot 則較無此問題。[^1]
- 有限角度取樣造成物件取樣不完整（incomplete sampling），是 blurring-ripple 與 truncation 等偽影的物理根源。[^2]

## 放射科醫師影像判讀重點
- 認識偽影來源可避免把 blurring-ripple 誤判為病灶、或把 truncation 邊緣誤讀為異常，藉此**降低召回率與偽陽性**。[^2]
- Motion artifact 因被 out-of-plane blurring 遮蔽而不易察覺，判讀時對可疑動作模糊的個案應留意品質，必要時重照。[^1]
- 定期品管（QC）與 ALARA 劑量管理為維持 DBT 影像品質之基礎。[^1]

> [!note] 考點：DBT 的下列偽影中，哪一項因 out-of-plane blurring 的遮蔽效應而「很少被察覺」？
> **Motion artifacts**。RadioGraphics 明載「Motion artifacts are difficult to recognize because of inherent out-of-plane blurring」；其餘 blurring-ripple、truncation、loss of skin and superficial tissue resolution 相對可辨識。[^1]

### 參考來源
[^1]: Tirada N, et al. Digital Breast Tomosynthesis: Physics, Artifacts, and Quality Control Considerations. RadioGraphics. 2019;39(2):413-426. 據 PubMed，[DOI](https://doi.org/10.1148/rg.2019180046)（原文：「Motion artifacts are difficult to recognize because of inherent out-of-plane blurring」）。
[^2]: Sujlana PS, et al. Digital breast tomosynthesis: Image acquisition principles and artifacts. Clin Imaging. 2018;55:188-195. 據 PubMed，[DOI](https://doi.org/10.1016/j.clinimag.2018.07.013)（DBT 有限角度取樣造成之偽影物理與辨識）。

> [!question]- Regarding DBT artifacts, which one is rarely appreciated because of the masking effect of out-of-plane blurring? (2019-388)
> 正確答案 **D**：Motion Artifacts。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "dbt-artifact")
```
