#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
全台美拍私房景點隨身手冊 生成器 (build_attractions_guide.py)
-----------------------------------------------------------------------------
功能說明：
1. 讀取 data/taiwan_attractions_unified.json 結構化景點資料。
2. 產出 100% 離線可用、深邃翡翠綠山林與文化意象設計、支援手機/平板/電腦的互動手冊。
3. 採用與美食手冊完全相同之架構（三級分頁：縣市 ➔ 鄉鎮市區 ➔ 景點類型、全文即時搜尋、卡片預渲染、Google Maps 導航）。
4. 輸出至「全台美拍私房景點隨身手冊.html」及「web_dist/attractions.html」。
=============================================================================
"""

import json
import os
import re
import html
import urllib.parse
from collections import Counter

BASE_DIR = "/Users/mac/AGY本地工作區/專案資料夾/美食景點整理"
UNIFIED_JSON_PATH = os.path.join(BASE_DIR, "data", "taiwan_attractions_unified.json")
OUTPUT_HTML_PATH = os.path.join(BASE_DIR, "全台美拍私房景點隨身手冊.html")
WEB_DIST_DIR = os.path.join(BASE_DIR, "web_dist")

def esc(text):
    if text is None:
        return ""
    return html.escape(str(text))

def render_attraction_card(s, is_dist=False):
    uid = s.get("uid", "")
    name = s.get("name", "")
    city = s.get("city", "")
    district = s.get("district", "")
    category = s.get("category", "")
    sub_cat = s.get("subCategory", "")
    rating = s.get("rating", "")
    dishes = s.get("dishes", [])
    dish_text = s.get("dishText", "")
    comment = s.get("comment", "")
    tips = s.get("tips", "")
    address = s.get("address", "")
    time_info = s.get("time", "")
    tags = s.get("tags", [])

    # 依據縣市設定膠囊配色（Inline CSS）
    if city == "嘉義市":
        region_style = "background-color:#fef3c7;color:#b45309;border:1px solid #fde68a;"
    elif city == "嘉義縣":
        region_style = "background-color:#f0fdf4;color:#15803d;border:1px solid #bbf7d0;"
    else:
        region_style = "background-color:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;"

    cat_style = "background-color:#f1f5f9;color:#334155;border:1px solid #e2e8f0;"
    card_bg_style = "background-color:#ffffff;border:1px solid #e2e8f0;"

    highlights_html = "".join(
        f'<span style="display:inline-block;font-size:12px;font-weight:700;color:#065f46;background-color:#d1fae5;padding:2.5px 8px;border-radius:6px;margin:2px 4px 2px 0;">{esc(d)}</span>'
        for d in dishes
    )

    tags_html = "".join(
        f'<span style="font-size:11px;color:#64748b;background-color:#f8fafc;border:1px solid #e2e8f0;padding:1px 6px;border-radius:4px;margin-right:4px;">#{esc(t)}</span>'
        for t in tags
    )

    map_q = s.get("mapQuery") or f"{city}{district} {name}"
    map_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(map_q)}"

    search_tokens = " ".join([
        name, city, district, category, sub_cat, dish_text, comment, tips, address, " ".join(tags)
    ]).lower()

    js_region = esc(f"{city}{district}")
    js_name = esc(name)
    js_addr = esc(address)
    js_highlights = esc(dish_text)

    card_html = f"""
    <article class="store-card"
               data-city="{esc(city)}"
               data-district="{esc(district)}"
               data-city-district="{esc(city)}・{esc(district)}"
               data-category="{esc(category)}"
               data-search="{esc(search_tokens)}"
               style="{card_bg_style}border-radius:14px;padding:15px;box-shadow:0 2px 6px rgba(15,23,42,0.04);display:flex;flex-direction:column;justify-content:space-between;transition:transform 0.15s ease,box-shadow 0.15s ease;">
      <div>
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;gap:6px;flex-wrap:wrap;">
          <div style="display:flex;gap:5px;align-items:center;flex-wrap:wrap;">
            <span style="font-size:11px;font-weight:800;padding:2.5px 8px;border-radius:6px;{region_style}">{esc(city)}・{esc(district)}</span>
            <span style="font-size:11px;font-weight:600;padding:2.5px 8px;border-radius:6px;{cat_style}">{esc(category)}｜{esc(sub_cat)}</span>
          </div>
          <span style="font-size:11px;font-weight:700;color:#047857;background-color:#ecfdf5;border:1px solid #a7f3d0;padding:2px 8px;border-radius:6px;">✨ {esc(rating)}</span>
        </div>

        <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:6px;">
          <h2 style="font-size:17px;font-weight:800;color:#0f172a;line-height:1.3;margin:0;">{esc(name)}</h2>
          <span style="font-size:12px;font-weight:700;color:#94a3b8;font-family:monospace;">#{esc(uid)}</span>
        </div>

        <div style="margin-bottom:8px;">
          <div style="font-size:11.5px;color:#047857;font-weight:700;margin-bottom:3px;">📸 必看亮點 / 推薦特色：</div>
          <div style="line-height:1.6;">{highlights_html}</div>
        </div>

        <div style="font-size:13.5px;color:#334155;margin-bottom:10px;line-height:1.55;flex:1;">{esc(comment)}</div>

        <div style="background-color:#f0fdf4;border-left:3.5px solid #059669;padding:9px 11px;border-radius:0 8px 8px 0;font-size:12.5px;color:#064e3b;margin-bottom:10px;line-height:1.5;">
          <b style="color:#047857;">💡 避坑與內行玩法：</b>{esc(tips)}
        </div>
      </div>

      <div>
        <div style="font-size:12px;color:#64748b;margin-bottom:8px;line-height:1.45;display:flex;flex-direction:column;gap:3px;">
          <div style="display:flex;align-items:flex-start;gap:5px;"><span>📍</span><span>{esc(address)}</span></div>
          <div style="display:flex;align-items:center;gap:5px;"><span>⏰</span><span>{esc(time_info)}</span></div>
        </div>

        <div style="display:flex;gap:7px;margin-top:4px;">
          <a href="{map_url}" target="_blank" rel="noopener noreferrer"
             style="flex:1;text-align:center;background-color:#059669;color:#ffffff;text-decoration:none;padding:7px 0;border-radius:8px;font-size:12.5px;font-weight:700;display:inline-flex;align-items:center;justify-content:center;gap:4px;">
            <span>🗺️ Google Maps 導航</span>
          </a>
          <button type="button" onclick="copyAttraction('{js_region}', '{js_name}', '{js_highlights}', '{js_addr}')"
                  style="flex:0.6;background-color:#f1f5f9;color:#334155;border:1px solid #cbd5e1;padding:7px 0;border-radius:8px;font-size:12.5px;font-weight:700;cursor:pointer;">
            📋 複製資訊
          </button>
        </div>

        <div style="margin-top:9px;padding-top:7px;border-top:1px dashed #f1f5f9;display:flex;flex-wrap:wrap;gap:4px;">
          {tags_html}
        </div>
      </div>
    </article>
    """
    return card_html

def build_guide(is_dist=False):
    with open(UNIFIED_JSON_PATH, "r", encoding="utf-8") as f:
        attractions = json.load(f)

    total_count = len(attractions)
    city_counts = Counter(s["city"] for s in attractions)
    dist_counts = Counter((s["city"], s["district"]) for s in attractions)

    city_icons = {
        "嘉義市": "🐓",
        "嘉義縣": "🌲",
        "臺南市": "🏛️"
    }

    # 1. 縣市分頁按鈕
    city_tab_buttons = [
        f"""        <button type="button" data-city-btn="all" onclick="selectCity('all')"
                style="flex:1;min-width:fit-content;padding:8px 14px;border-radius:12px;border:1.5px solid #064e3b;background-color:#064e3b;color:#ffffff;font-size:13.5px;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;gap:6px;white-space:nowrap;">
          <span>🗺️ 全部縣市</span>
          <span style="font-size:11.5px;padding:1px 7px;border-radius:999px;background-color:rgba(255,255,255,0.22);color:#ffffff;">{total_count}</span>
        </button>"""
    ]
    ordered_cities = ["嘉義市", "嘉義縣", "臺南市"]
    for c in ordered_cities:
        if c in city_counts:
            icon = city_icons.get(c, "📍")
            cnt = city_counts[c]
            city_tab_buttons.append(
                f"""        <button type="button" data-city-btn="{esc(c)}" onclick="selectCity('{esc(c)}')"
                style="flex:1;min-width:fit-content;padding:8px 14px;border-radius:12px;border:1.5px solid #e2e8f0;background-color:#f8fafc;color:#475569;font-size:13.5px;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;gap:6px;white-space:nowrap;">
          <span>{icon} {esc(c)}</span>
          <span style="font-size:11.5px;padding:1px 7px;border-radius:999px;background-color:rgba(100,116,139,0.15);color:inherit;">{cnt}</span>
        </button>"""
            )
    city_tabs_html = "\n".join(city_tab_buttons)

    # 2. 鄉鎮市區按鈕
    dist_buttons = [
        f"""        <button type="button" data-dist-btn="all" onclick="selectDistrict('all')"
                style="flex-shrink:0;padding:4px 11px;border-radius:8px;border:1px solid #cbd5e1;background-color:#ffffff;color:#047857;font-size:12.5px;font-weight:700;cursor:pointer;box-shadow:0 1px 2px rgba(0,0,0,0.06);">
          全部鄉鎮市區 ({total_count})
        </button>"""
    ]
    city_sort_order = {"嘉義市": 0, "嘉義縣": 1, "臺南市": 2}
    sorted_dists = sorted(
        dist_counts.items(),
        key=lambda x: (city_sort_order.get(x[0][0], 99), x[0][1])
    )
    for (c, d), cnt in sorted_dists:
        dist_key = f"{c}・{d}"
        dist_buttons.append(
            f"""        <button type="button" data-dist-btn="{esc(dist_key)}" data-dist-city="{esc(c)}" onclick="selectDistrict('{esc(dist_key)}')"
                style="flex-shrink:0;padding:4px 11px;border-radius:8px;border:1px solid transparent;background-color:transparent;color:#475569;font-size:12.5px;font-weight:600;cursor:pointer;">
          {esc(dist_key)} ({cnt})
        </button>"""
        )
    district_bar_html = "\n".join(dist_buttons)

    # 3. 預渲染卡片
    cards_prerendered = "\n".join(render_attraction_card(s, is_dist) for s in attractions)

    food_link = "index.html" if is_dist else "美食避雷隨身手冊.html"
    seaview_link = "seaview.html" if is_dist else "全台看海放空旅宿隨身手冊.html"
    attractions_link = "attractions.html" if is_dist else "全台美拍私房景點隨身手冊.html"

    full_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>全台美拍私房景點隨身手冊 ｜ 手機離線獨立版</title>
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="theme-color" content="#047857">
  <style>
    * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
    .no-scrollbar::-webkit-scrollbar {{ display: none; }}
    .no-scrollbar {{ -ms-overflow-style: none; scrollbar-width: none; }}
    @media (min-width: 680px) {{
      #storesGrid {{
        display: grid !important;
        grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)) !important;
      }}
    }}
  </style>
</head>
<body style="margin:0;padding:0 0 84px 0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'PingFang TC','Microsoft JhengHei',sans-serif;background-color:#f8fafc;color:#0f172a;line-height:1.55;-webkit-font-smoothing:antialiased;">

  <!-- 三大主題跨手冊切換列 -->
  <div style="background-color:#0f172a;padding:8px 12px;display:flex;justify-content:center;gap:8px;font-size:12.5px;font-weight:700;">
    <a href="{food_link}" style="color:#cbd5e1;text-decoration:none;padding:5px 12px;border-radius:999px;border:1px solid #334155;background:#1e293b;">🍱 美食避雷手冊</a>
    <a href="{attractions_link}" style="color:#ffffff;text-decoration:none;padding:5px 12px;border-radius:999px;border:1px solid #10b981;background:#065f46;">📸 私房美拍景點</a>
    <a href="{seaview_link}" style="color:#cbd5e1;text-decoration:none;padding:5px 12px;border-radius:999px;border:1px solid #334155;background:#1e293b;">🌊 看海放空旅宿</a>
  </div>

  <!-- 頂部橫幅（全內嵌 Inline CSS） -->
  <header style="background:linear-gradient(135deg,#064e3b 0%,#047857 50%,#059669 100%);background-color:#047857;color:#ffffff;padding:24px 16px 18px;text-align:center;box-shadow:0 4px 14px rgba(4,120,87,0.22);">
    <div style="display:inline-block;background-color:rgba(255,255,255,0.2);padding:4px 12px;border-radius:999px;font-size:12px;font-weight:700;letter-spacing:0.5px;margin-bottom:8px;border:1px solid rgba(255,255,255,0.3);">
      📸 手機離線獨立版 ｜ 免網路・免伺服器隨點隨開
    </div>
    <h1 style="font-size:22px;font-weight:800;letter-spacing:0.3px;margin:0 0 6px 0;color:#ffffff;">全台美拍私房景點隨身手冊</h1>
    <div style="font-size:13px;opacity:0.92;max-width:640px;margin:0 auto;color:#ecfdf5;">
      深度收錄嘉義市、嘉義縣＆臺南市共 {total_count} 處精選美拍・歷史古蹟・自然秘境實測攻略
    </div>
  </header>

  <!-- 黏性三層分頁導覽列（全內嵌 Inline CSS） -->
  <nav style="position:sticky;top:0;z-index:100;background-color:rgba(255,255,255,0.98);border-bottom:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(15,23,42,0.05);padding:10px 14px 10px;">
    <div style="max-width:1200px;margin:0 auto;">

      <!-- 核心主題大分頁導航（美食・景點・旅宿） -->
      <div style="display:flex;gap:6px;margin-bottom:10px;padding-bottom:10px;border-bottom:1.5px solid #f1f5f9;overflow-x:auto;" class="no-scrollbar">
        <a href="{food_link}" style="flex:1;min-width:fit-content;text-align:center;text-decoration:none;padding:7px 12px;border-radius:10px;font-size:13px;font-weight:700;background:#f8fafc;color:#475569;border:1px solid #cbd5e1;">
          🍱 美食避雷 (274)
        </a>
        <a href="{attractions_link}" style="flex:1;min-width:fit-content;text-align:center;text-decoration:none;padding:7px 12px;border-radius:10px;font-size:13px;font-weight:800;background:#059669;color:#ffffff;box-shadow:0 2px 6px rgba(5,150,105,0.25);">
          📸 私房景點 ({total_count})
        </a>
        <a href="{seaview_link}" style="flex:1;min-width:fit-content;text-align:center;text-decoration:none;padding:7px 12px;border-radius:10px;font-size:13px;font-weight:700;background:#f8fafc;color:#475569;border:1px solid #cbd5e1;">
          🌊 看海旅宿 (20)
        </a>
      </div>

      <!-- 第一層：台灣縣市分頁 -->
      <div id="cityTabs" class="no-scrollbar" style="display:flex;gap:8px;overflow-x:auto;margin-bottom:9px;padding-bottom:2px;">
{city_tabs_html}
      </div>

      <!-- 第二層：鄉鎮市區子分頁 -->
      <div id="districtBar" class="no-scrollbar" style="display:flex;align-items:center;gap:6px;overflow-x:auto;margin-bottom:9px;padding:6px 10px;background-color:#f1f5f9;border-radius:10px;">
        <span style="font-size:11.5px;font-weight:700;color:#475569;white-space:nowrap;margin-right:2px;">📍 鄉鎮市區：</span>
{district_bar_html}
      </div>

      <!-- 搜尋框 -->
      <div style="position:relative;margin-bottom:9px;">
        <input type="text" id="searchInput" oninput="handleSearch()" placeholder="🔍 搜尋景點名稱、特色亮點、避坑攻略、地址..."
               style="width:100%;padding:10px 14px 10px 38px;border-radius:10px;border:1.5px solid #cbd5e1;background-color:#f8fafc;font-size:13.5px;color:#0f172a;outline:none;-webkit-appearance:none;">
        <span style="position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:15px;color:#94a3b8;pointer-events:none;">📍</span>
      </div>

      <!-- 第三層：景點類型篩選膠囊列 -->
      <div id="catScroll" class="no-scrollbar" style="display:flex;gap:6px;overflow-x:auto;padding-bottom:2px;">
        <button type="button" data-cat-btn="all" onclick="selectCat('all')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #059669;background-color:#059669;color:#ffffff;font-size:12.5px;font-weight:700;cursor:pointer;">🏛️ 全部類型</button>
        <button type="button" data-cat-btn="歷史古蹟" onclick="selectCat('歷史古蹟')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">📜 歷史古蹟</button>
        <button type="button" data-cat-btn="文創園區" onclick="selectCat('文創園區')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🎨 文創園區</button>
        <button type="button" data-cat-btn="自然步道" onclick="selectCat('自然步道')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🌲 自然步道</button>
        <button type="button" data-cat-btn="親子休閒" onclick="selectCat('親子休閒')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🎠 親子休閒</button>
        <button type="button" data-cat-btn="宗教信仰" onclick="selectCat('宗教信仰')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">⛩️ 宗教信仰</button>
      </div>
    </div>
  </nav>

  <!-- 篩選狀態統計列 -->
  <div style="max-width:1200px;margin:0 auto;padding:12px 16px 4px;display:flex;justify-content:space-between;align-items:center;font-size:12.5px;color:#64748b;">
    <div id="breadcrumbText">目前分頁：<b style="color:#047857;">全部縣市 ▸ 全部鄉鎮市區</b></div>
    <div>顯示中：<b id="storeCount" style="color:#047857;">{total_count}</b> 處景點</div>
  </div>

  <!-- 預渲染之景點卡片列表 -->
  <main id="storesGrid" style="display:flex;flex-direction:column;gap:14px;padding:10px 14px;max-width:1200px;margin:0 auto;">
{cards_prerendered}
  </main>

  <!-- 底部手冊導覽浮動條（三大手冊常駐置底切換） -->
  <div style="position:fixed;bottom:12px;left:50%;transform:translateX(-50%);background:rgba(15,23,42,0.94);backdrop-filter:blur(10px);padding:6px 10px;border-radius:30px;display:flex;gap:6px;box-shadow:0 10px 25px rgba(0,0,0,0.35);z-index:900;max-width:96vw;white-space:nowrap;">
    <a href="{food_link}" style="color:#cbd5e1;text-decoration:none;font-size:12px;padding:5px 12px;border-radius:20px;transition:all 0.2s;">🍱 美食手冊 (274)</a>
    <a href="{attractions_link}" style="color:#ffffff;background:#059669;font-weight:700;text-decoration:none;font-size:12px;padding:5px 12px;border-radius:20px;">📸 私房景點 ({total_count})</a>
    <a href="{seaview_link}" style="color:#cbd5e1;text-decoration:none;font-size:12px;padding:5px 12px;border-radius:20px;transition:all 0.2s;">🌊 看海旅宿 (20)</a>
  </div>

  <!-- 底部簡易版權聲明 -->
  <footer style="text-align:center;padding:32px 16px 20px;font-size:12px;color:#94a3b8;border-top:1px solid #e2e8f0;margin-top:28px;">
    全台美拍私房景點隨身手冊 ｜ 離線獨立版 ｜ 實測彙編・無業配廣告
  </footer>

  <!-- 互動控制 JavaScript（全原生、無外部依賴、極速執行） -->
  <script>
    var currentCity = 'all';
    var currentDistrict = 'all';
    var currentCategory = 'all';
    var searchQuery = '';

    function selectCity(city) {{
      currentCity = city;
      currentDistrict = 'all';

      // 更新縣市分頁按鈕外觀
      var cityBtns = document.querySelectorAll('[data-city-btn]');
      cityBtns.forEach(function(btn) {{
        var c = btn.getAttribute('data-city-btn');
        if (c === city) {{
          btn.style.backgroundColor = '#064e3b';
          btn.style.color = '#ffffff';
          btn.style.borderColor = '#064e3b';
        }} else {{
          btn.style.backgroundColor = '#f8fafc';
          btn.style.color = '#475569';
          btn.style.borderColor = '#e2e8f0';
        }}
      }});

      // 依縣市過濾第二層鄉鎮市區按鈕
      var distBtns = document.querySelectorAll('[data-dist-btn]');
      distBtns.forEach(function(btn) {{
        var d = btn.getAttribute('data-dist-btn');
        var dCity = btn.getAttribute('data-dist-city');
        if (d === 'all') {{
          btn.style.display = 'inline-block';
        }} else if (city === 'all' || dCity === city) {{
          btn.style.display = 'inline-block';
        }} else {{
          btn.style.display = 'none';
        }}
      }});

      updateDistrictButtonsUI();
      filterStores();
    }}

    function selectDistrict(distKey) {{
      currentDistrict = distKey;
      updateDistrictButtonsUI();
      filterStores();
    }}

    function updateDistrictButtonsUI() {{
      var distBtns = document.querySelectorAll('[data-dist-btn]');
      distBtns.forEach(function(btn) {{
        var d = btn.getAttribute('data-dist-btn');
        if (d === currentDistrict) {{
          btn.style.backgroundColor = '#ffffff';
          btn.style.color = '#047857';
          btn.style.borderColor = '#cbd5e1';
          btn.style.fontWeight = '700';
          btn.style.boxShadow = '0 1px 2px rgba(0,0,0,0.06)';
        }} else {{
          btn.style.backgroundColor = 'transparent';
          btn.style.color = '#475569';
          btn.style.borderColor = 'transparent';
          btn.style.fontWeight = '600';
          btn.style.boxShadow = 'none';
        }}
      }});
    }}

    function selectCat(cat) {{
      currentCategory = cat;
      var catBtns = document.querySelectorAll('[data-cat-btn]');
      catBtns.forEach(function(btn) {{
        var c = btn.getAttribute('data-cat-btn');
        if (c === cat) {{
          btn.style.backgroundColor = '#059669';
          btn.style.color = '#ffffff';
          btn.style.borderColor = '#059669';
          btn.style.fontWeight = '700';
        }} else {{
          btn.style.backgroundColor = '#ffffff';
          btn.style.color = '#64748b';
          btn.style.borderColor = '#e2e8f0';
          btn.style.fontWeight = '600';
        }}
      }});
      filterStores();
    }}

    function handleSearch() {{
      var input = document.getElementById('searchInput');
      searchQuery = input.value.trim().toLowerCase();
      filterStores();
    }}

    function filterStores() {{
      var cards = document.querySelectorAll('.store-card');
      var visibleCount = 0;

      cards.forEach(function(card) {{
        var cCity = card.getAttribute('data-city');
        var cCityDist = card.getAttribute('data-city-district');
        var cCat = card.getAttribute('data-category');
        var cSearch = card.getAttribute('data-search') || '';

        var matchCity = (currentCity === 'all') || (cCity === currentCity);
        var matchDist = (currentDistrict === 'all') || (cCityDist === currentDistrict);
        var matchCat = (currentCategory === 'all') || (cCat === currentCategory);
        var matchSearch = (!searchQuery) || (cSearch.indexOf(searchQuery) !== -1);

        if (matchCity && matchDist && matchCat && matchSearch) {{
          card.style.display = 'flex';
          visibleCount++;
        }} else {{
          card.style.display = 'none';
        }}
      }});

      document.getElementById('storeCount').textContent = visibleCount;

      var bCity = (currentCity === 'all') ? '全部縣市' : currentCity;
      var bDist = (currentDistrict === 'all') ? '全部鄉鎮市區' : currentDistrict.replace(currentCity + '・', '');
      var bCat = (currentCategory === 'all') ? '全部類型' : currentCategory;
      document.getElementById('breadcrumbText').innerHTML = '目前分頁：<b style="color:#047857;">' + bCity + ' ▸ ' + bDist + ' ▸ ' + bCat + '</b>';
    }}

    function copyAttraction(region, name, highlights, address) {{
      var text = '【' + region + '】' + name + '\\n📸 必看特色：' + highlights + '\\n📍 地址：' + address;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).then(function() {{
          alert('已複製景點資訊至剪貼簿！\\n\\n' + text);
        }}).catch(function() {{
          fallbackCopy(text);
        }});
      }} else {{
        fallbackCopy(text);
      }}
    }}

    function fallbackCopy(text) {{
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      try {{
        document.execCommand('copy');
        alert('已複製景點資訊至剪貼簿！\\n\\n' + text);
      }} catch (err) {{
        prompt('請長按手動複製景點資訊：', text);
      }}
      document.body.removeChild(ta);
    }}
  </script>
</body>
</html>
"""
    return full_html

def main():
    # 產出本地離線手冊
    html_content = build_guide(is_dist=False)
    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"成功產生「景點手冊本機離線版」: {OUTPUT_HTML_PATH}")

    # 產出 web_dist/attractions.html
    html_dist = build_guide(is_dist=True)
    dist_file = os.path.join(WEB_DIST_DIR, "attractions.html")
    with open(dist_file, "w", encoding="utf-8") as f:
        f.write(html_dist)
    print(f"成功產生「PWA 靜態網站景點頁面」: {dist_file}")

if __name__ == "__main__":
    main()
