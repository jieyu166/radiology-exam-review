---
concepts: [ultrasound-prf-depth]
name: PRF vs Imaging Depth (Ultrasound)
subspecialty: [US, Physics]
aliases:
  - pulse repetition frequency
  - PRF
  - imaging depth PRF
  - 脈衝重複頻率
dateRev: 2026-06-15
---

# ultrasound-prf-depth

**增加成像深度，唯一隨之改變的是 PRF（脈衝重複頻率）——深度↑ → PRF↓。** 判讀分水嶺一：**PRF 受最大取樣深度限制**（須等回波返回才能發下一個脈衝）；判讀分水嶺二：**SPL、pulse duration、wavelength 由探頭/頻率與介質決定，與深度無關**。

## Summary
- **PRF = c / (2R)**（c＝介質聲速、R＝最大取樣深度）；故 **R↑ → PRF↓**。[^1]
- 反之 depth of view **R = 0.5 × (c / PRF)**——深度與 PRF 成反比。[^1]
- **與深度無關（不變）者**：[^1]
  - **Spatial pulse length（SPL）**＝波長 × 每脈衝週期數，由探頭/頻率定。
  - **Pulse duration（PD）**＝週期數 × 週期，由探頭/頻率定（典型 <1 μs）。
  - **Wavelength（λ）**＝ c / 頻率，由頻率與介質定。
- 連帶效應：深度↑ → PRF↓ → **frame rate 下降**（每條掃描線需更久）。[^1]

> [!note] 一句話記憶
> **深度變，只有 PRF 跟著變（成反比）**；SPL／PD／波長都由探頭頻率與介質決定，不隨深度改變。[^1]

### 參考來源
[^1]: *Pulse repetition frequency*. Radiopaedia.org（ultrasound physics）。PRF = c/(2R)、R = 0.5×(c/PRF)（實際查證 accessed 2026-06-15）。

## 題目
> [!question]- 增加最大成像深度，下列何者會改變？為什麼？
> **PRF（脈衝重複頻率）**——PRF = c/(2R)，深度 R↑ → PRF↓。SPL、pulse duration、wavelength 由探頭頻率/介質決定，與深度無關。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "ultrasound-prf-depth")
```
