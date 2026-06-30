---
concepts: [ultrasound-prf-depth]
name: PRF vs Imaging Depth (Ultrasound)
subspecialty: [US, Physics]
aliases:
  - pulse repetition frequency
  - PRF
  - imaging depth PRF
  - 脈衝重複頻率
dateRev: 2026-06-30
nonImaging: true
nonImagingReason: "純超音波物理/knobology（PRF=c/2R、深度-PRF反比、SPL/PD/波長不隨深度改變），無可判讀影像特徵；本概念不涉及 Doppler aliasing 影像表現"
same:
  - "[[ultrasound-attenuation]]"
  - "[[ultrasound-speed-artifact]]"
---

# ultrasound-prf-depth

**加深成像深度只改變一件事：PRF 下降——因為機器必須等最深的回波返回才能發下一個脈衝，深度越大、等待越久、頻率越低。** 記憶鉤：PRF＝「每秒能打幾發」，深度越深「來回時間越長」→ 每秒能打的發數（PRF）越少；SPL、pulse duration、波長都由探頭頻率決定，不受深度影響。判讀分水嶺一：**PRF = c / (2R)：深度 R↑ → PRF↓（成反比）；連帶 frame rate 也下降**；判讀分水嶺二：**SPL / pulse duration / wavelength 由探頭/頻率/介質決定，與成像深度無關——此三者為常見干擾選項**。

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

## 考題
```dataview
list from #交換 where contains(concepts, "ultrasound-prf-depth")
```
