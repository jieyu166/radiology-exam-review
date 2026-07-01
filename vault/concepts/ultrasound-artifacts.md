---
concepts: [ultrasound-artifacts]
name: Ultrasound Artifacts (Mirror, Ring-down, Refraction, Aliasing)
subspecialty: [US, Physics]
aliases:
  - ultrasound artifacts
  - aliasing
  - ring down artifact
  - mirror artifact
  - 超音波偽影
dateRev: 2026-06-29
same:
  - "[[ultrasound-speed-artifact]]"
  - "[[ultrasound-attenuation]]"
---

# ultrasound-artifacts

**超音波五種偽影各有成因：posterior enhancement（後方衰減少→增強）、mirror（強反射面照出鏡像）、ring-down（氣泡共振→後方連續亮線）、refraction（腹直肌-脂肪界面折射）、aliasing（都卜勒頻移超過 Nyquist 極限→波形反摺）。** 記憶鉤：aliasing 最容易考錯方向——「取樣率小於兩倍頻移（PRF < 2×頻移）」時才發生，題目若說「取樣率多於兩倍頻移」則是錯的。判讀分水嶺一：**ring-down 氣體/金屬共振、mirror 強反射鏡像、refraction 最常見於腹直肌-腹內脂肪界面**；判讀分水嶺二：**aliasing＝頻移 > PRF/2（Nyquist），即 PRF（取樣率）< 2×頻移——注意大小於方向不可記反**。

## Summary
- **Posterior enhancement**：病灶衰減少於周邊軟組織→後方回音增強。[^1]
- **Mirror artifact**：強反射面（**骨、頸動脈後壁**等）使結構在鏡像位置重複出現（含 color Doppler）。[^1]
- **Ring-down**：**氣泡/氣體**間困住的液體**共振**→後方連續高回音帶;Radiopaedia 明載 ring-down **『僅』與氣泡相關**。**金屬/膽固醇結晶**造成外觀相似但機轉不同的 **comet-tail**,勿與 ring-down 混為一談。[^1]
- **Refraction**：聲束於不同聲速介面折射;**最常見於腹直肌與腹內脂肪交界**。[^1]
- **Aliasing（都卜勒）**：當**都卜勒頻移 > Nyquist 極限（＝PRF 的一半）**時發生,即**取樣率(PRF)『小於』兩倍頻移**;表現為頻譜/彩流反摺。[^1]

## 影像判讀骨架：各偽影「長怎樣／成因／有用 vs 陷阱」

判讀總綱：B-mode 影像重建建立在四個假設上——(1) 聲束沿中央軸直線傳播；(2) 每個結構只反射聲束一次；(3) 只有位於聲束預定路徑上的結構會產生回波；(4) 結構深度與聲波往返時間成正比。**幾乎所有偽影都來自其中一個假設被打破**。[^2] 區分「真實結構 vs 偽影」的通則：真實結構在多個切面/探頭角度都能重現、邊界清楚、不會穿過解剖界線、且會擾動周邊彩流；偽影通常無法在其他切面重現、可穿越解剖界線、且不會加速或擾動周邊都卜勒血流。[^2]

### 一、反射／殘響（reverberation）家族
- **Reverberation（殘響）**：聲束在兩個近乎平行的強反射面間來回反射。影像上＝沿同一條掃描線、等間距、向深部逐漸變淡的多條平行亮線（"step-ladder／階梯狀"），且**不遵守解剖界線**。最常見的「第二反射面」其實是探頭本身→偽影出現在**真實反射面兩倍深度**處，且隨心動週期以約兩倍振幅與真實結構同向移動。陷阱：在 LA／LV 內被誤判為血栓或腫塊（源自心導管、節律器電極、主動脈鈣化）。[^2][^3]
- **Comet-tail（彗星尾）**：兩個**非常靠近**的反射面（多在同一結構內，如膽固醇結晶、金屬、人工瓣膜、玻璃）間的緻密殘響→緊接強反射體後方、向深部快速衰減變窄的短亮尾。有用徵象：膽囊腺肌瘤症（adenomyomatosis，Rokitansky-Aschoff sinus 內膽固醇結晶）的 comet-tail 是診斷依據。[^2][^3]
- **Ring-down（鳴響）**：聲束打到**被困住的氣泡/氣體**，氣泡共振後向探頭發出連續波→後方一條連續、不間斷、向深部延伸的高回音帶（與 comet-tail 的離散短線不同）。判讀分水嶺：**ring-down＝氣體特異性徵象**（腸腔氣、軟組織氣腫、膿瘍產氣菌、肋膜），腹部超音波常見、心臟超音波罕見。[^2][^3]

