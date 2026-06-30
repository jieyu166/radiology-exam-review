---
concepts: [breast-mri-kinetics]
name: Breast MRI Kinetic Curves & MRS
subspecialty: [Breast]
aliases:
  - kinetic curve
  - washout curve
  - breast MR spectroscopy
  - 動態曲線
dateRev: 2026-06-29
---

# breast-mri-kinetics

**乳房 MRI 動態曲線的判讀關鍵在「延遲期」——三型中 washout 最可疑，但定義門檻是 >10%，不是 >20%。** 早期峰值約在注射後 2–3 分鐘；延遲期：persistent（續升，偏良性）→ plateau（平台，良惡皆可）→ washout（峰後降 >10%，惡性常見）。記憶鉤：**「wash『out』→洗掉→惡性洗光光」**；另外 1H-MRS choline 峰升高代表細胞增生，也是惡性指標。

## 判讀骨架

### 兩相動力學（BI-RADS DCE kinetics）
動力學評估分為「初期 initial phase」與「延遲期 delayed phase」兩段,以注射後約 **2 分鐘**為分界（取早期上升幅度最快、延遲期 washout 最明顯的 ROI 評估,即報告「worst curve」最可疑曲線）。[^2][^3]

- **初期 initial phase（前 ~2 分鐘的上升幅度）**：依早期 signal intensity 上升速率分為 **slow／medium／fast** 三級。fast wash-in 偏惡性傾向（但非特異）。文獻定量例：**90 秒內峰值上升 >90% 視為 rapid enhancement,高度提示惡性**。[^2]
- **延遲期 delayed phase（~2 分鐘後的時間-訊號曲線型態,Kuhl curves）**：[^1][^2]
  - **Type I persistent（持續上升）**：延遲期續升,偏良性;操作型定義為延遲期相對初期強化 **再增加 >10%**。但**約 9% 惡性病灶仍可呈此型**,不能單憑 persistent 排除惡性。[^1]
  - **Type II plateau（平台）**：初期上升後訊號維持平穩;良惡皆可見,屬 **concerning（介於兩者間,delayed 變化在 ±10% 內）**。[^1][^2]
  - **Type III washout（流出）**：快速上升後峰值過後**訊號下降**;**strongly suggestive of malignancy**,操作型定義為延遲期較峰值**下降 >10%**（CAD／定量 DCE 操作型門檻;BI-RADS Atlas 與 Radiopaedia 主要以曲線型態質性描述,非硬性 % 門檻,數字定義依文獻略有出入）。[^1][^2]
  - 記憶：fast 初期 + washout 延遲 → 最像惡性;slow 初期 + persistent 延遲 → 最像良性。

### 形態優先於動力學（morphology > kinetics）
- **形態（morphology）才是 BI-RADS MRI 判讀主軸,動力學為輔。** 文獻明確：**形態上懷疑惡性的病灶,無論動力學曲線為何都應切片**;動力學的價值主要在「形態看似良性」的病灶上加分。[^3]
- **Mass（腫塊）**：評估 shape（oval／round／irregular）、margin（circumscribed vs not-circumscribed／irregular／spiculated）、internal enhancement（homogeneous／heterogeneous／rim enhancement）。其中 **rim enhancement、spiculated margin、irregular shape 偏惡性**。[^3]
- **Non-mass enhancement（NME,非腫塊強化）**：以**分布（distribution）**＋**內部型態（internal pattern）**判讀。分布如 focal／linear／segmental／regional／diffuse,其中 **segmental、linear 偏惡性（提示沿導管分布,如 DCIS）**;內部型態中 **clustered ring enhancement 顯著與惡性相關**,homogeneous 偏良性。NME 良惡性影像重疊大,判讀困難。[^3]

