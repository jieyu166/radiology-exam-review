---
concepts: [ultrasound-attenuation]
name: Ultrasound Attenuation (Absorption + Scattering)
subspecialty: [US, Physics]
aliases:
  - attenuation
  - ultrasound attenuation
  - acoustic attenuation
  - 超音波衰減
dateRev: 2026-06-14
same:
  - "[[ultrasound-prf-depth]]"
  - "[[ultrasound-speed-artifact]]"
---

# ultrasound-attenuation

**Attenuation（衰減）是超音波前進時「吸收＋散射」造成的能量總損耗，也是高頻探頭看得清楚但看不深的原因。** 記憶鉤：把超音波想成「跑步的訊號」——組織的阻礙（吸收成熱＋散射偏向）讓它越跑越弱，頻率越高跑越累（attenuation 係數隨頻率升高）；只有水和血液幾乎不阻礙它。判讀分水嶺一：**散射（scattering）＋吸收（absorption）的合併效應＝attenuation；勿與 acoustic impedance（決定界面反射比例）或 propagation（傳播行進）混淆**；判讀分水嶺二：**attenuation coefficient 隨頻率增加 → 高頻：解析度佳、穿透淺；低頻：穿透深、解析度差**。

## Summary
- **定義**：波在組織中傳播時，**振幅與強度隨深度遞減**的現象，即 attenuation。[^1]
- **組成**：反射、折射/繞射、**散射（scattering）**、**吸收（absorption）**、干涉等共同造成；其中**吸收（能量轉為熱）是主要貢獻**。[^1]
- **題目重點**：「散射與吸收的合併效應」＝ **attenuation**（衰減）。[^1]
- **頻率相依**：**attenuation coefficient 隨頻率升高而增加**——高頻 → 衰減快、穿透淺；低頻 → 穿透深、解析度差（時間增益補償 TGC 用以校正深部訊號衰減）。[^1]
- **組織差異**：衰減係數最高為**充氣肺、皮質骨**（近乎不透聲）；最低為**水、血液**；軟組織/肌肉介於其間。[^1]

## 易混概念辨異（常考干擾選項）
| 名詞 | 定義 | 與 attenuation 的差別 |
| --- | --- | --- |
| **Attenuation（答案）** | 振幅/強度遞減 = 吸收＋散射＋反射 | 「散射＋吸收的合併效應」即此[^1] |
| **Acoustic impedance** | Z = 密度 × 傳播速度 | 決定**界面反射**多寡，非能量損耗總和[^1] |
| **Propagation** | 波在介質中的傳播（含傳播速度）| 指「行進」本身，非「衰減」 |
| **Shear（剪力）** | 剪力波（彈性造影用）| 與散射＋吸收的合併損耗無關 |

> [!note] 一句話記憶
> **散射 + 吸收（+反射）的合併能量損耗 = attenuation**；別跟 impedance（界面反射）或 propagation（傳播）混。[^1]

### 參考來源
[^1]: *Attenuation (ultrasound)*. Radiopaedia.org, rID-67529, https://doi.org/10.53347/rID-67529 （引 Hedrick《Technology for Diagnostic Sonography》等；實際查證 accessed 2026-06-14）。

## 考題
```dataview
list from #交換 where contains(concepts, "ultrasound-attenuation")
```
