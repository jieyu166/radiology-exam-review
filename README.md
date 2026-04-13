# 放射科交換考題複習

放射科住院醫師交換考題線上複習系統，支援卡片翻牌、列表瀏覽、模擬考試三種模式。

## 功能特色

- **卡片模式**：逐題翻牌複習（題目 → 答案 → 詳解），支援觸控滑動與鍵盤導航
- **列表模式**：所有題目以可展開的 accordion 呈現，快速瀏覽
- **模擬考模式**：隨機抽題、倒數計時、自動評分與錯題分析
- **概念卡片**：疾病/概念知識卡片，與考題雙向連結
- **編輯介面**：醫師可直接在網頁上修改題目內容、標記已確認
- **內容審核**：每題有 `checked` 欄位，預設只顯示已確認內容
- **響應式設計**：手機、平板、桌面皆可使用

## 使用方式

### 線上使用

前往 GitHub Pages：`https://jieyu166.github.io/radiology-exam-review/`

### 本機使用

```bash
# 啟動本地伺服器
python -m http.server 8080
# 開啟瀏覽器前往 http://localhost:8080
```

### 編輯流程

1. 開啟「編輯模式」
2. 點擊題目的「編輯」按鈕
3. 修改內容後點「儲存」（暫存於 localStorage）
4. 完成所有修改後，點「匯出 JSON」下載更新的資料檔
5. 將下載的 JSON 檔案替換 `data/` 目錄中的對應檔案
6. `git commit` + `git push` 發布更新

## 資料來源

- 交換考題 PDF（2016-2023）
- 目前已匯入：2016 年（121 題、58 張圖片）

## 技術架構

- 純 HTML / JavaScript / CSS（無框架）
- 靜態網站，部署於 GitHub Pages
- 資料以 JSON 格式儲存
- PDF 解析使用 Python + PyMuPDF

## 專案結構

```
radiology-exam-review/
├── index.html              # SPA 入口
├── css/main.css            # 樣式
├── js/                     # JavaScript 模組
│   ├── app.js              # 路由
│   ├── data-loader.js      # 資料載入
│   ├── question-store.js   # 題目篩選
│   ├── card-mode.js        # 卡片模式
│   ├── list-mode.js        # 列表模式
│   ├── exam-mode.js        # 模擬考
│   ├── concept-cards.js    # 概念卡片
│   └── editor.js           # 編輯介面
├── data/
│   ├── index.json          # 年份索引
│   ├── 2016.json           # 2016 考題
│   ├── concepts.json       # 概念資料
│   └── images/2016/        # 考題圖片
└── scripts/
    └── parse_2016.py       # PDF 解析腳本
```
