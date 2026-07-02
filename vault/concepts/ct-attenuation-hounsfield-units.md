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
dateRev: 2026-07-02
---

# ct-attenuation-hounsfield-units

**CT值（Hounsfield unit）以Godfrey Hounsfield命名（他與Allan Cormack共同獲1979年諾貝爾醫學獎，但CT值僅以Hounsfield一人命名，並非兩人皆有冠名），其本質是「衰減係數」經線性轉換所得，並非直接等同物理密度——這是常考的精確度陷阱。**

## Summary
- **命名由來**：Hounsfield units（HU）以**Sir Godfrey Hounsfield**（CT發明者、諾貝爾獎得主）單獨命名（並非以「唯一發明者」命名——Allan Cormack亦獨立發明類似技術並共同獲1979年諾貝爾醫學獎，但CT值本身僅冠Hounsfield一人之名）。[^1]
- **HU與物理密度之關係**：HU是由**測量之衰減係數(attenuation coefficient)經線性轉換而得**（公式：HU = [(μX - μWater)/(μWater - μAir)] × 1000），**並非**與人體物理密度呈線性相關（衰減係數≠密度，尚受原子序、光子能量等因素影響）。[^1]
- **冠狀動脈CTA最佳血管內強化HU**：慣例上約**250–300 HU**（並非800 HU），以利區分低密度動脈粥狀硬化病灶(~40 HU)、中等密度纖維斑塊(~90 HU)、鈣化斑塊(>130 HU)。[^1]
- **正常肺實質HU**：約**-700至-950 HU**。[^1]
- **冠狀動脈鈣化分數（Agatston score）分級**：0分=無證據；1-10=minimal；11-100=mild；101-400=moderate；>400=severe；**>160分即有較高主要不良心臟事件(MACE)風險**。[^1]

> [!note] 考點：關於CT attenuation何者正確？
> **正常肺實質約-700至-950 HU（D）**——正確。HU以Hounsfield單獨命名(非唯一發明者，A誤)、HU與物理密度非線性相關(B誤，實為衰減係數之線性轉換)、冠狀動脈CTA最佳血管內強化約250-300 HU非800 HU(C誤)。[^1]

### 參考來源
[^1]: 官方2020詳解；Ref: Primer of Diagnostic Radiology, 5th ed. Weissleder. P.4（題目所引）——HU以Hounsfield命名(Cormack共同獲諾貝爾獎但CT值未冠其名)；HU為衰減係數經線性轉換所得非直接等同密度；冠狀動脈CTA最佳血管內強化250-300 HU；正常肺實質-700至-950 HU；Agatston分數分級(0/1-10/11-100/101-400/>400)，>160分MACE風險增加。

## 題目
> [!question]- About CT attenuation, which one is CORRECT (2020-307)
> **Normal lung parenchyma is about -700 to -950 HU（D）**——正確。HU以Hounsfield單獨命名(非唯一發明者)、HU非直接與物理密度線性相關(實為衰減係數之線性轉換)、冠狀動脈CTA最佳血管內強化約250-300 HU非800 HU，其餘選項皆錯誤。[^1]

## 考題
```dataview
list from #交換 where contains(concepts, "ct-attenuation-hounsfield-units")
```
