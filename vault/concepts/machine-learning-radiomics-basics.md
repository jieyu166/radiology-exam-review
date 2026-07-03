---
concepts: [machine-learning-radiomics-basics]
name: Machine Learning — Basic Techniques (Radiomics)
subspecialty: [NR, Physics]
aliases:
  - machine learning technique
  - neural networks
  - support vector machine
  - radiomics workflow
  - 機器學習技術
nonImaging: true
nonImagingReason: "機器學習技術分類主題，非影像判讀"
dateRev: 2026-07-03
---

# machine-learning-radiomics-basics

**機器學習(machine learning)技術涵蓋範圍廣泛——neural networks、decision trees、random forest、k-nearest neighbors(KNN)、support vector machine(SVM)、naïve Bayes、logistic regression 皆屬監督式(supervised)機器學習；k-means clustering、PCA 則屬非監督式(unsupervised)。這些是 radiomics/AI 輔助診斷之基礎演算法工具。** 判讀分水嶺：**「監督式 vs 非監督式」是核心分類——監督式用「有標籤」資料學分類/迴歸；非監督式用「無標籤」資料做分群/降維。考題問「何者屬機器學習」時，上述演算法「皆是」。**

## Summary
- **監督式學習(supervised)演算法**：**KNN、naïve Bayes、logistic regression、SVM、decision tree、random forest、neural networks/deep learning**——以有標籤資料學習模式，對未見資料做預測。[^1]
- **非監督式學習(unsupervised)**：**k-means clustering、PCA（主成分分析）**等，用於分群與降維（無標籤）。[^1]
- **Radiomics 標準工作流程（5 步）**：①影像獲取(CT/MRI/PET) ②前處理(重取樣/灰度正規化/偏差場校正) ③分割(手動/半自動/全自動) ④特徵提取(size/shape/texture 第一至高階，或深度特徵) ⑤AI 統計分析(資料準備/建模/驗證)。[^1]
- **關鍵概念**：**過度擬合(overfitting)**＝訓練集佳但測試集差；**訓練/驗證/測試集**分工；**交叉驗證**(K-fold、leave-one-out、nested、bootstrap)；**特徵可重現性**以 **ICC** 評估。[^1]

## 放射科醫師實務重點
- **監督 vs 非監督（考點核心）**：監督式（分類/迴歸，需標籤）涵蓋 KNN/SVM/決策樹/隨機森林/神經網路等；非監督式（分群/降維，無標籤）如 k-means/PCA——問「何者屬機器學習」時皆屬之。[^1]
- **深度學習之定位**：neural networks/deep learning 為機器學習之子集，可「自動」設計深度特徵，免除人工特徵工程，但需大量資料。[^1]
- **過度擬合是最大陷阱**：模型於訓練資料表現優異卻無法類推——緩解＝**增加樣本、資料增強、正則化(regularization)、適當交叉驗證**。[^1]
- **特徵可重現性(reproducibility)**：分割變異敏感之特徵應以 **ICC(組內相關係數)** 篩除；提升 radiomics 模型穩健性之關鍵前處理。[^1]
- **驗證分層**：**訓練集(學習)→驗證集(調超參數)→測試集(最終評估)**須分離；nested cross-validation 可防特徵選擇資訊洩露。[^1]

## 臨床/考試重點（5 句）
1. Radiomics＝從醫學影像萃取「大量定量特徵」，與 AI 結合以處理海量資料、輔助決策。[^1]
2. **AI 不會取代放射科醫師，但熟悉 radiomics/機器學習概念已是必備素養**（原文核心訊息）。[^1]
3. 機器學習演算法「皆屬」機器學習範疇——**neural networks、decision trees、KNN、SVM 為典型例**。[^1]
4. **過度擬合、樣本量不足、特徵不可重現**為 radiomics 研究常見缺陷，需交叉驗證與 ICC 把關。[^1]
5. 判讀時把「監督/非監督分類、radiomics 五步驟、過擬合、ICC 可重現性、獨立測試集」記牢，以評讀 AI 研究品質。[^1]

> [!note] 考點：何者屬於機器學習技術？
> **以上皆是（E）**——neural networks、decision trees、k-nearest neighbors(KNN)、support vector machine(SVM) 皆屬機器學習（監督式）技術範疇。[^1]

### 參考來源
[^1]: **Tier 1（全文已讀，開放取用）** Koçak B, Durmaz EŞ, Ateş E, Kılıçkesmez Ö. *Radiomics with artificial intelligence: a practical guide for beginners*. Diagn Interv Radiol. 2019 Nov;25(6):485-495（據 PubMed，DOI [10.5152/dir.2019.19321](https://doi.org/10.5152/dir.2019.19321)，PMC6837295，實際查證 accessed 2026-07-03）——機器學習分監督式(KNN/naïve Bayes/logistic regression/SVM/decision tree/random forest/neural networks)與非監督式(k-means/PCA)；radiomics 五步驟(獲取→前處理→分割→特徵提取→AI 分析)；關鍵概念過度擬合、訓練/驗證/測試集、交叉驗證(K-fold/leave-one-out/nested/bootstrap)、特徵可重現性以 ICC 評估。原「官方 2020 詳解（題目所引）」弱來源已由本次原文全文查核升級。

## 題目
> [!question]- Which is included in machine learning technique? (2020-284)
> **以上皆是（E）**——neural networks、decision trees、k-nearest neighbors、support vector machine 皆屬機器學習技術。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "machine-learning-radiomics-basics")
```
