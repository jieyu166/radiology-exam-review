---
concepts: [msk-mri-fat-suppression-magic-angle]
name: MSK MRI — Fat Suppression & Magic Angle
subspecialty: [MSK]
aliases:
  - magic angle artifact
  - fat suppression MRI
  - STIR frequency-selective opposed-phase
  - 魔術角假影
  - 肌肉骨骼MRI脂肪抑制
dateRev: 2026-07-10
---

# msk-mri-fat-suppression-magic-angle

**MSK MRI 兩個判讀分水嶺：（1）脂肪抑制三法各有物理機制——STIR 靠 T1（非選擇性、與金屬相容度最高），frequency-selective 與 opposed-phase 靠化學位移／同反相位（抑脂但不抑水）；（2）魔術角假影出現在「短 TE（<32–37 ms）＋膠原纖維走向約 55° 於 B0」時，肌腱、韌帶「與關節軟骨」皆會亮，勿誤判為肌腱病變。** 記憶鉤：短 TE 才有魔術角；GRE 是短 TE，評估軟骨時「照樣要擔心」魔術角。

## Summary
- **脂肪抑制三法**：常用為 frequency-selective（化學位移選擇性飽和）、short TI inversion recovery（STIR，靠脂肪短 T1）、opposed-phase／in-and-out-of-phase（同反相位）。STIR 為非選擇性、依 T1 抑制訊號，抑脂穩定但不會特別抑制水；frequency-selective 與 opposed-phase 抑制的是脂肪／脂-水界面訊號，**並非抑制水分子訊號**。[^1]
- **金屬植入物時選 STIR**：frequency-selective 與 opposed-phase 依賴磁場均勻度／化學位移精準度，金屬造成的 B0 不均會使其失效；STIR 依 T1 進行 inversion，**對磁場不均較不敏感**，故金屬旁的脂肪抑制效果優於前兩者。[^1]
- **魔術角（magic angle）本質**：緊密排列的膠原（肌腱、韌帶、軟骨、enthesis）內水分子受限、T2 極短故本應無訊號；當纖維走向與主磁場 B0 夾約 **54.74°（≈55°）** 時，偶極交互作用被平均掉、**T2 延長**，在**短 TE** 序列（訊號尚未衰減即被讀取）呈現偽高訊號。[^2][^3]
- **TE 依存**：魔術角僅見於**短 TE（<32 ms；文獻多以 TE>37 ms 可消除）**——T1WI、PD、GRE 最明顯；長 TE（T2WI）因訊號已衰減而不顯著（惟廣義上 STIR/DWI 亦可見殘餘效應）。[^2][^3]
- **易受影響的解剖**：走向彎曲、易接近 55° 之肌腱最常中招——**旋轉肌袖（supraspinatus）、踝部肌腱（peroneal）、biceps、外側半月板、關節軟骨**皆屬之。[^2][^3]

## 放射科醫師影像判讀重點
- **脂肪抑制選擇**：金屬旁或磁場不均區優先用 **STIR**；欲同時保留 SNR 又要均勻抑脂用 frequency-selective（但需良好 shimming）；opposed-phase 用於偵測脂-水並存（如骨髓、腎上腺）而非單純抑脂。[^1]
- **魔術角判讀主軸**：見到肌腱／軟骨在 **短 TE（T1/PD/GRE）** 序列局部高訊號、位置又約在 55° 走向處時，先想魔術角；**改用長 TE（T2WI，TE>37 ms）該高訊號應消失**——真正肌腱病變在長 TE 仍持續高訊號。[^2][^3]
- **軟骨評估的陷阱（本題考點）**：用 **GRE 快速成像評估膝／踝關節軟骨時仍需擔心魔術角**——GRE 屬短 TE，且關節軟骨富含定向膠原，正是魔術角好發組織；「評估軟骨用 GRE 不必擔心魔術角」為**錯誤**敘述。[^3]
- **biceps／peroneal tendon**：曲度大、走向多變，PD fat-sat（短 TE）評估時尤須警覺魔術角偽高訊號。[^2][^3]

