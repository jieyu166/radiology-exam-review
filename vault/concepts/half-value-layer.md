---
concepts: [half-value-layer]
name: Half-Value Layer (HVL)
subspecialty: [Physics]
aliases:
  - half value layer
  - HVL
  - 半值層
dateRev: 2026-07-03
---

# half-value-layer

**HVL＝使單能光子束強度（air kerma）衰減一半所需的物質厚度;每經過 n 個 HVL，穿透比例＝(1/2)ⁿ。** 判讀分水嶺：**n 個 HVL 後穿透分率＝2⁻ⁿ → 1 HVL=50%、2=25%、3=12.5%、4=6.25%、5≈3.1%、7≈0.8%;乳攝/診斷 X 光 HVL 以『mm 鋁』表示;HVL 反映束質（硬度），與半衰期（時間）不同。**

## Summary
- **定義**：使單能光子束 air kerma 衰減至**一半**所需的吸收體厚度;以**毫米鋁（mm Al）**量測。[^1]
- **指數衰減**：經 **n 個 HVL** 後穿透比例＝**(1/2)ⁿ**。[^1]
  - 1 HVL→50%、2→25%、3→12.5%、4→6.25%、**5→約 3.1%（≈3%）**、6→1.6%、7→0.8%。
- **意義（McKetty）**：**HVL 描述 X 光束品質/穿透力**；HVL 越大代表束質越硬（穿透力越強）；**加濾片降束強度、增 HVL、降病人曝露、改善影像品質**；亦以 homogeneity coefficient 描述束之單能程度。[^1][^3]
- **公式（單能）**：**HVL ＝ 0.693 / μ**（線性衰減係數）,由 Beer-Lambert（I=I₀e^(−μx)）導出;最準確於 narrow-beam 幾何量測。**多能束因 beam hardening，每一層 HVL 依序變大**（低能光子先被衰減）。[^2][^3]

> [!warning] 答案鍵存疑
> 官方原標 **B（50%）後改註「D??」**;依物理 **5 HVL 穿透＝(1/2)⁵≈3.1%≈3%（D）** 才正確,圖示亦為 5 層→3.1%。本卡採 **D**,B 應為筆誤。

> [!note] 考點：單能光子束經 5 個 HVL 後穿透比例?
> **約 3%（D）**——(1/2)⁵＝3.125%。1 HVL=50%、5 HVL≈3.1%。[^1]

### 參考來源
[^1]: 官方 2017 詳解；Bushberg JT et al. The Essential Physics of Medical Imaging, 3rd ed., p.49：HVL＝使 air kerma 減半之厚度（mm Al）;n 個 HVL 後穿透＝(1/2)ⁿ;5 HVL≈3.1%。
[^2]: Murphy A, et al. *Half-value layer*. Radiopaedia, rID-22271, DOI 10.53347/rID-22271（輔助來源）——**HVL＝使 X/γ 射束 air kerma 減半之物質厚度**；單能束 **HVL ＝ 0.693 / μ**（由 Beer-Lambert 導出），最準確於 narrow-beam 幾何量測；**多能束因 beam hardening 使每層 HVL 依序增大**——佐證定義與單能束 (1/2)ⁿ 衰減。
[^3]: **Tier 1** McKetty MH. *The AAPM/RSNA physics tutorial for residents. X-ray attenuation*. RadioGraphics 1998;18(1):151-63（據 PubMed，DOI [10.1148/radiographics.18.1.9460114](https://doi.org/10.1148/radiographics.18.1.9460114)；實際查證 accessed 2026-07-04）——衰減＝X 光束穿過物質強度衰減（吸收/散射），受束能量與吸收體原子序影響；**I=I₀e^(−μx)（單能束指數關係）**；**以 half-value layer（HVL）與 homogeneity coefficient 描述束之穿透力/品質**；**加濾片降束強度、增 HVL、降病人曝露、改善影像品質**——直接佐證 HVL 定義、束質意義與單能束 (1/2)ⁿ 衰減。原「官方/Radiopaedia」弱來源已由本次 RadioGraphics DOI Tier 1 查核升級。

## 題目
> [!question]- 單能光子束在經過五個半值層 (HVL) 厚之物質後，可穿透之光子比例約為? (2017-213)
> **約 3%（D）**——(1/2)⁵≈3.1%。⚠️ 官方原標 B(50%) 後改「D??」,依物理與圖示應為 D。1 HVL=50%、5 HVL≈3.1%。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "half-value-layer")
```
