---
concepts: [ct-attenuation-hounsfield-units]
name: CT Attenuation — Hounsfield Units
subspecialty: [Physics]
aliases:
  - Hounsfield units
  - HU
  - CT attenuation
  - normal lung parenchyma HU
  - 電腦斷層衰減值
nonImaging: true
nonImagingReason: "CT物理基礎原理，非個案影像判讀"
dateRev: 2026-07-10
---

# ct-attenuation-hounsfield-units

**CT 值（Hounsfield unit, HU）是「衰減係數經線性轉換」所得之無因次量（水=0、空氣=−1000 HU），並非直接等同物理密度（衰減還受原子序、光子能量影響）。以 Godfrey Hounsfield 單獨命名——他與 Allan Cormack 共獲 1979 諾貝爾醫學獎，但 CT 值僅冠 Hounsfield 一人之名。** 判讀分水嶺：**HU 是相對水/空氣的標準化刻度（線性轉換），不是密度；記關鍵值——正常肺 −700~−950、冠狀 CTA 最佳血管內強化 250-300 HU（非 800）、鈣化斑塊 >130 HU。**

## Summary
- **本質（線性轉換）**：HU 由**測量之衰減係數經線性轉換**而得：**HU = 1000 ×（μ − μ_water）/（μ_water − μ_air）**；**水 = 0 HU、空氣 = −1000 HU**（任意指定基準）。[^1][^2]
- **非直接密度**：HU **不等同物理密度**——衰減係數尚受**原子序、光子能量**影響（衰減 ≠ 密度）。[^1][^2]
- **能量依存（kVp 效應）**：診斷能量範圍內衰減由**光電效應（∝ Z、與光子能量 E 成反比）與康普頓散射**共同決定；**提高管電壓（keV/kVp）使光束變硬、低能光子被優先衰減之效應減弱**，故**骨、碘等高原子序物質之衰減與 HU 隨 kVp 上升而「下降」**（非上升）——此為雙能量/光子計數 CT 物質分解之物理基礎。[^4]
- **CT 影像本質**：CT 影像呈現的是**X 光衰減（X-ray attenuation）之空間分布**，並非 X 光穿透率、像素質量或體素密度本身。[^1][^4]
- **命名**：以 **Sir Godfrey Hounsfield**（CT 發明者、1979 諾貝爾醫學獎）**單獨命名**；Allan Cormack 亦獨立發明並共獲諾貝爾獎，但 CT 值未冠其名（非「唯一發明者」）。[^1]
- **刻度範圍**：空氣 −1000、多數軟組織 −100~+100、緻密骨（耳蝸）約 2000、金屬 >3000 HU。[^2]
- **關鍵臨床值**：**正常肺實質 −700~−950 HU**；**冠狀動脈 CTA 最佳血管內強化約 250-300 HU**（非 800），以區分低密度粥狀斑塊（~40）、纖維斑塊（~90）、鈣化斑塊（>130）。[^1]
- **Agatston 鈣化分數**：0（無）/1-10（minimal）/11-100（mild）/101-400（moderate）/>400（severe）；**>160 分 MACE 風險升高**。[^1]
- **視窗寬度（window width, WW）＝顯示的 CT 值範圍**：WW 越寬顯示的 HU 範圍越大、對比越低。**寬窗（wide window, ~400–2000 HU）用於「同一影像內衰減差異極大」的區域**（空氣與血管／皮質骨並列），故**肺窗 WW 最寬（典型 W:1500 L:−600）**；相較之下腦窗 W:80、縱膈 W:350、肝窗 W:150 皆為窄窗，用於衰減相近的軟組織。故各選項中「胸部肺窗」使用的 window width 最大。[^5]
- **典型 WW/WL 值**：腦 W80 L40、縱膈 W350 L50、肺 W1500 L−600、肝 W150 L30、骨窗 W1800 L400、顳骨 W2800–4000 L600–700（隨機構／廠商略異）。[^5]

