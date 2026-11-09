# 美食景點整理專案底層架構原則 (PROJECT_RULES.md)

本檔案為本專案不可違背之底層架構規範，所有操作與腳本開發皆必須嚴格遵守：

## 1. 雲端硬碟同步已全面取消且永久停用
- **嚴禁**建立、啟用或維護任何向 Google Drive（如 `~/Library/CloudStorage/GoogleDrive-...`）或 Apple iCloud Drive（`~/Library/Mobile Documents/...`）的檔案複製、同步腳本或 macOS LaunchAgent 監控服務。
- **嚴禁**在背景常駐執行定時同步行程或輪詢。

## 2. 發布與傳播渠道（雙軌制）
- **軌道一：本地單檔離線優先**
  - 所有手冊產出物（如《美食避雷隨身手冊.html》、《全台看海放空旅宿隨身手冊.html》）必須為 **100% 預渲染、內嵌 Inline CSS、零外部 CDN 依賴** 的純前端 HTML 單檔。
  - 支援 AirDrop、社群通訊軟體分享或在手機檔案中直接離線打開。
- **軌道二：GitHub Pages 靜態網站 (PWA)**
  - 靜態網站包統一存放於 `web_dist/`。
  - 透過 `scripts/deploy_web.py` 一鍵重新建置雙手冊並推送至 GitHub 儲存庫（`cieaerg-dotcom/food-guide`），觸發 GitHub Actions 線上部署。
