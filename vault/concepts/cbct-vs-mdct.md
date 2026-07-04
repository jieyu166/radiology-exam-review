---
concepts: [cbct-vs-mdct]
name: Cone Beam CT vs MDCT
subspecialty: [Physics]
nonImaging: true
nonImagingReason: "CBCT 與 MDCT 之成像物理比較主題，重點在硬體/幾何與解析度差異而非單一疾病影像判讀。"
aliases:
  - CBCT
  - cone beam CT
  - 錐狀束電腦斷層
dateRev: 2026-07-04
---

# cbct-vs-mdct

**CBCT 相較 MDCT：具較高空間解析度、可用較低劑量顯示高對比結構（骨/牙/顳骨/副鼻竇），但因單次緩慢旋轉取像而「時間解析度較低」、重建時間較長、散射偽影較多——「higher temporal resolution」為錯誤敘述。**

## Summary
- CBCT 使用**錐狀 X 光束＋平板偵測器（flat panel detector）**、單次旋轉取得容積資料，設計目的為以**相對低劑量、高空間解析度**顯示高對比結構（骨骼、牙齒）。[^1]
- 相較 MDCT：**空間解析度較高**、對高對比骨性結構之等向性（isotropic）解析度佳。[^1][^2]
- **時間解析度較低**：單次緩慢旋轉、取像時間較長，不利動態/心臟等時間敏感研究——考點所在（「higher temporal resolution」為錯誤）。[^1]
- **散射偽影（scatter artifact）較多**（錐狀束幾何）、重建時間較長；低對比偵測能力（low-contrast detectability）不如 MDCT。[^1]

## 技術要點
- 幾何差異：CBCT 為錐狀束＋2D 平板偵測器、單次旋轉即涵蓋整個 FOV；MDCT 為扇狀束＋多排偵測器、快速螺旋掃描。[^1]
- **散射（scatter）**是 CBCT 影像品質的主要限制，直接壓低低對比偵測能力，並增加偽影；文獻討論多種散射抑制方法。[^1]
- 臨床定位：CBCT 適用牙科、顳骨/副鼻竇等高對比骨性結構與介入導引；因低對比與時間解析度限制，**不應取代 conventional CT** 作全面評估。[^2][^3]

## 放射科醫師影像判讀重點
- 判讀 CBCT 須知其**低對比軟組織評估能力有限**：軟組織病變、實質器官細節仍應以 MDCT 為準。[^1][^2]
- CBCT 大 FOV 常見**偶然發現（incidental findings）**（如上頜竇滯留囊腫、鼻竇炎、頸動脈鈣化等），影像應由具資格者判讀。[^3]
- 對高對比骨/牙結構，CBCT 的高空間解析度為其優勢，但時間解析度低使其不適合動態掃描。[^1]

> [!note] 考點：關於 Cone Beam CT（CBCT）與 MDCT 相比，何者為錯誤？
> 錯誤者為 **Higher temporal resolution**——CBCT 的時間解析度**低於** MDCT（單次緩慢旋轉、取像時間長）。其餘正確：higher spatial resolution、longer reconstruction time、more scatter artifact。[^1]

### 參考來源
[^1]: Miracle AC, Mukherji SK. Conebeam CT of the head and neck, part 1: physical principles. AJNR Am J Neuroradiol. 2009;30(6):1088-95. 據 PubMed，[DOI](https://doi.org/10.3174/ajnr.A1653)（原文：CBCT 提供「relatively low-dose high-spatial-resolution visualization of high-contrast structures」；討論散射與低對比偵測限制）。
[^2]: Miracle AC, Mukherji SK. Conebeam CT of the head and neck, part 2: clinical applications. AJNR Am J Neuroradiol. 2009;30(7):1285-92. 據 PubMed，[DOI](https://doi.org/10.3174/ajnr.A1654)（副鼻竇/顳骨/顱顏之臨床應用與 CBCT 適用範圍）。
[^3]: Dief S, et al. A systematic review on incidental findings in cone beam computed tomography (CBCT) scans. Dentomaxillofac Radiol. 2019;48(7):20180396. 據 PubMed，[DOI](https://doi.org/10.1259/dmfr.20180396)（CBCT 不應取代 conventional radiographs；偶然發現頻率高）。

> [!question]- 關於 Cone beam CT (CBCT) 與 MDCT 相比，何者為錯誤？ (2019-344)
> 正確答案 **2**：Higher temporal resolution（錯誤，CBCT 時間解析度較低）。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "cbct-vs-mdct")
```
