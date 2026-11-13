#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣美食避雷隨身手冊 — 手機離線獨立版（Pre-rendered HTML + Full Inline CSS + Progressive JS）建置腳本
特色：
1. 完全零外部依賴（無任何外部 CDN、無外部字型、無外部 JS）。
2. 所有 103 間店家卡片、分頁按鈕與排版皆於建置時「預先渲染（Pre-rendered）」寫入 HTML 內，
   且每個元素皆直接內嵌完整 Inline CSS (`style="..."`)。
3. 即使在 iOS「檔案」App (QuickLook)、Google Drive 內建預覽器或飛航模式下（甚至在禁用 JS 的沙盒預覽環境），
   所有卡片與排版皆 100% 完整呈現、絕不跑版或空白。
4. 在支援 JS 的瀏覽器（Safari / Chrome）中，完整支援「縣市 ➔ 鄉鎮市區 ➔ 餐點分類」三級動態分頁與即時模糊搜尋。
"""

import os
import re
import json
import html as html_lib
from typing import List, Dict, Any

PROJECT_DIR = "/Users/mac/AGY本地工作區/專案資料夾/美食景點整理"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
UNIFIED_JSON_PATH = os.path.join(DATA_DIR, "taiwan_food_guides_unified.json")
OUTPUT_HTML_PATH = os.path.join(PROJECT_DIR, "美食避雷隨身手冊.html")
WEB_DIST_DIR = os.path.join(PROJECT_DIR, "web_dist")


def esc(text: str) -> str:
    """安全轉義 HTML 特殊字元。"""
    return html_lib.escape(str(text), quote=True)


def render_card_html(s: Dict[str, Any]) -> str:
    """產生單一店家卡片之預渲染 HTML，並將所有樣式以 Inline CSS 直接寫入標籤內。"""
    is_closed = bool(s.get("isClosed"))
    city = s["city"]
    district = s["district"]
    category = s["category"]
    sub_cat = s["subCategory"]
    uid = s["uid"]
    name = s["name"]
    rating = s["rating"]
    comment = s["comment"]
    tips = s["tips"]
    address = s["address"]
    time_str = s["time"]
    dish_text = s["dishText"]
    dishes = s.get("dishes", [])
    tags = s.get("tags", [])

    # 依據縣市與鄉鎮市區設定膠囊配色（Inline CSS）
    if city == "嘉義市" and district == "東區":
        region_style = "background-color:#ffedd5;color:#c2410c;border:1px solid #fed7aa;"
    elif city == "嘉義市":
        region_style = "background-color:#fef3c7;color:#b45309;border:1px solid #fde68a;"
    elif city == "嘉義縣":
        region_style = "background-color:#f0fdf4;color:#15803d;border:1px solid #bbf7d0;"
    elif city == "雲林縣":
        region_style = "background-color:#fefce8;color:#854d0e;border:1px solid #fef08a;"
    elif city == "臺南市":
        region_style = "background-color:#ecfdf5;color:#047857;border:1px solid #a7f3d0;"
    else:
        region_style = "background-color:#f8fafc;color:#475569;border:1px solid #e2e8f0;"

    # 依據類別區分標籤色彩與專屬區塊標題
    if category == "精選旅宿":
        cat_style = "background-color:#f3e8ff;color:#7e22ce;border:1px solid #e9d5ff;"
        feature_header = "🛏️ 住宿特色與房型亮點"
        feature_box_border = "#9333ea"
        feature_title_color = "#7e22ce"
        pill_bg = "#faf5ff"
        pill_color = "#6b21a8"
    elif category == "私房景點":
        cat_style = "background-color:#e0f2fe;color:#0369a1;border:1px solid #bae6fd;"
        feature_header = "📸 核心亮點與參觀重點"
        feature_box_border = "#0284c7"
        feature_title_color = "#0369a1"
        pill_bg = "#f0f9ff"
        pill_color = "#075985"
    else:
        cat_style = (
            "background-color:#fee2e2;color:#b91c1c;"
            if is_closed
            else "background-color:#f1f5f9;color:#475569;"
        )
        feature_header = "🍴 招牌必點與推薦吃法"
        feature_box_border = "#d97706"
        feature_title_color = "#b45309"
        pill_bg = "#fef3c7"
        pill_color = "#92400e"

    card_bg_style = (
        "background-color:#f8fafc;border:1.5px dashed #cbd5e1;opacity:0.88;"
        if is_closed
        else "background-color:#ffffff;border:1px solid #e2e8f0;"
    )

    dishes_html = "".join(
        f'<span style="display:inline-block;font-size:12.5px;font-weight:700;color:{pill_color};background-color:{pill_bg};padding:2px 8px;border-radius:6px;margin:2px 4px 2px 0;">{esc(d)}</span>'
        for d in dishes
    )

    map_q = s.get("mapQuery") or f"{city}{district} {name}"
    map_url = f"https://www.google.com/maps/search/?api=1&query={html_lib.escape(map_q, quote=True)}"
    search_blob = " ".join([
        name, city, district, category, sub_cat, dish_text, comment, tips, address, " ".join(tags)
    ]).lower()

    js_region = esc(f"{city}{district}")
    js_name = esc(name).replace("'", "\\'")
    js_dish = esc(dish_text).replace("'", "\\'")
    js_addr = esc(address).replace("'", "\\'")

    return f"""
      <article class="store-card"
               data-city="{esc(city)}"
               data-district="{esc(district)}"
               data-city-district="{esc(city)}・{esc(district)}"
               data-category="{esc(category)}"
               data-search="{esc(search_blob)}"
               style="{card_bg_style}border-radius:18px;padding:16px;box-shadow:0 4px 10px -2px rgba(15,23,42,0.05);display:flex;flex-direction:column;margin-bottom:4px;box-sizing:border-box;">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;margin-bottom:8px;flex-wrap:wrap;">
          <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
            <span style="font-size:11px;font-weight:800;padding:2.5px 8px;border-radius:6px;{region_style}">{esc(city)}・{esc(district)}</span>
            <span style="font-size:11px;font-weight:600;padding:2.5px 8px;border-radius:6px;{cat_style}">{esc(category)}｜{esc(sub_cat)}</span>
          </div>
          <span style="font-size:11px;font-weight:700;color:#b45309;background-color:#fffbeb;border:1px solid #fde68a;padding:2px 8px;border-radius:6px;">{esc(rating)}</span>
        </div>

        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
          <span style="font-size:11px;font-weight:800;padding:2px 7px;border-radius:6px;background-color:#0f172a;color:#ffffff;flex-shrink:0;">{esc(uid)}</span>
          <h2 style="font-size:17px;font-weight:800;color:#0f172a;line-height:1.3;margin:0;">{esc(name)}</h2>
        </div>

        <div style="background-color:#fffbeb;border-left:3.5px solid {feature_box_border};padding:8px 11px;border-radius:0 10px 10px 0;margin-bottom:10px;">
          <div style="font-size:11px;font-weight:800;color:{feature_title_color};margin-bottom:4px;">{feature_header}</div>
          <div style="display:flex;flex-wrap:wrap;gap:4px;">{dishes_html}</div>
        </div>

        <div style="font-size:13.5px;color:#334155;margin-bottom:10px;line-height:1.55;flex:1;">{esc(comment)}</div>

        <div style="background-color:#fff1f2;border:1px solid #fecdd3;border-radius:10px;padding:8px 11px;margin-bottom:11px;font-size:12.5px;color:#9f1239;display:flex;align-items:flex-start;gap:6px;line-height:1.5;">
          <span style="flex-shrink:0;">⚠️</span>
          <div><b style="font-weight:800;">避坑與內行提醒：</b>{esc(tips)}</div>
        </div>

        <div style="border-top:1px solid #f1f5f9;padding-top:9px;margin-bottom:12px;font-size:12px;color:#64748b;display:flex;flex-direction:column;gap:3px;">
          <div style="display:flex;align-items:flex-start;gap:5px;"><span>📍</span><span>{esc(address)}</span></div>
          <div style="display:flex;align-items:flex-start;gap:5px;"><span>🕒</span><span>{esc(time_str)}</span></div>
        </div>

        <div style="display:flex;gap:8px;margin-top:auto;">
          <a href="{map_url}" target="_blank" rel="noopener noreferrer"
             style="flex:1;padding:9px 10px;border-radius:10px;font-size:13px;font-weight:700;text-align:center;background-color:#d97706;color:#ffffff;border:1px solid #d97706;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;gap:5px;">
            📍 Google 地圖導航
          </a>
          <button type="button" onclick="copyStore('{js_region}', '{js_name}', '{js_dish}', '{js_addr}')"
             style="flex:1;padding:9px 10px;border-radius:10px;font-size:13px;font-weight:700;text-align:center;background-color:#f8fafc;color:#475569;border:1px solid #e2e8f0;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;gap:5px;">
            📋 複製資訊
          </button>
        </div>
      </article>"""


def build_offline_standalone_html(stores: List[Dict[str, Any]]) -> str:
    """建置 100% 預渲染 + Inline CSS 之單檔離線獨立版 HTML。"""
    from collections import Counter

    cards_prerendered = "\n".join(render_card_html(s) for s in stores)
    total_count = len(stores)

    city_counts = Counter(s["city"] for s in stores)
    dist_counts = Counter((s["city"], s["district"]) for s in stores)

    city_icons = {
        "嘉義市": "🐓",
        "嘉義縣": "🌲",
        "臺南市": "🏛️",
        "雲林縣": "🌾",
        "高雄市": "⚓",
        "臺中市": "☀️",
        "臺北市": "🏙️"
    }

    # 動態產生縣市下拉式選項
    city_options = [
        f'<option value="all">🗺️ 全部（直轄市）縣 ({total_count})</option>'
    ]
    ordered_cities = ["嘉義市", "嘉義縣", "臺南市", "雲林縣"] + [c for c in city_counts if c not in ["嘉義市", "嘉義縣", "臺南市", "雲林縣"]]
    for c in ordered_cities:
        if c in city_counts:
            icon = city_icons.get(c, "📍")
            cnt = city_counts[c]
            city_options.append(f'<option value="{esc(c)}">{icon} {esc(c)} ({cnt})</option>')
    city_select_options_html = "\n".join(city_options)

    # 建立縣市與鄉鎮市區層級關係字典供前端聯動使用
    city_districts_map = {}
    for (c, d), cnt in dist_counts.items():
        if c not in city_districts_map:
            city_districts_map[c] = []
        city_districts_map[c].append({"district": d, "count": cnt})
    for c in city_districts_map:
        city_districts_map[c].sort(key=lambda x: x["district"])
    city_districts_json = json.dumps(city_districts_map, ensure_ascii=False)

    # 動態產生預設鄉鎮市區下拉選項
    dist_options = [
        f'<option value="all">📍 全部鄉鎮市區 ({total_count})</option>'
    ]
    city_sort_order = {"嘉義市": 0, "嘉義縣": 1, "臺南市": 2, "雲林縣": 3}
    sorted_dists = sorted(
        dist_counts.items(),
        key=lambda x: (city_sort_order.get(x[0][0], 99), x[0][1])
    )
    for (c, d), cnt in sorted_dists:
        dist_key = f"{c}・{d}"
        dist_options.append(f'<option value="{esc(dist_key)}" data-city="{esc(c)}">{esc(c)}・{esc(d)} ({cnt})</option>')
    district_select_options_html = "\n".join(dist_options)

    cy_east = dist_counts.get(("嘉義市", "東區"), 0)
    cy_west = dist_counts.get(("嘉義市", "西區"), 0)
    tn_xinying = dist_counts.get(("臺南市", "新營區"), 0)
    tn_houbi = dist_counts.get(("臺南市", "後壁區"), 0)
    tn_liuying = dist_counts.get(("臺南市", "柳營區"), 0)
    tn_yanshui = dist_counts.get(("臺南市", "鹽水區"), 0)
    tn_total = city_counts.get("臺南市", 0)
    cx_count = city_counts.get("嘉義縣", 0)
    yl_total = city_counts.get("雲林縣", 0)
    cy_total = cy_east + cy_west

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>台灣私房美食・景點・住宿避雷隨身手冊 ｜ 手機離線獨立版</title>
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="theme-color" content="#b45309">
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
    <a href="美食避雷隨身手冊.html" style="color:#ffffff;text-decoration:none;padding:5px 12px;border-radius:999px;border:1px solid #d97706;background:#b45309;">🍱 美食・景點・住宿手冊</a>
    <a href="全台美拍私房景點隨身手冊.html" style="color:#cbd5e1;text-decoration:none;padding:5px 12px;border-radius:999px;border:1px solid #334155;background:#1e293b;">📸 私房美拍景點</a>
    <a href="全台看海放空旅宿隨身手冊.html" style="color:#cbd5e1;text-decoration:none;padding:5px 12px;border-radius:999px;border:1px solid #334155;background:#1e293b;">🌊 看海放空旅宿</a>
  </div>

  <!-- 頂部橫幅（全內嵌 Inline CSS） -->
  <header style="background:linear-gradient(135deg,#78350f 0%,#b45309 50%,#d97706 100%);background-color:#b45309;color:#ffffff;padding:18px 16px 16px;text-align:center;box-shadow:0 4px 14px rgba(180,83,9,0.22);">
    <h1 style="font-size:22px;font-weight:800;letter-spacing:0.3px;margin:0;color:#ffffff;">台灣私房美食・景點・住宿避雷隨身手冊</h1>
  </header>

  <!-- 黏性三層分頁導覽列（全內嵌 Inline CSS） -->
  <nav style="position:sticky;top:0;z-index:100;background-color:rgba(255,255,255,0.98);border-bottom:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(15,23,42,0.05);padding:10px 14px 10px;">
    <div style="max-width:1200px;margin:0 auto;">

      <!-- 核心主題大分頁導航（美食・景點・旅宿） -->
      <div style="display:flex;gap:6px;margin-bottom:10px;padding-bottom:10px;border-bottom:1.5px solid #f1f5f9;overflow-x:auto;" class="no-scrollbar">
        <a href="美食避雷隨身手冊.html" style="flex:1;min-width:fit-content;text-align:center;text-decoration:none;padding:7px 12px;border-radius:10px;font-size:13px;font-weight:800;background:#b45309;color:#ffffff;box-shadow:0 2px 6px rgba(180,83,9,0.25);">
          🍱 全能避雷手冊 ({total_count})
        </a>
        <a href="全台美拍私房景點隨身手冊.html" style="flex:1;min-width:fit-content;text-align:center;text-decoration:none;padding:7px 12px;border-radius:10px;font-size:13px;font-weight:700;background:#f8fafc;color:#475569;border:1px solid #cbd5e1;">
          📸 私房景點 (22)
        </a>
        <a href="全台看海放空旅宿隨身手冊.html" style="flex:1;min-width:fit-content;text-align:center;text-decoration:none;padding:7px 12px;border-radius:10px;font-size:13px;font-weight:700;background:#f8fafc;color:#475569;border:1px solid #cbd5e1;">
          🌊 看海旅宿 (20)
        </a>
      </div>

      <!-- 第一層與第二層：下拉式選單（直轄市/縣 ➔ 鄉鎮市區） -->
      <div style="display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
        <div style="flex:1;min-width:140px;">
          <label for="citySelect" style="display:block;font-size:11px;font-weight:800;color:#64748b;margin-bottom:4px;">🏛️ （直轄市）縣：</label>
          <select id="citySelect" onchange="onCitySelectChange(this.value)"
                  style="width:100%;padding:9px 12px;border-radius:12px;border:1.5px solid #cbd5e1;background-color:#ffffff;color:#0f172a;font-size:13.5px;font-weight:700;outline:none;box-shadow:0 1px 3px rgba(0,0,0,0.04);cursor:pointer;">
{city_select_options_html}
          </select>
        </div>

        <div style="flex:1;min-width:140px;">
          <label for="districtSelect" style="display:block;font-size:11px;font-weight:800;color:#64748b;margin-bottom:4px;">📍 鄉鎮市區：</label>
          <select id="districtSelect" onchange="onDistrictSelectChange(this.value)"
                  style="width:100%;padding:9px 12px;border-radius:12px;border:1.5px solid #cbd5e1;background-color:#ffffff;color:#0f172a;font-size:13.5px;font-weight:700;outline:none;box-shadow:0 1px 3px rgba(0,0,0,0.04);cursor:pointer;">
{district_select_options_html}
          </select>
        </div>
      </div>

      <!-- 搜尋框 -->
      <div style="position:relative;margin-bottom:9px;">
        <span style="position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:14px;color:#64748b;">🔍</span>
        <input type="text" id="searchInput" placeholder="搜尋店名、鄉鎮市區、特色必點、景點、旅宿（如：火雞肉飯、智選、花磚、阿里山、涼麵）..."
               style="width:100%;padding:9px 34px 9px 36px;border:1.5px solid #e2e8f0;border-radius:12px;font-size:14px;background-color:#f8fafc;color:#0f172a;outline:none;box-sizing:border-box;">
        <button type="button" id="clearBtn" onclick="clearSearchInput()"
                style="position:absolute;right:10px;top:50%;transform:translateY(-50%);width:22px;height:22px;border-radius:50%;border:none;background-color:#cbd5e1;color:#334155;font-size:12px;cursor:pointer;display:none;align-items:center;justify-content:center;">✕</button>
      </div>

      <!-- 第三層：餐點分類膠囊 -->
      <div id="catScroll" class="no-scrollbar" style="display:flex;gap:6px;overflow-x:auto;padding-bottom:2px;">
        <button type="button" data-cat-btn="all" onclick="selectCat('all')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #d97706;background-color:#d97706;color:#ffffff;font-size:12.5px;font-weight:700;cursor:pointer;">🍽️ 全部類型</button>
        <button type="button" data-cat-btn="正餐主食" onclick="selectCat('正餐主食')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🍱 正餐主食</button>
        <button type="button" data-cat-btn="在地小吃" onclick="selectCat('在地小吃')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🍜 在地小吃</button>
        <button type="button" data-cat-btn="異國料理" onclick="selectCat('異國料理')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🍕 異國特色</button>
        <button type="button" data-cat-btn="私房景點" onclick="selectCat('私房景點')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">📸 私房景點</button>
        <button type="button" data-cat-btn="精選旅宿" onclick="selectCat('精選旅宿')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🏨 精選旅宿</button>
        <button type="button" data-cat-btn="麵點湯包" onclick="selectCat('麵點湯包')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🥟 麵點湯包</button>
        <button type="button" data-cat-btn="早餐早午餐" onclick="selectCat('早餐早午餐')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🍳 早餐早午餐</button>
        <button type="button" data-cat-btn="宵夜炭烤日料" onclick="selectCat('宵夜炭烤日料')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🌙 宵夜炭烤日料</button>
        <button type="button" data-cat-btn="鍋物補湯" onclick="selectCat('鍋物補湯')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🍲 鍋物補湯</button>
        <button type="button" data-cat-btn="烘焙甜點冰品" onclick="selectCat('烘焙甜點冰品')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🍰 烘焙甜點冰品</button>
        <button type="button" data-cat-btn="手搖咖啡茶飲" onclick="selectCat('手搖咖啡茶飲')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🥤 手搖咖啡茶飲</button>
      </div>
    </div>
  </nav>

  <!-- 篩選狀態統計列 -->
  <div style="max-width:1200px;margin:0 auto;padding:12px 16px 4px;display:flex;justify-content:space-between;align-items:center;font-size:12.5px;color:#64748b;">
    <div id="breadcrumbText">目前分頁：<b style="color:#b45309;">全部縣市 ▸ 全部鄉鎮市區</b></div>
    <div>顯示中：<b id="storeCount" style="color:#b45309;">{total_count}</b> 筆資料</div>
  </div>

  <!-- 預渲染卡片列表（即使禁用 JS 亦可 100% 呈現所有卡片與完整排版） -->
  <main id="storesGrid" style="display:flex;flex-direction:column;gap:14px;padding:10px 14px;max-width:1200px;margin:0 auto;">
{cards_prerendered}
  </main>

  <!-- 查無結果提示框（預設隱藏） -->
  <div id="emptyState" style="display:none;text-align:center;padding:56px 20px;color:#64748b;max-width:1200px;margin:0 auto;">
    <div style="font-size:38px;margin-bottom:10px;">🔍</div>
    <div style="font-weight:800;font-size:16px;margin-bottom:4px;color:#0f172a;">在此區域或分類下找不到相符的項目</div>
    <div style="font-size:13px;">請嘗試切換上方「縣市／鄉鎮市區」分頁或清除搜尋關鍵字</div>
  </div>

  <!-- 複製成功提示 Toast -->
  <div id="toast" style="position:fixed;bottom:64px;left:50%;transform:translateX(-50%) translateY(120px);background-color:rgba(15,23,42,0.95);color:#ffffff;padding:10px 20px;border-radius:999px;font-size:13px;font-weight:600;box-shadow:0 10px 25px rgba(0,0,0,0.2);transition:transform 0.25s ease;z-index:999;pointer-events:none;">
    已複製資訊！
  </div>

  <!-- 底部手冊導覽浮動條（三大手冊常駐置底切換） -->
  <div style="position:fixed;bottom:12px;left:50%;transform:translateX(-50%);background:rgba(15,23,42,0.94);backdrop-filter:blur(10px);padding:6px 10px;border-radius:30px;display:flex;gap:6px;box-shadow:0 10px 25px rgba(0,0,0,0.35);z-index:900;max-width:96vw;white-space:nowrap;">
    <a href="美食避雷隨身手冊.html" style="color:#ffffff;background:#b45309;font-weight:700;text-decoration:none;font-size:12px;padding:5px 12px;border-radius:20px;">🍱 全能手冊 ({total_count})</a>
    <a href="全台美拍私房景點隨身手冊.html" id="attractionsBottomLink" style="color:#cbd5e1;text-decoration:none;font-size:12px;padding:5px 12px;border-radius:20px;transition:all 0.2s;">📸 私房景點 (22)</a>
    <a href="全台看海放空旅宿隨身手冊.html" id="seaviewBottomLink" style="color:#cbd5e1;text-decoration:none;font-size:12px;padding:5px 12px;border-radius:20px;transition:all 0.2s;">🌊 看海旅宿 (20)</a>
  </div>

  <script>
    // 漸進式增強腳本：直接操作已預先渲染於 HTML 中的 DOM 卡片，極速切換分頁與搜尋
    var currentCity = "all";
    var currentDistrict = "all";
    var currentCat = "all";
    var searchQuery = "";
    var cityDistrictsMap = {city_districts_json};

    function applyFilters() {{
      var cards = document.querySelectorAll(".store-card");
      var q = searchQuery.trim().toLowerCase();
      var visibleCount = 0;

      for (var i = 0; i < cards.length; i++) {{
        var card = cards[i];
        var cCity = card.getAttribute("data-city");
        var cDistrict = card.getAttribute("data-district");
        var cCityDist = card.getAttribute("data-city-district");
        var cCat = card.getAttribute("data-category");
        var cSearch = card.getAttribute("data-search") || "";

        var matchCity = (currentCity === "all" || cCity === currentCity);
        var matchDist = (currentDistrict === "all" || cCityDist === currentDistrict || cDistrict === currentDistrict);
        var matchCat = (currentCat === "all" || cCat === currentCat);
        var matchQ = (!q || cSearch.indexOf(q) !== -1);

        if (matchCity && matchDist && matchCat && matchQ) {{
          card.style.display = "flex";
          visibleCount++;
        }} else {{
          card.style.display = "none";
        }}
      }}

      document.getElementById("storeCount").textContent = visibleCount;
      document.getElementById("emptyState").style.display = (visibleCount === 0) ? "block" : "none";

      var cityText = (currentCity === "all") ? "全部縣市" : currentCity;
      var distText = (currentDistrict === "all") ? "全部鄉鎮市區" : currentDistrict;
      var catText = (currentCat === "all") ? "" : (" ➔ " + currentCat);
      document.getElementById("breadcrumbText").innerHTML =
        '目前分頁：<b style="color:#b45309;">' + cityText + " ▸ " + distText + catText + "</b>";
    }}

    function onCitySelectChange(city) {{
      currentCity = city;
      currentDistrict = "all";
      updateDistrictSelectOptions();
      applyFilters();
    }}

    function onDistrictSelectChange(dist) {{
      currentDistrict = dist;
      applyFilters();
    }}

    function updateDistrictSelectOptions() {{
      var distSelect = document.getElementById("districtSelect");
      distSelect.innerHTML = "";

      var defaultOpt = document.createElement("option");
      defaultOpt.value = "all";

      if (currentCity === "all") {{
        defaultOpt.textContent = "📍 全部鄉鎮市區 ({total_count})";
        distSelect.appendChild(defaultOpt);

        for (var c in cityDistrictsMap) {{
          var list = cityDistrictsMap[c];
          for (var i = 0; i < list.length; i++) {{
            var item = list[i];
            var opt = document.createElement("option");
            opt.value = c + "・" + item.district;
            opt.textContent = c + "・" + item.district + " (" + item.count + ")";
            distSelect.appendChild(opt);
          }}
        }}
      }} else {{
        var list = cityDistrictsMap[currentCity] || [];
        var citySum = 0;
        for (var i = 0; i < list.length; i++) {{ citySum += list[i].count; }}
        defaultOpt.textContent = "📍 全部" + currentCity + "行政區 (" + citySum + ")";
        distSelect.appendChild(defaultOpt);

        for (var i = 0; i < list.length; i++) {{
          var item = list[i];
          var opt = document.createElement("option");
          opt.value = item.district;
          opt.textContent = item.district + " (" + item.count + ")";
          distSelect.appendChild(opt);
        }}
      }}
      distSelect.value = "all";
    }}

    function updateTabStyles() {{
      // 更新餐點分類按鈕樣式
      var catBtns = document.querySelectorAll("[data-cat-btn]");
      for (var k = 0; k < catBtns.length; k++) {{
        var cBtn = catBtns[k];
        var isCatAct = (cBtn.getAttribute("data-cat-btn") === currentCat);
        cBtn.style.backgroundColor = isCatAct ? "#d97706" : "#ffffff";
        cBtn.style.color = isCatAct ? "#ffffff" : "#64748b";
        cBtn.style.borderColor = isCatAct ? "#d97706" : "#e2e8f0";
        cBtn.style.fontWeight = isCatAct ? "700" : "600";
      }}
    }}

    function selectCity(city) {{
      var citySelect = document.getElementById("citySelect");
      if (citySelect) {{ citySelect.value = city; }}
      onCitySelectChange(city);
    }}

    function selectDistrict(dist) {{
      var distSelect = document.getElementById("districtSelect");
      if (distSelect) {{ distSelect.value = dist; }}
      onDistrictSelectChange(dist);
    }}

    function selectCat(cat) {{
      currentCat = cat;
      updateTabStyles();
      applyFilters();
    }}

    function clearSearchInput() {{
      searchQuery = "";
      var input = document.getElementById("searchInput");
      input.value = "";
      document.getElementById("clearBtn").style.display = "none";
      applyFilters();
    }}

    function showToast(msg) {{
      var toast = document.getElementById("toast");
      toast.textContent = msg;
      toast.style.transform = "translateX(-50%) translateY(0)";
      setTimeout(function() {{
        toast.style.transform = "translateX(-50%) translateY(120px)";
      }}, 2000);
    }}

    function copyStore(region, name, dish, address) {{
      var text = "【" + region + "】" + name + "\\n特色/必點：" + dish + "\\n地址：" + address;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).then(function() {{
          showToast("已複製資訊：" + name);
        }}).catch(function() {{
          showToast("已複製資訊：" + name);
        }});
      }} else {{
        showToast("已複製資訊：" + name);
      }}
    }}

    document.getElementById("searchInput").addEventListener("input", function(e) {{
      searchQuery = e.target.value;
      document.getElementById("clearBtn").style.display = searchQuery ? "flex" : "none";
      applyFilters();
    }});
  </script>
</body>
</html>
"""


