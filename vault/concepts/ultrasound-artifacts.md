---
concepts: [ultrasound-artifacts]
name: Ultrasound Artifacts (Mirror, Ring-down, Refraction, Aliasing)
subspecialty: [US, Physics]
aliases:
  - ultrasound artifacts
  - aliasing
  - ring down artifact
  - mirror artifact
  - 超音波偽影
dateRev: 2026-06-17
same:
  - "[[ultrasound-speed-artifact]]"
  - "[[ultrasound-attenuation]]"
---

# ultrasound-artifacts

**超音波五種偽影各有成因：posterior enhancement（後方衰減少→增強）、mirror（強反射面照出鏡像）、ring-down（氣泡共振→後方連續亮線）、refraction（腹直肌-脂肪界面折射）、aliasing（都卜勒頻移超過 Nyquist 極限→波形反摺）。** 記憶鉤：aliasing 最容易考錯方向——「取樣率小於兩倍頻移（PRF < 2×頻移）」時才發生，題目若說「取樣率多於兩倍頻移」則是錯的。判讀分水嶺一：**ring-down 氣體/金屬共振、mirror 強反射鏡像、refraction 最常見於腹直肌-腹內脂肪界面**；判讀分水嶺二：**aliasing＝頻移 > PRF/2（Nyquist），即 PRF（取樣率）< 2×頻移——注意大小於方向不可記反**。

## Summary
- **Posterior enhancement**：病灶衰減少於周邊軟組織→後方回音增強。[^1]
- **Mirror artifact**：強反射面（**骨、頸動脈後壁**等）使結構在鏡像位置重複出現（含 color Doppler）。[^1]
- **Ring-down**：**氣泡/氣體**使超音波引起**共振振動**→後方連續高回音帶（金屬亦可）。[^1]
- **Refraction**：聲束於不同聲速介面折射;**最常見於腹直肌與腹內脂肪交界**。[^1]
- **Aliasing（都卜勒）**：當**都卜勒頻移 > Nyquist 極限（＝PRF 的一半）**時發生,即**取樣率(PRF)『小於』兩倍頻移**;表現為頻譜/彩流反摺。[^1]

> [!warning] 兩題重點
> - **2016-192 正解 E**：A 後方增強、B mirror、C ring-down、D refraction 描述**皆正確** → 「none of above（無錯誤）」。
> - **2016-193 正解 C**：Aliasing 的描述「occurs when sampling rate is **more than** twice the Doppler shift」**錯**——應為**取樣率『小於』兩倍頻移（頻移超過 Nyquist=PRF/2）**才 aliasing。A（ring-down 氣體/金屬）、B（partial torsion 高阻力波形）皆正確。

### 參考來源
[^1]: 超音波偽影標準物理教學（mirror／ring-down／refraction／posterior enhancement／aliasing）。**Aliasing 依 Nyquist：頻移 > PRF/2（取樣率 < 2×頻移）時發生**;ring-down＝氣泡共振;refraction 常見腹直肌-腹脂交界。相關速度/衰減偽影見 [[ultrasound-speed-artifact]]、[[ultrasound-attenuation]]。

## 題目
> [!question]- Aliasing 何時發生?（193 關鍵）
> 當**都卜勒頻移超過 Nyquist 極限（PRF 的一半）**,即**取樣率(PRF)小於兩倍頻移**時發生。提高 PRF/scale、降頻、增大角度、改基線可緩解。[^1]

> [!question]- ring-down 與 mirror 偽影的機轉?
> **ring-down＝氣泡/氣體共振**→後方連續高回音;**mirror＝強反射面（骨/血管後壁）**使結構鏡像重複。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "ultrasound-artifacts")
```
