#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Food Guide App Generator
將結構化店家資料填入行動友善的單檔離線 Web App 範本。
"""

import os
import sys
import json
import argparse

TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), "..", "templates", "guide_app_template.html")

def generate_html(data_json_path, output_html_path, title, subtitle, region, badge="在地私房精選", theme_color="#d97706"):
    with open(data_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    stores = data if isinstance(data, list) else data.get("stores", [])
    
    # 統計各類別
    categories = []
    for s in stores:
        c = s.get("category", "其他")
        if c not in categories:
            categories.append(c)

    cat_buttons = []
    for c in categories:
        count = sum(1 for s in stores if s.get("category") == c)
        cat_buttons.append(f'<button class="filter-btn" data-cat="{c}">{c} ({count})</button>')
        
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        tpl = f.read()

    rendered = tpl.replace("{{TITLE}}", title)
    rendered = rendered.replace("{{SUBTITLE}}", subtitle)
    rendered = rendered.replace("{{HEADER_BADGE}}", badge)
    rendered = rendered.replace("{{THEME_COLOR}}", theme_color)
    rendered = rendered.replace("{{REGION_NAME}}", region)
    rendered = rendered.replace("{{CATEGORY_BUTTONS}}", "\n      ".join(cat_buttons))
    rendered = rendered.replace("{{STORES_JSON}}", json.dumps(stores, ensure_ascii=False, indent=2))
    
    os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(rendered)
        
    print(f"成功產生美食手冊 Web App: {output_html_path} (共 {len(stores)} 間店家)")

def main():
    parser = argparse.ArgumentParser(description="產生行動版美食隨身手冊 HTML")
    parser.add_argument("--input", required=True, help="結構化店家 JSON 檔案")
    parser.add_argument("--output", required=True, help="輸出的 HTML 檔案路徑")
    parser.add_argument("--title", required=True, help="手冊大標題")
    parser.add_argument("--subtitle", required=True, help="副標題")
    parser.add_argument("--region", default="", help="城市或行政區名稱（供 Google 地圖查詢前綴）")
    parser.add_argument("--badge", default="在地私房精選", help="頂部小標籤")
    parser.add_argument("--color", default="#d97706", help="主題顏色色碼")
    args = parser.parse_args()

    generate_html(args.input, args.output, args.title, args.subtitle, args.region, args.badge, args.color)

if __name__ == "__main__":
    main()
