---
concepts: [fluoroscopy-radiation-safety]
name: Fluoroscopy / C-arm Radiation Safety
subspecialty: [Physics, IR]
aliases:
  - fluoroscopy dose
  - C-arm radiation safety
  - pulsed fluoroscopy
  - 透視輻射防護
dateRev: 2026-07-12
nonImaging: true
nonImagingReason: "透視輻射安全/劑量主題（frame rate、distance/time/shielding、ALARA、皮膚劑量），非影像判讀"
---

# fluoroscopy-radiation-safety

**C 臂透視防護最直接的動作：降 frame rate 少照就少劑量；散射從 X 光管那一側打出來，所以要站影像接收器那一側。** 判讀分水嶺一：**降 frame rate（脈衝透視）→ 直接減少每單位時間劑量**；判讀分水嶺二：**散射來自入射（X 光管）側 → 工作人員站影像接收器側；II 貼近病人（縮短 air gap）亦降劑量**。記憶鉤：想像 X 光是水槍——水槍頭噴最多，你要躲在靶板後面，不要站槍口前。

## Summary
- **降 frame rate（脈衝透視）**：**直接減少病人與工作人員劑量**;脈衝式透視的減劑量來自「降低每秒幀數」而非脈衝本身（單純脈衝反而拉高 tube current 以維持 SNR）。[^1][^4]
- **站位**：散射主要來自病人**入射（X 光管）側** → 工作人員應**站在影像接收器側**,勿站 X 光管側。[^1]
- **幾何**：影像接收器(II)**貼近病人**、避免拉長 air gap;拉長 source-skin distance（如 51→65 cm 降至 62%）與縮短 air gap（10→1 cm 降至 78%）皆降病人劑量;放大模式/大視野增加劑量;過度準直反增劑量。[^1][^4]
- **小兒移除 anti-scatter grid**：小兒透視移除濾柵可使病人劑量降半以上（連續→7.5 fps 併移 grid,1 歲兒可降 87%）。[^4]
- **皮膚劑量閾值（確定性效應）**：peak skin dose **2–5 Gy 暫時性紅斑＋脫毛、5–10 Gy 持續紅斑/永久部分脫毛、10–15 Gy 乾/濕性脫屑＋微血管擴張、>15 Gy 真皮壞死需手術**;明顯變化約於照後 1 個月顯現。[^5]
- 其他：縮短透視時間、last-image-hold、適當準直;**遠離散射源（操作者劑量依距離平方反比遞減）**、穿鉛衣/甲狀腺護蓋、懸吊鉛屏。[^1]

## 技術要點
- **降 frame rate（脈衝透視）**：以低畫面更新率脈衝式透視取代連續透視，**直接減少每單位時間曝光**，是同時降低病人與工作人員劑量最有效的單一設定。[^1][^2]
- **散射幾何與站位**：散射線主要來自病人**入射（X 光管）側**；C 臂倒置（X 光管在上）時工作人員頭頸暴露大增，應使**X 光管在檢查床下方、影像接收器在上**，並站於接收器側。[^1][^2]
- **air gap 與放大**：影像接收器（II）應**貼近病人**縮短 air gap；拉長 source-skin distance 反而**增加皮膚劑量**；放大模式/大視野增加劑量，故放大時應縮短接收器與病人距離。[^2]
- **距離平方反比**：工作人員劑量隨與散射源（病人）距離增加而依**平方反比**遞減，退後一步即顯著降低受曝。[^1]
- **時間與影像保留**：縮短總透視時間、善用 **last-image-hold** 與 fluoro-loop 回放，避免不必要的持續曝光。[^1]
- **準直與濾片**：適當準直縮小照野可同時降低病人與散射劑量；beam filtration（濾片）濾除低能光子、通常**降低**病人皮膚劑量（Mahesh RadioGraphics 2001 亦列 beam filtration 為降皮膚劑量技術之一;官方 2018-352 標示濾片為「非降劑量」於物理上存疑，見下方 warning）。[^2][^3][^6]
- **屏蔽（ALARA）**：鉛衣、甲狀腺護蓋、含鉛眼鏡、懸吊鉛屏與床側鉛簾為個人防護基本配備，落實 ALARA 原則。[^1]

> [!note] 考點：C 臂血管介入,何者可降低工作人員劑量?
> **降低透視 frame rate**。C 臂倒置時應站影像接收器側（非 X 光管側）、勿拉長 source-detector air gap、勿用過大視野。[^1]

