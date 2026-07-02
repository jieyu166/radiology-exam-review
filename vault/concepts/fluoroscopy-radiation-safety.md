---
concepts: [fluoroscopy-radiation-safety]
name: Fluoroscopy / C-arm Radiation Safety
subspecialty: [Physics, IR]
aliases:
  - fluoroscopy dose
  - C-arm radiation safety
  - pulsed fluoroscopy
  - 透視輻射防護
dateRev: 2026-06-29
nonImaging: true
nonImagingReason: "透視輻射安全/劑量主題（frame rate、distance/time/shielding、ALARA、皮膚劑量），非影像判讀"
---

# fluoroscopy-radiation-safety

**C 臂透視防護最直接的動作：降 frame rate 少照就少劑量；散射從 X 光管那一側打出來，所以要站影像接收器那一側。** 判讀分水嶺一：**降 frame rate（脈衝透視）→ 直接減少每單位時間劑量**；判讀分水嶺二：**散射來自入射（X 光管）側 → 工作人員站影像接收器側；II 貼近病人（縮短 air gap）亦降劑量**。記憶鉤：想像 X 光是水槍——水槍頭噴最多，你要躲在靶板後面，不要站槍口前。

## Summary
- **降 frame rate（脈衝透視）**：**直接減少病人與工作人員劑量**。[^1]
- **站位**：散射主要來自病人**入射（X 光管）側** → 工作人員應**站在影像接收器側**,勿站 X 光管側。[^1]
- **幾何**：影像接收器(II)**貼近病人**、避免拉長 air gap;放大模式/大視野增加劑量。[^1]
- 其他：縮短透視時間、last-image-hold、適當準直;**遠離散射源（操作者劑量依距離平方反比遞減）**、穿鉛衣/甲狀腺護蓋、懸吊鉛屏。[^1]

> [!note] 考點：C 臂血管介入,何者可降低工作人員劑量?
> **降低透視 frame rate**。C 臂倒置時應站影像接收器側（非 X 光管側）、勿拉長 source-detector air gap、勿用過大視野。[^1]

### 參考來源
[^1]: 透視輻射防護標準物理：Bushberg JT, et al. *The Essential Physics of Medical Imaging* 3rd ed., p.309（官方 2016 詳解所引）＋ ICRP/NCRP 職業劑量原則。本次以 Radiopaedia *Fluoroscopy* 確認基本構造,**操作者劑量細節以 Bushberg 為據**：脈衝/降 frame rate 減劑量;散射主要來自病人入射（X 光管）側 → 站影像接收器側;II 貼近病人（縮短 air gap）;放大/大視野增劑量;距離平方反比、準直、屏蔽。
[^2]: Bushberg JT et al. *The Essential Physics of Medical Imaging*, 3rd Ed., Lippincott Williams & Wilkins, 2011, p.309-310（2018 交換考題詳解 p.255 引用；Tier 2 教科書）。降低病人劑量：使用低畫面更新率之脈衝式透視（low frame rate pulsed fluoroscopy）；縮短X光管至病人皮膚距離會『增加』皮膚劑量（應拉長）；放大功能應『縮短』影像接收器與病人距離；X光濾片（beam filtration）應使用以減少低能量光子劑量（非避免）。
[^3]: *Practical Neuroangiography*, 2nd Edition, p.107（2018 交換考題詳解 p.262 引用；Tier 2 教科書）。血管攝影降低病人劑量方法含減少幾何放大、盡量準直、降低攝影張數(frame rate)、適當使用濾片。官方標示「Maximize the use of filters」為「非降低劑量」之答案，惟濾片通常降低病人劑量，此標示物理上存疑，待醫師確認。

## 題目
> [!question]- 執行血管攝影診療時，下列何種機器設定可降低病人所接受到之劑量? (2018-344)
> **使用低畫面更新率之脈衝式透視攝影模式 (low frame rate pulsed fluoroscopy)（A）**——直接減少單位時間曝光。縮短X光管到病人皮膚距離會增加皮膚劑量(B錯)、放大時應縮短接收器與病人距離(C錯)、應使用X光濾片減低能光子劑量(D錯)。[^2]

> [!warning] 2018-352 官方答案標示為A，但物理上存疑
> 官方題目「下列何者『非』降低病人劑量」答案標示A（Maximize the use of filters）。惟增加濾片（beam filtration）通常『會』降低病人劑量，故A作為「非降低劑量」之答案於物理上有爭議；B（減少幾何放大）、C（盡量準直）、D（盡量降低攝影張數/frame rate）皆明確可降劑量。暫依官方標示記A，建議醫師對照原始考卷與Practical Neuroangiography p107確認。

> [!question]- Which of the followings is not reducing radiation exposure of the patient during angiography? (2018-352)
> **Maximize the use of filters（A，官方標示）**——⚠️惟增加濾片通常會降低病人劑量，此答案物理上存疑，見上方warning。Minimize geometric magnification(B)、collimate(C)、keep filming rates low(D)皆明確降低劑量。[^3]

## 考題
```dataview
list from #交換 where contains(concepts, "fluoroscopy-radiation-safety")
```