## 放射科醫師影像判讀重點
- **量測概念**：HU 是相對水/空氣的標準化值，同一組織在不同 kVp 可略有差異（雙能量 CT 利用此特性）。[^2]
- **顯示 ≠ 數值**：影像明暗由 window/level 決定，與底層 HU 分開；量測要用 ROI 讀實際 HU。[^2]
- **常用閾值**：脂肪負 HU（−100~−50）、單純液體 ~0、急性血 +50~+70、鈣化/骨/對比劑數百以上——用於病灶定性。[^2]
- **冠狀 CTA**：目標管腔強化 250-300 HU 兼顧斑塊對比；**過高之 over-opacification（>500 HU）會遮蔽鈣化/斑塊評估**，故對比劑劑量宜依體重/BMI/心率個別化以降低過度強化。[^1][^3]
- **陷阱**：把 HU 直接當密度、或忽略 kVp/能量對 HU 的影響，是常見物理誤區。[^1][^2]

## 臨床重點（5 句）
1. **定義**：HU＝衰減係數線性轉換，水 0、空氣 −1000。[^1][^2]
2. **非密度**：受原子序/光子能量影響，HU ≠ 物理密度。[^1]
3. **命名**：僅冠 Hounsfield（Cormack 共獲諾貝爾但無冠名）。[^1]
4. **關鍵值**：肺 −700~−950、冠狀 CTA 250-300、鈣化 >130。[^1]
5. **Agatston**：分級 + >160 分 MACE 風險增加。[^1]

> [!note] 考點：關於CT attenuation何者正確？
> **正常肺實質約 −700 至 −950 HU（D）**——正確。HU 以 Hounsfield 單獨命名（非唯一發明者，A 誤）；HU 為衰減係數之線性轉換、非直接與物理密度線性相關（B 誤）；冠狀動脈 CTA 最佳血管內強化約 250-300 HU 非 800（C 誤）。[^1][^2]

