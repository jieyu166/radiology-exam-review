---
concepts: [ct-scan-parameters]
name: CT Scan Parameters — Pitch, Speed, Motion Artifact
subspecialty: [RP]
aliases:
  - CT pitch
  - rotation time
  - detector coverage
  - CT motion artifact
  - CT 掃描參數
dateRev: 2026-07-02
---

# ct-scan-parameters

**CT 掃描關鍵參數：Pitch = 每轉一圈床台移動距離 / beam collimation，僅適用於 helical 模式，axial 模式下不需調整。減少 motion artifact 靠加快掃描速度（縮短 rotation time、增加 pitch）。**

## Summary
- **Pitch**：僅適用於 helical 模式，axial 模式下不適用。[^1]
- **Detector Coverage**：axial 與 helical 皆需設定。[^1]
- **Rotation Time**：兩種模式皆需設定。[^1]
- **Motion Artifact**：加快掃描速度（縮短 rotation time）可減少。[^2]

## 放射科醫師影像判讀重點
- **Pitch 只屬 helical、axial 不適用**：pitch = 每轉床台移動距離 / beam collimation，僅 helical（螺旋）模式需設定；axial（步進）模式床台不移動故無 pitch 概念——此為常見選擇題陷阱（axial 模式下不需調 pitch/speed）。[^1]
- **判讀運動假影的來源與對策**：心臟、呼吸、腸蠕動造成的模糊/重影 → 縮短 rotation time、提高 pitch（加快掃描），代價是每圈光子量下降、雜訊上升；迭代重建可在低劑量下抑制雜訊部分補回品質。[^2][^3]
- **高 pitch 的取捨**：提高 pitch 縮短掃描時間、降劑量並減少運動假影，但過高會使 z 軸取樣不足，產生**插值假影與雜訊增加**（速度-品質取捨），判讀薄層/血管檢查時須留意。[^1][^3]
- **雜訊-劑量-對比的參數判讀**：降 mAs 減劑量但增雜訊（tube current modulation 依衰減自動調變最實用）；降 kVp 大幅降劑量並提高碘對比雜訊比（適合血管/對比劑檢查），但胖病人穿透不足、雜訊上升。[^3]
- **劑量指標判讀陷阱**：CTDIvol 與 DLP 是**機器輻射輸出量、非病人實際器官劑量**；SSDE（size-specific dose estimate）依病人體徑校正，較能反映實際劑量，最佳化與報告時應以 SSDE 對照。[^3]

## 技術要點
- **Pitch 的定義與影響**：pitch = 每旋轉一圈床台移動距離 / 束準直(beam collimation)，僅適用於 helical(螺旋)模式；提高 pitch 縮短掃描時間、降劑量並減少運動假影，但過高會使 z 軸取樣不足、增加影像雜訊與插值假影，是速度-品質的取捨。[^1][^3]
- **管電流(mAs)與雜訊-劑量取捨**：劑量與 mAs 近似成正比，降 mAs 減劑量但增影像雜訊；tube current modulation(依病人衰減自動調變 mA)可在維持影像品質下有效降劑量，是最實用的降劑量參數之一。[^3]
- **管電壓(kVp)**：降低 kVp 大幅降劑量並提高碘對比雜訊比(適合血管/對比劑檢查)，但在較胖病人會使穿透不足、雜訊上升，須依體型選擇。[^3]
- **旋轉時間與運動假影**：縮短 rotation time(加快掃描)可減少心臟/呼吸等運動假影，代價是每圈光子量下降、雜訊上升；迭代重建(iterative reconstruction)可在低劑量下抑制雜訊、部分補回品質。[^2][^3]
- **劑量指標判讀**：CTDIvol 與 DLP 為機器輻射輸出量、非個別病人實際器官劑量；size-specific dose estimate(SSDE)依病人體徑校正，較能反映實際劑量，報告與最佳化時應以 SSDE 對照。[^3]

## 陷阱
- axial 模式下 Pitch & Speed 不需調整。[^1]

### 參考來源
[^1]: 2019 交換考詳解；GE Lightspeed VCT 操作介面。
[^2]: 2019 交換考詳解；GE Lightspeed CT console。
[^3]: **Tier 1** Litmanovich DE, Tack DM, Shahrzad M, Bankier AA. *Dose reduction in cardiothoracic CT: review of currently available methods.* RadioGraphics 2014;34(6):1469-1489（據 PubMed，DOI [10.1148/rg.346140084](https://doi.org/10.1148/rg.346140084)；實際查證 accessed 2026-07-04）——系統整理影響 CT 劑量與影像品質的掃描參數：管電流調變、管電壓、pitch、旋轉時間、掃描長度、迭代重建與雜訊抑制，並說明 CTDIvol/DLP 為輸出量、SSDE 較能反映個別病人劑量；提供在維持影像品質下降劑量的實務取捨。原「官方詳解/GE console」弱來源已由本次 DOI Tier 1 查核升級。

## 考題
```dataview
list from #交換 where contains(concepts, "ct-scan-parameters")
```
