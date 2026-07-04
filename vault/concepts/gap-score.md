---
concepts: [gap-score]
name: GAP Score (IPF/ILD Prognosis)
subspecialty: [CH]
aliases:
  - GAP score
  - CT-GAP score
  - ILD prognosis
  - 肺纖維化預後評分
dateRev: 2026-06-30
nonImaging: true
nonImagingReason: "GAP score 為 IPF/ILD 臨床預後評分（Gender＋Age＋Physiology：FVC%、DLCO%），由人口學與肺功能數值換算 stage I–III 與死亡率，本質無影像判讀特徵；CT-GAP 變體雖納入 CT 纖維化評分，但僅為次要延伸且檔內已涵蓋，核心概念不可作影像補強。"
same:
  - "[[ipf]]"
---

# gap-score

**GAP score 用三個字母記住 IPF 預後工具：G = Gender（男性較差）、A = Age（越老越差）、P = Physiology，即 FVC% 與 DLCO% 兩項肺功能；分三個 stage 預測 1/2/3 年死亡率。** 判讀分水嶺一：**P 涵蓋兩項生理值（FVC + DLCO），缺一不完整。** 判讀分水嶺二：**CT-GAP 以 CT 纖維化程度評分補強，於 DLCO 無法取得或進展期時預測稍佳。**

## Summary
- **GAP score 變數**：[^1]
  - **G**ender（性別,男性風險高）;
  - **A**ge（年齡）;
  - **P**hysiology：**FVC%** 與 **DLCO%**（兩項肺功能）。
  - 總分對應 **stage I/II/III** 與遞增的 1/2/3 年死亡率。
- **CT-GAP**：以 **CT 纖維化程度評分**納入,於部分情境（如 DLCO 不可得、stage 3 後）預測表現稍佳。[^2]
- **用途**：半定量、簡便的預後分層工具;ILD 評估常與影像進展 marker（[[pulmonary-fibrosis-signs|traction bronchiectasis]]）併用。[^2]

## 技術要點
- **四變數兩生理值**：GAP＝**G**ender（男性風險高）＋**A**ge（年齡）＋**P**hysiology；P 涵蓋 **FVC%** 與 **DLCO%** 兩項肺功能，**缺一不完整**（常見陷阱：以為 P 只有單一肺功能值）。[^1]
- **點數分期與死亡率**：GAP index 為簡易點數評分，分 **stage I / II / III**，**1 年死亡率約 6% / 16% / 39%**，並對應遞增之 2、3 年死亡率。[^1]
- **DLCO 缺值處理**：DLCO 常因病人無法配合而缺值；此時 **CT-GAP** 以 CT 纖維化程度評分替代肺功能，於 DLCO 不可得或進展期（stage 3 後）預測表現稍佳。[^2]
- **半定量預後工具定位**：GAP 為簡便、可床邊計算的預後分層工具，適合門診分層與研究族群比較，非診斷 IPF 之依據。[^1]
- **與影像 marker 併用**：ILD 評估常將 GAP 與影像進展指標（如 [[pulmonary-fibrosis-signs|traction bronchiectasis]]、纖維化範圍變化）併用，提升預後判讀。[^2]

> [!note] 考點
> **GAP＝Gender＋Age＋Physiology(FVC、DLCO)**,分 stage I–III 預測死亡率;CT-GAP 加 CT 纖維化評分。[^1]

### 參考來源
[^1]: Ley B et al. *A Multidimensional Index and Staging System for Idiopathic Pulmonary Fibrosis*（GAP model）. Ann Intern Med 2012;156(10):684-691（據 PubMed，DOI [10.7326/0003-4819-156-10-201205150-00004](https://doi.org/10.7326/0003-4819-156-10-201205150-00004)；PMID 22586007；實際查證 accessed 2026-07-05）：GAP＝Gender、Age、2 lung physiology variables（FVC、DLCO）;GAP index 為簡易點數評分，分 stage I/II/III，**1 年死亡率分別約 6%、16%、39%**；derivation/validation c-index 約 68–71。（**provenance**：本概念整合自演講筆記《Imaging for ILD》吳銘庭 2021-01-23。）
[^2]: CT-GAP 文獻（以 CT 纖維化分級納入 GAP）：於 DLCO 缺值或進展期預測稍佳;半定量預後工具。

## 考題
```dataview
list from #交換 where contains(concepts, "gap-score")
```
