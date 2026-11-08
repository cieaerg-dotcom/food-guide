# 🍽️ 美食景點整理 (Curated Food & Travel Guides)

本專案致力於將社群平台（Threads、Instagram、Dcard 等）與老饕社群的私房推薦、真實評價與避雷心得，萃取並整理為**行動優先（Mobile-First）的離線單檔 Web App 隨身手冊**，並結合 **macOS 系統級即時雲端同步**，讓使用者在手機上隨時離線瀏覽、即時搜尋與一鍵地圖導航。

---

## 📂 目前收錄進度與成果（單一檔案跨縣市鄉鎮區整合版）

所有縣市與鄉鎮市區資料已統一格式並整合進單一離線互動手冊 **[`美食避雷隨身手冊.html`](./美食避雷隨身手冊.html)**（共收錄 **103 間**）：

| 縣市分頁 | 鄉鎮市區子分頁 | 收錄數量 | 核心亮點 |
| :--- | :--- | :---: | :--- |
| **嘉義市** | **東區** | **32 間** | 五千金炒飯、豆豆小籠湯包、黃記／南門白醋涼麵、劉湯圓（脆圓）、阿霞滷肉飯、阿婆烤玉米 |
| **嘉義市** | **西區** | **28 間** | 緯英海南雞飯、桔吉力早餐、大眾水餃、霜空咖啡、友愛鹹酥雞、今生茶記 |
| **臺南市** | **新營區** | **42 間** | 溪北飯桌、小紅堂牛肉麵、燒蛋一下、阿翔蚵仔煎（鐵板炒飯）、榮昌雞肉飯、惟式巴斯克 |
| **臺南市** | **後壁區** | **1 間** | 樂檸漢堡（新營服務區北上店，可由外圍後方秘密便道進入） |

---

## 🏗️ 專案目錄結構

```text
/Users/mac/AGY本地工作區/專案資料夾/美食景點整理/
├── README.md                          # 專案說明文件與操作手冊
├── 美食避雷隨身手冊.html               # 全台縣市 × 鄉鎮市區整合版單檔離線手冊 (103 間)
├── guides/                            # 手冊備份歸檔目錄
│   └── 美食避雷隨身手冊.html
├── data/                              # 原始社群爬取與統一結構化之 JSON 數據庫
│   ├── taiwan_food_guides_unified.json # 全台跨縣市鄉鎮市區統一格式總表 (103 間)
│   ├── chiayi_stores_structured.json  # 嘉義市 60 間結構化資料
│   ├── tainan_xinying_structured.json # 臺南市（新營／後壁）43 間結構化資料
│   └── threads_chiayi_raw.json        # 嘉義貼文與 154 則串文留言完整結構數據
├── scripts/                           # 專案自動化建置與同步腳本
│   ├── build_unified_guide.py         # 跨縣市鄉鎮區資料正規化與單檔 HTML 建置腳本
│   └── deploy_web.py                  # 本機與 GitHub Pages 網頁自動建置同步腳本
├── logs/                              # 同步與背景監控日誌
│   └── food_guides_sync.log
└── .agents/skills/                    # 專案內嵌 Skill
    └── curated-food-guide-builder/    # 社群美食指南自動化工作流
```

---

## ☁️ 網站發布與本機同步架構 (GitHub Pages)

本專案已停止 Google Drive / iCloud 雲端同步，改採 **本機 ➔ GitHub Pages 網頁同步**：

* **網站原始碼目錄**：`web_dist/`（包含 PWA 快取與離線網頁檔案）
* **自動部署腳本**：[`scripts/deploy_web.py`](./scripts/deploy_web.py)
* **自動發布機制**：
  1. 當本機修改或抓取新店家後，執行 `python3 scripts/deploy_web.py`。
  2. 腳本會自動重新產製手冊與網站包，並透過 Git 提交推送到 GitHub。
  3. GitHub Actions 會自動啟動，在 1~2 分鐘內將最新店家資料發布至 GitHub Pages 線上網站。
  4. 手機已安裝的 PWA 或網頁將自動無縫接收最新資料。

---

## 🛠️ 如何擴充新城市（工作流）

本專案已建立專屬 Skill：`curated-food-guide-builder`。若未來想新增其他城市（如台南市區、高雄、台中等）：
1. 提供 Threads 貼文網址給 AGY。
2. 執行第一階段爬蟲抓取主貼文與所有分頁留言：
   ```bash
   python3 .agents/skills/curated-food-guide-builder/scripts/extract_threads_thread.py \
     --url "<Threads_貼文網址>" \
     --output "data/城市名_raw.json"
   ```
3. 經由 AGY 進行 Google 評價與營業狀態核查後，產出行動版單檔 HTML：
   ```bash
   python3 .agents/skills/curated-food-guide-builder/scripts/generate_guide_app.py \
     --input "data/結構化店家.json" \
     --output "城市美食精選隨身手冊.html" \
     --title "城市美食精選隨身手冊" \
     --subtitle "在地精選避雷手札" \
     --region "城市名"
   ```
4. 檔案存檔後將自動同步至雲端供手機隨時查閱。

---

## 📱 手機瀏覽與分享方式

1. **自己瀏覽**：從手機 Google Drive App 或 iPhone「檔案」App 點選 `index.html`，即可滿版順跑，離線亦可搜尋與查看。
2. **分享他人**：
   * **Google Drive 共用**：將雲端「美食隨身手冊」資料夾開啟「知道連結者皆可檢視」傳送。
   * **LINE / AirDrop 單檔傳送**：HTML 手冊為完全自給自足單檔，直接傳送即可在對方手機瀏覽器完美運行。
