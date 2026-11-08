#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
全台看海放空旅宿隨身手冊 生成器 (build_seaview_guide.py)
-----------------------------------------------------------------------------
功能說明：
1. 讀取 data/taiwan_seaview_stays_structured.json 結構化資料。
2. 產出 100% 離線可用、極簡蔚藍海洋設計風格、支援手機/平板/電腦的互動手冊。
3. 提供縣市快捷分區、看海情境標籤篩選、關鍵字全文即時搜尋、一鍵 Google Maps 導航。
4. 輸出至「全台看海放空旅宿隨身手冊.html」及「web_dist/seaview.html」。
=============================================================================
"""

import json
import os
import html
import urllib.parse

def load_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def render_stay_card(s):
    uid = html.escape(s.get('uid', ''))
    name = html.escape(s.get('name', ''))
    city = html.escape(s.get('city', ''))
    district = html.escape(s.get('district', ''))
    area = html.escape(s.get('area', ''))
    stype = html.escape(s.get('type', '海景旅宿'))
    vibe = html.escape(s.get('vibeTag', '看海放空'))
    likes = html.escape(s.get('likes', ''))
    price = html.escape(s.get('priceLevel', '親民平價'))
    seaview = html.escape(s.get('seaViewFeature', ''))
    address = html.escape(s.get('address', ''))
    tips = html.escape(s.get('stayTips', ''))
    map_q = s.get('mapQuery') or f"{city}{district} {name}"
    map_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(map_q)}"
    
    # 亮點列表
    hl_html = "".join([f"<li>{html.escape(h)}</li>" for h in s.get('highlights', [])])
    
    # 設備標籤
    amenities = s.get('amenities', [])
    amen_html = "".join([f'<span class="amen-tag">{html.escape(a)}</span>' for a in amenities])
    
    solo_badge = '<span class="badge badge-solo">一人獨旅極推</span>' if s.get('soloFriendly') else ''
    
    return f"""
    <div class="stay-card" data-city="{city}" data-district="{district}" data-vibe="{vibe}" data-solo="{str(s.get('soloFriendly')).lower()}" data-search="{name.lower()} {city} {district} {area} {seaview.lower()} {tips.lower()}">
      <div class="card-top">
        <div class="location-cluster">
          <span class="region-pill">{city} · {district}</span>
          <span class="area-pill">{area}</span>
        </div>
        <div class="likes-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
          {likes} 讚推
        </div>
      </div>
      
      <div class="card-header">
        <h3 class="stay-name">{name}</h3>
        <div class="stay-meta">
          <span class="badge badge-type">{stype}</span>
          <span class="badge badge-vibe">{vibe}</span>
          {solo_badge}
        </div>
      </div>

      <div class="price-box">
        <span class="price-icon">💰</span>
        <span class="price-val">{price}</span>
      </div>

      <div class="seaview-feature">
        <div class="feature-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
          起床看海視覺體驗
        </div>
        <p class="feature-desc">{seaview}</p>
      </div>

      <div class="highlights-box">
        <div class="box-label">脆友精選口碑亮點：</div>
        <ul class="highlight-list">
          {hl_html}
        </ul>
      </div>

      <div class="amen-container">
        {amen_html}
      </div>

      {f'''<div class="tips-box">
        <span class="tips-tag">放空與避坑建議</span>
        <p class="tips-text">{tips}</p>
      </div>''' if tips else ''}

      <div class="card-footer">
        <span class="address-text" title="{address}">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
          {address}
        </span>
        <a href="{map_url}" target="_blank" rel="noopener noreferrer" class="nav-btn">
          <span>開啟導航</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
        </a>
      </div>
    </div>
    """

def generate_html(stays, output_path, is_web_dist=False):
    total_count = len(stays)
    food_link = "index.html" if is_web_dist else "美食避雷隨身手冊.html"
    
    # 計算各縣市數量
    city_counts = {}
    for s in stays:
        c = s.get('city', '其他')
        city_counts[c] = city_counts.get(c, 0) + 1
        
    cities_sorted = sorted(city_counts.items(), key=lambda x: -x[1])
    
    # 渲染所有旅宿卡片
    cards_html = "\n".join([render_stay_card(s) for s in stays])
    
    # 縣市按鈕
    city_tabs_html = f'<button class="tab-btn active" data-city="all">全部縣市 ({total_count})</button>'
    for c, cnt in cities_sorted:
        city_tabs_html += f'<button class="tab-btn" data-city="{c}">{c} ({cnt})</button>'

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>全台看海放空旅宿隨身手冊 🌊 醒來即是大海</title>
  <style>
    :root {{
      --bg-ocean: #f0f7fa;
      --card-bg: #ffffff;
      --text-main: #1e293b;
      --text-muted: #64748b;
      --accent-deep-blue: #0284c7;
      --accent-teal: #0d9488;
      --accent-coral: #f43f5e;
      --border-color: #e2e8f0;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
      --shadow-md: 0 4px 12px rgba(2, 132, 199, 0.08);
      --shadow-lg: 0 10px 25px -5px rgba(2, 132, 199, 0.12);
      --radius: 16px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-tap-highlight-color: transparent;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", "Noto Sans TC", sans-serif;
      background: var(--bg-ocean);
      color: var(--text-main);
      line-height: 1.5;
      padding-bottom: 60px;
    }}

    /* 頂部海浪光影 Header */
    .header {{
      background: linear-gradient(135deg, #0284c7 0%, #0369a1 50%, #0f172a 100%);
      color: #ffffff;
      padding: 40px 20px 28px;
      text-align: center;
      position: relative;
      overflow: hidden;
    }}

    .header::after {{
      content: "";
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 16px;
      background: var(--bg-ocean);
      border-radius: 20px 20px 0 0;
    }}

    .header-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(255, 255, 255, 0.18);
      backdrop-filter: blur(8px);
      padding: 4px 14px;
      border-radius: 30px;
      font-size: 0.85rem;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
      border: 1px solid rgba(255, 255, 255, 0.25);
    }}

    .header h1 {{
      font-size: 1.75rem;
      font-weight: 800;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }}

    .header p {{
      font-size: 0.95rem;
      color: #e0f2fe;
      max-width: 600px;
      margin: 0 auto;
    }}

    /* 控制面板區 */
    .sticky-controls {{
      position: sticky;
      top: 0;
      z-index: 50;
      background: rgba(240, 247, 250, 0.95);
      backdrop-filter: blur(12px);
      padding: 12px 16px;
      border-bottom: 1px solid var(--border-color);
    }}

    .search-wrapper {{
      max-width: 760px;
      margin: 0 auto 10px;
      position: relative;
    }}

    .search-input {{
      width: 100%;
      height: 44px;
      padding: 0 40px 0 42px;
      border-radius: 12px;
      border: 1.5px solid #cbd5e1;
      background: #ffffff;
      font-size: 0.95rem;
      outline: none;
      transition: all 0.2s;
    }}

    .search-input:focus {{
      border-color: var(--accent-deep-blue);
      box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
    }}

    .search-icon {{
      position: absolute;
      left: 14px;
      top: 13px;
      color: var(--text-muted);
    }}

    .clear-btn {{
      position: absolute;
      right: 12px;
      top: 11px;
      background: none;
      border: none;
      color: #94a3b8;
      cursor: pointer;
      display: none;
    }}

    /* 縣市分頁標籤 */
    .filter-tabs-wrapper {{
      max-width: 760px;
      margin: 0 auto 8px;
      display: flex;
      gap: 8px;
      overflow-x: auto;
      scrollbar-width: none;
      -webkit-overflow-scrolling: touch;
      padding-bottom: 2px;
    }}
    .filter-tabs-wrapper::-webkit-scrollbar {{ display: none; }}

    .tab-btn {{
      flex-shrink: 0;
      padding: 6px 14px;
      border-radius: 20px;
      border: 1px solid #cbd5e1;
      background: #ffffff;
      color: var(--text-main);
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .tab-btn.active {{
      background: var(--accent-deep-blue);
      color: #ffffff;
      border-color: var(--accent-deep-blue);
      box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);
    }}

    /* 情境篩選 Pill */
    .vibe-pills-wrapper {{
      max-width: 760px;
      margin: 0 auto;
      display: flex;
      gap: 6px;
      overflow-x: auto;
      scrollbar-width: none;
    }}
    .vibe-pills-wrapper::-webkit-scrollbar {{ display: none; }}

    .vibe-pill {{
      flex-shrink: 0;
      padding: 4px 10px;
      border-radius: 8px;
      background: #e2e8f0;
      color: #475569;
      font-size: 0.78rem;
      cursor: pointer;
      transition: all 0.15s;
    }}

    .vibe-pill.active {{
      background: #0284c7;
      color: #ffffff;
    }}

    /* 卡片清單網格 */
    .container {{
      max-width: 760px;
      margin: 16px auto;
      padding: 0 16px;
    }}

    .stats-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      font-size: 0.85rem;
      color: var(--text-muted);
    }}

    .grid {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    /* 單張卡片樣式 */
    .stay-card {{
      background: var(--card-bg);
      border-radius: var(--radius);
      padding: 20px;
      box-shadow: var(--shadow-sm);
      border: 1px solid var(--border-color);
      transition: transform 0.2s, box-shadow 0.2s;
    }}

    .stay-card:hover {{
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
      border-color: #bae6fd;
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }}

    .location-cluster {{
      display: flex;
      gap: 6px;
    }}

    .region-pill {{
      font-size: 0.75rem;
      font-weight: 600;
      color: #0369a1;
      background: #e0f2fe;
      padding: 2px 8px;
      border-radius: 6px;
    }}

    .area-pill {{
      font-size: 0.75rem;
      color: #475569;
      background: #f1f5f9;
      padding: 2px 8px;
      border-radius: 6px;
    }}

    .likes-badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.75rem;
      font-weight: 700;
      color: #e11d48;
      background: #ffe4e6;
      padding: 2px 8px;
      border-radius: 12px;
    }}

    .card-header {{
      margin-bottom: 10px;
    }}

    .stay-name {{
      font-size: 1.25rem;
      font-weight: 700;
      color: #0f172a;
      line-height: 1.3;
      margin-bottom: 6px;
    }}

    .stay-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}

    .badge {{
      font-size: 0.72rem;
      padding: 2px 7px;
      border-radius: 4px;
      font-weight: 500;
    }}

    .badge-type {{
      background: #f0fdf4;
      color: #166534;
      border: 1px solid #bbf7d0;
    }}

    .badge-vibe {{
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
    }}

    .badge-solo {{
      background: #fdf2f8;
      color: #be185d;
      border: 1px solid #fbcfe8;
    }}

    .price-box {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: #f8fafc;
      padding: 6px 10px;
      border-radius: 8px;
      font-size: 0.85rem;
      color: #334155;
      margin-bottom: 12px;
    }}

    .seaview-feature {{
      background: linear-gradient(135deg, #f0fdfa 0%, #e0f2fe 100%);
      border: 1px solid #bae6fd;
      border-radius: 10px;
      padding: 10px 12px;
      margin-bottom: 12px;
    }}

    .feature-title {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.82rem;
      font-weight: 700;
      color: #0284c7;
      margin-bottom: 4px;
    }}

    .feature-desc {{
      font-size: 0.88rem;
      color: #0f172a;
      line-height: 1.45;
    }}

    .highlights-box {{
      margin-bottom: 12px;
    }}

    .box-label {{
      font-size: 0.78rem;
      font-weight: 600;
      color: #64748b;
      margin-bottom: 5px;
    }}

    .highlight-list {{
      padding-left: 18px;
      font-size: 0.86rem;
      color: #334155;
    }}

    .highlight-list li {{
      margin-bottom: 3px;
    }}

    .amen-container {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 12px;
    }}

    .amen-tag {{
      font-size: 0.72rem;
      color: #475569;
      background: #f1f5f9;
      padding: 2px 7px;
      border-radius: 4px;
    }}

    .tips-box {{
      background: #fffbeb;
      border-left: 3px solid #f59e0b;
      padding: 8px 10px;
      border-radius: 0 8px 8px 0;
      margin-bottom: 14px;
      font-size: 0.82rem;
    }}

    .tips-tag {{
      display: inline-block;
      font-weight: 700;
      color: #b45309;
      margin-bottom: 2px;
    }}

    .tips-text {{
      color: #78350f;
      line-height: 1.4;
    }}

    .card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 10px;
      border-top: 1px solid #f1f5f9;
      font-size: 0.82rem;
    }}

    .address-text {{
      color: #64748b;
      display: flex;
      align-items: center;
      gap: 4px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      max-width: 60%;
    }}

    .nav-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #0284c7;
      color: #ffffff;
      text-decoration: none;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      transition: background 0.15s;
    }}

    .nav-btn:hover {{
      background: #0369a1;
    }}

    .empty-state {{
      text-align: center;
      padding: 60px 20px;
      color: var(--text-muted);
      display: none;
    }}

    /* 底部手冊切換浮動條 */
    .bottom-nav-bar {{
      position: fixed;
      bottom: 12px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.9);
      backdrop-filter: blur(10px);
      padding: 6px 14px;
      border-radius: 30px;
      display: flex;
      gap: 12px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.25);
      z-index: 100;
    }}

    .nav-link-btn {{
      color: #cbd5e1;
      text-decoration: none;
      font-size: 0.8rem;
      padding: 4px 10px;
      border-radius: 20px;
      transition: all 0.2s;
    }}

    .nav-link-btn.active {{
      background: #0284c7;
      color: #ffffff;
      font-weight: 600;
    }}
  </style>
</head>
<body>

  <header class="header">
    <div class="header-badge">🌊 醒來即是大海 · 靜心放空精選</div>
    <h1>全台看海放空旅宿隨身手冊</h1>
    <p>收錄 Threads 萬人共鳴推薦：起床即是太平洋與台灣海峽，適合一個人的療癒發呆之旅</p>
  </header>

  <div class="sticky-controls">
    <div class="search-wrapper">
      <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <input type="text" id="searchInput" class="search-input" placeholder="搜尋旅宿、海景特色、鄉鎮、亮點...">
      <button id="clearBtn" class="clear-btn">✕</button>
    </div>

    <div class="filter-tabs-wrapper" id="cityTabs">
      {city_tabs_html}
    </div>

    <div class="vibe-pills-wrapper" id="vibePills">
      <span class="vibe-pill active" data-vibe="all">全部氛圍</span>
      <span class="vibe-pill" data-vibe="solo">限一人獨旅</span>
      <span class="vibe-pill" data-vibe="浴缸">海景浴缸</span>
      <span class="vibe-pill" data-vibe="泳池">無邊際泳池</span>
      <span class="vibe-pill" data-vibe="日出">看日出</span>
      <span class="vibe-pill" data-vibe="沙灘">直通沙灘</span>
    </div>
  </div>

  <div class="container">
    <div class="stats-bar">
      <span>目前顯示：<strong id="visibleCount">{total_count}</strong> 間看海放空旅宿</span>
      <span>全離線單檔 · 支援一鍵導航</span>
    </div>

    <div class="grid" id="staysGrid">
      {cards_html}
    </div>

    <div class="empty-state" id="emptyState">
      <h3>沒有找到相符的看海旅宿</h3>
      <p style="margin-top:6px;">試著清除搜尋條件或選擇「全部縣市」</p>
    </div>
  </div>

  <div class="bottom-nav-bar">
    <a href="{food_link}" class="nav-link-btn">🍲 美食隨身手冊</a>
    <a href="javascript:void(0)" class="nav-link-btn active">🌊 看海旅宿手冊 ({total_count})</a>
  </div>

  <script>
    const searchInput = document.getElementById('searchInput');
    const clearBtn = document.getElementById('clearBtn');
    const cityTabs = document.querySelectorAll('.tab-btn');
    const vibePills = document.querySelectorAll('.vibe-pill');
    const cards = document.querySelectorAll('.stay-card');
    const visibleCount = document.getElementById('visibleCount');
    const emptyState = document.getElementById('emptyState');

    let currentCity = 'all';
    let currentVibe = 'all';

    function filterStays() {{
      const query = searchInput.value.trim().toLowerCase();
      clearBtn.style.display = query ? 'block' : 'none';
      let count = 0;

      cards.forEach(card => {{
        const cardCity = card.getAttribute('data-city');
        const cardSearch = card.getAttribute('data-search');
        const cardVibe = card.getAttribute('data-vibe');
        const cardSolo = card.getAttribute('data-solo') === 'true';

        // 縣市篩選
        const matchCity = (currentCity === 'all') || (cardCity === currentCity);

        // 氛圍篩選
        let matchVibe = true;
        if (currentVibe === 'solo') {{
          matchVibe = cardSolo;
        }} else if (currentVibe !== 'all') {{
          matchVibe = cardVibe.includes(currentVibe) || cardSearch.includes(currentVibe);
        }}

        // 關鍵字搜尋
        const matchSearch = !query || cardSearch.includes(query);

        if (matchCity && matchVibe && matchSearch) {{
          card.style.display = 'block';
          count++;
        }} else {{
          card.style.display = 'none';
        }}
      }});

      visibleCount.textContent = count;
      emptyState.style.display = count === 0 ? 'block' : 'none';
    }}

    searchInput.addEventListener('input', filterStays);
    clearBtn.addEventListener('click', () => {{
      searchInput.value = '';
      filterStays();
      searchInput.focus();
    }});

    cityTabs.forEach(tab => {{
      tab.addEventListener('click', () => {{
        cityTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentCity = tab.getAttribute('data-city');
        filterStays();
      }});
    }});

    vibePills.forEach(pill => {{
      pill.addEventListener('click', () => {{
        vibePills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        currentVibe = pill.getAttribute('data-vibe');
        filterStays();
      }});
    }});
  </script>
</body>
</html>
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ 看海放空旅宿手冊已生成：{output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "data", "taiwan_seaview_stays_structured.json")
    out_html = os.path.join(base_dir, "全台看海放空旅宿隨身手冊.html")
    dist_html = os.path.join(base_dir, "web_dist", "seaview.html")
    
    os.makedirs(os.path.join(base_dir, "web_dist"), exist_ok=True)
    
    stays = load_data(json_path)
    generate_html(stays, out_html, is_web_dist=False)
    generate_html(stays, dist_html, is_web_dist=True)
