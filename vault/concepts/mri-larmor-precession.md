---
concepts: [mri-larmor-precession]
name: MRI Physics — Larmor Precession Direction
subspecialty: [Physics]
aliases:
  - Larmor equation
  - precession direction
  - gyromagnetic ratio
  - 拉莫爾進動方向
dateRev: 2026-07-03
---

# mri-larmor-precession

**Larmor 方程式 ω₀ = γB₀ 描述質子磁矩向量（magnetic moment）繞外加靜磁場 B₀ 進動（precession）的角頻率——進動路徑呈『圓錐狀』環繞 B₀ 軸（如陀螺般錐狀擺動），與磁矩向量維持固定夾角，而非任意平面的擺動或偏離 B₀ 軸的路徑。** 判讀分水嶺：**磁矩 μ 因外加磁場而繞 B₀ 軸『圓錐狀』掃描（wobble/陀螺進動）；進動頻率正比於 B₀（場愈強、進動愈快）；正確方向＝與 μ 呈固定張角、繞 B₀ 軸連續圓形旋轉。**

## Summary
- **Larmor 方程式**：**ω₀ = γB₀**——ω₀＝進動（角）頻率（MHz）、γ＝旋磁比（gyromagnetic ratio，MHz/tesla；¹H 約 42.58 MHz/T）、B₀＝靜磁場強度（tesla）。[^1][^2]
- **進動本質**：質子磁矩向量繞外加磁場 B₀ **進動**，路徑呈**圓形/圓錐狀，如陀螺（spinning top）般錐狀擺動**（secondary spin / wobble），與 μ 維持固定夾角。[^1][^2]
- **頻率正比 B₀**：**場愈強、進動頻率愈高**（如 ¹H 於 1.5T ≈ 63.9 MHz、3T ≈ 127.7 MHz）；決定共振所需 RF 頻率。[^2]
- **正確進動方向**：與 μ 向量呈固定張角、以**圓錐狀**繞 B₀ 軸連續旋轉——非平面內簡單擺動、非偏離 B₀ 軸之路徑。[^1][^2]

## 放射科醫師影像判讀重點
- **陀螺類比**：磁矩像旋轉陀螺在重力下之進動——繞主軸（B₀）畫圓錐。[^2]
- **頻率-場強**：ω₀ ∝ B₀；高場 MRI 進動更快、SNR 較高、RF 頻率需相應提高。[^2]
- **共振條件**：RF 脈衝頻率須等於 Larmor 頻率才能激發（共振），是選頻/選層基礎。[^2]
- **旋磁比**：不同核種 γ 不同（¹H 最常用）；同一 B₀ 下不同核種進動頻率不同。[^2]
- **判圖要點**：選「與 μ 固定夾角、繞 B₀ 圓錐掃描」之路徑，非平面擺動。[^1]

## 臨床重點（5 句）
1. **方程式**：ω₀ = γB₀。[^1][^2]
2. **進動**：磁矩繞 B₀ 呈圓錐（陀螺）路徑。[^1][^2]
3. **頻率 ∝ B₀**：高場進動更快。[^2]
4. **共振**：RF = Larmor 頻率才激發。[^2]
5. **判圖**：固定張角繞 B₀ 圓錐掃描為正確方向。[^1]

> [!note] 考點：磁矩向量的進動(precession)方向應選擇圖中何者?
> **選項 A**——呈現與 μ 向量固定夾角、環繞 B₀ 軸的圓錐狀進動路徑，符合「陀螺般錐狀擺動」之物理定義（非平面擺動、非偏離 B₀ 軸）。[^1][^2]

### 參考來源
[^1]: 官方 2017 詳解；Ref: Magnetic Resonance Imaging: Physical Principles and Sequence Design, 1999, p.3-4（題目所引）——Larmor 方程式 ω₀=γB₀ 描述磁矩進動頻率；外加磁場使原子核產生二次自旋/搖擺，進動路徑呈圓形如陀螺般錐狀擺動環繞主磁場。
[^2]: Weerakkody Y, et al. *Larmor frequency*. Radiopaedia, rID-5855, DOI 10.53347/rID-5855——Larmor/precessional frequency＝**質子磁矩繞外加磁場 B₀ 進動之速率**；**頻率正比於 B₀ 強度（ω₀=γB₀）**；奇數質子/中子核具磁偶極矩而進動。佐證磁矩繞 B₀ 圓錐進動與頻率-場強關係。

## 題目
> [!question]- Larmor equation 表示 magnetic moment vector 的 precession frequency 與外加磁場的關係如下 ω₀=γB₀，請於下圖選擇 precession 的方向為何 (2017-331)
> **選項 A**——呈現與 μ 向量固定夾角、環繞 B₀ 軸的圓錐狀進動路徑，符合陀螺般錐狀擺動之物理定義。[^1][^2]

## 考題
```dataview
list from #交換 where contains(concepts, "mri-larmor-precession")
```
