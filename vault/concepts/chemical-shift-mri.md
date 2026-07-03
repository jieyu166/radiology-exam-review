---
concepts: [chemical-shift-mri]
name: Chemical Shift MRI (In-phase / Opposed-phase)
subspecialty: [ABD, MSK]
aliases:
  - in-phase opposed-phase
  - India ink artifact
  - 化學位移 MRI
dateRev: 2026-07-03
---

# chemical-shift-mri

**In-/opposed-phase 是同 TR、兩個不同 TE 的成對 GRE 序列，利用脂與水進動頻率不同而週期性同/反相位。Opposed-phase（反相位）在「同一體素內同時有微觀脂 + 水」時訊號抵消 → 掉訊號＝偵測微觀/細胞內脂（脂肪肝、腎上腺腺瘤）；並在脂-水界面產生 India ink artifact。In-phase 在 1.5T 之 TE 較長、T2\* 效應較強 → 鐵/出血/金屬/黑色素在 in-phase 掉訊號更明顯（與脂相反）。** 判讀分水嶺：**「反相位掉訊號＝微觀脂」（≠ 巨觀塊狀脂，塊狀脂內無水不會整體掉，只在邊緣有 India ink）；「in-phase 掉訊號＝鐵/磁化率」——兩者方向相反，是分辨脂 vs 鐵的關鍵。**

## Summary
- **序列本質**：IP/OOP＝**同 TR、兩個不同 TE 之成對 GRE**（1.5T：OOP≈2.2 ms、IP≈4.4 ms）；脂與水頻率差使其週期性同相/反相。[^1]
- **Opposed-phase（反相位）**：同一體素內**微觀脂 + 水**向量相反 → **訊號抵消（signal drop）＝微觀/細胞內脂**（脂肪肝、focal fatty sparing/infiltration、腎上腺腺瘤 vs 癌/轉移、lipid-poor AML、RCC、胸腺增生、骨髓）。[^1]
- **India ink artifact（2nd-kind 化學位移）**：反相位在**脂-水界面**產生黑色勾邊（如器官/脂肪交界）。[^1]
- **In-phase（同相位）susceptibility**：1.5T 之 IP **TE 較長、T2\* 效應較強** → **鐵沉積、出血、金屬、黑色素在 in-phase 掉訊號更明顯**（與脂相反）——見 [[hepatic-iron-overload-mri]]、[[gre-hemorrhage-detection]]。[^1]
- **巨觀（塊狀）脂不表現反相位整體掉訊號**：因體素內無水可抵消，僅在其**邊緣**呈 India ink（干擾選項）。[^1]

## 放射科醫師影像判讀重點
- **脂 vs 鐵方向相反**：微觀脂在 **OOP** 掉；鐵/磁化率在 **IP** 掉——看是哪個 TE 掉訊號即可分辨。[^1]
- **腎上腺腺瘤**：OOP 相對 IP 掉訊號 ≥ 某比例（chemical shift ratio / adrenal SI index）→ 富脂腺瘤，與癌/轉移鑑別。[^1]
- **脂肪肝/hemochromatosis**：脂肪肝 OOP 掉、鐵過載 IP 掉；兩者並存時看 TE 判斷主導。[^1]
- **India ink**：正常脂-水界面之黑線，勿誤為病灶；也可用來確認 OOP 影像。[^1]
- **巨觀脂陷阱**：myelolipoma 等塊狀脂於 OOP 不整體掉訊號，靠 India ink 邊緣或脂抑制序列確認。[^1]

## 臨床重點（5 句）
1. **兩序列**：同 TR、兩 TE 之成對 GRE。[^1]
2. **OOP 掉＝微觀脂**：脂肪肝、腎上腺腺瘤等。[^1]
3. **IP 掉＝鐵/磁化率**：與脂相反，可分辨。[^1]
4. **India ink**：脂-水界面黑勾邊（2nd-kind chemical shift）。[^1]
5. **巨觀脂**：OOP 不整體掉訊號，僅邊緣 India ink。[^1]

> [!note] 考點：關於 chemical shift（in-/opposed-phase）成像
> **反相位掉訊號代表「微觀/細胞內脂」**（脂肪肝、腎上腺腺瘤）；**巨觀塊狀脂不會整體掉訊號**（僅邊緣 India ink）；**in-phase 掉訊號代表鐵/出血/金屬/黑色素（磁化率）**——脂與鐵掉訊號的 TE 方向相反，是核心鑑別。[^1]

### 參考來源
[^1]: Gaillard F, et al. *In-phase and out-of-phase sequences*. Radiopaedia, rID-42534, DOI 10.53347/rID-42534——IP/OOP＝同 TR、兩 TE 之成對 GRE；主用途為以 **OOP 相對 IP 掉訊號偵測微觀（細胞內）脂**（脂肪肝、focal fatty sparing、腎上腺腺瘤、lipid-poor AML、RCC、胸腺增生、骨髓）；**hemochromatosis 之鐵於 in-phase（TE 較長）掉訊號**；反相位脂-水界面 India ink artifact。原「官方 2019 詳解／MRI physics」弱來源已由此一手來源查核取代。

## 題目
> [!question]- 關於化學位移成像（in-/opposed-phase），何者敘述正確？ (2019)
> **反相位掉訊號＝微觀/細胞內脂；in-phase 掉訊號＝鐵/出血/金屬/黑色素（磁化率）；巨觀塊狀脂不會在反相位整體掉訊號（僅邊緣 India ink）。**[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "chemical-shift-mri")
```