## 臨床重點（5 句）
- STIR、frequency-selective、opposed-phase 為三大抑脂法，機制各異；僅 STIR 對磁場不均（含金屬）穩健。[^1]
- 魔術角＝短 TE＋膠原走向≈55°→偽高訊號，易誤為肌腱病變。[^2][^3]
- 出現於 T1/PD/GRE（短 TE），T2WI（長 TE, >37 ms）可消除。[^2][^3]
- 關節軟骨與 enthesis 同屬膠原組織，**GRE 評估軟骨仍會受魔術角影響**。[^3]
- 旋轉肌袖、踝部與 biceps 肌腱因走向彎曲最常見魔術角。[^2][^3]

### 參考來源
[^1]: *Fat-suppressed imaging sequences / short tau inversion recovery (STIR)*. Radiopaedia.org（實際查證 accessed 2026-07-05）——脂肪抑制常用法含 frequency-selective（化學位移飽和）、STIR（依脂肪短 T1，非選擇性、對磁場不均與金屬較穩健）與同反相位法；frequency-selective 與 opposed-phase 抑制脂肪／脂-水界面而非水本身。
[^2]: *Magic angle effect (MRI artifact)*. Radiopaedia.org（實際查證 accessed 2026-07-05）——魔術角為短 TE（<32 ms；T1WI/PD/GRE）序列假影，見於緊密膠原於 **54.74°** 於 B0 時 T2 延長、呈偽高訊號，可誤判為 tendinopathy。
[^3]: **Tier 1** Richardson ML, Amini B, Richards TL. *Some new angles on the magic angle: what MSK radiologists know and don't know about this phenomenon.* Skeletal Radiol. 2018;47(12):1673–1681（DOI [10.1007/s00256-018-3011-8](https://doi.org/10.1007/s00256-018-3011-8)，PubMed 查證 accessed 2026-07-05）——魔術角於 55°、強烈 TE 依存（短 TE 最顯，TE>37 ms 可消除）；除肌腱、韌帶外，**軟骨、enthesis、周邊神經、椎間盤亦受影響**，故 GRE（短 TE）評估關節軟骨仍會遇魔術角。基礎 TE 閾值另見 Erickson SJ 等 *Radiology* 1991;181:389–392（DOI [10.1148/radiology.181.2.1924777](https://doi.org/10.1148/radiology.181.2.1924777)）。

## 題目
> [!question]- 下列有關 Musculoskeletal MRI 的技術, 下列敘述何者錯誤? (2022-402)
> **答案：C（關鍵）**。「評估膝或踝關節軟骨、使用 GRE 快速成像時不必擔心 magic angle artifacts」為**錯誤**——關節軟骨富含定向膠原、GRE 屬短 TE 序列，正是魔術角好發情境，仍須警覺。其餘正確：STIR/frequency-selective/opposed-phase 為抑脂三法（後兩者不抑水）；膠原走向≈55°、TE≤20 ms 會產生魔術角；biceps／peroneal tendon 以 PD fat-sat（短 TE）評估要注意魔術角；金屬植入物時 STIR 抑脂優於 frequency-selective 與 opposed-phase。[^1][^2][^3]

> [!question]- Regarding the MRI protocol for evaluation of diabetic pedal disease, which of the following statements is **TRUE**? (2021-043)
> **D（A STIR sequence can be useful to provide more homogeneous fat suppression）**——STIR 為非選擇性、依脂肪短 T1 反轉抑制訊號，對磁場不均（足部小關節、金屬）較不敏感，故抑脂較 frequency-selective 均勻。A 錯：兩足應分開成像（用 head coil 同時掃兩足影像品質差）；B 錯：FOV 不應一律放大（大 FOV 使足部小骨受 volume averaging 判讀受限，僅懷疑感染近端擴散才含小腿）；C 錯：T2 需脂肪抑制以免高訊號脂肪掩蓋水腫；E 錯：IV gadolinium 有助辨識膿瘍、竇道、壞死區並鑑別蜂窩組織炎與感染性關節炎/腱鞘炎。

## 考題
```dataview
list from #交換 where contains(concepts, "msk-mri-fat-suppression-magic-angle")
```
