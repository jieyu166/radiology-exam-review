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
dateRev: 2026-06-17
---

# digital-radiography-detectors

**記住兩步驟 vs 三步驟：直接（direct）只需 X 光→電荷（靠 a-Se 光導體），間接（indirect）多一步 X 光→可見光（靠 CsI 閃爍體）→電荷。** 考試問「直接偵測器的正確描述」，答案就是「X 光直接轉成電荷」。記憶鉤：**「direct＝直達電荷，中間沒有光；indirect＝多一道光」**。

## Summary
- **直接偵測器（direct conversion）**：**非晶硒（amorphous selenium, a-Se）光導體層** + TFT 讀出陣列;**X 光光子『直接』轉換成電荷**後讀出（2016-146 正解 D）。[^1]
- **間接偵測器（indirect conversion）**：**閃爍體（如 CsI）先把 X 光轉成可見光**,再由光二極體陣列轉成電荷。[^1]
- 選項對錯:A（CCD 直接被 X 光照 → 錯,CCD 屬間接需閃爍體）、B（X 光直接轉成可見光 → 那是『間接』）、C（X 光直接被讀取 → 不精確）、**D（X 光直接轉成電荷 → 正確,即 direct/a-Se）**。[^1]

> [!note] 考點：直接數位偵測器的正確描述?
> **X 光光子直接轉換成電荷**（非晶硒 a-Se 光導體）後讀出。間接型才需閃爍體先轉成可見光。[^1]

### 參考來源
[^1]: *Flat panel detector*. Radiopaedia.org（實際查證 accessed 2026-06-17）：**direct** flat panel detector＝**photoconductor layer of amorphous selenium (a-Se)** + TFT;**indirect**＝scintillator（X 光先轉可見光）+ photodiode;「X-rays converted into electrical charges, either directly or indirectly」。

## 考題
```dataview
list from #交換 where contains(concepts, "digital-radiography-detectors")
```
