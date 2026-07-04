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

## 技術要點
- **強度—kVp 平方律**：X 光管輸出強度（exposure/intensity）與管電壓的**平方（kVp²）**成正比，故 kVp 小幅提高即顯著增加輸出。[^1]
- **強度—mAs 線性**：與管電流×曝光時間（mAs）成**線性正比**，mAs 加倍則強度加倍；記憶鉤「電壓平方、電流時間一次方」。[^1]
- **計算範例（考題）**：110 kVp/10 mAs→32 mR，改 125 kVp（mAs 不變）→ 32 × (125/110)² ≈ 32 × 1.291 ≈ **41 mR**。[^1]
- **比值套用步驟**：新強度 = 原強度 × (新kVp/原kVp)² × (新mAs/原mAs)；僅變 kVp 時 mAs 比值為 1，只需平方項。[^1]
- **臨床意涵**：提高 kVp 兼增穿透力與輸出，惟同時降低影像對比；調整曝光參數需權衡劑量、對比與雜訊。[^2]

> [!note] 考點：側面胸部110 kVp/10 mAs產生32 mR，改為125 kVp時X光強度？
> **41 mR（B）**——X光強度與kVp²成正比：32 × (125/110)² ≈ 41 mR。[^1]

### 參考來源
[^1]: 102年第一次專門職業及技術人員高等考試 放射師考試（2018 交換考題詳解 p.289 引用；Tier 2/3 國考題）。X光強度與管電壓平方(kVp²)成正比、與mAs線性正比；32×(125/110)²≈41 mR。
[^2]: **Tier 1** McCollough CH. *The AAPM/RSNA physics tutorial for residents. X-ray production*. RadioGraphics 1997;17(4):967-84（據 PubMed，DOI [10.1148/radiographics.17.4.9225393](https://doi.org/10.1148/radiographics.17.4.9225393)；實際查證 accessed 2026-07-05）——X 光經 bremsstrahlung 與 characteristic 兩機轉產生；**X 光量（quantity）與管電壓平方（tube potential squared）、管電流、曝光時間及陽極原子序成正比，與距離平方成反比**；亦受電壓波形（generator type）與濾器影響。佐證本卡強度 ∝ kVp²、∝ mAs 之量化關係；原 Tier-2/3 國考題引用已由本 RadioGraphics DOI Tier 1 查核升級。

## 題目
> [!question]- 某個側面胸部照射使用110 kVp/10 mAs，產生強度為32 mR的X光，如果將電壓改變成125 kVp時，其X光強度是? (2018-379)
> **41 mR（B）**——X光強度∝kVp²，32×(125/110)²≈41 mR。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "xray-tube-output")
```
