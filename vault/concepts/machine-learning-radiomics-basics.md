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
[^1]: **Tier 2（全文已讀，開放取用）** Koçak B, Durmaz EŞ, Ateş E, Kılıçkesmez Ö. *Radiomics with artificial intelligence: a practical guide for beginners*. Diagn Interv Radiol. 2019 Nov;25(6):485-495（據 PubMed，DOI [10.5152/dir.2019.19321](https://doi.org/10.5152/dir.2019.19321)，PMC6837295，實際查證 accessed 2026-07-03）——機器學習分監督式(KNN/naïve Bayes/logistic regression/SVM/decision tree/random forest/neural networks)與非監督式(k-means/PCA)；radiomics 五步驟(獲取→前處理→分割→特徵提取→AI 分析)；關鍵概念過度擬合、訓練/驗證/測試集、交叉驗證(K-fold/leave-one-out/nested/bootstrap)、特徵可重現性以 ICC 評估。
[^2]: *Radiomics*. Radiopaedia.org（實際查證 accessed 2026-07-05）：radiomics 工作流程步驟為 initial image processing（重建演算法影響影像品質）→ image segmentation（手動／半自動／全自動 AI，2D ROI 或 3D VOI）→ features extraction and qualification（形狀、密度、強度、紋理等 semantic 與 agnostic 特徵）→後續建模；可套用於 X 光、超音波、CT、MRI、PET。**Backpropagation** 屬神經網路訓練演算法，非 radiomics 標準工作流程步驟（Q2022-381 之答案 E）。另 *Deep learning*. Radiopaedia.org（accessed 2026-07-05）：deep learning 為 machine learning 之子集，基於「多層」人工神經網路；convolutional neural network(CNN) 為其影像應用之主要架構——MLP／CNN／RNN／restricted Boltzmann machine 皆屬神經網路型深度學習架構，**support vector machine(SVM) 屬傳統機器學習、非深度學習**（Q2022-382 之答案 E）。
[^3]: **Tier 1** Chartrand G, Cheng PM, Vorontsov E, et al. *Deep Learning: A Primer for Radiologists*. RadioGraphics 2017;37(7):2113-2131（DOI [10.1148/rg.2017170077](https://doi.org/10.1148/rg.2017170077)，PMID 29131760；據 PubMed／RSNA 摘要實際查證 accessed 2026-07-05）——為放射科醫師回顧深度學習核心概念、技術需求與臨床應用；deep learning 建立於多層人工神經網路，CNN 為醫學影像分類之主力架構，並與傳統機器學習方法（如 SVM）作區分。

## 題目
> [!question]- Which is included in machine learning technique? (2020-284)
> **以上皆是（E）**——neural networks、decision trees、k-nearest neighbors、support vector machine 皆屬機器學習技術。[^1]

> [!question]- Which is not the typical process in radiomic analysis? (2022-381)
> **Backpropagation（E，關鍵）**——radiomics 標準流程為 segmentation → feature extraction → feature selection → 建模與 cross-validation；backpropagation 是神經網路（深度學習）之訓練演算法，並非 radiomics 分析之典型步驟。[^1][^2]

> [!question]- Which is not typically included in deep learning? (2022-382)
> **Support vector machine（E，關鍵）**——multilayer perceptron、convolutional neural network、recurrent neural network、restricted Boltzmann machine 皆屬神經網路型深度學習架構；SVM 屬傳統（非深度）機器學習分類器。[^2][^3]

## 考題
```dataview
list from #交換 where contains(concepts, "machine-learning-radiomics-basics")
```
