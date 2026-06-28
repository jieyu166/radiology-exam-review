---
concepts: [ultrasound-speed-artifact]
name: Speed Displacement (Propagation Velocity) Artifact
subspecialty: [US, Physics]
aliases:
  - speed displacement artifact
  - propagation velocity artifact
  - speed propagation artifact
  - 傳播速度假影
dateRev: 2026-06-15
same:
  - "[[ultrasound-attenuation]]"
  - "[[ultrasound-prf-depth]]"
---

# ultrasound-speed-artifact

**機器永遠假設聲速 1540 m/s，若組織實際較慢（如脂肪），回波晚到→誤判更深；若較快則誤判較淺。** 記憶鉤：「慢→晚回→被認為更深」；脂肪聲速約 1450 m/s，比假設慢，所以脂肪後方的結構在影像上會被向深方錯位。判讀分水嶺一：**深度 = 1540 × 飛行時間 ÷ 2（固定公式）；實際快慢決定回波早晚，進而決定位移方向**；判讀分水嶺二：**較慢 → 置於較深（deeper）、較快 → 置於較淺（shallower）；屬軸向（深度軸）位移，非側向**。

## Summary
- 機器以**固定 1540 m/s**（軟組織平均聲速）× 來回時間 ÷ 2 計算深度，不論實際組織。[^1]
- **實際聲速 < 1540（較慢，如脂肪）**：回波延遲返回 → 機器判為**更深** → 回波置於**真實位置的深部**。[^1]
- 實際聲速 > 1540（較快）則相反，置於較淺處。[^1]
- 表現：影像中結構出現**局部不連續/錯位**（focal discontinuity & displacement）。[^1]
- 此為**軸向（深度方向）位移**，非側向；故不會把回波擺到「外側」。[^1]

> [!note] 一句話記憶
> **慢→深、快→淺**。機器假設 1540 m/s；介質較慢＝回波晚到＝被當成更深。[^1]

### 參考來源
[^1]: *Speed displacement artifact（propagation velocity artifact）*. Radiopaedia.org（ultrasound artifacts）。機器假設 1540 m/s；真實聲速顯著偏離時深度換算錯誤，較慢者顯示更深（實際查證 accessed 2026-06-15）。

## 考題
```dataview
list from #交換 where contains(concepts, "ultrasound-speed-artifact")
```