### 參考來源
[^1]: 透視輻射防護標準物理：Bushberg JT, et al. *The Essential Physics of Medical Imaging* 3rd ed., p.309（官方 2016 詳解所引）＋ ICRP/NCRP 職業劑量原則。本次以 Radiopaedia *Fluoroscopy* 確認基本構造,**操作者劑量細節以 Bushberg 為據**：脈衝/降 frame rate 減劑量;散射主要來自病人入射（X 光管）側 → 站影像接收器側;II 貼近病人（縮短 air gap）;放大/大視野增劑量;距離平方反比、準直、屏蔽。
[^2]: Bushberg JT et al. *The Essential Physics of Medical Imaging*, 3rd Ed., Lippincott Williams & Wilkins, 2011, p.309-310（2018 交換考題詳解 p.255 引用；Tier 2 教科書）。降低病人劑量：使用低畫面更新率之脈衝式透視（low frame rate pulsed fluoroscopy）；縮短X光管至病人皮膚距離會『增加』皮膚劑量（應拉長）；放大功能應『縮短』影像接收器與病人距離；X光濾片（beam filtration）應使用以減少低能量光子劑量（非避免）。
[^3]: *Practical Neuroangiography*, 2nd Edition, p.107（2018 交換考題詳解 p.262 引用；Tier 2 教科書）。血管攝影降低病人劑量方法含減少幾何放大、盡量準直、降低攝影張數(frame rate)、適當使用濾片。官方標示「Maximize the use of filters」為「非降低劑量」之答案，惟濾片通常降低病人劑量，此標示物理上存疑，待醫師確認。
[^4]: **Tier 1（全文）** Hernanz-Schulman M, Goske MJ, Bercha IH, Strauss KJ. *Pause and Pulse: Ten Steps That Help Manage Radiation Dose During Pediatric Fluoroscopy.* AJR Am J Roentgenol 2011;197(2):475-481（DOI [10.2214/AJR.10.6122](https://doi.org/10.2214/AJR.10.6122)；全文實讀 accessed 2026-07-12）——DAP/air kerma–area product 隨與射源距離不變；pulsed fluoroscopy 之減劑量來自「降低每秒幀數」而非脈衝本身（單純脈衝會拉高 tube current 維持 SNR）；小兒移除 anti-scatter grid 使病人劑量降半以上（連續→7.5 fps 併移 grid，1 歲兒降 87%）；拉長 source-skin distance（51→65 cm 降至 62%）、縮短 air gap（10→1 cm 降至 78%）皆降病人劑量；過度準直反增劑量。
[^5]: **Tier 1（全文 Table 1）** Balter S, Hopewell JW, Miller DL, Wagner LK, Zelefsky MJ. *Fluoroscopically Guided Interventional Procedures: A Review of Radiation Effects on Patients' Skin and Hair.* Radiology 2010;254(2):326-341（DOI [10.1148/radiol.2542082312](https://doi.org/10.1148/radiol.2542082312)，PMID 20093507；Table 1 全文實讀 accessed 2026-07-12）——皮膚確定性效應閾值（peak skin dose）：2–5 Gy 暫時性紅斑＋脫毛、5–10 Gy 持續紅斑/永久部分脫毛、10–15 Gy 乾/濕性脫屑＋微血管擴張、>15 Gy 真皮壞死需手術；明顯變化約於照後 1 個月顯現。
[^6]: **Tier 1（摘要）** Mahesh M. *Fluoroscopy: Patient Radiation Exposure Issues.* RadioGraphics 2001;21(4):1033-1045（DOI [10.1148/radiographics.21.4.g01jl271033](https://doi.org/10.1148/radiographics.21.4.g01jl271033)，PMID 11452079；摘要 accessed 2026-07-12）——降皮膚劑量技術含 intermittent exposure、grid removal、last image hold、dose spreading、beam filtration、pulsed fluoroscopy。
[^7]: **Radiopaedia（snippet/403，未實讀全文）** *Fluoroscopy*. Radiopaedia.org（rID 未取得，WebFetch 403；accessed 2026-07-12）——pulsed fluoroscopy 作減劑量、flat panel detector 漸取代 image intensifier。

## 題目
> [!question]- 執行血管攝影診療時，下列何種機器設定可降低病人所接受到之劑量? (2018-344)
> **使用低畫面更新率之脈衝式透視攝影模式 (low frame rate pulsed fluoroscopy)（A）**——直接減少單位時間曝光。縮短X光管到病人皮膚距離會增加皮膚劑量(B錯)、放大時應縮短接收器與病人距離(C錯)、應使用X光濾片減低能光子劑量(D錯)。[^2]

> [!warning] 2018-352 官方答案標示為A，但物理上存疑
> 官方題目「下列何者『非』降低病人劑量」答案標示A（Maximize the use of filters）。惟增加濾片（beam filtration）通常『會』降低病人劑量，故A作為「非降低劑量」之答案於物理上有爭議；B（減少幾何放大）、C（盡量準直）、D（盡量降低攝影張數/frame rate）皆明確可降劑量。暫依官方標示記A，建議醫師對照原始考卷與Practical Neuroangiography p107確認。

> [!question]- Which of the followings is not reducing radiation exposure of the patient during angiography? (2018-352)
> **Maximize the use of filters（A，官方標示）**——⚠️惟增加濾片通常會降低病人劑量，此答案物理上存疑，見上方warning。Minimize geometric magnification(B)、collimate(C)、keep filming rates low(D)皆明確降低劑量。[^3]

> [!question]- 在執行小兒 Fluoroscopy 時，必須特別注意輻射劑量的控制。下列哪項措施無法減少暴露於病人的輻射劑量？ (2021-372)
> **A（使用 anti-scatter grids）**——鉛柵置於病人與偵測器之間以攔阻散射、提升影像對比，代價是必須提高入射劑量以維持 SNR（Bucky factor），因此反而『增加』病人劑量，無法減劑量。降低 pulsed fluoroscopy frame rate（B，少照少劑量）、檢查台盡量遠離射源（C，拉長 source 距離降入射皮膚劑量）、不使用 electronic magnification（D，放大會增劑量）皆能降低病人劑量。

> [!question]- While performing interventional radiology procedures, the x-ray tubes ___ the table have low operator doses, and it is recommended that operators stand at the ___ side for lateral projections. (2021-108)
> **C（under; image receptor）**——散射線主要來自病人入射（X 光管）側，故將 X 光管置於檢查床下方可降低操作者劑量；側位投影時操作者應站在影像接收器側，避開 X 光管側（該側散射強度大增）。

## 考題
```dataview
list from #交換 where contains(concepts, "fluoroscopy-radiation-safety")
```