### 背景實質強化 BPE 與技術
- **BPE（background parenchymal enhancement）**：正常纖維腺體組織對 gadolinium 的攝取,分 minimal／mild／moderate／marked 與對稱性。典型 BPE 為雙側對稱瀰漫、**slow early + persistent delayed**;但 moderate/marked、非對稱或非瀰漫的 BPE 可呈 **rapid early + plateau/washout**,可能遮蔽或模擬病灶。BPE 對判讀表現影響小,但與乳癌風險、治療結果相關。[^4]
- **DCE 技術**：**時間解析度（temporal resolution）是時間-訊號曲線品質的主要決定因子**,愈高曲線愈平滑;完整 TIC 約需 12 分鐘掃描。ROI 取點應放在病灶內**強化最快、washout 最明顯**的至少數個 pixel,並取 early phase 點。[^2]

### 判讀陷阱
- **良性也可 washout**：纖維腺瘤（fibroadenoma）常見 fast wash-in,但 **washout 不常見**——一旦出現需謹慎,不能因「良性形態」就忽略;乳突瘤（papilloma）等亦可呈可疑動力學。[^5]
- **惡性也可 persistent**：約 9% 惡性病灶呈 type I persistent,故 **persistent 不能排除惡性**。[^1]
- **核心原則：kinetics 為輔、morphology 為主。** 形態可疑就切片,不被良性曲線安慰。[^3]

### 輔助序列
- **Abbreviated MRI（縮短協定）**：核心為注射後 **early post-contrast T1WI + MIP**,因乳房 MRI 的病灶顯著度與癌偵測主要由**早期強化**驅動,而非延遲期動力學;與全協定在 BI-RADS 分類上一致性高。常加 T2WI 提供形態資訊（囊腫、發炎）。[^6]
- **DWI／ADC**：restricted diffusion（低 ADC）為鑑別良惡的有用輔助,可協助減少不必要切片;為 abbreviated 與全協定的常見加項。[^6]
- **MRS**：**1H-MRS choline peak 升高 → 細胞增生指標**（偏惡性）。[^1]

### 其他 breast MRI 判讀考點（RG 2006;26:1719-34）
- **動力學曲線評估的組成**：含**初期峰值（initial peak/slow-medium-fast）＋延遲期型態（persistent/plateau/washout）**;**不包含「time to peak」**（非標準描述項）。[^7]
- **T2 訊號**：viable 強化部分的 **T2 高訊號高度提示良性組織**;但 **T2 訊號無法可靠區分黏液性纖維腺瘤與髓質癌**——因髓質癌（medullary cancer）也常呈 T2 等/高訊號（約 60%）,易與 myxoid fibroadenoma 混淆。[^7]
- **敏感度/特異度**：MRI 偵測乳癌**敏感度很高（多數研究約 90%）**;對 DCIS 敏感度差異大（**40%–100%**）;**電腦輔助（CAD/類神經網路 clustering）『可』輔助評估強化**（非不能）;乳房 MRI **特異度相對較低**為缺點,故有嚴格判讀準則。[^7]
- **腫塊邊緣**：**邊緣（margin）為腫塊最具預測性的特徵**;**不規則/毛刺緣（irregular/spiculated）PPV 約 84–91%**（非 60–70%）;**節段性（segmental）分布強化約 78% 為惡性**。[^7]
- **構造扭曲（architectural distortion）**：不強化者可能為 radial scar;強化者高度提示侵襲癌;**hook sign（desmoplastic tethering，自病灶中心朝胸肌的毛刺狀牽引）高度提示『惡性』（非良性）**——惡性 29.3% vs 良性 3.2%。[^7]

> [!note] 考點：關於 breast MRI,何者「錯誤」?
> 「**washout 定義為峰後訊號下降 >20%**」錯誤——常用操作型定義為**>10%**。峰值 2–3 分(對)、washout 惡性常見(對)、plateau 良惡皆可(對)、choline 升高＝增生(對)。[^1][^2]

> [!note] 考點群（RG 2006 breast MRI）
> ① kinetic curve 不含「time to peak」;② T2 訊號無法可靠區分 myxoid fibroadenoma 與 medullary cancer（後者也常 T2 高）;③ CAD/類神經網路『可』輔助評估強化;④ spiculated margin PPV 84–91%（非 60–70%）;⑤ hook sign 提示惡性（非良性）。[^7]

