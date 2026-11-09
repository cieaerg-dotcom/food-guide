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
    else:
        region_style = "background-color:#ecfdf5;color:#047857;border:1px solid #a7f3d0;"

    cat_style = (
        "background-color:#fee2e2;color:#b91c1c;"
        if is_closed
        else "background-color:#f1f5f9;color:#475569;"
    )

    card_bg_style = (
        "background-color:#f8fafc;border:1.5px dashed #cbd5e1;opacity:0.88;"
        if is_closed
        else "background-color:#ffffff;border:1px solid #e2e8f0;"
    )

    dishes_html = "".join(
        f'<span style="display:inline-block;font-size:12.5px;font-weight:700;color:#92400e;background-color:#fef3c7;padding:2px 8px;border-radius:6px;margin:2px 4px 2px 0;">{esc(d)}</span>'
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

        <div style="background-color:#fffbeb;border-left:3.5px solid #d97706;padding:8px 11px;border-radius:0 10px 10px 0;margin-bottom:10px;">
          <div style="font-size:11px;font-weight:800;color:#b45309;margin-bottom:4px;">🍴 招牌必點與推薦吃法</div>
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
            📋 複製店訊
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
        "高雄市": "⚓",
        "臺中市": "☀️",
        "臺北市": "🏙️"
    }

    # 動態產生縣市分頁按鈕
    city_tab_buttons = [
        f"""        <button type="button" data-city-btn="all" onclick="selectCity('all')"
                style="flex:1;min-width:fit-content;padding:8px 14px;border-radius:12px;border:1.5px solid #0f172a;background-color:#0f172a;color:#ffffff;font-size:13.5px;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;gap:6px;white-space:nowrap;">
          <span>🗺️ 全部縣市</span>
          <span style="font-size:11.5px;padding:1px 7px;border-radius:999px;background-color:rgba(255,255,255,0.22);color:#ffffff;">{total_count}</span>
        </button>"""
    ]
    ordered_cities = ["嘉義市", "嘉義縣", "臺南市"] + [c for c in city_counts if c not in ["嘉義市", "嘉義縣", "臺南市"]]
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

    # 動態產生鄉鎮市區按鈕
    dist_buttons = [
        f"""        <button type="button" data-dist-btn="all" onclick="selectDistrict('all')"
                style="flex-shrink:0;padding:4px 11px;border-radius:8px;border:1px solid #cbd5e1;background-color:#ffffff;color:#b45309;font-size:12.5px;font-weight:700;cursor:pointer;box-shadow:0 1px 2px rgba(0,0,0,0.06);">
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

    cy_east = dist_counts.get(("嘉義市", "東區"), 0)
    cy_west = dist_counts.get(("嘉義市", "西區"), 0)
    tn_xinying = dist_counts.get(("臺南市", "新營區"), 0)
    tn_houbi = dist_counts.get(("臺南市", "後壁區"), 0)
    cx_count = city_counts.get("嘉義縣", 0)

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>台灣私房美食避雷隨身手冊 ｜ 手機離線獨立版</title>
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

  <!-- 頂部橫幅（全內嵌 Inline CSS） -->
  <header style="background:linear-gradient(135deg,#78350f 0%,#b45309 50%,#d97706 100%);background-color:#b45309;color:#ffffff;padding:24px 16px 18px;text-align:center;box-shadow:0 4px 14px rgba(180,83,9,0.22);">
    <div style="display:inline-block;background-color:rgba(255,255,255,0.2);padding:4px 12px;border-radius:999px;font-size:12px;font-weight:700;letter-spacing:0.5px;margin-bottom:8px;border:1px solid rgba(255,255,255,0.3);">
      ✈️ 手機離線獨立版 ｜ 免網路・免伺服器隨點隨開
    </div>
    <h1 style="font-size:22px;font-weight:800;letter-spacing:0.3px;margin:0 0 6px 0;color:#ffffff;">台灣私房美食避雷隨身手冊</h1>
    <div style="font-size:13px;opacity:0.92;max-width:640px;margin:0 auto;color:#fffbeb;">
      收錄嘉義市（東區 {cy_east}／西區 {cy_west}）、嘉義縣（{cx_count} 間）＆ 臺南市（新營區 {tn_xinying}／後壁區 {tn_houbi}）共 {total_count} 間實測指南
    </div>
  </header>

  <!-- 黏性三層分頁導覽列（全內嵌 Inline CSS） -->
  <nav style="position:sticky;top:0;z-index:100;background-color:rgba(255,255,255,0.98);border-bottom:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(15,23,42,0.05);padding:12px 14px 10px;">
    <div style="max-width:1200px;margin:0 auto;">

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
        <span style="position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:14px;color:#64748b;">🔍</span>
        <input type="text" id="searchInput" placeholder="搜尋店名、鄉鎮市區、必點菜色（如：湯包、涼麵、炒飯、巴斯克、牛肉麵）..."
               style="width:100%;padding:9px 34px 9px 36px;border:1.5px solid #e2e8f0;border-radius:12px;font-size:14px;background-color:#f8fafc;color:#0f172a;outline:none;box-sizing:border-box;">
        <button type="button" id="clearBtn" onclick="clearSearchInput()"
                style="position:absolute;right:10px;top:50%;transform:translateY(-50%);width:22px;height:22px;border-radius:50%;border:none;background-color:#cbd5e1;color:#334155;font-size:12px;cursor:pointer;display:none;align-items:center;justify-content:center;">✕</button>
      </div>

      <!-- 第三層：餐點分類膠囊 -->
      <div id="catScroll" class="no-scrollbar" style="display:flex;gap:6px;overflow-x:auto;padding-bottom:2px;">
        <button type="button" data-cat-btn="all" onclick="selectCat('all')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #d97706;background-color:#d97706;color:#ffffff;font-size:12.5px;font-weight:700;cursor:pointer;">🍽️ 全部類型</button>
        <button type="button" data-cat-btn="正餐主食" onclick="selectCat('正餐主食')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🍱 正餐主食</button>
        <button type="button" data-cat-btn="在地小吃" onclick="selectCat('在地小吃')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🍜 在地小吃</button>
        <button type="button" data-cat-btn="麵點湯包" onclick="selectCat('麵點湯包')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🥟 麵點湯包</button>
        <button type="button" data-cat-btn="早餐早午餐" onclick="selectCat('早餐早午餐')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🍳 早餐早午餐</button>
        <button type="button" data-cat-btn="宵夜炭烤日料" onclick="selectCat('宵夜炭烤日料')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🌙 宵夜炭烤日料</button>
        <button type="button" data-cat-btn="鍋物補湯" onclick="selectCat('鍋物補湯')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🍲 鍋物補湯</button>
        <button type="button" data-cat-btn="烘焙甜點冰品" onclick="selectCat('烘焙甜點冰品')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🍰 烘焙甜點冰品</button>
        <button type="button" data-cat-btn="手搖咖啡茶飲" onclick="selectCat('手搖咖啡茶飲')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">🥤 手搖咖啡茶飲</button>
        <button type="button" data-cat-btn="已歇業提醒" onclick="selectCat('已歇業提醒')" style="flex-shrink:0;padding:5px 12px;border-radius:999px;border:1px solid #e2e8f0;background-color:#ffffff;color:#64748b;font-size:12.5px;font-weight:600;cursor:pointer;">⚠️ 已歇業</button>
      </div>
    </div>
  </nav>

  <!-- 3 秒精準避坑總覽橫幅（預先渲染並內嵌樣式） -->
  <section style="max-width:1200px;margin:14px auto 4px;padding:0 14px;">
    <div id="strategyCard" style="background-color:#fffbeb;border:1px solid #fde68a;border-radius:16px;padding:13px 15px;font-size:12.5px;color:#78350f;box-shadow:0 2px 6px rgba(217,119,6,0.05);">
      <div id="strategyTitle" style="font-weight:800;font-size:13.5px;color:#92400e;margin-bottom:6px;">
        ⚡ 跨縣市 3 秒精準避坑總覽（點選上方「縣市」與「鄉鎮市區」可快速切換分頁）
      </div>
      <div id="strategyBody" style="line-height:1.65;">
        • <b>嘉義市（東區 {cy_east} 間／西區 {cy_west} 間）</b>：必吃緯英海南雞飯、五千金炒飯、豆豆／京站湯包、黃記／南門白醋涼麵；<b>阿婆烤玉米（東區）與友愛鹹酥雞（西區）為極難買到的排隊魔王</b>；阿霞滷肉飯務必請店家滷汁少一點。<br>
        • <b>臺南市（新營區 {tn_xinying} 間／後壁區 {tn_houbi} 間）</b>：正餐首推溪北飯桌、小紅堂牛肉麵、燒蛋一下、阿豪冰糖豬腳；阿翔蚵仔煎必點「鐵板炒飯＋乾煎魚肚」，榮昌雞肉飯必加「半熟煎鴨蛋」；伯恩意麵份量精緻、金丘腿庫飯出餐較慢。
      </div>
    </div>
  </section>

  <!-- 篩選狀態統計列 -->
  <div style="max-width:1200px;margin:0 auto;padding:10px 16px 4px;display:flex;justify-content:space-between;align-items:center;font-size:12.5px;color:#64748b;">
    <div id="breadcrumbText">目前分頁：<b style="color:#b45309;">全部縣市 ▸ 全部鄉鎮市區</b></div>
    <div>顯示中：<b id="storeCount" style="color:#b45309;">{total_count}</b> 間店舖</div>
  </div>

  <!-- 預渲染之 103 間店家卡片列表（即使禁用 JS 亦可 100% 呈現所有卡片與完整排版） -->
  <main id="storesGrid" style="display:flex;flex-direction:column;gap:14px;padding:10px 14px;max-width:1200px;margin:0 auto;">
{cards_prerendered}
  </main>

  <!-- 查無結果提示框（預設隱藏） -->
  <div id="emptyState" style="display:none;text-align:center;padding:56px 20px;color:#64748b;max-width:1200px;margin:0 auto;">
    <div style="font-size:38px;margin-bottom:10px;">🔍</div>
    <div style="font-weight:800;font-size:16px;margin-bottom:4px;color:#0f172a;">在此區域或分類下找不到相符的店家</div>
    <div style="font-size:13px;">請嘗試切換上方「縣市／鄉鎮市區」分頁或清除搜尋關鍵字</div>
  </div>

  <!-- 複製成功提示 Toast -->
  <div id="toast" style="position:fixed;bottom:64px;left:50%;transform:translateX(-50%) translateY(120px);background-color:rgba(15,23,42,0.95);color:#ffffff;padding:10px 20px;border-radius:999px;font-size:13px;font-weight:600;box-shadow:0 10px 25px rgba(0,0,0,0.2);transition:transform 0.25s ease;z-index:999;pointer-events:none;">
    已複製店舖資訊！
  </div>

  <!-- 底部手冊導覽浮動條 -->
  <div style="position:fixed;bottom:12px;left:50%;transform:translateX(-50%);background:rgba(15,23,42,0.92);backdrop-filter:blur(10px);padding:6px 14px;border-radius:30px;display:flex;gap:12px;box-shadow:0 10px 25px rgba(0,0,0,0.25);z-index:900;">
    <a href="javascript:void(0)" style="color:#ffffff;background:#0284c7;font-weight:600;text-decoration:none;font-size:12px;padding:4px 12px;border-radius:20px;">🍲 美食隨身手冊 ({total_count})</a>
    <a href="全台看海放空旅宿隨身手冊.html" id="seaviewLink" style="color:#cbd5e1;text-decoration:none;font-size:12px;padding:4px 12px;border-radius:20px;transition:all 0.2s;">🌊 看海旅宿手冊 (20)</a>
  </div>

  <script>
    // 漸進式增強腳本：直接操作已預先渲染於 HTML 中的 DOM 卡片，極速切換分頁與搜尋
    var currentCity = "all";
    var currentDistrict = "all";
    var currentCat = "all";
    var searchQuery = "";

    var STRATEGY_NOTES = {{
      "all": {{
        title: "⚡ 跨縣市 3 秒精準避坑總覽（點選上方「縣市」與「鄉鎮市區」可快速切換分頁）",
        html: "• <b>嘉義市（東區 {cy_east} 間／西區 {cy_west} 間）</b>：必吃阿宏師火雞片飯＋半熟蛋、桃城三禾、大人味日印珈哩、五千金炒飯、豆豆／京站湯包、黃記／南門白醋涼麵；阿岸米糕附柴魚高湯；<b>阿婆烤玉米、友愛鹹酥雞與大人味咖哩為極難排到的名店</b>。<br>• <b>嘉義縣（{cx_count} 間）</b>：竹香園甕缸烤雞（中埔）、烘焙旅程手作蜂巢可頌（水上）、朴子第一市場九十年麻糬棟。<br>• <b>臺南市（新營區 {tn_xinying} 間／後壁區 {tn_houbi} 間）</b>：正餐首推溪北飯桌、小紅堂牛肉麵、燒蛋一下、阿豪冰糖豬腳；阿翔蚵仔煎必點「鐵板炒飯＋乾煎魚肚」，榮昌雞肉飯必加「半熟煎鴨蛋」；伯恩意麵份量精緻、金丘腿庫飯出餐較慢。"
      }},
      "嘉義市": {{
        title: "⚡ 嘉義市（東區／西區）3 秒精準避坑指南",
        html: "• <b>東區亮點（{cy_east} 間）</b>：阿宏師火雞片飯加半熟蛋、桃城三禾火雞肉飯、大人味咖哩（<b>每天午晚各限18份</b>）、五千金炒飯、豆豆小籠湯包、黃記涼麵涼圓、劉湯圓（<b>必加脆圓</b>）、阿霞火雞肉飯（<b>反向推手切滷肉飯，務必請店家滷汁少一點</b>）、古月焗烤（<b>必點偏甜酥皮濃湯</b>）、卡早起晨（<b>辣醬必加外帶必包</b>）。<br>• <b>西區亮點（{cy_west} 間）</b>：蕭老師火雞肉飯配炸排骨、阿岸米糕（<b>附贈柴魚大骨湯</b>）、咱台灣人的冰（<b>陳澄波故居蜜蕃薯</b>）、大盛居定食、隱燃燒肉丼、米半鐵板燒、緯英海南雞飯、桔吉力早餐（<b>建議電話預訂外帶</b>）、大眾水餃（<b>必加特製辣醬</b>）、霜空咖啡、友愛鹹酥雞。<br>• <b>歇業提醒</b>：西區 WT Food Drinks 與東區二奶巷星馬叻沙（租約到期）暫停營業，請勿白跑撲空！"
      }},
      "嘉義縣": {{
        title: "⚡ 嘉義縣（中埔鄉／水上鄉／朴子市）3 秒精準避坑指南",
        html: "• <b>中埔鄉</b>：竹香園甕缸雞（<b>招牌脆皮烤雞附筍乾大骨湯，炸地瓜酥必沾梅粉，假日人潮極多務必提早訂位</b>）。<br>• <b>水上鄉</b>：烘焙旅程（<b>田園蜂巢手作可頌天花板，建議提早於官方IG預留避免售罄</b>）。<br>• <b>朴子市</b>：麻糬棟（<b>朴子第一市場近百年老攤，招牌鹹綠豆花生手工麻糬冷熱皆軟Q</b>）。"
      }},
      "臺南市": {{
        title: "⚡ 臺南市（新營區／後壁區）3 秒精準避坑指南",
        html: "• <b>新營區聚餐與日料推薦（{tn_xinying} 間）</b>：簡餐聚會首推旭更廚房（<b>老件復古美店，建議提前電話訂位</b>）；日料聚餐推禾沐（<b>環境寬敞好訂位</b>）；老屋日料推樸拾（<b>全店僅約10席吧檯位不接電話預訂，招牌火焰鮭魚捲</b>）；高階日料選青鮨（<b>Omakase需預約</b>）；海鮮熱炒首推海口現撈（<b>在地人一生推，附大停車場</b>）與海宴（<b>包廂宴席</b>）。<br>• <b>新營區正餐小吃與甜點</b>：溪北飯桌（咖哩）、小紅堂（牛肉麵）、康樂胚芽意麵（<b>招牌手工大燒賣與黑白切骨頭肉必點</b>）、阿翔蚵仔煎（<b>鐵板炒飯＋乾煎魚肚</b>）、榮昌雞肉飯（<b>必加半熟煎鴨蛋</b>）；伯恩意麵份量精緻、金丘腿庫飯出餐較慢。<br>• <b>後壁區秘技（{tn_houbi} 間）</b>：樂檸漢堡（新營服務區北上店）可騎機車走外圍後方秘密便道免上國道進入，穿短褲享升級優惠！"
      }}
    }};

    function applyFilters() {{
      var cards = document.querySelectorAll(".store-card");
      var q = searchQuery.trim().toLowerCase();
      var visibleCount = 0;

      for (var i = 0; i < cards.length; i++) {{
        var card = cards[i];
        var cCity = card.getAttribute("data-city");
        var cCityDist = card.getAttribute("data-city-district");
        var cCat = card.getAttribute("data-category");
        var cSearch = card.getAttribute("data-search") || "";

        var matchCity = (currentCity === "all" || cCity === currentCity);
        var matchDist = (currentDistrict === "all" || cCityDist === currentDistrict);
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

    function updateTabStyles() {{
      // 更新縣市分頁按鈕樣式
      var cityBtns = document.querySelectorAll("[data-city-btn]");
      for (var i = 0; i < cityBtns.length; i++) {{
        var btn = cityBtns[i];
        var isAct = (btn.getAttribute("data-city-btn") === currentCity);
        btn.style.backgroundColor = isAct ? "#0f172a" : "#f8fafc";
        btn.style.color = isAct ? "#ffffff" : "#475569";
        btn.style.borderColor = isAct ? "#0f172a" : "#e2e8f0";
      }}

      // 更新鄉鎮市區按鈕顯示與樣式
      var distBtns = document.querySelectorAll("[data-dist-btn]");
      for (var j = 0; j < distBtns.length; j++) {{
        var dBtn = distBtns[j];
        var dVal = dBtn.getAttribute("data-dist-btn");
        var dCity = dBtn.getAttribute("data-dist-city");
        if (dVal === "all" || currentCity === "all" || dCity === currentCity) {{
          dBtn.style.display = "inline-block";
        }} else {{
          dBtn.style.display = "none";
        }}
        var isDistAct = (dVal === currentDistrict);
        dBtn.style.backgroundColor = isDistAct ? "#ffffff" : "transparent";
        dBtn.style.color = isDistAct ? "#b45309" : "#475569";
        dBtn.style.borderColor = isDistAct ? "#cbd5e1" : "transparent";
        dBtn.style.fontWeight = isDistAct ? "700" : "600";
      }}

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

      // 更新 3 秒避坑指南文字
      var note = STRATEGY_NOTES[currentCity] || STRATEGY_NOTES["all"];
      document.getElementById("strategyTitle").innerHTML = note.title;
      document.getElementById("strategyBody").innerHTML = note.html;
    }}

    function selectCity(city) {{
      currentCity = city;
      currentDistrict = "all";
      updateTabStyles();
      applyFilters();
    }}

    function selectDistrict(dist) {{
      currentDistrict = dist;
      updateTabStyles();
      applyFilters();
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
      var text = "【" + region + "】" + name + "\\n必點：" + dish + "\\n地址：" + address;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).then(function() {{
          showToast("已複製：" + name);
        }}).catch(function() {{
          showToast("已複製：" + name);
        }});
      }} else {{
        showToast("已複製：" + name);
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
    with open(os.path.join(WEB_DIST_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(web_index_html)

    manifest_data = {
        "name": "台灣私房美食避雷隨身手冊",
        "short_name": "美食避雷手冊",
        "description": f"收錄嘉義市與臺南市 {len(all_stores)} 間在地口碑與避坑指南",
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

    sw_js = """const CACHE_NAME = 'tw-food-guide-v2';
const ASSETS = ['./', './index.html', './seaview.html', './manifest.json'];

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
