---
name: curated-food-guide-builder
description: >-
  Extracts, verifies, and compiles local foodie recommendations and hidden gems from Threads posts, comments, or web reviews into a mobile-friendly offline interactive HTML guide, complete with Google Maps navigation, categorized filters, avoidance tips, and automated Google Drive/iCloud synchronization.
---

# Curated Food Guide Builder (社群私房美食指南萃取與雲端同步工作流)

## 概述 (Overview)

本 Skill 專門用於將社群平台（特別是 Threads 貼文、串文及大量留言討論串）中的在地美食推薦、私房清單與避雷心得，經由深層網路擷取、Google 評價與現況核實，自動封裝成高質感的**行動優先（Mobile-First）單檔離線 HTML 互動手冊**，並配置 **macOS LaunchAgent 系統級背景監控服務**，實現本地工作區與 Google Drive / iCloud 雲端的即時雙向持續同步。

---

## 核心產出架構 (Workflow Architecture)

```
[ Threads / 社群貼文或分享連結 ]
               │
               ▼ (Phase 1)
   Threads 深層數據爬取 (GraphQL + Googlebot UA + 分頁游標)
               │
               ▼ (Phase 2)
   店家結構化萃取 + Google 評價/歇業現況/避雷技巧核實
               │
               ▼ (Phase 3)
   產生行動優先單檔 HTML Web App (即時搜尋 + 分類 + 地圖導航)
               │
               ▼ (Phase 4)
   雙雲端自動同步 (Google Drive + iCloud + macOS LaunchAgent 監控)
```

---

## 標準執行步驟 (Standard Operating Procedure)

### 第一階段：Threads 數據深層採集
Threads 前端採用客戶端 Hydration 與 GraphQL API，單純以一般瀏覽器 User-Agent 抓取僅能取得少量 SSR 標籤。
1. 使用 `Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)` 作為 User-Agent，取得初始 HTML。
2. 解析頁面中的 `LSD` token、`APP_ID` 以及 `adp_BarcelonaPostPageDownwardQueryRelayPreloader` 中的 `queryID`（doc_id）與 `variables`。
3. 呼叫 `https://www.threads.net/api/graphql`，提取：
   * 原作者主貼文（Caption）。
   * 原作者的自身延伸串文（`self_thread`，通常含有清單的第 10～50 項）。
   * 讀者留言與推薦（`direct_replies`）。
4. 依據 `page_info.has_next_page` 與 `end_cursor` 進行分頁迭代，直到抓完所有討論。
5. 工具腳本：
   ```bash
   python3 scripts/extract_threads_thread.py --url "<Threads_URL>" --output "/tmp/threads_extracted.json"
   ```

### 第二階段：店家數據結構化與情報核對（跨縣市鄉鎮市區統一格式）
將抓取到的原始留言整理為標準 JSON 陣列（儲存於 `data/taiwan_food_guides_unified.json`），每筆店家包含：
* `uid`：店家唯一識別編號（如 `CY-01`、`TN-01`）
* `name`：店家全名（標準招牌名稱）
* `city`：台灣縣市名稱（如：`嘉義市`、`臺南市`）
* `district`：鄉鎮市區名稱（如：`東區`、`西區`、`新營區`、`後壁區`）
* `category`：統一 9 大主分類（`正餐主食`、`在地小吃`、`麵點湯包`、`早餐早午餐`、`宵夜炭烤日料`、`鍋物補湯`、`烘焙甜點冰品`、`手搖咖啡茶飲`、`已歇業提醒`）
* `subCategory`：細部屬性標籤
* `rating`：評價或推薦亮點標籤
* `dishes` / `dishText`：推薦必點菜色陣列與文字
* `comment`：特色與饕客評價整理
* `tips`：**避雷與內行吃法重點**（如：醬汁需叫少一點、外帶務必提早電話預訂、特製辣醬是靈魂、排隊數小時名店等；若已歇業需特別標明）
* `address`：完整地址（含縣市與鄉鎮市區）
* `time`：營業時段或出爐提醒
* `tags`：關鍵字標籤陣列

