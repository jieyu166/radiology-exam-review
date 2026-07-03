---
concepts: [ultrasound-display-modes]
name: Ultrasound Pulse-Echo Display Modes (A/B/M-mode)
subspecialty: [US, Physics]
aliases:
  - A-mode
  - B-mode
  - M-mode
  - real-time imaging
  - 超音波顯示模式
dateRev: 2026-07-03
nonImaging: true
nonImagingReason: "超音波顯示模式基本原理定義題，無特定病例影像特徵"
---

# ultrasound-display-modes

**超音波脈衝回音顯示模式：A-mode 一維振幅圖（振幅在縱軸、深度/時間在橫軸）、B-mode 以亮度對應回音振幅（現代二維灰階基礎）、M-mode 單一掃描線隨時間展開（橫軸時間、縱軸深度，呈現運動，常用於心臟）、real-time 每秒多幀動態呈現——A-mode 的軸向配置（振幅縱軸 vs 時間橫軸）常被對調作為考題陷阱。**

## Summary
- **A-mode（amplitude mode）**：一維影像，**振幅（amplitude）沿縱軸、深度/時間沿橫軸**；為最早的顯示模式，現多用於眼科生物測量。考題常將橫縱軸對調設陷阱。[^1]
- **B-mode（brightness mode）**：以**回音振幅對應亮點（brightness of a dot）**呈現，為現代**二維灰階影像**之基礎顯示模式。[^1][^2]
- **M-mode（motion mode）**：**單一掃描線**，**橫軸＝時間、縱軸＝深度（離探頭距離）**，用以呈現結構運動；具**優異的軸向與時間解析度**，尤常用於心臟。[^2]
- **Real-time imaging（即時成像）**：每秒多張影像幀之動態呈現，於選定區域即時更新。[^1]

## 物理原理與判讀重點
- **三模式的軸向對照（易混淆重點）**：A-mode＝振幅(y)／深度(x)；M-mode＝深度(y)／**時間(x)**；B-mode＝以亮度編碼回音強度成點，多點成線、多線成 2D 影像。**A-mode 與 M-mode 縱軸皆為深度**，差別在橫軸（A-mode 為單次深度掃描、M-mode 為時間展開）。[^1][^2]
- **回音亮度的意義**：B/M-mode 之亮點**亮度正比於反射波振幅**（反映介面聲阻抗差異），這是灰階影像的物理根基。[^2]
- **M-mode 的解析度優勢**：以**單線高幀率**取得，故**時間解析度極高**，最能刻畫高速運動結構之路徑與時序（相對於幀率受限的 2D real-time）。[^2]

## 臨床應用重點（5 句）
1. **B-mode／real-time** 是今日臨床絕大多數超音波檢查的預設模式（腹部、婦產、血管、肌骨等灰階即時掃描）。[^1]
2. **M-mode 於心臟超音波**評估瓣膜與室壁運動時序——如二尖瓣前葉最大早期擺動與室間隔之垂直距離（**E-point septal separation, EPSS**）可估算射血分數，並藉時間解析度分辨 E、A 波。[^2]
3. **M-mode 於肺部超音波**用於判斷氣胸（正常「海岸徵象 seashore」消失、氣胸呈「條碼/平流層徵象」）。[^2]
4. **A-mode 現存主要用途在眼科生物測量**（如眼軸長量測），因其一維振幅資訊對單軸距離量測精確。[^1]
5. 選擇模式取決於臨床問題：需**空間全貌**用 B-mode／real-time、需**運動時序**用 M-mode、需**單軸精密測距**用 A-mode。[^1][^2]

> [!note] 考點：關於 pulse-echo display modes 之敘述，何者錯誤？
> **A-mode 振幅/時間軸敘述相反（A）為錯誤**——A-mode 應為振幅沿縱軸、深度/時間沿橫軸，非題目所述之橫縱軸對調配置。B-mode 亮度對應回音振幅、M-mode 橫軸時間縱軸深度（呈現心臟運動）、real-time 每秒多幀動態呈現，皆為正確敘述。[^1][^2]

### 參考來源
[^1]: 官方 2020 詳解（題目所引）；原引 Hagen-Ansert SL. *Textbook of Diagnostic Sonography*. I-1-14——A-mode 一維、振幅沿縱軸/時間沿橫軸；B-mode 以亮度對應回音強度；M-mode 橫軸時間縱軸深度呈現運動（尤心臟）；real-time 每秒多幀動態——顯示模式定義，已由 [^2] Radiopaedia 一手物理條目查核並補強應用。
[^2]: **Tier 1/2** *M-mode (ultrasound)*. Radiopaedia.org（實際查證 accessed 2026-07-03）：M-mode 為單一掃描線之圖形化顯示，**abscissa（橫軸）＝時間、ordinate（縱軸）＝離探頭距離（深度）**，具優異軸向與時間解析度；亮點亮度正比於反射波振幅；臨床用於心臟（mitral valve excursion、EPSS 估 EF、E/A 波時序）與肺部（氣胸）等高速運動結構之判讀。

## 題目
> [!question]- About "the pulse-echo display modes", which of the following statement is wrong? (2020-418)
> **A-mode 敘述（A）為錯誤**——A-mode 應為振幅沿縱軸、深度/時間沿橫軸，題目敘述橫縱軸相反。B/M-mode 亮度對應回音振幅、M-mode 橫軸時間縱軸深度、real-time 每秒多幀，皆正確。[^1][^2]

## 考題
```dataview
list from #交換 where contains(concepts, "ultrasound-display-modes")
```
