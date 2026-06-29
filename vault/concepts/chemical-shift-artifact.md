---
concepts: [chemical-shift-artifact]
name: MRI Chemical Shift Artifact
subspecialty: [NR, ABD]
aliases:
  - chemical shift artifact
  - India ink artifact
  - 化學位移假影
dateRev: 2026-06-29
---

# chemical-shift-artifact

**化學位移假影來自脂肪與水的共振頻率不同：Type 1 是空間位移（沿頻率編碼方向，各序列皆有）；Type 2 是訊號抵消（只在反相位、且像素內脂肪與水並存才抵消，產生器官邊緣的 India ink 黑線）。** 考試陷阱：「純脂肪區在 out-of-phase 完全失訊號」是錯的——抵消需要脂＋水同時存在，純脂肪沒有水可以抵消。記憶鉤：「抵消要兩個人，純脂肪是獨居，沒人抵消它」。

## Summary
- **物理根源**：脂肪與水的質子共振頻率差約 **3.5 ppm**；在 **1.5T** 約相當於 **220 Hz** 的頻率差，這個差異同時驅動兩型偽影與 in/opposed-phase 成像。[^2]

### 第一型（misregistration，空間位移）
- **影像長相**：沿**頻率編碼方向**，脂水介面一側出現**黑帶**、相對側出現**白帶**（black/white boundary，黑白成對）；這是脂肪訊號在頻率編碼軸上被「錯誤定位」、與水訊號重疊或分離造成。[^2][^3]
- **位移幅度**：以接收頻寬／像素換算——例如頻寬 32 kHz、矩陣 256 時每像素約 125 Hz，220 Hz 約位移 **1.8 像素**。[^2]
- **加重因子**：**高場強**（頻率差絕對值變大）與**低接收頻寬**（每像素 Hz 變小、位移像素數變多）會使黑白帶更明顯；故調**寬接收頻寬**或降場強可減輕。[^2][^3]
- **判讀利用**：脂肪介面的黑白帶可標示**腎、腎上腺、後腹腔脂肪**等含大量脂肪結構的邊界，協助定位；亦見於各序列（自旋迴訊為主），常不明顯。[^1][^3]

### 第二型（India ink / boundary artifact，邊界勾邊）
- **影像長相**：**反相位(opposed-phase)** 梯度迴訊上，沿**含水脂介面的 voxel** 出現**對稱的黑線勾邊**，**完整環繞器官各邊**（不限頻率編碼方向）。[^3][^4]
- **成因**：邊界 voxel 內同時含脂與水，在反相位 TE 時兩者相位相反、訊號相消為零 → 黑線。**與脂肪『量』無關**，只看介面 voxel 是否脂水並存，故各方向皆對稱勾邊。[^4][^5]
- **判讀利用**：用以**辨識器官邊界**，並可作為「此為反相位影像」的內部確認；回到 in-phase TE 即消失。[^3][^5]
- **與第一型區分**：第一型只沿頻率編碼軸、黑白成對；第二型各邊對稱黑線、僅反相位出現。[^4][^5]

### in/opposed-phase 訊號掉落（與第二型須區分的概念）
- 用於偵測 **voxel 內微觀脂肪（intracytoplasmic / microscopic fat）**：**腎上腺腺瘤、脂肪肝、含脂病灶**在反相位**整體訊號下降**（signal drop），這是「同一 voxel 內脂水並存而相消」的**訊號強度下降**，**不是第二型的邊緣勾邊**——兩者機制相關但表現須分清：一個是病灶內部均勻變暗、一個是介面黑線。[^1][^2]
- **判讀陷阱**：小腺瘤受周邊脂肪 partial volume 影響、訊號掉落可能很**輕微**；應**早採反相位 TE** 以減少 T2* 效應假性訊號損失（含鐵血黃素沈積反而在 in-phase 較暗，見下）。[^2]

### 判讀陷阱（共通）
- **黑白帶／勾邊勿誤為病灶或鈣化**：第一型黑帶、第二型 India ink 黑線都是偽影，不可當作真實低訊號病灶或邊緣鈣化。[^3][^4]
- **與其他黑線偽影區分**：第二型黑線屬脂水相消，與磁感受性(susceptibility)黑線、流動／截斷偽影不同；定位於脂水介面且僅反相位出現是辨識關鍵。[^3][^5]
- **可調參數減輕第一型**：加寬接收頻寬、降低場強、或改變頻率編碼方向。[^2][^3]

- **純脂肪區在反相位『不會』完全失訊號**——抵消需脂＋水並存；故「純脂肪在 out-of-phase 完全失去強度」**錯誤**（2016-092 正解 B）。[^1]
- **Hemosiderosis**：肝脾在 out-of-phase 反而較亮（in-phase TE 較長、T2* 效應使 in-phase 變暗）。[^1]

> [!note] 考點：何者「為非」？
> 「**純脂肪區在 out-of-phase 完全失去強度**」為非——抵消需**脂＋水同一像素**並存；純脂肪不抵消。其餘(type2 反相位、India ink 環繞、hemosiderosis out-of-phase 較亮)正確。[^1]

### 參考來源
[^1]: MRI 化學位移假影經實際查證（accessed 2026-06-17，Radiopaedia *chemical shift artifact*）：脂水頻率差；type1 頻率編碼方向位移(各序列)、type2 反相位抵消(需脂+水)；India ink 環繞器官；hemosiderosis out-of-phase 較亮(in-phase T2*)。
[^2]: Tier 1。Merkle EM 等，*Chemical Shift MR Imaging of the Adrenal Gland: Principles, Pitfalls, and Applications*，RadioGraphics 2016;36(2):414-432（DOI 10.1148/rg.2016150139；PubMed 26849154）＋脂水 3.5 ppm／1.5T 約 220 Hz、頻寬-像素位移換算（accessed 2026-06-29，mrimaster/mri-q chemical shift 教學頁）：化學位移成像原理、微觀脂肪反相位訊號掉落（腎上腺腺瘤、脂肪肝）、輕微掉落與早採反相位 TE 以減 T2* 等判讀陷阱。
[^3]: Tier 1。Hood MN 等／*In-Phase and Opposed-Phase Imaging: Applications of Chemical Shift and Magnetic Susceptibility in the Chest and Abdomen*，RadioGraphics 2019;39(4)（DOI 10.1148/rg.2019180043，摘要層級可及；accessed 2026-06-29）：第一型沿頻率編碼方向呈黑白帶、隨高場強與低接收頻寬加重、脂水介面（腎/腎上腺/後腹腔）標示；第二型 opposed-phase 沿脂水介面對稱黑線勾邊。
[^4]: Tier 2。Radiopaedia *black boundary artifact*（type 2 chemical shift / India ink artifact，accessed 2026-06-29）：反相位梯度迴訊、沿所有脂水介面 voxel 之黑線（不限頻率編碼方向）、與脂肪量無關、對稱環繞器官；與第一型區分。
[^5]: Tier 2。mriquestions.com *Chemical Shift 2nd Kind* 與 radiologykey.com *Chemical Shift Type 2 Artifact*（accessed 2026-06-29）：邊界 voxel 脂水相位相反相消產生黑線、各方向對稱、用以辨識器官邊界與確認反相位影像、回到 in-phase TE 即消失、與第一型及其他黑線偽影區分。

## 考題
```dataview
list from #交換 where contains(concepts, "chemical-shift-artifact")
```
