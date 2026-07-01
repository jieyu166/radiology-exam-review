---
concepts: [ultrasound-attenuation]
name: Ultrasound Attenuation (Absorption + Scattering)
subspecialty: [US, Physics]
aliases:
  - attenuation
  - ultrasound attenuation
  - acoustic attenuation
  - 超音波衰減
dateRev: 2026-07-01
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
- **量化單位**：衰減係數以 **dB/cm/MHz** 表示，隨頻率近乎線性增加（故高頻解析度好但穿透差、衰減快為必然取捨）；粗略經驗值約「每公分等於發射頻率（MHz）的 dB 數」，5 MHz 探頭軟組織約 5 dB/cm。[^2] **實際組織別衰減係數差異極大**：**水 0.02 dB/cm/MHz、肝臟 0.4 dB/cm/MHz、骨骼 20 dB/cm/MHz**（水與骨骼相差約千倍），此即為何充氣肺／皮質骨後方幾乎全塌陷成聲影，而水／血液幾乎不衰減。[^3]

## 為何「衰減」是影像判讀的根本：從物理到讀片
> 此節聚焦 attenuation 如何「決定影像長相」；各偽影的逐項外觀、三型聲影與鑑別陷阱見 [[ultrasound-artifacts]]，此處不重複，只補成因橋樑。

- **判讀骨架**：機器假設聲束沿掃描線均勻衰減，並用 **TGC（time gain compensation，時間增益補償）** 依深度逐段加大增益來「拉平」深部訊號；**任何局部組織衰減偏離此假設，就在後方留下亮/暗線索**——這正是聲影與後方增強的共同來源。[^2][^3]
- **後方增強（acoustic enhancement）＝低衰減的足跡**：聲束穿過囊腫/積液等**低衰減**結構時損耗少，TGC 又照常加大深部增益 → **過度補償** → 病灶後方出現亮帶。判讀用途：**亮帶是「囊性/含液」的旁證**（與真實高回音組織區分）。[^2][^3]
- **聲影（acoustic shadowing）＝高衰減/強反射的足跡**：結石、鈣化、骨、氣體屬**高衰減**，聲束幾乎無法穿透 → 後方訊號塌陷成暗帶。判讀用途：**暗帶提示鈣化/結石/氣體**；clean/dirty/partial 三型之分見 [[ultrasound-artifacts]]。[^2][^3]
- **頻率-深度-解析度的影像取捨**：attenuation 隨頻率升高 → **高頻探頭**：淺層解析度佳但**深部因衰減快而變暗、訊號雜訊比掉、看不深**；**低頻探頭**：穿透深但軸向解析度差。讀片時若深部變暗模糊，先想「探頭頻率過高／TGC 深段未拉足」而非真病灶。[^2][^4]
- **常見讀片陷阱**：TGC 深段拉過頭會造成**假性後方增強**（非真囊腫）；高頻探頭掃深部臟器時的**深部暈暗**易被誤判為實質病灶或積液——降頻或調 TGC 後若消失即為衰減所致。[^3][^4]

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
[^2]: Grogan SP, Mount CA. *Ultrasound Physics and Instrumentation*. **StatPearls** (Internet). Treasure Island (FL): StatPearls Publishing; bookshelf ID NBK570593（教科書級章節，accessed 2026-06-30）：衰減率約「每公分 dB ≈ 發射頻率 MHz」，頻率↑→穿透↓、解析度↑（反向取捨）；TGC 為依深度補償衰減的增益控制；acoustic shadowing（高衰減/強反射體後方訊號塌陷）與 posterior acoustic enhancement（低衰減含液結構後方相對增亮）皆以衰減為機轉。https://www.ncbi.nlm.nih.gov/books/NBK570593/
[^3]: **Tier 1（全文已讀，via 個人訂閱 pubs.rsna.org，accessed 2026-07-01）** Baad M, Lu ZF, Reiser I, Paushter D. *Clinical Significance of US Artifacts*. **RadioGraphics**. 2017;37(5):1408-1423. [DOI](https://doi.org/10.1148/rg.2017160175)。重點：吸收為衰減主因，但反射、散射、波束發散亦有貢獻；吸收與散射皆隨頻率增加，故衰減係數（dB/cm/MHz）幾近線性隨頻率上升，此即高頻解析度佳但穿透差之取捨來源；**組織別衰減係數：水 0.02、肝臟 0.4、骨骼 20 dB/cm/MHz**；TGC 依回聲到達時間調整深部增益之假設與真實組織衰減之偏差，即為衰減相關偽影（後方增強＝TGC 對低衰減結構過度補償；聲影）之成因。
[^4]: Hsu P-C, Chang K-V, et al. *Artifacts in Musculoskeletal Ultrasonography: From Physics to Clinics*. **Diagnostics** (Basel). 2020;10(9):645（同行評審綜述，full-text via PMC PMC7555047）：頻率-穿透-解析度取捨、posterior enhancement 與 acoustic shadowing 之影像表現與成因。[DOI](https://doi.org/10.3390/diagnostics10090645)

## 考題
```dataview
list from #交換 where contains(concepts, "ultrasound-attenuation")
```