### 參考來源
[^1]: *Breast MRI enhancement curves*（Kuhl curves）. Radiopaedia.org（輔助層級,實際查證 accessed 2026-06-20）：type I persistent（續升、偏良性,**~9% 惡性仍可呈此**）、type II plateau（concerning）、type III washout（峰後下降、**strongly suggestive of malignancy**）。延遲期 washout 量化常用門檻為峰後**下降 >10%**（CAD/定量 DCE 操作型定義;BI-RADS Atlas 與 Radiopaedia 主要以曲線型態質性描述,非硬性 % 門檻）。1H-MRS choline 升高為細胞增生（惡性）指標。
[^2]: Cheng L, Li X. Breast magnetic resonance imaging: kinetic curve assessment. *Gland Surg* 2013;2(1):50-53. PMC4115717（開放全文已讀,accessed 2026-06-29）：初期相以注射後約 2 分鐘為界;90 秒內峰值上升 >90% 為 rapid enhancement,高度提示惡性;延遲期 type I/II/III（persistent/plateau/washout）;**時間解析度為 TIC 品質主要決定因子**;完整 TIC 約 12 分鐘;ROI 取病灶強化最快、washout 最明顯處至少數 pixel。
[^3]: Macura KJ, et al. 與 ACR BI-RADS MRI lexicon 相關之形態 vs 動力學文獻（依摘要與搜尋層級,未讀全文,accessed 2026-06-29）：BI-RADS MRI 以形態為主軸（mass: shape/margin/internal enhancement;NME: distribution/internal pattern）;**形態懷疑惡性者無論動力學皆應切片**,動力學主要對形態良性病灶加分;clustered ring enhancement、segmental/linear NME、rim enhancement、spiculated margin 偏惡性。對應文獻：BI-RADS-MRI: A Primer, AJR 2006;186:1718（doi:10.2214/AJR.05.0572）。
[^4]: *Background Parenchymal Enhancement on Breast MRI: A Comprehensive Review*. PMC7207072（開放全文,依摘要與內文段落層級,accessed 2026-06-29）：BPE 分 minimal/mild/moderate/marked 與對稱性;典型為雙側對稱瀰漫、slow early + persistent delayed;moderate/marked 或非對稱者可 rapid early + plateau/washout;對判讀表現影響小,但與乳癌風險、治療結果相關。
[^5]: *Utility/diagnostic validity of abbreviated breast MRI* 等比較研究（依摘要層級,未讀全文,accessed 2026-06-29）：fibroadenoma 常見 fast wash-in,但 **washout 不常見**;washout kinetics 典型提示惡性——良性病灶出現 washout 為判讀陷阱。
[^6]: Mann RM, et al. *Abbreviated Breast MRI: State of the Art*. *Radiology* 2023（doi:10.1148/radiol.221822,依摘要與搜尋層級,未讀全文,accessed 2026-06-29）：abbreviated 核心為 early post-contrast T1WI + MIP,因病灶顯著度與癌偵測主要由早期強化驅動;與全協定 BI-RADS 分類一致性高;常加 T2WI（形態）、DWI/ADC（restricted diffusion 鑑別良惡、減少不必要切片）。
[^7]: 官方 2017 詳解；Kuhl C. The Current Status of Breast MR Imaging Part I/II. RadioGraphics 2006;26(6):1719-34（乳房 MRI 判讀綜述）：kinetic curve 含 initial peak＋delayed phase（不含 time to peak）;T2 高訊號偏良性但無法可靠分 myxoid fibroadenoma 與 medullary cancer（後者也常 T2 高）;敏感度 ~90%、DCIS 40-100%、CAD 可輔助、特異度較低;margin 最具預測性、spiculated PPV 84-91%、segmental 78% 惡性;hook sign（架構扭曲 desmoplastic tethering）提示惡性（惡性 29.3% vs 良性 3.2%）。

## 考題
```dataview
list from #交換 where contains(concepts, "breast-mri-kinetics")
```
