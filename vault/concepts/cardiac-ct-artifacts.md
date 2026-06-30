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
- **Noise（quantum mottle）**：低光子量;**降低法＝iterative reconstruction**（亦可增 mAs/kVp/厚度、降 kernel 銳利度）。[^1]
- **Slab/banding artifact**：軸狀分段(slab)接合處的條帶;**成因＝掃描期間對比劑強化隨時間變化**（非 beam hardening、非 helical 模式）。[^1]

> [!note] 考點
> 降 beam-hardening＝**增 tube potential**;降 noise＝**iterative reconstruction**;slab/banding 成因＝**掃描期間對比變化**。[^1]

### 參考來源
[^1]: 官方 2017 詳解；RadioGraphics 2016;36:2064-2083：beam-hardening 用高 kVp/濾片/虛擬單能量;noise 用 iterative reconstruction;slab/banding 因掃描期間對比變化。

## 題目
> [!question]- 降低心臟 CT 的 beam-hardening artifact 用何調整? (2017-160)
> **增加 tube potential（高 kVp）**。亦可用 X 光濾片、虛擬單能量高能影像、iterative reconstruction。[^1]

> [!question]- 何種演算法可降低心臟 CT 的雜訊(noise)? (2017-161)
> **Iterative reconstruction（迭代重建）**。filtered back-projection、adaptive filtration、partial scanning 非降噪主力。[^1]

> [!question]- 心臟 CT 的 slab/banding artifact 成因? (2017-162)
> **掃描期間對比強化隨時間變化（changes in contrast enhancement over the scan duration）**。非 helical 模式、beam hardening、釓對比劑。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "cardiac-ct-artifacts")
```
