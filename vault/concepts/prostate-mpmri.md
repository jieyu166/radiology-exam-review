---
concepts: [prostate-mpmri]
name: Multiparametric Prostate MRI (mpMRI / PI-RADS)
subspecialty: [ABD]
aliases:
  - multiparametric prostate MRI
  - mpMRI
  - PI-RADS
  - 多參數攝護腺MRI
dateRev: 2026-06-17
---

# prostate-mpmri

**攝護腺 mpMRI 的三組序列是「結構＋細胞密度＋灌流」：T2WI 看形態、DWI/ADC 看細胞密度（PZ 主導）、DCE 看血流（二元開關）。** Opposed-phase（化學位移）是肝、腎上腺的工具，不屬於 mpMRI——這是唯一的排除考點。判讀分水嶺一：**PZ → DWI/ADC、TZ → T2WI 主導**；判讀分水嶺二：**opposed-phase 不屬 mpMRI 序列**。

## Summary
- **三大序列**：[^1]
  - **T2WI**：解剖、分區評分（TZ 主導）。
  - **DWI（高 b 值）＋ ADC map**：細胞密度,**PZ 主導序列**(option A、B 屬之)。
  - **動態對比增強（DCE）**：早期強化,輔助 PZ（option D 屬之）。
- **不屬 mpMRI**：**opposed-phase image（化學位移成像）** → 故為「不含」之正解（2016-159 正解 C）。[^1]
- PI-RADS v2.1：以上述序列綜合評 1–5 分,評估可疑攝護腺癌。[^1]

> [!note] 考點：何者「不」屬 mpMRI 序列?
> **Opposed-phase image**。mpMRI＝**T2WI ＋ DWI/ADC ＋ DCE**。[^1]

### 參考來源
[^1]: *Prostate Imaging Reporting and Data System (PI-RADS)*. Radiopaedia.org（實際查證 accessed 2026-06-17）：multiparametric prostate MRI 由 **T2W、DWI（含 ADC）、dynamic contrast enhancement (DCE)** 構成;PI-RADS 綜合此三者預測臨床顯著攝護腺癌機率。

## 考題
```dataview
list from #交換 where contains(concepts, "prostate-mpmri")
```
