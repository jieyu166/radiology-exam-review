---
concepts: [proton-density-mri]
name: Proton Density-Weighted MRI
subspecialty: [Physics]
aliases:
  - proton density weighted
  - PD weighted image
  - 質子密度加權
dateRev: 2026-06-29
nonImaging: true
nonImagingReason: "PD 加權序列物理；判讀向度已涵蓋、餘為物理參數"
---

# proton-density-mri

**PD 加權的參數記憶：「長 TR 抑制 T1、短 TE 抑制 T2，剩下的就是質子密度本身」。** 兩個參數都「一長一短」，把 T1 和 T2 對比都壓下去才讓質子密度主導；長 TR 同時帶來高 SNR。考試陷阱是「短 TR ＋ 長 TE」——那個組合根本不存在有意義的權重，是 PD 的完全相反。判讀分水嶺一：**PD ＝ 長 TR ＋ 短 TE**；判讀分水嶺二：**長 TR → 高 SNR；後顱窩 MS 斑塊在 PD 較 T2 明顯（CSF 不過亮）**。

## Summary
- **參數**：**長 TR（減 T1 權重）＋ 短 TE（減 T2 權重）→ 質子密度權重**;故「**短 TR ＋ 長 TE 產生 PD**」**錯誤**＝題目正解（2016-197 正解 C,參數相反）。[^1]
- **SNR 高**：因長 TR,PD 的 SNR 高於相對應的 T1W 或 T2W(option A 對)。[^1]
- **MSK 應用**：對組織內質子密度差異敏感（如軟骨、半月板）,PD（含 fat-sat）為關節成像主力(option B 對)。[^1]
- **後顱窩 MS**：病灶在 PD 上可能較 T2 更明顯（PD 上 CSF 不致過亮蓋過病灶）(option D 對)。[^1]

> [!note] 考點：PD 影像何者「為非」?
> 「**短 TR ＋ 長 TE 產生 PD**」非——PD 為 **長 TR ＋ 短 TE**。PD SNR 高、MSK 敏感、後顱窩 MS 較 T2 明顯皆對。[^1]

### 參考來源
[^1]: 質子密度加權 MRI 標準物理：**長 TR（抑 T1）＋ 短 TE（抑 T2）→ PD 權重**;長 TR 致高 SNR;MSK（軟骨/半月板）主力;後顱窩 MS 斑塊可較 T2 明顯。

## 考題
```dataview
list from #交換 where contains(concepts, "proton-density-mri")
```
