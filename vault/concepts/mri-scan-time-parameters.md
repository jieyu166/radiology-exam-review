---
concepts: [mri-scan-time-parameters]
name: MRI Scan Time — Governing Parameters
subspecialty: [Physics, MR]
aliases:
  - MRI scan time
  - MRI acquisition time formula
  - MRI掃描時間參數
dateRev: 2026-07-02
nonImaging: true
nonImagingReason: "MRI掃描時間之物理參數公式，非影像判讀"
---

# mri-scan-time-parameters

**MRI掃描時間公式口訣「TR × Ny × NSA ÷ ETL」：TR（重複時間）、Ny（相位編碼步數）、NSA/NEX（激發次數）都會影響掃描時間，唯獨頻率編碼步數（Nx, frequency-encoding）不影響——因為頻率編碼是在單一次讀出（readout）中一次採樣完成，不需重複。這是本題最容易誤判的陷阱。**

## Summary
- **掃描時間公式**：**Scan time = TR · Ny · NSA / ETL**（TR＝repetition time；Ny＝number of phase-encoding steps；NSA＝number of signal averages／NEX；ETL＝echo train length＝number of echoes）。[^1]
- **影響掃描時間之參數**：[^1]
  - **TR（repetition time）**：每次重複之時間間隔，直接乘入。
  - **Phase-encoding step (Ny)**：相位編碼步數，每一步需一次TR，直接乘入。
  - **NEX/NSA (number of excitations)**：訊號平均次數，直接乘入。
- **不影響掃描時間之參數**：**Frequency-encoding step (Nx)**——頻率編碼於單一次讀出（readout）內一次採樣完成，不需額外重複，故與掃描時間無關。[^1]

> [!note] 考點：何者MRI掃描參數與掃描時間「無關」？
> **Frequency-encoding step (Nx)（B）**——頻率編碼在單一讀出內完成採樣，不影響掃描時間。TR、phase-encoding step (Ny)、NEX皆直接乘入掃描時間公式。[^1]

### 參考來源
[^1]: R. H. Hashemi, et al. *MRI the basics*, 3rd Ed., Lippincott Williams & Wilkins, 2010, p.165（2018 交換考題詳解 p.254 引用；Tier 2 教科書）。Scan time = TR·Ny·NSA/ETL；TR、phase-encoding步數Ny、NSA(NEX)皆影響掃描時間；frequency-encoding步數Nx於單一讀出內採樣完成，不影響掃描時間。

## 題目
> [!question]- 下列哪個MRI掃描參數與掃描時間無關? (2018-343)
> **Frequency-encoding step (Nx)（B）**——頻率編碼在單一讀出內採樣完成，不影響掃描時間。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "mri-scan-time-parameters")
```
