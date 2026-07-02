---
concepts: [xray-tube-output]
name: X-ray Tube Output — kVp & mAs Relationships
subspecialty: [Physics]
aliases:
  - x-ray intensity kVp
  - tube output
  - mAs exposure
  - X光強度電壓關係
dateRev: 2026-07-02
nonImaging: true
nonImagingReason: "X光管輸出/曝光量與kVp/mAs關係之物理計算，非影像判讀"
---

# xray-tube-output

**X光強度（intensity/exposure）與管電壓平方（kVp²）成正比、與mAs成線性正比。所以電壓從110→125 kVp時，強度變為原本的(125/110)²倍。記憶鉤：電壓「平方」、電流時間「一次方」。**

## Summary
- **X光強度 ∝ kVp²**：X光管輸出強度（exposure/intensity）與管電壓的**平方**成正比。[^1]
- **X光強度 ∝ mAs**：與管電流×時間（mAs）成**線性**正比。[^1]
- **本題計算**：110 kVp/10 mAs產生32 mR，改為125 kVp（mAs不變）→ 強度 = 32 × (125/110)² = 32 × 1.291 ≈ **41 mR**。[^1]

> [!note] 考點：側面胸部110 kVp/10 mAs產生32 mR，改為125 kVp時X光強度？
> **41 mR（B）**——X光強度與kVp²成正比：32 × (125/110)² ≈ 41 mR。[^1]

### 參考來源
[^1]: 102年第一次專門職業及技術人員高等考試 放射師考試（2018 交換考題詳解 p.289 引用；Tier 2/3 國考題）。X光強度與管電壓平方(kVp²)成正比、與mAs線性正比；32×(125/110)²≈41 mR。

## 題目
> [!question]- 某個側面胸部照射使用110 kVp/10 mAs，產生強度為32 mR的X光，如果將電壓改變成125 kVp時，其X光強度是? (2018-379)
> **41 mR（B）**——X光強度∝kVp²，32×(125/110)²≈41 mR。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "xray-tube-output")
```
