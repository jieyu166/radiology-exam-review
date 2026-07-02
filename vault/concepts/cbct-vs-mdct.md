---
tags: [concept, HN, NR]
aliases: [CBCT, cone beam CT, 錐形束電腦斷層]
---

**Cone Beam CT (CBCT)** 與 **MDCT** 相比，具有較高空間解析度但**較低時間解析度 (temporal resolution)**。

## Summary

CBCT 特性 [^1]：
- **較高 spatial resolution** — 適合高對比結構（骨骼、牙齒）
- **較低 temporal resolution** — 旋轉速度慢，不適合動態研究
- **較長 reconstruction time**
- **較多 scatter artifact** — 錐形束幾何
- 較低劑量（相對於 MDCT full scan）
- 主要應用：牙科、耳鼻喉科（顳骨/副鼻竇）、介入導引

## 陷阱

- CBCT temporal resolution **低於** MDCT — 非高於
- 「Higher temporal resolution」為錯誤敘述

### 參考來源

[^1]: AJNR Am J Neuroradiol 37:481-86

## 考題

```dataview
TABLE WITHOUT ID file.link AS 卡片, questionText AS 題目
FROM "vault/cards"
WHERE contains(concepts, "cbct-vs-mdct")
```
