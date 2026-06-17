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

**超音波機器固定假設聲速 1540 m/s 來換算深度；若實際介質聲速「較慢」，回波較晚返回 → 被誤判為「較深」而置於真實位置之後（deeper）。** 判讀分水嶺一：**深度 = 假設聲速 × 飛行時間 ÷ 2**，與實際組織無關；判讀分水嶺二：**較慢 → 較深、較快 → 較淺**（位移方向由 1540 與實際聲速的相對快慢決定）。

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

## 題目
> [!question]- 介質傳播速度比軟組織「慢」時，回波會被放在哪裡？
> **比真實位置更深（deeper）**——較慢→回波晚返回→機器（固定 1540 m/s）誤判為更深。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "ultrasound-speed-artifact")
```
