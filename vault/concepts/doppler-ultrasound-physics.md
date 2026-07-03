---
concepts: [doppler-ultrasound-physics]
name: Doppler Ultrasound — Sensitivity to Doppler Shift
subspecialty: [US, Physics]
aliases:
  - Doppler shift sensitivity
  - Doppler angle
  - operating frequency Doppler
  - 都卜勒頻移敏感度
dateRev: 2026-07-03
---

# doppler-ultrasound-physics

**都卜勒頻移（Doppler shift）與操作頻率（operating/transmitted frequency f₀）成正比——依都卜勒方程式 Δf = 2f₀(v/c)cosθ，提高 f₀ 直接增加偵測到的頻移量，是增加系統對頻移敏感度最直接有效的方法。** 判讀分水嶺：**Δf ∝ f₀（操作頻率）→ 提高 f₀ 增 Δf；都卜勒角 θ 越接近 90°、cosθ→0 頻移越小（理想 θ<60°）；重新定位 sample volume、改變 sample gate 大小屬影像/訊號優化，非直接增加頻移物理量。**

## Summary
- **都卜勒方程式**：**Δf = 2f₀(v/c)·cosθ**（f₀＝操作/發射頻率、v＝血流速度、c＝聲速、θ＝聲束與血流夾角）。[^1][^2]
- **提高操作頻率（f₀）**：**Δf 與 f₀ 成正比** → 直接增加頻移，是增加系統對都卜勒頻移敏感度**最直接**的方法。[^1][^2]
- **都卜勒角 θ**：cosθ 隨角度增加而變小（**θ→90°、cosθ→0，頻移消失**）；理想都卜勒角應**盡量小（<60°）**。[^1][^2]
- **其他選項**：重新定位 sample volume（影響取樣位置）、改變 sample gate 大小（影響空間解析/訊號強度）——**非直接增加頻移量**。[^1]

## 放射科醫師影像判讀重點
- **角度校正**：keep θ<60°；θ=90° 時無頻移（血管垂直聲束會「消失」），需調整探頭/轉向。[^2]
- **頻率取捨**：f₀↑ → 頻移↑ + 空間解析↑，但**穿透↓、易 aliasing**（需提高 PRF/scale）。[^2]
- **正/負頻移**：反射體朝探頭＝正頻移（received>emitted）、遠離＝負頻移——判血流方向。[^2]
- **敏感度優化**：欲增頻移敏感度優先調 f₀ 與角度，而非 gate/位置。[^1]
- **陷阱**：增大都卜勒角反而降頻移（cosθ 變小），勿誤以為「增角＝增敏」。[^1]

## 臨床重點（5 句）
1. **方程式**：Δf = 2f₀(v/c)cosθ。[^1][^2]
2. **f₀↑ → Δf↑**：最直接增敏感度。[^1][^2]
3. **角度**：θ<60° 佳，θ=90° 無頻移。[^1][^2]
4. **取捨**：f₀↑ 穿透↓、易 aliasing。[^2]
5. **方向**：正/負頻移判血流方向。[^2]

> [!note] 考點：何者最可能增加系統對都卜勒頻移的敏感度?
> **Increasing the operating frequency（C）**——依都卜勒方程式，頻移與操作頻率成正比。增加都卜勒角度反使 cosθ 變小、降低頻移；重新定位 sample volume、改變 sample gate 大小非直接增加頻移的方法。[^1][^2]

### 參考來源
[^1]: 官方 2017 詳解；Ref: Sonography Exam Review: Physics, Abdomen, OB/GYN, 2nd ed., p.76（題目所引）——都卜勒方程式 Δf=2f₀v·cosθ/c；提高操作頻率直接增加頻移敏感度；增加角度使 cosθ 變小反而降低頻移。
[^2]: Weerakkody Y, et al. *Doppler shift*. Radiopaedia, rID-25283, DOI 10.53347/rID-25283——Doppler shift＝反射體相對探頭運動致頻率改變（朝向＝正頻移、遠離＝負頻移）；**方程式 ΔF = 2f₀(v/c)cos(θ)**（f₀ 發射頻率、v 速度、c 聲速、θ 聲束與血流夾角）；頻移大小受角度影響。

## 題目
> [!question]- Which of the following will most likely increase the system's sensitivity of the Doppler shifts? (2017-269)
> **Increasing the operating frequency（C）**——依都卜勒方程式 Δf=2f₀v·cosθ/c，頻移與操作頻率成正比。增加都卜勒角度反使頻移降低（cosθ 變小）；重新定位 sample volume、改變 sample gate 大小非直接增加頻移的方法。[^1][^2]

## 考題
```dataview
list from #交換 where contains(concepts, "doppler-ultrasound-physics")
```
