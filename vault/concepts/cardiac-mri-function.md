---
concepts: [cardiac-mri-function]
name: Cardiac MRI — Ventricular Volumes & Function
subspecialty: [CV]
aliases:
  - cardiac MRI function
  - right ventricular volume
  - ejection fraction
  - 心臟MRI功能
dateRev: 2026-06-29
---

# cardiac-mri-function

**Cardiac MRI（cine SSFP）是量測心室容積與射出分率的 gold standard，尤其右心室形狀不規則，最需要「逐切面堆疊計算（Simpson 法）」而非幾何假設。** Echo 依賴形狀假設、聲窗受限；CT 有輻射；導管攝影侵入且同樣仰賴幾何假設——只有 CMR 不做幾何假設、直接加總，因此 RV 功能量化首選 CMR。記憶鉤：「RV 長得奇怪、估不準——只有一層一層疊才是真相」。

## Summary
- **Cardiac MR（cine）**：**量測 RV/LV 容積與 EF 最準確的方法**（gold standard）;短軸堆疊、Simpson 法、無幾何假設,特別適合形狀不規則的 **右心室**。[^1]
- **Echo**：方便但受聲窗與幾何假設限制,RV 量化較不準。[^1]
- **Cardiac CT**：可評容積但有輻射、時間解析較差。[^1]
- **導管 RV 攝影**：侵入性、依賴幾何假設。[^1]

> [!note] 考點：最準確量測 RV 容積與 EF 的工具?
> **Cardiac MR imaging**——cine 短軸堆疊、無幾何假設,為 RV 功能參考標準。[^1]

## 一般放射科判讀骨架

### 主力序列：cine balanced SSFP
- **功能評估主力序列是 cine balanced SSFP（bSSFP，廠商名 TrueFISP／FIESTA／Balanced FFE）**：以 T2/T1 對比形成「亮血池-暗心肌」的高對比,心內外膜邊界清晰,適合做容積與室壁運動評估。心電圖門控、分段擷取整個心動週期（一般 25–30 phases/cycle）。[^2]
- **短軸堆疊（short-axis stack）覆蓋全心**：先以單張長軸（2-chamber、4-chamber）定位,再規劃一疊垂直於左心室長軸的短軸切面,自二尖瓣環/心底涵蓋到心尖,典型 8–12 層、層厚約 6–8 mm（含 gap）,確保全心室納入計算。[^2]

### 量測：容積、EF 與心肌質量
- **以短軸 Simpson（disc-summation）法逐層描繪**：分別在舒張末期（end-diastole）與收縮末期（end-systole）於每層描出心內膜輪廓,各層面積 ×（層厚＋層間距）後加總,得 EDV 與 ESV;**SV = EDV − ESV、EF = SV/EDV**,並以同法描心外膜算出心肌質量（心肌體積 × 1.05 g/mL）。逐層加總不做幾何假設,是 CMR 對形狀不規則 RV 量化勝過 echo 的關鍵。[^2][^3]
- **乳頭肌與肌小樑（trabeculation）的納入慣例會影響數值**：SCMR 後處理共識要求乳頭肌/肌小樑「要嘛一致算進心肌質量、要嘛一致算進血池容積,不可兩邊都算」。若把乳頭肌計入血池(常見簡化做法),會高估 EDV/ESV、略為低估 EF;將其排除於血池(歸入心肌)則 EF 約增加數個百分點——判讀與追蹤時務必前後一致。[^3][^4]

### 正常參考值（依性別、以體表面積標準化）
- **心室容積與心肌質量需以體表面積（BSA）標準化**,且**男女分別給參考範圍**（男性 LV/RV 容積與心肌質量普遍大於女性）。[^3]
- SCMR 2025 normal values（成人）約：**LVEF 男 66±7%、女 67±6%;RVEF 男 60±9%、女 63±7%**（注意 RVEF 正常下限略低於 LVEF）。[^3]

### 其他判讀向度
- **局部室壁運動（regional wall motion）**：於 cine 上分節（AHA 17-segment）評估收縮增厚與運動,描述 hypokinesis／akinesis／dyskinesis,輔助缺血/梗塞定位。[^2]
- **瓣膜逆流以 phase-contrast（PC，2D velocity-encoded）量化**：於瓣膜上方垂直流向放置切面,直接量前向與逆向流得 regurgitant volume／regurgitant fraction;亦可用「LV SV（cine）− 前向流（PC）」的間接法。VENC 須略高於預期峰值流速以避免 aliasing。4D flow 為進階全方向流速技術。[^5]
- **心肌應變（strain）／tagging**：tagging（SPAMM）或 feature-tracking 量化心肌縱向/環向/徑向應變,可早於 EF 下降前偵測收縮功能異常。[^5]

