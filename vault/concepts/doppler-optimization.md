---
concepts: [doppler-optimization]
name: Doppler Sensitivity Optimization
subspecialty: [US, Physics]
aliases:
  - Doppler optimization
  - Doppler sensitivity
  - 都卜勒敏感度
dateRev: 2026-06-30
nonImaging: true
nonImagingReason: "核心為都卜勒掃描操作 knobology（gain/power/PRF-scale/angle 調整以取得正確波形），屬操作技術而非影像病灶判讀，無影像-假象判讀補強價值"
same:
  - "[[ultrasound-attenuation]]"
---

# doppler-optimization

**都卜勒頻移＝2f₀(v/c)cosθ，cosθ 在 0° 時最大、90° 時歸零——角度越小訊號越強，不是越大。** 四項提升敏感度的操作：增 gain、增 power、降 PRF（scale）、縮小角度趨近 0°；「增大角度」是唯一反向操作，也是考題陷阱。記憶鉤：**「探頭要跟血流平行（角度越小）才聽得到，垂直就聾了」**。

## Summary
- **都卜勒頻移公式**：**F = 2·f₀·(v/c)·cosθ**（f₀＝發射頻率、v＝血流速、c＝聲速、θ＝聲束與血流夾角）→ 頻移**正比於 cosθ**。[^1]
- **減小 Doppler 角度(趨近 0°)**：**0° 時頻移/速度最大且最真**；角度越大 cosθ 越小、訊號越弱。**<60° 才準確，>60° 誤差達 20–30%**。故「**增大**都卜勒角度」**錯誤**（2016-091 正解 D）。[^2]
- **增加 Doppler gain**：放大接收訊號 → 敏感度↑（過高則雜訊）。[^3]
- **增加 power output**：發射功率↑ → 訊號↑（受 MI/TI 安全限制）。[^3]
- **降低 Doppler scale(PRF)**：偵測慢速血流（過低易 aliasing）。[^3]

> [!note] 考點：何者「不」能提升都卜勒敏感度？
> 「**增大 Doppler 角度**」——角度應**減小**（趨 0°，cosθ↑）才增強訊號，>60° 不可靠。其餘（增 gain、增 power、降 scale）皆可提升。[^1][^2]

### 參考來源
[^1]: *Doppler shift*. Radiopaedia.org（實際查證 accessed 2026-06-17）：頻移公式 **F = 2f₀(v/c)cosθ**，θ 為聲束與血流軸夾角。
[^2]: *Doppler angle correction*. Radiopaedia.org（實際查證 accessed 2026-06-17）：**0° 時速度最大且最真**；角度修正在 **<60°** 準確，**>60°** 計算速度誤差達 **20–30%**。
[^3]: gain、power output、PRF(scale) 為都卜勒操作參數的標準超音波物理教學（提升敏感度＝增 gain/power、降 PRF；過低 PRF 致 aliasing）。

> [!question]- 下列何者「不」能提升都卜勒超音波敏感度？
> **增大 Doppler 角度**（應減小趨 0°）。增 gain、增 power output、降 scale(PRF) 皆可提升。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "doppler-optimization")
```
