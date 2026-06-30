---
concepts: [ultrasound-tissue-interaction]
name: Ultrasound–Tissue Interaction (Impedance / Scattering)
subspecialty: [US, Physics]
aliases:
  - acoustic impedance
  - scattering echogenicity
  - reflection transmission
  - 超音波與組織交互
dateRev: 2026-06-30
same:
  - "[[ultrasound-attenuation]]"
  - "[[ultrasound-prf-depth]]"
  - "[[ultrasound-speed-artifact]]"
---

# ultrasound-tissue-interaction

**超音波在組織裡做兩件不同的事：大界面靠「聲阻抗差（impedance mismatch）」決定反射/穿透比例；各組織肉眼可見的回音紋理則靠「小界面散射（scattering/backscatter）」產生。** 記憶鉤：「大邊界靠阻抗、細紋理靠散射」——impedance 決定有多少能量能穿過去，scattering 決定肝腎脾各自看起來什麼樣。判讀分水嶺一：**acoustic impedance（Z＝密度×聲速）差 → 決定界面反射與穿透比例；差值越大反射越多（如組織/氣體、組織/骨）**；判讀分水嶺二：**各組織 echogenicity 與紋理（speckle）← backscatter（散射）；非鏡面反射（reflection）所致**。

## Summary
- **Acoustic impedance（Z＝密度×聲速）**：相鄰組織的 **impedance 差**決定該界面**反射與穿透**能量之比例（差越大反射越多）——故「造成穿透與反射差異」者＝**impedance**。[^1]（2016-074 正解 A）
- **Scattering（散射）**：超音波遇**小於波長的小界面**產生各向散射；**backscatter** 決定組織的**回音性與特徵紋理（speckle）**——故「各組織不同 echogenicity 之主因」＝**scattering**。[^1]（2016-075 正解 C）
- 對照：**reflection**（鏡面，大平滑界面）、**refraction**（折射，方向改變）、**diffraction**（繞射）——非組織紋理之主因。[^1]
- **影像判讀關聯——鏡面 vs 散射回音**：大而平滑的界面（橫膈、膀胱壁、骨皮質）產生**鏡面反射（specular）**，回音強且具角度依賴性（探頭需近垂直才接收得到，傾斜即訊號掉落＝anisotropy）；實質臟器內無數小於波長的小界面則以**backscatter（散射）**產生角度較不敏感的均勻 speckle 紋理，肝/腎/脾因散射特性不同而有各自 echogenicity。[^2]
- **影像判讀關聯——折射造成的定位誤差**：超音波斜射過兩側聲速不同的界面時依 Snell's law 改變方向，機器仍假設聲束直行，故把回波**錯位（mispositioning）**，並在大曲面（囊腫、膽囊、胎兒頭顱）邊緣兩側形成沿軸向延伸的**邊緣陰影（edge shadow／edge artifact）**——與 [[ultrasound-artifacts]] 的折射型 artifact 為同一物理機制（此處談機制，artifact 影像表現詳該筆記）。[^2]
- 相關：能量總損耗＝[[ultrasound-attenuation]]（吸收＋散射＋反射）。

> [!note] 兩考點
> ①「穿透 vs 反射差異」← **impedance**（界面聲阻抗差）。②「各組織不同 echogenicity」← **scattering**（小界面 backscatter）。[^1]

### 參考來源
[^1]: 超音波物理經實際查證（accessed 2026-06-17，Radiopaedia *acoustic impedance* / *scattering*）：impedance 失配決定界面反射/穿透；組織回音性/紋理（speckle）源自小界面 backscatter（散射）。與 [[ultrasound-attenuation]] 互補。
[^2]: 超音波物理章節經查證（accessed 2026-06-30）。Radiology Key, *Physics of Ultrasound*（textbook chapter mirror，<https://radiologykey.com/physics-of-ultrasound-2/>）：acoustic impedance＝tissue density × propagation speed；反射能量正比於兩側 impedance 差。「Specular reflection occurs when the sound waves encounter large smooth surfaces… reflected back in a relatively uniform direction」，斜射時依 Snell's law 折射、放射師接收不到回波而產生 anisotropy；「Scatter refers to the propagation of incident sound waves in oblique directions… the random image pattern created by backscatter is termed speckle」。折射型錯位/邊緣陰影之影像表現另見 RadioGraphics ultrasound artifacts 教學（Feldman MK, et al. *US artifacts.* RadioGraphics 2009;29(4):1179–89，DOI 10.1148/rg.295085199，refraction/edge-shadow 段落）。

## 考題
```dataview
list from #交換 where contains(concepts, "ultrasound-tissue-interaction")
```
