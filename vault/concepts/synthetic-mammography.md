---
concepts: [synthetic-mammography]
name: Synthetic Mammography (SM)
subspecialty: [Breast, Physics]
nonImaging: true
nonImagingReason: "合成乳房攝影之影像重建技術與優缺點主題，重點在成像原理而非單一疾病影像判讀。"
aliases:
  - SM
  - synthesized 2D mammogram
  - 合成乳房攝影
dateRev: 2026-07-04
---

# synthetic-mammography

**Synthetic Mammography（SM）由 DBT 資料重建為 2D 影像，取代額外的 FFDM 取像故「不需額外輻射劑量」；優點含降低總劑量、縮短檢查時間、提升鈣化/星芒緣/結構扭曲之顯著度；缺點為 pseudocalcification 偽陽性與動作偽影評估困難。**

## Summary
- SM 為由 DBT 切面重建的 2D 影像，**取代 FFDM，不需額外 radiation exposure**；SM+DBT 組合較 FFDM+DBT 組合可降低約一半劑量。[^1][^2]
- **優點**：reduced radiation dose、較 FFDM/DBT 併用**縮短取像時間**、提升 calcifications/spiculated margins/architectural distortion 之 conspicuity（顯著度）。[^1]
- **缺點/偽影**：blurring subcutaneous tissue、MLO 上 axilla 解析度下降、**pseudocalcifications（偽鈣化，可致偽陽性）**、foreign body 附近解析度下降、以及 motion artifact 評估困難。[^1]
- 臨床效能：SM 取代 2D DM 併用 DBT 時，仍維持 DBT 之降低召回率、提升癌症偵測率與相近之陽性預測值（PPV）。[^1]

## 技術要點
- SM 由 DBT 三維資料以重建演算法投影合成 2D 影像，**免除單獨 FFDM 取像 → 降低組合檢查之總輻射劑量**（以 SM 取代 FFDM，DBT+SM 相對 DBT+FFDM 劑量約減半）。[^1][^2]
- 已獲 FDA 核准，且與 DBT 併用時被證實對 FFDM 為 non-inferior。[^1]
- 與 2D DM 的關鍵差異：影像「取得方式（合成而非直接曝照）」、乳腺密度評估、以及鈣化等表現的可視化。[^1]

## 放射科醫師影像判讀重點
- 判讀 SM 時須辨識 **pseudocalcification**：合成過程可能產生類鈣化亮點，勿誤判為真鈣化而造成偽陽性召回。[^1]
- MLO 上腋窩區與異物（foreign body）周邊解析度較 FFDM 差，皮下組織可能模糊——評估這些區域須謹慎。[^1]
- 動作偽影於 SM 上不易評估，品質存疑時對照 DBT 切面或重照。[^1]

> [!note] 考點：關於由 DBT 重建之 Synthetic Mammography（SM），下列敘述何者正確？
> A–D 皆正確（故選 E「All of the above」/或在另一版本選「以上皆非為錯誤」對應之 D）：SM 不需額外輻射曝露；偽影含 blurring subcutaneous tissue、MLO axilla 解析度下降、pseudocalcifications、foreign body 附近解析度下降；優點含降低劑量、縮短時間、提升鈣化/星芒緣/結構扭曲顯著度；缺點含 pseudocalcification 偽陽性與 motion artifact 評估困難。[^1]

### 參考來源
[^1]: Chikarmane SA. Synthetic Mammography: Review of Benefits and Drawbacks in Clinical Use. J Breast Imaging. 2022;4(2):124-134. 據 PubMed，[DOI](https://doi.org/10.1093/jbi/wbac008)（SM 之優缺點、偽影與臨床效能回顧）。
[^2]: Svahn TM, Houssami N, Sechopoulos I, Mattsson S. Review of radiation dose estimates in digital breast tomosynthesis relative to those in two-view full-field digital mammography. Breast. 2015;24(2):93-9. 據 PubMed，[DOI](https://doi.org/10.1016/j.breast.2014.12.002)（以合成 2D 取代 FFDM 使乳房劑量約減半）。

> [!question]- Regarding SM reconstructed from DBT, which statement is correct? (2019-405)
> 正確答案 **E**：All of the above（A–D 皆正確）。[^1]

> [!question]- 關於由 DBT 重建之 SM，下列何者敘述錯誤？ (2019-423)
> 正確答案 **D**（該版本 D 為錯誤敘述，因 A–C 皆正確）。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "synthetic-mammography")
```
