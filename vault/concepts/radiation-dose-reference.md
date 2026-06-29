---
concepts: [radiation-dose-reference]
name: Effective Dose Reference Values (Mettler 2008 Catalog)
subspecialty: [Physics]
aliases:
  - effective dose
  - radiation dose reference
  - 有效劑量參考值
  - Mettler catalog
dateRev: 2026-06-19
---

# radiation-dose-reference

**有效劑量從平片 mSv 以下、CT 個位數，到介入（TIPS ~70 mSv）遞升；記憶鉤：「平片＜乳攝＜腰椎平片＜頭CT＜IVU＜鋇劑灌腸≈腹骨盆CT＜Gallium/PCI＜CTCA＜Tl-201＜TIPS」。** 判讀分水嶺一：**X光（<2 mSv）≪ CT（6–16 mSv）；鋇劑灌腸（~8）竟與腹骨盆CT相當，是陷阱**；判讀分水嶺二：**核醫中 Tl-201（~22–41 mSv）、Gallium（~15 mSv）劑量遠超 Tc-99m 系列；介入中 TIPS 最高（~70 mSv）**。

## Summary（Mettler 2008 catalog 代表值）[^1]

### Radiography / 攝影
| 檢查 | 有效劑量 (mSv) |
|---|---|
| 四肢（extremity）／DXA 骨密度 | **0.001** |
| 牙科 bitewing | 0.005 |
| 胸部 X 光（PA＋lateral） | **0.1**（PA 單張 ~0.02） |
| 頭顱（skull） | 0.1 |
| 頸椎 | 0.2 |
| 骨盆（pelvis） | **0.6** |
| 腹部（KUB）／髖 | **0.7** |
| 胸椎 | 1.0 |
| 腰椎（lumbar spine） | **1.5** |
| 乳房攝影（mammography） | **0.4** |

### Fluoroscopy / 對比攝影
| 檢查 | 有效劑量 (mSv) |
|---|---|
| 食道鋇劑（esophagram） | 1.5 |
| IVU（靜脈尿路攝影） | **3** |
| ERCP | 4 |
| 上消化道（upper GI） | **6** |
| 鋇劑灌腸（barium enema） | **8** |

### CT
| 檢查 | 有效劑量 (mSv) |
|---|---|
| 頭部 | **2** |
| 頸部 | 3 |
| 冠狀動脈鈣化分數 | 3 |
| 胸部 | **7** |
| 胸部（肺栓塞 protocol） | 10 |
| 腹部 | 8 |
| 骨盆 | 6 |
| 腹部＋骨盆 | **10** |
| CT colonography | 10 |
| **CT 冠狀動脈攝影（CTCA）** | **~16** |

### Interventional / 血管介入
| 檢查 | 有效劑量 (mSv) |
|---|---|
| 診斷性冠狀動脈攝影 | **7** |
| 頭頸血管攝影 | 5 |
| 冠狀動脈介入（PCI）／RF ablation | **15** |
| **TIPS** | **~70**（最高之一） |

### Nuclear medicine / 核醫（含 catalog 重點）
| 檢查（放射藥物） | 有效劑量 (mSv) |
|---|---|
| 肺通氣（Xe-133／Tc-99m aerosol） | 0.3–0.5 |
| 肺灌注（Tc-99m MAA） | **2** |
| 腎臟（Tc-99m MAG3／DTPA） | ~1.8–2.6 |
| 肝膽（Tc-99m IDA） | ~3 |
| 腦（Tc-99m HMPAO） | ~6.9 |
| **骨掃描（Tc-99m MDP）** | **~6.3** |
| **FDG PET（F-18）** | **~7**（PET/CT 約 14） |
| 心肌灌注（Tc-99m sestamibi, stress+rest） | ~9–12 |
| Gallium（Ga-67） | **~15** |
| **心肌灌注（Tl-201）** | **~22–41**（核醫中偏高） |

> [!note] 考點：相對高低排序
> 四檢查（骨盆X光~0.6 < 全脊椎/腰椎X光~1.5 < 頭CT~2 < **鋇劑灌腸~8**）中**鋇劑灌腸最高**；但放眼全部，**TIPS(~70) > Tl-201(~40) > CTCA(~16) > PCI/Gallium(~15) > 腹骨盆CT/鋇劑灌腸(~8–10)**。核醫骨掃描 ~6.3、FDG PET ~7（PET/CT ~14）。[^1][^2]

> [!note] 2016-116 選項小數已修正
> 原資料庫選項顯示 007/07/7/7（小數點遺失），**已修正為 0.007 / 0.07 / 0.7 / 7 mSv**，正解 **C＝0.7 mSv**（乳攝 4-view 約 0.4–0.7）。

### 參考來源
[^1]: Mettler FA Jr, Huda W, Yoshizumi TT, Mahesh M. *Effective Doses in Radiology and Diagnostic Nuclear Medicine: A Catalog*. Radiology. 2008;248(1):254-263. https://doi.org/10.1148/radiol.2481071451 （含 radiography／fluoroscopy／CT／interventional／nuclear medicine 各檢查之代表性有效劑量;上表為其 rounded representative values）。
[^2]: *Typical Radiation Doses*（MSD Manual Professional Edition，本於 Mettler 等；實際查證 accessed 2026-06-17）：數位乳攝 0.21、CT 頭 2、鋇劑灌腸 6、腰椎X光(側位)1.5、CT 腹骨盆 7.7 mSv（與 [^1] 大致一致）。

## 考題
```dataview
list from #交換 where contains(concepts, "radiation-dose-reference")
```