### 參考來源
[^1]: 官方 2020 詳解；Ref: Weissleder R, et al. Primer of Diagnostic Radiology, 5th ed., p.4（題目所引）——HU 以 Hounsfield 命名（Cormack 共獲諾貝爾但 CT 值未冠其名）；HU 為衰減係數經線性轉換、非直接等同密度；冠狀 CTA 最佳血管內強化 250-300 HU；正常肺 −700~−950 HU；Agatston 分級（0/1-10/11-100/101-400/>400）、>160 分 MACE 風險增加。
[^2]: *Hounsfield unit*. Radiopaedia.org, rID-38181, DOI 10.53347/rID-38181（輔助來源）——HU 為無因次量、**衰減係數之線性轉換**；**水 = 0、空氣 = −1000 HU**（任意指定）；刻度 −1000（空氣）、−100~+100（多數組織）、~2000（緻密骨）、>3000（金屬）；顯示由 window/level 決定。
[^3]: **Tier 1** Zhu X, Zhu Y, Xu H, et al. *An individualized contrast material injection protocol with respect to patient-related factors for dual-source CT coronary angiography*. Clin Radiol 2013;69(2):e86-92（據 PubMed，DOI [10.1016/j.crad.2013.09.018](https://doi.org/10.1016/j.crad.2013.09.018)，實際查證 accessed 2026-07-03）——冠狀動脈 CTA 之對比劑注射協定依 **體重/BMI/心率個別化**可降低個體差異與**動脈過度強化（over-opacification，定義為衰減 >500 HU）之發生率**；佐證本檔「冠狀 CTA 目標強化 250-300 HU、過高遮蔽鈣化」之臨床要點。原「官方詳解／Radiopaedia only」弱來源已由本次期刊查核升級。
[^4]: **Tier 1（RadioGraphics）** Leng S, Bruesewitz M, Tao S, Rajendran K, Halaweish AF, Campeau NG, Fletcher JG, McCollough CH. *Photon-counting Detector CT: System Design and Clinical Applications of an Emerging Technology*. RadioGraphics 2019;39(3):683-702（DOI [10.1148/rg.2019180115](https://doi.org/10.1148/rg.2019180115)，STATdx/RSNA 全文查證 accessed 2026-07-05）——CT 衰減物理：診斷能量範圍內以**光電效應（衰減 ∝ 有效原子序 Z、與光子能量 E 成反比）與康普頓散射**為主；因使用多能量（polyenergetic）光束，穿過物體時**低能光子被優先衰減、有效能量往高端位移（beam hardening）**，並影響鄰近軟組織之 **CT 值準確度**——支持本檔「HU 受光子能量/kVp 影響、高 Z 物質（骨/碘）HU 隨管電壓上升而下降」及「CT 影像呈現的是 X 光衰減分布」之要點。
[^5]: **Radiopaedia（公開）**：*Windowing (CT)*. rID-52108（DOI [10.53347/rID-52108](https://doi.org/10.53347/rID-52108)），https://radiopaedia.org/articles/windowing-ct （accessed 2026-07-10）。window width＝影像中 CT 值的顯示範圍，寬窗顯示更寬範圍、對比較低；**寬窗（400–2000 HU）用於衰減差異大的區域（肺、皮質骨）**，窄窗（50–350 HU）用於衰減相近之軟組織；典型值 腦 W80/L40、肺 W1500/L−600、縱膈 W350/L50、肝 W150/L30、骨 W1800/L400。佐證「肺窗 window width 最寬」之考點。

## 題目
> [!question]- About CT attenuation, which one is CORRECT (2020-307)
> **Normal lung parenchyma is about −700 to −950 HU（D）**——正確。HU 以 Hounsfield 單獨命名（非唯一發明者）、HU 非直接與物理密度線性相關（為衰減係數之線性轉換）、冠狀 CTA 最佳血管內強化約 250-300 HU 非 800，其餘皆錯。[^1][^2]

> [!question]- 有關 Hounsfield Units (HU) 的敘述，何者正確？（2022-297）
> A. HU的單位與衰減係數 (attenuation coefficient) 相同，皆為 cm⁻¹
> B. 一般來說，掃描參數 tube voltage (keV) 設定越高，骨骼的 HU 數值也越高
> C. 水的 HU 數值為0，是反覆觀測的經驗數值
> D. 空氣的 HU 數值為 -1000，是被定義的
>
> **答案：D**。空氣 −1000 HU 與水 0 HU 皆為 **HU 定義式所指定之基準**（HU = 1000×(μ−μ_water)/(μ_water−μ_air)），非經驗觀測值（C 誤、D 正確）。HU 為經線性轉換之**無因次量**，與衰減係數（單位 cm⁻¹）單位不同（A 誤）。提高管電壓（kVp）使光束變硬、光電效應（∝Z、與能量成反比）減弱，**骨骼等高原子序物質之衰減與 HU 反而下降**，非上升（B 誤）。[^1][^2][^4]

> [!question]- CT images depict patterns of:（2022-351）
> A. X-ray attenuation（X-ray transmission / Pixel mass / Voxel density）
>
> **答案：A（X-ray attenuation）**。CT 影像重建呈現的是各體素之**X 光衰減（衰減係數）空間分布**，再以 HU 線性轉換顯示；並非 X 光穿透率、像素質量或體素密度本身。[^1][^2][^4]

> [!question]- CT images depict patterns of:（2022-405）
> A. X-ray attenuation（X-ray transmission / Pixel mass / Voxel density）
>
> **答案：A（X-ray attenuation，關鍵）**。CT 重建各體素之衰減係數（μ）空間分布並以 HU 線性轉換顯示；X 光穿透率（transmission）是偵測器原始量、非影像所呈現的量，pixel mass／voxel density 亦非直接呈現量。[^1][^2][^4]

> [!question]- Which CT image most likely uses the greatest display window width? (2021-107)
> **C（Chest lung，肺窗）——正確答案。** window width 是顯示的 CT 值範圍；**肺內空氣與血管衰減差異極大，需最寬的視窗（典型 W:1500 HU）**才能同時顯示，故肺窗使用的 window width 最大。相較之下腦（tissue）W:80、縱膈 W:350、肝 W:150 皆為窄窗，用於衰減相近的軟組織。寬窗＝範圍大、對比低。[^1][^5]

## 考題
```dataview
list from #交換 where contains(concepts, "ct-attenuation-hounsfield-units")
```
