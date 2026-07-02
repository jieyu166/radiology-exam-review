---
concepts: [ct-image-quality-parameters]
name: CT Image Quality — Low Contrast, Noise & Spatial Resolution
subspecialty: [Physics, CT]
aliases:
  - CT low contrast detectability
  - CT noise SNR
  - CT image quality parameters
  - 電腦斷層影像品質
dateRev: 2026-07-02
nonImaging: true
nonImagingReason: "CT影像品質物理參數（低對比/雜訊/解析度取捨），非影像判讀"
---

# ct-image-quality-parameters

**CT低對比度偵測靠「降低雜訊」——增加切片厚度是唯一能同時提高SNR、改善低對比度的選項；反直覺的是它會犧牲空間解析度。降mAs、用銳利骨核心、縮小FOV都會增加雜訊或只改善空間解析度，反而傷害低對比度。記憶鉤：低對比＝比雜訊，厚切片壓雜訊、薄切片看細節。**

## Summary
- **CT signal-to-noise ratio（SNR）影響因子**：mAs（增加mAs提升SNR）、切片厚度（較厚切片提升SNR）、病人體型（體型越大SNR越低）。[^1]
- **提高低對比度（low contrast detectability）之方式**：**增加重組切片厚度（slice thickness）**——較厚切片減少雜訊、提升SNR，從而改善低對比度偵測（代價為空間解析度變差、partial volume artifact）。[^1]
- **降低低對比度（傷害）之方式**：[^1]
  - **降低mAs**：減少光子數→增加雜訊→低對比度變差。
  - **使用bone algorithm（銳利核心）取代soft tissue algorithm**：高解析度銳利核心不平滑高頻訊號→增加雜訊→低對比度變差（但空間解析度較佳）。
  - **縮小掃描照野（scan FOV）**：主要改善**橫軸空間解析度（transaxial resolution）**，非改善低對比度。

> [!note] 考點：何種方式調整掃描參數可能「提高」CT影像之低對比度？
> **增加重組切片厚度（slice thickness）（C）**——較厚切片減少雜訊、提升SNR，改善低對比度偵測。降低mAs(A)增加雜訊、使用bone algorithm(B)增加雜訊、縮小FOV(D)僅改善橫軸空間解析度，皆不改善低對比度。[^1]

### 參考來源
[^1]: Bushberg JT et al. *The Essential Physics of Medical Imaging*, Lippincott Williams & Wilkins, 2011, p.366（2018 交換考題詳解 p.254 引用；Tier 2 教科書）。CT SNR受mAs（增加提升SNR）、切片厚度（增厚提升SNR）、病人體型（增大降SNR）影響；增加切片厚度提升SNR、改善低對比度（代價空間解析度）；高解析度銳利核心增加雜訊；縮小FOV改善橫軸空間解析度而非低對比度。

## 題目
> [!question]- 以下列何種方式調整掃描參數可能提高電腦斷層掃描影像之低對比度 (low contrast)? (2018-113)
> **增加重組切片厚度 (slice thickness)（C）**——較厚切片減少雜訊、提升SNR，改善低對比度偵測。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "ct-image-quality-parameters")
```
