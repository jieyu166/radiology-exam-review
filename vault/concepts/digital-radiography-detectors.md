---
concepts: [digital-radiography-detectors]
name: Digital Radiography Detectors (Direct vs Indirect)
subspecialty: [Physics]
aliases:
  - flat panel detector
  - direct digital detector
  - indirect digital detector
  - amorphous selenium
  - 數位偵測器
dateRev: 2026-06-29
nonImaging: true
nonImagingReason: "純數位 X 光偵測器物理/工程主題（direct/indirect 轉換、a-Se 光導體、CsI 閃爍體、TFT 讀出），無影像判讀內容"
---

# digital-radiography-detectors

**記住兩步驟 vs 三步驟：直接（direct）只需 X 光→電荷（靠 a-Se 光導體），間接（indirect）多一步 X 光→可見光（靠 CsI 閃爍體）→電荷。** 考試問「直接偵測器的正確描述」，答案就是「X 光直接轉成電荷」。記憶鉤：**「direct＝直達電荷，中間沒有光；indirect＝多一道光」**。

## Summary
- **直接偵測器（direct conversion）**：**非晶硒（amorphous selenium, a-Se）光導體層** + TFT 讀出陣列;**X 光光子『直接』轉換成電荷**後讀出（2016-146 正解 D）。[^1]
- **間接偵測器（indirect conversion）**：**閃爍體（如 CsI）先把 X 光轉成可見光**,再由光二極體陣列轉成電荷。[^1]
- 選項對錯:A（CCD 直接被 X 光照 → 錯,CCD 屬間接需閃爍體）、B（X 光直接轉成可見光 → 那是『間接』）、C（X 光直接被讀取 → 不精確）、**D（X 光直接轉成電荷 → 正確,即 direct/a-Se）**。[^1][^2]
- **系統概觀（Körner）**：**indirect＝閃爍體（CsI/Gd₂O₂S）先轉可見光再由 a-Si photodiode+TFT 讀出；direct＝a-Se 光導體將 X 光直接轉電荷、由 TFT 讀出**；CsI 針狀結構減少光散射以維持空間解析度，DR 相較 CR 具較高 DQE 與工作流程效率。[^2]

> [!note] 考點：直接數位偵測器的正確描述?
> **X 光光子直接轉換成電荷**（非晶硒 a-Se 光導體）後讀出。間接型才需閃爍體先轉成可見光。[^1]

### 參考來源
[^1]: *Flat panel detector*. Radiopaedia.org（實際查證 accessed 2026-06-17）：**direct** flat panel detector＝**photoconductor layer of amorphous selenium (a-Se)** + TFT;**indirect**＝scintillator（X 光先轉可見光）+ photodiode;「X-rays converted into electrical charges, either directly or indirectly」。
[^2]: **Tier 1** Körner M, Weber CH, Wirth S, et al. *Advances in digital radiography: physical principles and system overview*. RadioGraphics 2007;27(3):675-86（據 PubMed，DOI [10.1148/rg.273065075](https://doi.org/10.1148/rg.273065075)；Review；實際查證 accessed 2026-07-04）——數位放射之物理原理與系統概觀：**間接轉換平板＝閃爍體（CsI/Gd₂O₂S）先將 X 光轉可見光、再由 a-Si photodiode+TFT 陣列讀出；直接轉換平板＝a-Se 光導體將 X 光直接轉為電荷、由 TFT 讀出**；並比較 CR 與 DR 之 DQE、空間解析度與工作流程。佐證 direct（a-Se 直接轉電荷）vs indirect（閃爍體先轉光）之核心區別。原「Radiopaedia」弱來源已由本次 RadioGraphics DOI Tier 1 查核升級。

## 考題
```dataview
list from #交換 where contains(concepts, "digital-radiography-detectors")
```
