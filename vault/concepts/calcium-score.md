---
concept: calcium-score
name: Coronary Artery Calcium (CAC) Score
subspecialty: [CV]
aliases:
  - coronary artery calcium score
  - CAC score
  - Agatston score
  - 冠狀動脈鈣化分數
dateRev: 2026-06-14
concepts: [Calcium Score]
---

# calcium-score

**CAC 分數是用非顯影心電圖閘控 CT 量化冠狀動脈鈣化、預測無症狀者心血管風險的工具。** 判讀分水嶺一：**CAC = 0 是強力的「陰性風險因子」**（power of zero，心血管事件與疾病別死亡率低）；判讀分水嶺二：**CAC ≥ 400 = 高風險**，且會因 blooming 降低 CCTA 的 specificity（見 [[ccta]]）。

## Summary
- **方法**：Agatston 法最常用——鈣化定義為**≥130 HU**、面積 **≥1 mm²**；分數 = 斑塊面積 × 依峰值 HU 之加權係數，加總各病灶。[^1]
- **用途**：建議用於**無症狀**個體預測心血管疾病與疾病別死亡率風險、重新分層（reclassification）、並輔助一級預防決策。[^1]
- **CAC = 0**：可靠的**負向風險因子**（power of zero）。[^1]
- **CAC ≥ 400**：高風險族群。[^1]
- **MESA 計算器**：以 MESA 族群資料，依 CAC 分數與事件給出年齡/性別/種族百分位與風險。[^1]
- **與 CCTA 連結**：高 CAC（>400）之重度鈣化 blooming 會**顯著降低 CCTA 的 specificity / PPV**（見 [[ccta]]，ACCURACY trial）。[^1]

## 方法（Agatston）
非顯影、ECG 閘控 CT；鈣化定義為 **≥130 HU 且面積 ≥1 mm²**。Agatston 分數由「病灶面積 × 依該病灶最高 HU 之加權係數」整合而得，再加總全部冠狀動脈病灶。為最廣泛使用的計分法。[^1]

## 風險分層與臨床應用
- **CAC = 0**：強力負向預測（事件與疾病別死亡率低）；**CAC ≥ 400**：高風險。[^1]
- 常用 Agatston 分層（mild / moderate / severe）：0、1–99、100–399、≥400（數值越高、斑塊負擔與風險越高）。[^1]
- 主要定位於**無症狀**個體的風險預測與重新分層，輔助是否啟動一級預防（如 statin）的決策。[^1]
- **重掃間隔（SCCT 指引）**：初始 CAC = 0 → 5 年後重掃；CAC > 0 → 3–5 年後重掃（在進展會改變處置時）。[^1]

> [!note] CAC 與 CCTA 的關係
> CAC 為**非顯影**鈣化定量（風險預測）；CCTA 為**顯影**管腔評估（狹窄偵測）。高 CAC（>400）的 blooming 會降低 CCTA specificity——這正是 ACCURACY trial 中「calcium >400 顯著降低 specificity」的機轉（詳見 [[ccta]]）。

### 參考來源
[^1]: Gupta A, Bera K, Kikano E, Pierce JD, Gan J, Rajdev M, Ciancibello LM, Gupta A, Rajagopalan S, Gilkeson RC. *Coronary Artery Calcium Scoring: Current Status and Future Directions*. RadioGraphics. 2022;42(4). https://doi.org/10.1148/rg.210122 （Free Access，實際查證 accessed 2026-06-14）。

## 題目
> [!question]- Agatston CAC 分數中，鈣化的定義門檻為何？
> **≥130 HU 且面積 ≥1 mm²**；分數 = 病灶面積 × 依峰值 HU 之加權係數，加總全部病灶。[^1]

> [!question]- 「CAC = 0」的臨床意義是什麼？
> 強力的**負向風險因子**（power of zero）——心血管事件與疾病別死亡率風險低；SCCT 建議 5 年後再重掃。[^1]

> [!question]- 為什麼高 CAC 會影響 CCTA 判讀？
> 高 CAC（>400）之重度鈣化 blooming 造成管腔高估／偽陽性，**降低 CCTA 的 specificity**（ACCURACY trial）。見 [[ccta]]。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "calcium-score")
```
