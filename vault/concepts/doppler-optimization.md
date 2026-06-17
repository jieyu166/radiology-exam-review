---
concepts: [doppler-optimization]
name: Doppler Sensitivity Optimization
subspecialty: [US, Physics]
aliases:
  - Doppler optimization
  - Doppler sensitivity
  - 都卜勒敏感度
dateRev: 2026-06-17
same:
  - "[[ultrasound-attenuation]]"
---

# doppler-optimization

**提升都卜勒對低速/微弱血流的敏感度：增加 gain、增加 power output、降低 scale(PRF)、並把『都卜勒角度減小(趨近 0°)』——『增大』角度反而降低訊號。** 判讀分水嶺一：**角度越小(趨 0°)cosθ 越大→訊號越強**；判讀分水嶺二：**降低 scale(PRF)** 才測得到慢速血流(但過低會 aliasing)。

## Summary
- **增加 Doppler gain**：放大接收訊號 → 敏感度↑（過高則雜訊）。[^1]
- **增加 power output**：發射功率↑ → 訊號↑（受 MI/TI 安全限制）。[^1]
- **降低 Doppler scale(PRF)**：偵測慢速血流（過低易 aliasing）。[^1]
- **減小 Doppler 角度(趨近 0°)**：頻移 ∝ cosθ；角度越小訊號越強。故「**增大**都卜勒角度」**錯誤**（2016-091 正解 D；增角度→cosθ↓→訊號↓，>60° 不可靠）。[^1]

> [!note] 考點：何者「不」能提升都卜勒敏感度？
> 「**增大 Doppler 角度**」——角度應**減小**（趨 0°）才增強訊號。其餘（增 gain、增 power、降 scale）皆可提升。[^1]

### 參考來源
[^1]: 都卜勒物理標準教學（Radiopaedia *Doppler ultrasound*）：頻移 ∝ cosθ；提升敏感度＝增 gain/power、降 PRF、減小角度；角度 >60° 不可靠。

> [!warning] 來源待補（依 SOP 需以一手來源重核）
> Radiopaedia 條目未逐字核實，都卜勒角度/PRF 為標準物理教學。

> [!question]- 下列何者「不」能提升都卜勒超音波敏感度？
> **增大 Doppler 角度**（應減小趨 0°）。增 gain、增 power output、降 scale(PRF) 皆可提升。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "doppler-optimization")
```
