---
concepts: [ultrasound-reflection-scatter]
name: Ultrasound Reflection, Scatter, and Turbulent Flow
subspecialty: [US, Physics]
aliases:
  - specular reflection
  - Rayleigh scatter
  - Reynolds number
  - turbulent flow ultrasound
  - 超音波反射散射
dateRev: 2026-07-01
---

# ultrasound-reflection-scatter

**聲波垂直（90度角）撞擊大而平滑的界面時發生鏡面反射（specular reflection）；預測流體是否呈紊流（turbulent flow）最一致的指標是雷諾數（Reynolds number），而非都卜勒偏移、阻力指數或壓力梯度。**

## Summary
- **鏡面反射（specular reflection）**：聲波以**90度角**撞擊**大而平滑**的界面時發生的反射型態；相對地，**nonspecular（diffuse）reflection** 發生於粗糙界面，**Rayleigh's scatter** 則發生於遠小於波長的散射體（如紅血球）。[^1]
- **紊流最一致的預測指標**：**雷諾數（Reynolds number）**——流體力學中量度慣性力與黏性力比值的無量綱量；雷諾數越大，流場越不穩定、越易形成紊亂不規則之紊流。都卜勒偏移、阻力指數（RI）、壓力梯度雖與血流異常相關，但**並非預測紊流最一致的指標**。[^2]

## 放射科醫師影像判讀重點
- **反射型態決定影像外觀**：大而平滑界面（如橫膈、膀胱壁）的**鏡面反射**具角度依賴性，聲束需近垂直才回波強、邊界清晰;紅血球等遠小於波長的散射體以 **Rayleigh 散射**產生瀰漫低回聲，是血流可被都卜勒偵測的物理基礎。[^3]
- **層流 vs 紊流的頻譜表現**：正常層流呈**窄頻譜、收縮期有清晰頻譜窗（spectral window）**;紊流時流速分佈變寬 → **頻譜增寬（spectral broadening）、窗填實**，是狹窄下游的判讀線索。[^3]
- **狹窄處的整合判讀**：頻譜都卜勒對狹窄的速度剖面改變（收縮／舒張速度、增寬）比彩色影像更敏感;報告狹窄應**整合彩色（定位混疊／花色血流）與頻譜（量化速度、增寬）** 兩者。[^3]

## 技術要點
- **取樣避免偽影**：都卜勒需足夠取樣才不落入陷阱——脈衝重複頻率（PRF）過低會**混疊（aliasing）**，角度校正錯誤會使速度量測失真;判讀速度前先確認取樣角度 ≤60°、基線與尺標設定正確。[^3]
- **鏡面反射的角度依賴**：欲最佳化平滑界面回波，聲束應盡量垂直入射;評估血流則相反——都卜勒角越接近 0°（平行血流）頻移越大、越準。[^3]

## 陷阱
- 「都卜勒偏移」或「阻力指數」常被誤認為紊流的最佳預測指標——實際上這些反映血流速度或波形特徵，紊流的物理本質仍以雷諾數（慣性力/黏性力比值）判定最一致。[^2]

### 參考來源
[^1]: 2019 交換考詳解；Sonography Exam Review: Physics, Abdomen, Obstetrics and Gynecology, Edition 2, p.36。
[^2]: 2019 交換考詳解；Sonography Exam Review: Physics, Abdomen, Obstetrics and Gynecology, Edition 2, p.76。
[^3]: **Tier 1** Grenier N, Basseau F, Rey MC, LaGoarde-Segot L. *Interpretation of Doppler signals*. Eur Radiol 2001;11(8):1295-1307（據 PubMed，DOI [10.1007/s003300100913](https://doi.org/10.1007/s003300100913)；實際查證 accessed 2026-07-04）——European Radiology 回顧:結合彩色與頻譜都卜勒提供血流動力學與血管壁／管徑資訊;頻譜波形對狹窄之速度剖面改變（如頻譜增寬）較彩色影像更敏感;需足夠取樣以避免判讀頻譜與彩色影像時的陷阱。原「官方/物理考試手冊」弱來源已由本次 DOI Tier 1 查核升級（惟超音波物理之雷諾數／散射基礎屬物理學範疇，PubMed 收錄有限，物理定義仍以物理教材為準）。

## 考題
```dataview
list from #交換 where contains(concepts, "ultrasound-reflection-scatter")
```
