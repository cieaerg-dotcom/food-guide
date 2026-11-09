---
name: curated-food-guide-builder
description: >-
  Extracts, verifies, and compiles local foodie recommendations and hidden gems from Threads posts, comments, or web reviews into a mobile-friendly offline interactive HTML guide, complete with Google Maps navigation, categorized filters, avoidance tips, and GitHub Pages PWA deployment.
---

# Curated Food Guide Builder (社群私房美食指南萃取與靜態網站發布工作流)

## 概述 (Overview)

本 Skill 專門用於將社群平台（特別是 Threads 貼文、串文及大量留言討論串）中的在地美食推薦、私房清單與避雷心得，經由深層網路擷取、Google 評價與現況核實，自動封裝成高質感的**行動優先（Mobile-First）單檔離線 HTML 互動手冊**，並結合 **GitHub Pages 靜態網站自動化部署 (PWA)**。

> ⚠️ **【重要架構原則】本專案已全面永久取消 Google Drive 與 iCloud Drive 雲端硬碟同步，改採全本地離線單檔與 GitHub Pages 部署。**

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

### 第二階段：店家數據結構化與情報核對（含爭議對照庫與 Google 評論審查）
在將留言收錄進資料庫前，必須嚴格執行「**防商業水軍與社群爭議深度核查**」：
1. **識別官方自薦與親友拉抬**：過濾店家官方帳號、同名帳號與特定帳號互相 @ 吹捧。
2. **踢除連鎖加盟與粗飽型店家**：非在地老饕私房、依靠廉價麵食冰品吃到飽或大型商業集團網美店一律排除。
3. **比對社群踩雷爭議對照庫**：
   - 提取待審店家是否命中 `data/community_controversy_reference.json`（如知名大排長龍店或曾有重大爭議之店家）。
   - **非一刀切封殺**，而是帶著脆友指控的具體痛點（如排隊性價比低、某道菜腥柴、加湯縮水等），調閱 **Google 評論** 進行針對性核實。
   - 做出正確判斷：若食安嚴重則排除；若屬瑕不掩瑜或情境爭議，則在卡片 `tips` 中明確揭露真實老饕反饋與避坑指南（哪道菜必避、哪個時段人少、破除觀光神話）。
4. 將抓取到的原始留言整理為標準 JSON 陣列（儲存於 `data/taiwan_food_guides_unified.json`），每筆店家包含：
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

### 第四階段：網站靜態發布與本地部署（GitHub Pages PWA 架構，停用雲端硬碟同步）
> ⚠️ **【專案核心底層架構原則】**
> **雲端硬碟（Google Drive / iCloud Drive）同步機制已永久取消且停用。**
> 嚴禁再建立 macOS LaunchAgent 服務對第三方雲端硬碟進行同步或輪詢。
> 所有手冊的發布與分發一律依循：
> 1. 本地單檔離線 HTML（`美食避雷隨身手冊.html`、`全台看海放空旅宿隨身手冊.html`）。
> 2. GitHub Pages 靜態網站自動部署（執行 `python3 scripts/deploy_web.py`）。

---

### 【核心作業規則】單店名快速審查與自動收錄閉環工作流 (Single Store Instant Audit & Ingestion)
當使用者僅丟出單一店名時，背景自主啟動以下自動化閉環處理，無需逐一詢問或等待確認：
1. **爭議庫快速比對**：執行 `python3 scripts/check_controversy_reference.py "<店名>"`，核查是否命中社群踩雷爭議名單。
2. **多維度現況核查**：聯網查證 Google 評論與在地評價，核對店家存續狀態、核心必點、價格與真實痛點。
3. **價值判定與自動收錄**：
   - 若為重大地雷、衛生食安問題嚴重或已永久歇業，予以排除並回報具體原因。
   - 若為真實口碑佳、值得收錄之好店，直接以標準結構化格式寫入 `data/taiwan_food_guides_unified.json`（賦予獨立 UID、分類、必點菜色與避坑吃法攻略）。
4. **自動化編譯與部署**：執行 `python3 scripts/deploy_web.py`，完成單檔離線 HTML 與 GitHub Pages PWA 自動同步發布。
5. **回報結論**：直接提供核查結果、避坑重點與收錄狀態。

工具腳本：
```bash
python3 scripts/deploy_web.py
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
