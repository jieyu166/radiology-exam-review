---
concepts: [contrast-enhanced-mra]
name: MR Angiography Techniques (Gadolinium vs Non-contrast)
subspecialty: [CV, Physics]
aliases:
  - contrast-enhanced MRA
  - time-resolved MRA
  - time-of-flight
  - 磁振血管攝影
dateRev: 2026-06-29
---

# contrast-enhanced-mra

**MRA 分成「要打藥」與「不打藥」兩路：記清楚哪些靠流入/血池天然對比，哪些必須依賴釓劑。** 需打釓的是 CE-MRA 及 time-resolved MRA（如 TRICKS/TWIST，動態多時相抓動靜脈期）；不需打藥的是 TOF（靠流入增強）、phase-contrast、cine SSFP（血池天然高訊號評心室功能）、navigator-gated ECG-triggered 3D whole-heart（同樣用 SSFP 血池）。記憶鉤：「要看時間相、要抓動靜脈→打釓；流入自然亮、血池夠→免打」。

## Summary
- **需打釓**：[^1]
  - **Time-resolved MRA（如 TRICKS、TWIST）**：打藥後連續擷取多時相,看動/靜脈期變化(下肢/血管)。
  - 一般 first-pass CE-MRA。
- **不需釓（非對比）**：[^1]
  - **TOF angiography**：流入增強(inflow),非對比。
  - **Cine SSFP（心臟）**：評心室功能,血池天然高訊號,不需釓。
  - **Navigator-gated、ECG-triggered 3D whole-heart MRA**：用 SSFP 血池對比,不需釓。

> [!note] 考點：哪種 MR 掃描通常需打釓?
> **Time-resolved MR angiography（下肢）**。TOF、cine SSFP、navigator 3D whole-heart 皆非對比、不需釓。[^1]

## 判讀骨架（CE-MRA 技術與閱片）

### 原理：釓縮短 T1，靠 timing 而非流動
- CE-MRA 用**快速 3D spoiled（擾相）梯度回訊（SPGR/FLASH）序列**、極短 TR/TE，在動脈期擷取；血管亮度來自**釓劑縮短血液 T1**（順磁性釓使血池 T1 大幅下降而呈高訊號），而非 TOF 的流入增強，因此**不受流動相關假象（飽和、亂流去相位）影響**。[^2][^3]
- 典型劑量約 0.1 mmol/kg（0.5 mol/L 製劑約 15–20 mL），以 ~8–12 秒注入，後接生理食鹽水沖洗（saline chaser）將殘留對比劑推入中央循環、維持團注緊實度。[^2]
- 影像品質依賴**脂肪抑制**與**減影（subtraction，以打藥前 mask 減去打藥後影像）**，並常用部分 k-space／平行成像縮短掃描時間。[^2]

### Timing：閱片純淨度的命門
- **k-space 中央決定對比**：影像對比（亮暗）由 k-space 中央低頻決定。CE-MRA 多採 **centric／elliptic-centric** 排序——**先填中央**，使中央採集對齊動脈期峰值濃度；缺點是對 timing 更敏感。[^3][^4]
- **timing 太早**：中央 k-space 在團注到達前就填完 → 動脈訊號不足、出現環狀假象（見下）。**太晚**：靜脈已增強 → **靜脈污染（venous contamination）**，靜脈高訊號遮蔽動脈。[^3][^4]
- 「只有一次機會做對」：團注從注射端到目標血管的傳輸時間個體差異大（如腎動脈年輕健康者約 10 秒，老年合併心衰可達 50 秒以上），故須測時。[^3]
- **測時方法**：
  - **Test bolus（小團注試打）**：先打 1–2 mL 釓並連續單切面取像，量測對比劑抵達目標的延遲時間，再據以排程正式掃描。[^3][^4]
  - **Bolus tracking／自動觸發（SmartPrep、CARE Bolus、fluoro triggering、MR 螢光透視）**：用 2D 監測序列即時看對比劑抵達目標動脈，達閾值即觸發 3D 採集。[^1][^3]
  - **Time-resolved（TWIST／TRICKS）**：連續多時相採集，犧牲部分空間解析度換取時間解析度，**自動涵蓋動脈期**而免測時，特別適合動靜脈分流、血流方向（如下肢 run-off、AVM/AVF、肺動靜脈畸形）的動態評估。[^1][^3]

### 假象與陷阱（閱片必辨）
- **Maki／ringing（環狀／截斷）假象**：timing 過早、中央 k-space 在團注到達前填入 → 血管**中央呈帶狀低訊號（central dark band）**，邊緣較亮，狀似 ringing。centric／elliptic-centric 排序比 sequential 更易出現。勿誤判為血栓、內膜剝離或假性管腔。[^3][^4]
- **靜脈污染**：timing 過晚使靜脈共顯，遮蔽鄰近動脈（如頸部時下頷下靜脈、下肢小腿期靜脈），導致動脈評估困難或高估狹窄旁訊號。time-resolved 可回溯純動脈期影像規避。[^3][^4]
- **Truncation／ringing（Gibbs）假象**：高低訊號交界（血管壁邊緣）因有限取樣出現平行交替亮暗條紋，可在管腔內造成假性低訊號條，勿當作病灶。[^4]
- **環狀／截斷 ≠ 真狹窄**：減影殘影、配準失準（病人移動使打藥前後 mask 不對齊）會在血管邊緣造成虛影或假性管腔缺損。[^2][^4]