### 二、衰減相關：聲影 vs 增強
- **Acoustic shadowing（聲影）**：高衰減/強反射體後方回波顯著減弱。分三型——**clean（乾淨）**＝鈣化/結石/骨後方均勻無回音帶（強反射）；**dirty（髒）**＝氣體後方異質、雜亂的低回音帶（多向散射所致）；**partial（部分）**＝碎裂鈣化後方的低回音。陷阱：聲影同時遮蔽彩流訊號，可能掩蓋瓣膜逆流而低估嚴重度（人工瓣、節律器導線、緻密鈣化）；解法為換切面。[^1][^3]
- **Posterior / acoustic enhancement（後方增強）**：聲束通過低衰減結構（囊腫、積液、膿瘍、血腫）後，深部回波相對增強→囊腫後方一條亮帶。有用徵象：協助判定病灶為囊性（如 Baker's cyst、完全肌腱撕裂處積液→"cartilage interface sign"）。注意 TGC 過度補償也可造成假性增強;降低深部 gain 可減輕。[^1]

### 三、路徑／鏡像／側葉
- **Mirror image（鏡像）**：強反射面（**肺-橫膈界面、骨皮質、頸動脈後壁**等）如鏡子般在其深部重複出現淺層結構的副本。鏡像與真實結構**反向移動**、副本在反射面對側等距處。彩流與頻譜都會被一起鏡射（故可出現「雙主動脈」、雙下腔靜脈;機械二尖瓣的 LVOT 流被鏡射成假性 MR＝"pseudo-MR"）。陷阱：誤判為第二條血管或瓣膜逆流;降低深部 gain 或換角度可減輕。[^1][^2]
- **Side-lobe／grating-lobe（側葉／柵葉）**：主聲束以外的離軸能量（單晶為 side lobe，陣列探頭為 grating lobe）打到強反射體後，被機器誤判為來自中央主束→在主軸上投出「鬼影」弧線。最易在囊腫/膀胱等無回音腔內、或探頭與目標間有大量耦合劑時出現假性內部回音。陷阱：囊腫內假沉積物、瓣環/人工瓣旁假血栓或假贅生物、主動脈竇-管接合處側葉誤判為剝離皮瓣;微移探頭看回音是否恆存可鑑別。[^1][^2]

### 四、聲速／折射相關
- **Refraction（折射）／edge shadow（邊緣聲影）**：聲束以非垂直角度通過聲速不同的界面被折彎。**Edge（邊緣）偽影**＝聲束打到圓形結構（囊腫、神經鞘瘤、肌腱）的弧形邊緣大部分被反射偏離→沿邊緣外緣投出細長低回音平行線（lateral edge shadow）。判讀分水嶺：**最常見於腹直肌-腹內脂肪交界**;陷阱是被誤判為增厚的腱旁組織或病灶。心臟超音波中折射造成「lens/double image」，可在長軸出現不可能的解剖關係（如交錯重複的二尖瓣影）。[^1][^2]
- **Speed displacement（聲速位移偽影）**：機器假設軟組織聲速恆為 1540 m/s。聲束通過高聲速區（如肌肉 ~1580 m/s）回波較快返回→結構被畫得較淺;通過低聲速區（如脂肪 ~1450 m/s）→畫得較深。臨床表現：US 導引注射時針穿過肌肉-脂肪界面，針幹在脂肪側看似被折彎（彎向高聲速側）。[^1]
- **Range ambiguity（距離模糊）**：第一脈波回波在第二脈波發出後才返回，被誤認為第二脈波回波→深部結構（如大囊腫後壁）的回波被畫成淺層的假性線狀回音（似囊內分隔）。降低 PRF 可減輕。[^1]

### 五、都卜勒專屬
- **Aliasing（混疊）**：頻移 > Nyquist 極限（PRF/2）時頻譜/彩流反摺。鑑別於真實亂流：aliasing 是「色標連續環繞反摺（紅↔藍經過淺色端）」而非經黑色平流區的真實逆向血流;提高 PRF/scale、降低都卜勒頻率、移基線可消除。[^1]
- **Twinkling artifact（閃爍偽影）**：彩流模式下，強反射且**表面粗糙**的結構（最典型為結石）後方出現快速變換的紅藍雜訊色塊。機轉以機器內在「相位/時脈抖動（phase/clock jitter）」窄頻雜訊為主，表面粗糙度再使雜訊頻譜變寬;高度依賴機器設定（PRF、color-write priority、灰階與都卜勒 gain）。有用徵象：偵測小結石（泌尿道、膽道）比聲影更敏感;struvite（鳥糞石）等粗糙結石閃爍最明顯。[^4]
- **Anisotropy（各向異性）**：纖維走向結構（肌腱、韌帶、神經）在聲束**非垂直入射**時訊號被反射偏離探頭→看似低回音，易誤判為肌腱病變或撕裂。判讀關鍵：這是**角度依賴**的偽影而非真病灶;把探頭調到與纖維垂直（如 heel-toe、傾斜探頭）後低回音消失即可確認。最常見陷阱部位：Achilles 腱止點、肱二頭肌長頭腱。[^1]