def main() -> None:
    with open(UNIFIED_JSON_PATH, "r", encoding="utf-8") as f:
        all_stores = json.load(f)

    rendered_html = build_offline_standalone_html(all_stores)
    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    # 同步產生網站部署專用目錄 (web_dist/)，包含 index.html、PWA manifest.json 與離線 Service Worker (sw.js)
    os.makedirs(WEB_DIST_DIR, exist_ok=True)
    pwa_head_inject = """  <link rel="manifest" href="manifest.json">
  <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 rx=%2222%22 fill=%22%23b45309%22/><text y=%22.88em%22 x=%2250%%22 text-anchor=%22middle%22 font-size=%2265%22>🍜</text></svg>">
  <script>
    if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
      window.addEventListener('load', function() {
        navigator.serviceWorker.register('./sw.js').catch(function() {});
      });
    }
  </script>
</head>"""
    web_index_html = rendered_html.replace("</head>", pwa_head_inject, 1)
    web_index_html = web_index_html.replace('href="全台看海放空旅宿隨身手冊.html"', 'href="seaview.html"')
    web_index_html = web_index_html.replace('href="全台美拍私房景點隨身手冊.html"', 'href="attractions.html"')
    web_index_html = web_index_html.replace('href="美食避雷隨身手冊.html"', 'href="index.html"')
    with open(os.path.join(WEB_DIST_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(web_index_html)

    manifest_data = {
        "name": "台灣私房美食・景點・住宿避雷隨身手冊",
        "short_name": "避雷隨身手冊",
        "description": f"收錄嘉義縣市與臺南市 {len(all_stores)} 筆在地實測美食・景點・住宿避雷指南",
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": "#f8fafc",
        "theme_color": "#b45309",
        "icons": [
            {
                "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%23b45309'/><text y='.88em' x='50%' text-anchor='middle' font-size='65'>🍜</text></svg>",
                "sizes": "192x192 512x512",
                "type": "image/svg+xml"
            }
        ]
    }
    with open(os.path.join(WEB_DIST_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, ensure_ascii=False, indent=2)

    sw_js = """const CACHE_NAME = 'tw-food-guide-v4';
const ASSETS = ['./', './index.html', './attractions.html', './seaview.html', './manifest.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return res;
      })
      .catch(() => caches.match(event.request))
  );
});
"""
    with open(os.path.join(WEB_DIST_DIR, "sw.js"), "w", encoding="utf-8") as f:
        f.write(sw_js)

    print(f"成功產生「手機離線獨立版（100% 預渲染 + 內嵌 Inline CSS）」: {OUTPUT_HTML_PATH}")
    print(f"成功產生「PWA 靜態網站部署包」: {WEB_DIST_DIR}/ (含 index.html, manifest.json, sw.js)")
    print(f"檔案大小: {os.path.getsize(OUTPUT_HTML_PATH):,} bytes，共預渲染 {len(all_stores)} 張完整店家卡片。")


if __name__ == "__main__":
    main()