### 第三階段：產生單檔行動版 HTML 手冊（支援縣市 ➔ 鄉鎮市區 ➔ 餐點類型三級分頁）
使用預載的現代 CSS 與原生 JavaScript 模板，輸出為純前端單檔 HTML（`美食避雷隨身手冊.html`）：
1. **免網路離線可用**：無需依賴外部 CDN 或龐大框架，純原生支援 iOS Safari 與 Android Chrome。
2. **三級行政區與分類分頁**：第一層切換「台灣縣市」、第二層切換「鄉鎮市區」、第三層切換「餐點類型」，並支援即時模糊搜尋。
3. **導航整合**：每個店家卡片附帶 Google Maps 精準導航按鈕，點擊可直接喚起地圖。
4. **貼心互動**：附有一鍵複製店訊功能（含區域、店名、必點與地址）。
5. 工具腳本：
   ```bash
   python3 scripts/build_unified_guide.py
   ```

### 第四階段：配置多端雲端自動即時同步
為了讓使用者在手機上隨時看到最新版本，並能將檔案分享給他人：
1. 專案工作區路徑：`/Users/mac/AGY本地工作區/專案資料夾/美食景點整理/美食避雷隨身手冊.html`
2. Google 雲端硬碟目標：`~/Library/CloudStorage/GoogleDrive-cieaer.g@gmail.com/我的雲端硬碟/AGY工作區GD/美食隨身手冊/`
3. Apple iCloud Drive 目標：`~/Library/Mobile Documents/com~apple~CloudDocs/AGY工作區i/美食隨身手冊/`
4. 部署 `~/Library/LaunchAgents/com.foodguide.sync.plist` 服務，監聽本地手冊檔案。只要手冊更新存檔，系統在 2 秒內自動比對 SHA256 並同步至 Google Drive 與 iCloud，手機端即刻自動同步。
5. 工具腳本：
   ```bash
   python3 .agents/skills/curated-food-guide-builder/scripts/setup_cloud_sync.py \
     --files "/Users/mac/AGY本地工作區/專案資料夾/美食景點整理/美食避雷隨身手冊.html"
   ```

---

## 內建工具腳本說明 (Utility Scripts)

| 腳本名稱 | 說明 |
| :--- | :--- |
| [`scripts/extract_threads_thread.py`](./scripts/extract_threads_thread.py) | 模擬 Googlebot 解析 Threads 貼文短網址、抓取 token 並分頁拉取所有留言與串文。 |
| [`scripts/generate_guide_app.py`](./scripts/generate_guide_app.py) | 依據標準化店家 JSON 注入範本，產生包含搜尋、分類與導航之單檔 HTML 手冊。 |
| [`scripts/setup_cloud_sync.py`](./scripts/setup_cloud_sync.py) | 自動設定 macOS LaunchAgent 監控本地檔案，自動同步至 Google Drive 與 iCloud。 |

---

## 常見陷阱與注意事項 (Common Pitfalls)

1. **Threads 資料截斷問題**：
   * 原作者貼文若超過字數常會以自身回文（`self_thread`）接續（例如 10～21 號店在第一則回覆，22～31 號店在第二則回覆）。若僅爬取 `direct_replies` 會遺漏原作者的後續清單，必須同時檢查 `self_thread` 與 `direct_replies`。
2. **店家營業狀態變更**：
   * 社群推薦常含有數年前甚至已歇業的店家（如 WT 早午餐）。提取時必須使用網路搜尋進行存續狀態查核，已歇業店家應特別標記警示，避免讀者白跑。
3. **單檔 HTML 獨立性**：
   * 產生的手冊必須維持完全自給自足（所有 CSS 與 JS 內嵌在單一 `.html` 檔案中），嚴禁引用未經快取的外部不穩定 CDN，以保證手機離線或傳送給他人時能 100% 完整打開運作。
