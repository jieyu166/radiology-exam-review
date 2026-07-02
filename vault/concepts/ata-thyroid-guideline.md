---
tags: [concept, HN]
aliases: [ATA 2015, thyroid nodule management, TI-RADS]
---

**2015 ATA guideline** 依甲狀腺結節超音波特徵分為 high / intermediate / low / very low suspicion，各有不同 FNA 建議閾值。

## Summary

### High suspicion sonographic patterns [^1]
- Hypoechoic + irregular margin
- Hypoechoic + taller-than-wide
- Interrupted rim calcification with soft tissue extrusion
- FNA threshold: **≥ 1 cm**

### FNA 建議閾值
| Suspicion level | FNA threshold |
|----------------|---------------|
| High | ≥ 1 cm |
| Intermediate | ≥ 1 cm |
| Low | ≥ 1.5 cm |
| Very low | ≥ 2 cm |
| Benign (spongiform) | 不建議 FNA |

## 陷阱

- High suspicion FNA 閾值為 **≥ 1 cm**（非 0.5 cm）
- Spongiform nodule 屬 very low suspicion / benign，不需 FNA
- ACR TI-RADS 與 ATA 系統略有不同

### 參考來源

[^1]: 2015 ATA Management Guidelines for Adult Patients with Thyroid Nodules

## 考題

```dataview
TABLE WITHOUT ID file.link AS 卡片, questionText AS 題目
FROM "vault/cards"
WHERE contains(concepts, "ata-thyroid-guideline")
```
