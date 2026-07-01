---
concepts: [mri-flow-and-diffusion-artifacts]
name: MRI Diffusion Artifacts & Flow-Related Enhancement
subspecialty: [Physics]
aliases:
  - diffusion MRI artifacts
  - flow-related enhancement
  - time-of-flight enhancement
  - 擴散造影偽影 血流相關增強
dateRev: 2026-07-01
---

# mri-flow-and-diffusion-artifacts

**擴散造影（DWI）三大偽影：渦電流（eddy currents，使影像幾何扭曲）、動作偽影（motion artifacts）、鬼影（ghosting，訊號錯位重複）——三者皆源自擴散序列所需的強梯度切換與長掃描時間。血流相關增強（flow-related enhancement, FRE，即 time-of-flight 效應）強度受 TR 長短、flip angle 大小、切面厚度三者共同影響，三者缺一不可。**

## Summary
- **Diffusion MRI 常見偽影**：**渦電流（eddy currents）**——強擴散梯度切換在鄰近導體感應出渦電流，扭曲影像幾何（如剪切、拉伸）；**動作偽影（motion artifacts）**——長 TE 與強梯度使影像對頭動特別敏感；**鬼影（ghosting）**——k-space 資料錯位重建造成之重複影像偽影。三者皆為 DWI 序列常見偽影。[^1]
- **Flow-related enhancement（FRE，流入相關增強）之影響因子**：**TR 長短**（最佳 TR＝切面厚度/流速；TR 太短則血液來不及流出、太長則靜止組織訊號無法飽和）、**flip angle 大小**（角度愈大訊號愈亮但 flow ghost 亦增加，偏 T1 加權）、**slice thickness 厚薄**（切面愈薄、流速愈快，FRE 愈明顯）——三者皆會影響 FRE 強度，並無「不影響」的選項。[^2]

## 判讀骨架
- **FRE 原理**：血液流入成像切面時未經歷先前的飽和脈衝（RF saturation），故訊號較周圍已飽和的靜止組織亮，是 time-of-flight MR angiography 的成像基礎；through-plane flow（垂直於切面的流動）效應最明顯。
- **DWI 偽影對策**：渦電流可用次級補償線圈或預失真梯度脈衝校正；動作偽影可用心電/呼吸導航或平行成像縮短擷取時間降低。

### 參考來源
[^1]: *J Magn Reson Imaging*. 2006 Sep;24(3):478-88（2018 交換考題詳解 p.61 引用；Tier 1）。Diffusion MRI 常見偽影含渦電流、動作偽影、鬼影。
[^2]: *Magnetic Resonance Imaging - E-Book: Physical and Biological Principles*, p.334（2018 交換考題詳解 p.62 引用；Tier 3 教科書）。Flow-related enhancement 受 TR 長短、flip angle 大小、slice thickness 厚薄共同影響。

## 考題
```dataview
list from #交換 where contains(concepts, "mri-flow-and-diffusion-artifacts")
```
