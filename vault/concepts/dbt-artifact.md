---
concepts: [dbt-artifact]
name: Digital Breast Tomosynthesis (DBT) Artifacts
subspecialty: [BR]
aliases:
  - DBT 偽影
  - 乳房斷層攝影偽影
dateRev: 2026-07-02
---

# dbt-artifact

**DBT 四大偽影中，motion artifact 因 out-of-plane blurring 的遮蔽效應而「很少被察覺」。** Blurring-ripple、truncation、loss of skin resolution 較易辨識。

## Summary
- **Blurring-ripple artifact**：高對比物體周圍出現漣漪 [^1]
- **Truncation artifact**：視野邊緣組織截斷 [^1]
- **Loss of skin and superficial tissue resolution**：淺層組織解析度下降 [^1]
- **Motion artifact**：因 out-of-plane blurring masking 而**不易察覺** [^1]

### 參考來源
[^1]: 2019 交換考詳解。

## 考題
> [!question]- 相關考題
> ```dataview
> TABLE WITHOUT ID file.link AS "概念卡", concepts AS "概念"
> FROM "vault/cards"
> WHERE contains(concepts, this.file.name)
> ```
