---
concepts: [hrct-lung-technique]
name: HRCT of the Lung — Technique
subspecialty: [CH, Physics]
aliases:
  - HRCT
  - high resolution CT lung
  - 高解析度電腦斷層
dateRev: 2026-07-03
---

# hrct-lung-technique

**肺部 HRCT 用『銳利（hard/sharp）重組 kernel』來凸顯細微結構,不是用平滑 kernel 降噪;薄切（約 0.625–1.25 mm）、吸氣＋必要時吐氣相,主要用於評估瀰漫性肺病。** 判讀分水嶺：**重組 kernel 是空間解析度與雜訊的取捨——肺／骨等要找小而離散的特徵（骨折、結節、細網狀）用 sharp kernel 凸顯邊緣（代價噪訊高）;腦／腹部等軟組織用 soft kernel 降噪。HRCT 選 sharp 而非 smooth,故「用 ultra-smooth kernel 降噪」是錯的。**

## Summary
- **重組 kernel**：HRCT 用 **sharp（hard）kernel** 凸顯肺實質細微結構（細網狀、結節、支氣管壁、小葉間隔）;**非** ultra-smooth kernel。[^1]
  - Sharp kernel：空間解析度高、邊緣銳利,**代價是影像雜訊高**;適合肺、骨等高對比解剖。
  - Soft kernel：降噪、影像平滑,適合腦／腹部等低對比軟組織。
- **切片厚度**：薄切約 **0.5–0.625 mm**（現代掃描器）至 1.25 mm。[^1][^2]
- **呼吸相**：**全吸氣**為主,必要時加**吐氣相**偵測 air trapping。[^1]
- **主要角色**：評估**瀰漫性肺病**（ILD、emphysema、bronchiectasis、small airways disease）。[^1][^3]

## 技術要點（Kazerooni）
- **三支柱**：**薄切（≤1–1.5 mm）＋high-spatial-frequency（sharp/bone）重組演算法＋足夠 kVp/mAs**，以最大化空間解析度顯示次級肺小葉層級結構。[^3]
- **補充相位**：**吐氣相**偵測 air trapping（小氣道病）、**俯臥相**區分下肺墜積性變化（dependent atelectasis）與早期纖維化。[^3]
- **陷阱（Kazerooni）**：**sharp kernel 雖解析度高但影像雜訊高**——不可為降噪改用 smooth kernel（會犧牲細微結構顯示）；呼吸/運動假影與 dependent opacity 為常見誤判源。[^3]

> [!note] 考點：關於肺部 HRCT,何者「不正確」?
> 「**用 ultra-smooth kernel 來降噪**」不正確——HRCT 用 **sharp（hard）kernel** 凸顯細微結構（噪訊較高但解析度佳）。吸／吐氣相、0.625–1.25 mm 薄切、主用於瀰漫性肺病皆正確。[^1]

### 參考來源
[^1]: 官方 2017 詳解；Elicker BM, Webb WR. *Fundamentals of High-Resolution Lung CT*, p.10：HRCT 用 sharp/hard 重組 kernel 凸顯肺與骨等小而離散特徵(代價噪訊高),軟組織用 soft kernel 降噪;薄切、吸／吐氣相、主評估瀰漫性肺病。
[^2]: Weerakkody Y, et al. *HRCT chest (protocol)*. Radiopaedia, rID-68126, DOI 10.53347/rID-68126（輔助來源）——**現代掃描器以 0.5–0.625 mm 薄切 + sharp reconstruction algorithm 取得 HRCT**；ILD 時另加**吐氣相、俯臥相**輔助——佐證 HRCT 用 sharp（非 smooth）kernel、薄切、吐氣相。
[^3]: **Tier 1** Kazerooni EA. *High-resolution CT of the lungs*. AJR Am J Roentgenol 2001;177(3):501-19（據 PubMed，DOI [10.2214/ajr.177.3.1770501](https://doi.org/10.2214/ajr.177.3.1770501)；Review；實際查證 accessed 2026-07-04）——肺 HRCT 技術與判讀之經典綜述：**薄切（≤1–1.5 mm）＋high-spatial-frequency（sharp/bone）重組演算法**以顯示次級肺小葉層級結構，**吐氣相偵測 air trapping、俯臥相區分墜積性變化與早期纖維化**；並討論 sharp kernel 之高雜訊代價與呼吸/dependent opacity 等假影陷阱。佐證 HRCT 用 sharp（非 smooth）kernel、薄切、吐/俯臥相之技術要點。原「官方/Radiopaedia」弱來源已由本次 AJR DOI Tier 1 查核升級。

## 題目
> [!question]- 關於肺部 high resolution CT,何者「不正確」? (2017-178)
> 「**用 ultra-smooth kernel 降噪**」不正確——HRCT 用 **sharp（hard）kernel** 凸顯細微結構。吸／吐氣相、0.625–1.25 mm 薄切、主用於瀰漫性肺病皆正確。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "hrct-lung-technique")
```
