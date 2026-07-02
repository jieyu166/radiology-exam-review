---
concepts: [cardiac-ct-artifacts]
name: Cardiac CT Artifacts & Image Quality
subspecialty: [CV, Physics]
aliases:
  - cardiac CT artifacts
  - beam hardening
  - slab banding artifact
  - iterative reconstruction noise
  - 心臟CT假影
dateRev: 2026-06-19
---

# cardiac-ct-artifacts

**心臟 CT 影像品質：beam-hardening 用『高 kVp/濾片/虛擬單能量』降低、noise 用『迭代重建』降低、slab/banding 因『掃描期間對比變化』。** 判讀分水嶺一：**beam-hardening（鈣化/對比劑旁暗紋）→ 增 tube potential(kVp)、X 光濾片、虛擬單能量高能影像、iterative recon**;判讀分水嶺二：**quantum mottle(noise)→ 增 mAs/kVp/厚度、降 kernel 銳利度、『iterative reconstruction』;slab/banding artifact → 掃描期間 contrast enhancement 變化（多 slab 接合處）**。

## Summary
- **Beam-hardening artifact**：鈣化/高對比旁的暗紋;**降低法＝增 tube potential(高 kVp)、X 光 beam filtration、虛擬單能量高能影像、iterative reconstruction**。[^1]
- **非心臟部位範例（後顱窩岩骨間暗帶）**：兩側緻密岩骨(petrous bone)間之黑色帶狀假影(dark band artifact)亦為典型beam hardening artifact——X光束通過高密度骨質後低能光子被優先吸收、能譜偏移，可用**calibration correction + iterative beam hardening correction**降低。[^3]
- **Noise（quantum mottle）**：低光子量;**降低法＝iterative reconstruction**（亦可增 mAs/kVp/厚度、降 kernel 銳利度）。[^1]
- **Slab/banding artifact**：軸狀分段(slab)接合處的條帶;**成因＝掃描期間對比劑強化隨時間變化**（非 beam hardening、非 helical 模式）。[^1]

> [!note] 考點
> 降 beam-hardening＝**增 tube potential**;降 noise＝**iterative reconstruction**;slab/banding 成因＝**掃描期間對比變化**。[^1]

## 增加 tube potential 可改善哪些偽影（2018-178）
- **可被增加 tube potential 改善**：beam hardening（高衰減結構旁暗亮條紋）、metal/streak artifact（金屬旁條紋/風車偽影）、quantum mottle（低光子計數之顆粒感雜訊）——三者皆列於文獻中「增加 tube potential」為改善對策之一。[^2]
- **不會被增加 tube potential 改善：slab/banding artifact**——此偽影成因為**掃描期間對比劑強化程度隨時間變化**（多見於分段拼接處），與光子能量/劑量無關，須靠**增加每心週期 z 軸覆蓋範圍、減少所需成像心週期數、維持均勻對比強化程度**等技術對策，而非調整 tube potential。[^2]

### 參考來源
[^1]: 官方 2017 詳解；RadioGraphics 2016;36:2064-2083：beam-hardening 用高 kVp/濾片/虛擬單能量;noise 用 iterative reconstruction;slab/banding 因掃描期間對比變化。
[^2]: *Artifacts at Cardiac CT: Physics and Solutions.* RadioGraphics 2016;36:page 2066（2018 交換考題詳解 p.72 引用；Tier 1）。Beam hardening、metal/streak artifact、quantum mottle 皆可由增加 tube potential 改善；slab/banding 成因為掃描期間對比劑強化變化，改善靠增加每心週期 z 覆蓋範圍/減少心週期數/維持均勻對比強化，與 tube potential 無關。
[^3]: 官方2020詳解；Ref: Bushberg JT et al., The Essential Physics of Medical Imaging, 3rd Ed., 2011, p.367-368（題目所引）；RadioGraphics 2004——後顱窩岩骨間黑色帶狀假影為beam hardening artifact，可用calibration correction + iterative beam hardening correction降低。

## 題目
> [!question]- 降低心臟 CT 的 beam-hardening artifact 用何調整? (2017-160)
> **增加 tube potential（高 kVp）**。亦可用 X 光濾片、虛擬單能量高能影像、iterative reconstruction。[^1]

> [!question]- 何種演算法可降低心臟 CT 的雜訊(noise)? (2017-161)
> **Iterative reconstruction（迭代重建）**。filtered back-projection、adaptive filtration、partial scanning 非降噪主力。[^1]

> [!question]- 心臟 CT 的 slab/banding artifact 成因? (2017-162)
> **掃描期間對比強化隨時間變化（changes in contrast enhancement over the scan duration）**。非 helical 模式、beam hardening、釓對比劑。[^1]

> [!question]- 於電腦斷層掃描影像中，造成後顱窩中岩骨(petrous bone)間的黑色帶狀假影的原因為何？(2020-414)
> **射束硬化（beam hardening，A）**。[^3]

## 考題
```dataview
list from #交換 where contains(concepts, "cardiac-ct-artifacts")
```