### 與組織特徵序列分工（本檔聚焦 function,組織特徵帶過）
- 本概念聚焦「功能評估」。**疤痕/纖維化看 LGE（late gadolinium enhancement）;瀰漫性病變與水腫看 T1／T2 mapping、ECV**,這些屬組織特徵化序列,與 cine 功能評估分工互補（詳見對應組織特徵概念）。[^2]

### 技術陷阱
- **心律不整／屏氣不佳致模糊**：R-R 間期不規則或屏氣失敗會造成 ghosting／diffuse blurring;可改用非門控、free-breathing 的 real-time cine 補救。[^6]
- **through-plane motion 與短軸定位**：心臟長軸方向的收縮位移使心底切面在收縮末期可能滑出原切面（尤其最基底層),造成心底層心室/心房界面判定困難,需逐層核對心底層的歸屬,並確保短軸堆疊規劃正確涵蓋心尖到心底。[^2][^3]
- **dark-rim artifact**：見於首渡灌注影像心內膜下的一過性低訊號帶,主因為 Gibbs（truncation）效應疊加運動,易誤判為心內膜下灌注缺損。[^6]
- **bSSFP off-resonance banding／flow artifact**：場不均勻造成暗帶,3T 更明顯;以局部 shimming、縮短 TR 或 frequency scout 緩解。[^6]

### 參考來源
[^1]: 心臟 MR 功能評估（Radiopaedia *cardiac MRI*／心臟影像教科書）：cine SSFP 短軸堆疊以 Simpson 法量化,**為 RV/LV 容積與 EF 的參考標準**,優於 echo（幾何假設）、CT（輻射/時間解析）、導管攝影（侵入）。
[^2]: Tier 2 教學文獻整合（PMC 開放全文）：*Cardiac MRI: An Alternative Method to Determine the Left Ventricular Function*（Diagnostics 2023, PMC10137814, doi:10.3390/diagnostics13081437）＋ MRIquestions *Ventricular function*：LV/RV 功能研究以 bSSFP/TrueFISP cine、2/3/4-chamber 定位後取 8–12 層短軸堆疊（自二尖瓣至心尖、整個心動週期）為核心;局部室壁運動於 cine 分節評估;LGE 看疤痕、T1/T2 mapping 看瀰漫病變屬組織特徵化分工。
[^3]: Tier 1/2 指引層級（SCMR 2025 reference values, *J Cardiovasc Magn Reson* 2025, PMC12159681, doi:10.1016/j.jocmr.2025.101868）：成人 LVEF 男 66±7%（53–79）、女 67±6%（55–80）;RVEF 男 60±9%（44–77）、女 63±7%（49–77）;所有容積/質量以 BSA 標準化並男女分列;乳頭肌/肌小樑須一致歸入心肌質量「或」血池容積、不可重複計入。
[^4]: Tier 2 開放文獻（Circ Cardiovasc Imaging 2024 meta-analysis, doi:10.1161/CIRCIMAGING.123.016090,及對應 Simpson 法乳頭肌討論 PMC4044521）：乳頭肌計入血池會高估 EDV/ESV 並略低估 EF;將乳頭肌排除於血池量得之 EF 平均約高出數個百分點（文獻引約 6%）,故乳頭肌/肌小樑處理慣例顯著影響 LV 參數,前後須一致。
[^5]: Tier 1/2 文獻（*Role of CMR in Native Valvular Regurgitation*, Front Cardiovasc Med 2022, doi:10.3389/fcvm.2022.881141;JACC: Cardiovascular Imaging 2021, doi:10.1016/j.jcmg.2020.09.029）：瓣膜逆流以 2D PC velocity mapping 於瓣上垂直切面直接量逆流量/逆流分率,或用 cine SV 減前向流之間接法,VENC 須避免 aliasing,4D flow 為進階全方向流速;心肌應變以 tagging/feature-tracking 量化。
[^6]: Tier 1 主流影像期刊（*Artifacts at Cardiac MRI: Imaging Appearances and Solutions*, RadioGraphics 2024, doi:10.1148/rg.230200, PMID 39745866;dark-rim 補充 MRIquestions）：心律不整/屏氣不佳致 ghosting 與 blurring,可改 real-time free-breathing cine;dark-rim artifact 為 Gibbs 疊加運動之心內膜下一過性低訊號,勿誤判灌注缺損;bSSFP 場不均勻造成 off-resonance banding,3T 尤甚,以 shimming／短 TR／frequency scout 緩解。

## 考題
```dataview
list from #交換 where contains(concepts, "cardiac-mri-function")
```