### CE-MRA vs 非對比（選擇與判讀差異）
- **不受飽和／亂流低估**：TOF 對**平面內流動飽和（in-plane saturation）**與狹窄後亂流去相位敏感，會在狹窄處出現**訊號流失而高估或假性製造狹窄**；CE-MRA 不靠流動，較不受此影響。[^5][^6]
- **CE-MRA 對頸動脈狹窄反而傾向「高估」**：相對 3D TOF，對比劑減影 MRA 在頸動脈傾向**高估狹窄嚴重度**（一研究多數血管 CE-MRA 量到更重狹窄）；判讀時對臨界（如 ~70%）病灶宜謹慎、必要時搭配其他方式。[^7]
- **QISS（quiescent-interval single-shot）**：非對比技術，較 TOF **不易高估狹窄、狹窄後訊號流失較少**，在 CKD 不宜打釓時為下肢 run-off 的替代。其他非對比選項含 phase-contrast、FSD-prepared SSFP。[^5][^6]

### 安全：NSF 與釓沉積（CKD）
- **NSF（腎源性系統性纖維化）**：與舊型 group I 線性釓劑＋重度腎功能不全相關。現行 **group II（多為大環狀，macrocyclic）製劑** 即使在 CKD 4/5 期（含洗腎）NSF 風險可忽略；ACR 立場為 group II 風險足夠低，門診常規不強制先驗 eGFR。[^8]
- **釓沉積（gadolinium retention）**：可在腦／骨等組織殘留，但 group II 製劑分子穩定、解離少，目前無證實的臨床不良後果；CKD 仍以 group II、最低有效劑量為原則。[^8]

### 應用部位
- 頸部（頸動脈／椎動脈）、胸主動脈與腹主動脈、**腎動脈**（評腎血管性高血壓狹窄）、**下肢 run-off**（bolus-chase 或 time-resolved 涵蓋動靜脈期）、肺血管與分流評估。[^2][^3]

### 參考來源
[^1]: MR 血管攝影技術（Radiopaedia *MR angiography*／心血管 MR 教科書）：CE-MRA 與 time-resolved MRA（TRICKS/TWIST）需釓;TOF（inflow）、cine SSFP、navigator-gated 3D whole-heart（SSFP 血池）為非對比技術。（輔助層級）
[^2]: IMAIOS e-MRI, *Contrast-enhanced MR Angiography*（教學章節，Tier 2）：3D T1 SPGR 序列、釓縮短 T1、約 0.1 mmol/kg 劑量＋saline chaser、脂肪抑制與減影、bolus-chase 與時間解析法、應用部位。https://www.imaios.com/en/e-mri/mra-and-flow-mri/contrast-enhanced-mra
[^3]: Maki JH 等, *Contrast-enhanced MR Angiography*（CME tutorial／MRI Questions, Tier 2）：3D spoiled GRE、釓 T1 縮短、centric/elliptic-centric k-space 排序、test bolus 與 MR fluoroscopy 觸發、團注傳輸時間個體差異（腎動脈 10 vs ≥50 秒）、ringing/Maki 假象、靜脈污染機轉。https://mriquestions.com/contrast-enhanced-mra.html
[^4]: Wang Y 等／Saloner 等綜述（*Magnetic Resonance Angiography: Technique*, Radiology Key 章節，Tier 2）：k-space 中央決定對比、centric 排序對 timing 敏感、Maki/ringing 與 truncation（Gibbs）假象、減影配準失準殘影。https://radiologykey.com/magnetic-resonance-angiography-technique/
[^5]: Edelman RR 等, *Noncontrast MRA for the Diagnosis of Peripheral Vascular Disease*（**Circulation: Cardiovascular Imaging**, Tier 1）：QISS 較 TOF 不易高估狹窄、狹窄後訊號流失較少；非對比法在 CKD 之角色。https://www.ahajournals.org/doi/10.1161/CIRCIMAGING.118.008844
[^6]: *Nonenhanced Methods for Lower-Extremity MRA: A Phantom Study*（PMC, Tier 2）：TOF 因 in-plane 飽和與狹窄後亂流去相位造成訊號流失而誇大狹窄；QISS 在高流速下訊號較一致。https://pmc.ncbi.nlm.nih.gov/articles/PMC3210566/
[^7]: *Contrast material–enhanced MRA overestimates severity of carotid stenosis, compared with 3D time-of-flight MRA*（**Journal of Vascular Surgery**, Tier 1/PubMed 12844086）：CE-MRA 相對 3D TOF 傾向高估頸動脈狹窄嚴重度。https://pubmed.ncbi.nlm.nih.gov/12844086/
[^8]: ACR Manual on Contrast Media（2024/2025）與腎功能不全釓劑投予指引 v3（PMC12052744, Tier 2）：group II（多大環狀）釓劑在 CKD 4/5（含洗腎）NSF 風險可忽略、門診不強制先驗 eGFR；釓沉積無證實臨床後果。https://pmc.ncbi.nlm.nih.gov/articles/PMC12052744/

## 考題
```dataview
list from #交換 where contains(concepts, "contrast-enhanced-mra")
```
