---
concepts: [ultrasound-speed-artifact]
name: Speed Displacement (Propagation Velocity) Artifact
subspecialty: [US, Physics]
aliases:
  - speed displacement artifact
  - propagation velocity artifact
  - speed propagation artifact
  - 傳播速度假影
dateRev: 2026-06-30
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

## 影像辨識（與 ultrasound-artifacts 互補）
- **辨識點一：介面的「階梯狀錯位／斷裂」（step-off / focal discontinuity）。** 經過脂肪的那段聲束下方結構被整段往深方推移，使本應連續的界面在影像上出現局部不連續或台階狀位移，是本偽影最典型的視覺表徵。[^2][^3]
- **經典範例：肝—橫膈介面。** 肝內局部脂肪沉積（focal steatosis）使其後方的橫膈出現遠端位移／斷裂，看似橫膈被「截斷」或下移；這是判讀脂肪肝時最常被引用的 speed displacement 例子。[^2][^3]
- **方向口訣（介質的相對位置決定推移方向）：** 被脂肪「包住」的軟組織（脂肪在淺層）→ 其後結構往深方位移；軟組織中的脂肪團塊本身 → 遠端界面往深方位移。皆為**軸向（沿聲束）**位移。[^2]
- **乳房／矽膠情境：** 乳房脂肪（~1450 m/s）造成測距與深度誤差；矽膠植入物聲速更低（約 990–1000 m/s），是其後方多重殘響與深部結構錯位／變形的來源，判讀乳房植入物時務必納入考量。[^4]
- **可量化的後果：沿聲束的距離／深度測量會失準**，在脂肪介入聲束路徑時尤甚；做精確測距時要意識到此誤差。[^2][^4]

> [!note] 判讀陷阱與破解
> 此偽影**隨探頭角度改變而出現或消失**——換角度掃描時錯位會變動。懷疑是偽影而非真病灶（如疑似「主動脈重複」「雙胞胎」「界面斷裂」）時，**改用不同切面／角度重掃**：真結構在多平面一致，偽影則隨幾何改變。[^3][^5]

### 參考來源
[^1]: *Speed displacement artifact（propagation velocity artifact）*. Radiopaedia.org（ultrasound artifacts）。機器假設 1540 m/s；真實聲速顯著偏離時深度換算錯誤，較慢者顯示更深（accessed 2026-06-30）。
[^2]: Tier 1 — Feldman MK, Katyal S, Blackwood MS. *US Artifacts*. RadioGraphics 2009;29(4):1179–1189. DOI: 10.1148/rg.294085199。脂肪聲速 1450 m/s（較假設 1540 m/s 慢約 6%），脂肪下方標的因回波延遲返回而被誤判更深（misregistration），造成沿聲束方向之測距誤差。
[^3]: Tier 1 — Hindi A, Peterson C, Barr RG 等相關 RSNA 教學文獻所載肝—橫膈例：肝內局部脂肪致橫膈介面出現遠端位移與局部不連續（focal discontinuity & distal displacement），為 speed displacement artifact 之經典影像表現（與 RadioGraphics 2017;37(5):1408 *Clinical Significance of US Artifacts*, DOI: 10.1148/rg.2017160175 同義；全文需授權，此處退摘要／教科書層級）。
[^4]: Tier 2 — *Ultrasound Artifacts*（RadiologyKey／Diagnostic Ultrasound 教科書線上版）。脂肪約 1450 m/s 致軸向測量誤差；矽膠植入物聲速約 990–1000 m/s，為其後方殘響與結構錯位來源；偽影最明顯於脂肪—軟組織介面（accessed 2026-06-30）。
[^5]: Tier 2 — *Ultrasound Physics and Artifacts Part 1*（The Radiology Review, RSNA physics tutorial 性質教學）。較慢介質使結構顯示更深、較快者更淺；以不同切面／角度重掃確認偽影與真病灶（accessed 2026-06-30）。

## 考題
```dataview
list from #交換 where contains(concepts, "ultrasound-speed-artifact")
```
