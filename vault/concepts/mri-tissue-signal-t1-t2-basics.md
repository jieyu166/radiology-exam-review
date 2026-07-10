---
concepts: [mri-tissue-signal-t1-t2-basics]
name: MRI Tissue Signal Basics (T1/T2)
subspecialty: [Physics]
aliases:
  - T1 T2 signal
  - MRI tissue signal
  - fat bright T1
  - fluid bright T2
  - MR 組織訊號基礎
dateRev: 2026-07-10
---

# mri-tissue-signal-t1-t2-basics

**MRI 訊號的兩條記憶主線：脂肪（fat）縱向磁化回復快（短 T1）→ 在 T1WI 呈亮（bright）；水／體液（fluid）的橫向磁化衰減慢（長 T2）→ 在 T2WI 呈亮（bright）。** 判讀分水嶺：**「亮」要先問是哪一種加權**——T1WI 上發亮多來自脂肪（也含 methemoglobin、釓對比劑、黑色素、蛋白性液體等）；T2WI 上發亮多來自高含水量（水腫、囊液、CSF、多數病灶）。本題（fat 於 T1、fluid 於 T2）兩者皆 bright，故答案為 bright; bright。[^1][^2]

## Summary
- **脂肪 on T1WI＝亮**：脂肪質子縱向磁化快速回復（短 T1），在短 TR/短 TE 的 T1WI 呈高訊號。[^1][^2]
- **水／體液 on T2WI＝亮**：水有長 T2，橫向磁化衰減慢，在長 TR/長 TE 的 T2WI 呈高訊號；多數病灶含水量增加故 T2 亮。[^1][^2]
- **水 on T1WI＝暗**：水縱向磁化回復慢，RF 後可用橫向磁化少，在 T1WI 呈低訊號。[^1]
- **對比機轉**：脂肪相對水有**短 T1、短 T2**；選短 TR 可依 T1 差異產生 T1 對比，選長 TE 可依 T2 差異產生 T2 對比。[^2]

## 影像診斷
### T1 weighted image（T1WI）
- 參數：**短 TR、短 TE**。[^1]
- **脂肪亮、（純）水／CSF 暗**；提供釓（順磁性）對比劑最佳對比。[^1][^2]
- T1WI 高訊號常見成因（判讀清單）：脂肪、methemoglobin、釓對比劑、黑色素（melanin）、緩慢血流、蛋白性液體、鈣／銅／錳／鐵等。[^1]

### T2 weighted image（T2WI）
- 參數：**長 TR、長 TE**。[^2]
- **水／體液亮**；病理過程多因含水量升高而在 T2 呈高訊號，故 T2WI 對「找病灶」敏感。[^2]

## 鑑別與報告要點
| 組織 | T1WI | T2WI | 備註 |
|---|---|---|---|
| 脂肪 fat | **亮** | 中～亮（依序列） | 本題 T1 亮；fat-sat 可壓抑確認 |
| 水／CSF／單純囊液 | 暗 | **亮** | 本題 T2 亮 |
| 亞急性出血（methemoglobin） | 亮 | 視期別 | T1 亮的非脂肪成因之一 |
| 蛋白性／黏液性液體 | 常亮 | 常亮 | T1 亦可亮，勿誤判為脂肪 |

### 參考來源
[^1]: *T1 weighted image*. Radiopaedia.org rID 5852（DOI 10.53347/rID-5852；實際查證 accessed 2026-07-10）：T1WI 為短 TR、短 TE；**Fat quickly realigns its longitudinal magnetization with B0 and therefore appears bright on a T1 weighted image**；water 縱向磁化回復慢、RF 後橫向磁化少，故**低訊號、呈暗**；Summary：TR short、TE short、**fat bright、fluid dark**；T1 高訊號成因含 fat、methemoglobin、釓對比劑、melanin、slow-flowing blood、proteinaceous fluid、calcium/copper/manganese/iron。
[^2]: **Tier 1** Bitar R, Leung G, Perng R, et al. *MR Pulse Sequences: What Every Radiologist Wants to Know but Is Afraid to Ask.* RadioGraphics 2006;26(2):513–537（DOI 10.1148/rg.262055063；正文查證 accessed 2026-07-10）：**fat has a shorter T1 (recovers faster) and a shorter T2 than water, which has a relatively long T1 and T2**；**T2-weighted images … the fluid causes the affected areas to appear bright on T2-weighted images**（多數病理含水量升高故 T2 亮）；短 TR 產生 T1 對比、長 TE 產生 T2 對比。
[^3]: 【2021 官方詳解】(2021-055)：Fat appears bright on T1 weighted SE images, and fluids appear bright on T2 weighted images（答案 A：bright; bright）。

## 題目
> [!question]- Fat appears ____ on T1 weighted SE images, and fluids appear ____ on T2 weighted images. (2021-055)
> **A（bright; bright）**——脂肪短 T1→T1WI 亮；水長 T2→T2WI 亮。故 fat 於 T1WI、fluid 於 T2WI 皆為 bright；其餘（bright;dark／dark;bright／dark;dark）皆與物理原理不符。[^1][^2][^3]

## 考題
```dataview
list from #交換 where contains(concepts, "mri-tissue-signal-t1-t2-basics")
```