> [!warning] 兩題重點
> - **2016-192 正解 E**：A 後方增強、B mirror、C ring-down、D refraction 描述**皆正確** → 「none of above（無錯誤）」。
> - **2016-193 正解 C**：Aliasing 的描述「occurs when sampling rate is **more than** twice the Doppler shift」**錯**——應為**取樣率『小於』兩倍頻移（頻移超過 Nyquist=PRF/2）**才 aliasing。A（ring-down 氣體/金屬）、B（partial torsion 高阻力波形）皆正確。

### 參考來源
[^1]: Radiopaedia *Ultrasound artifacts*、*Aliasing artifact*、*Ring down artifact*（輔助來源，實際查證 accessed 2026-06-20）：aliasing＝Doppler 間歇取樣率不足、無法正確記錄方向/速度（Nyquist：頻移 > PRF/2、即取樣率 PRF < 2×頻移時發生）;ring-down＝『僅』氣泡間困住液體共振→後方連續訊號（金屬/膽固醇之相似外觀屬機轉不同的 comet-tail）;mirror＝強反射面鏡像;refraction 常見於腹直肌-腹脂交界。posterior enhancement、acoustic shadowing 三型、speed displacement、range ambiguity、edge artifact、anisotropy 之影像表現與成因另以 [^2] 同行期刊綜述交叉佐證。相關速度/衰減偽影見 [[ultrasound-speed-artifact]]、[[ultrasound-attenuation]]。
[^2]: Hsu P-C, Chang K-V, et al. *Artifacts in Musculoskeletal Ultrasonography: From Physics to Clinics*. **Diagnostics** (Basel). 2020;10(9):645（同行評審期刊綜述，full-text via PMC PMC7555047）。逐項影像-成因-解法：focal zone/beam-width、posterior enhancement、acoustic shadowing（clean/partial/dirty）、reverberation（comet-tail 樣）、ring-down（氣泡共振→向深部衰減的連續條紋）、mirror image（強反射面如長骨對側等距副本）、anisotropy（非垂直入射→肌腱假性低回音）、side-lobe（離軸能量→囊內鬼影）、refraction（聲速差→深度誤判）、edge artifact（弧形邊緣→外緣低回音平行線）、range ambiguity（降 PRF 可改善）。[DOI](https://doi.org/10.3390/diagnostics10090645)
[^3]: Le Polain de Waroux J-B, et al. *Fact or Artifact in Two-Dimensional Echocardiography: Avoiding Misdiagnosis and Missed Diagnosis*. **J Am Soc Echocardiogr** (JASE). 2016;29(5):381-391（同行評審期刊綜述，full-text via PMC PMC4851918）。提供重建四假設、reverberation 「step-ladder」與兩倍深度／兩倍振幅同向移動、comet-tail（緊鄰多層強反射體）、ring-down（困住氣泡共振）、mirror（鏡像反向移動、彩流一併鏡射、pseudo-MR）、side-lobe vs grating-lobe 弧線鬼影穿越解剖界線、聲影遮蔽彩流低估逆流、以及「真實結構 vs 偽影」鑑別通則。[DOI](https://doi.org/10.1016/j.echo.2016.01.009)
[^4]: Kamaya A, Tuthill T, Rubin JM. *Twinkling Artifact on Color Doppler Sonography: Dependence on Machine Parameters and Underlying Cause*. **AJR Am J Roentgenol**. 2003;180(1):215-222（同行評審期刊原著）。twinkling 機轉以機器內在相位/時脈抖動（phase/clock jitter）窄頻雜訊為主、表面粗糙度使頻譜變寬;高度依賴 PRF、color-write priority、灰階與都卜勒 gain;struvite 結石後方閃爍與頻譜變寬最強;偵測小結石較聲影敏感。[DOI](https://doi.org/10.2214/ajr.180.1.1800215)
[^5]: *Problem solving in Abdominal imaging*, 1st Edition, Chapter 1, Page 6-8（2018 交換考題詳解 p.132 引用；Tier 2 教科書）。Acoustic shadowing為高衰減/強反射結構後方訊號減弱；探頭周邊聲束不均勻造成的偽影為side lobe artifact，非acoustic shadowing。

## 題目
> [!question]- Which of the following statements about sonography artifact is wrong. (2018-240)
> **Acoustic shadowing is the result of nonuniformity of the ultrasound beam at the periphery of the transducer（D）**——此描述其實是**side lobe artifact**的成因，非acoustic shadowing（聲影是高衰減/強反射結構後方訊號減弱），此敘述混淆兩者，錯誤。組織諧波成像有助於大體型/雜訊多組織(A)、殘響造成腺肌症comet-tail(B)、彩色都卜勒可加強腺肌症殘響效應(C)、鏡像偽影源自兩強反射面間反彈(E)皆為正確描述。[^5]

## 考題
```dataview
list from #交換 where contains(concepts, "ultrasound-artifacts")
```
