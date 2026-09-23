# Taiwan Weather Forecast 台灣互動式天氣預報系統 🌤️

> **從氣象資料到互動式天氣預報應用**  
> *CWA API × JSON × Python × SQLite × Streamlit*  
> *Code Smarter, Build a Better Tomorrow! 與你一起用 AI 寫程式，探索更大的世界！*

本專案依據《AI 創新微課程 Taiwan Weather Forecast》教學大綱全流程 24 個步驟所打造，整合中央氣象署 (CWA) 開放資料平台、SQLite 關聯式資料庫、Pandas 資料分析處理、Folium 互動式地理圖資視覺化、Plotly 雙溫折線圖，以及 Streamlit 現代化 Web 儀表板架構。

---

## 🌐 線上網頁版展示 (Live Demo on GitHub Pages)

- **GitHub Pages 專屬網址**：**[https://yb-802.github.io/HW1-Taiwan-Weather/](https://yb-802.github.io/HW1-Taiwan-Weather/)**
  - 免安裝任何 Python 環境，使用瀏覽器即可直接體驗全功能互動式台灣天氣地圖、雙溫折線圖、預報數據表與 AI 生活穿搭顧問！

---

## 🌟 核心特色功能

1. **中央氣象署 CWA Open Data 串接**：
   - 支援輸入個人 CWA API 授權碼即時獲取官方 JSON 資料。
   - 內建**離線擬真示範資料產生機制**，無金鑰或離線環境亦可立即可視化展示。
2. **SQLite 資料庫持久化 (data.db)**：
   - 嚴謹的關聯式資料表設計 `TemperatureForecasts(id, regionName, dataDate, minT, maxT)`。
   - 具備 `UNIQUE(regionName, dataDate)` 與 `INSERT OR REPLACE` 機制，確保重啟與重複執行不重複插入（海報 Step 20）。
3. **台灣地圖視覺化 (Folium + streamlit-folium)**：
   - 標記全台 6 大核心分區（北部、中部、南部、東北部、東部、東南部）。
   - 依據當日平均氣溫動態漸層著色（藍 `< 20°C`、綠 `20~25°C`、橘 `25~30°C`、紅 `> 30°C`）。
   - 點擊標記即可顯示地區天氣詳細資訊彈窗 (Popup)。
4. **一週氣溫折線圖 (Plotly Interactive Chart)**：
   - 最高氣溫 (MaxT - 紅線) 與最低氣溫 (MinT - 藍線) 雙軌趨勢對比。
   - 支援懸停數值提示 (Hover Tooltip) 與數據點標註。
5. **預報數據表格與 CSV 匯出**：
   - 清晰表格化呈現 Date, MinT, MaxT, AvgT 及溫差指標，並支援一鍵匯出 CSV。
6. **AI 天氣顧問與生活提醒**：
   - 依據氣象數值智慧運算今日穿搭指南（短袖/洋蔥式/保暖毛衣）、出行建議與防護提醒。
7. **課程 24 步驟學習地圖**：
   - 內建完整的 24 步實作架構回顧，清楚對照海報學習進程。

---

## 📂 專案檔案結構

```text
HW1-Taiwan-Weather/
├── index.html          # GitHub Pages 線上網頁版首頁 (純 HTML5)
├── style.css           # 現代化響應式深藍科技感風格樣式表 (純 CSS3)
├── app.js              # 前端互動邏輯 (Leaflet 台灣地圖、Chart.js 折線圖、AI 運算)
├── app.py              # Streamlit 核心 Python Web 應用程式
├── cwa_api.py          # CWA API 串接、JSON 解析與擬真資料產生模組
├── database.py         # SQLite (data.db) 資料庫初始化、寫入與 SQL 查詢
├── data.db             # SQLite 資料庫檔案 (已內建初始氣候資料)
├── requirements.txt    # 專案相依 Python 套件清單
├── .gitignore          # Git 忽略設定
└── README.md           # 專案說明文件
```

---

## 🚀 快速開始 (Quick Start)

### 1. 安裝相依套件

確保已安裝 Python 3.10+，於專案目錄執行：

```bash
pip install -r requirements.txt
```

### 2. 啟動 Web 應用

執行 Streamlit 服務：

```bash
streamlit run app.py
```

或使用 Python 模組指令啟動：

```bash
python -m streamlit run app.py
```

啟動後，瀏覽器將自動開啟或請訪問：`http://localhost:8501`。

---

## 🗺️ 氣溫視覺化溫標對照 (Temperature Color Scale)

| 平均氣溫範圍 | 標記顏色 | 體感說明 |
| :--- | :--- | :--- |
| **< 20°C** | 🔵 藍色 | 寒冷 / 偏涼 |
| **20°C ~ 25°C** | 🟢 綠色 | 舒適宜人 |
| **25°C ~ 30°C** | 🟠 橘色 | 溫暖微熱 |
| **> 30°C** | 🔴 紅色 | 炎熱高溫 |

---

## 📚 對應海報 24 個學習步驟

| 步驟編號 | 學習主題 | 對應程式模組 / 實作成果 |
| :---: | :--- | :--- |
| 1 ~ 3 | 課程介紹、生活重要性、CWA Open Data 平台 | 系統設計、側邊欄 API Key 設定介面 |
| 4 ~ 7 | Requests 抓取、JSON 解析、MinT/MaxT 提取、Pandas 整理 | `cwa_api.py` 中的解析與結構化轉換 |
| 8 ~ 10 | 建立 SQLite、表結構設計、SQL 驗證 | `database.py` (TemperatureForecasts 表) |
| 11 ~ 16 | Streamlit 入門、SQL 讀取、地區選單、折線圖、資料表、整合介面 | `app.py` 儀表板、Plotly 折線圖與表格 |
| 17 ~ 18 | Folium 地圖視覺化、日期切換聯動 | `app.py` 中的 Folium 台灣著色地圖 |
| 19 ~ 20 | 完整成果儀表板、重複執行防重複插入與品質優化 | `INSERT OR REPLACE`、響應式佈局 |
| 21 | 專案上傳至 GitHub | 本專案遠端儲存庫與版本管理 |
| 22 ~ 24 | 延伸 AI 生活應用、重點回顧與未來展望 | AI 天氣穿搭指南模組與技術導覽 |

---

## 👨‍💻 授權與致謝

- **授權協議**：MIT License
- **氣象資料來源**：[中華民國交通部中央氣象署開放資料平台](https://opendata.cwa.gov.tw/)
