#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
社群踩雷爭議對照與深度核查工具 (check_controversy_reference.py)
-----------------------------------------------------------------------------
功能：
1. 讀取 data/community_controversy_reference.json 爭議對照庫。
2. 比對推薦名單或待審查店家。
3. 【核心原則】：非強制一刀切封殺，而是命中時提示：
   - 脆友指控之具體痛點 (communityPainPoints)
   - 需前往 Google 評論深入核查的維度 (auditFocus)
   - 綜合判斷指引 (judgmentGuideline)
4. 輔助團隊做出立體、客觀、不盲從且實事求是的收錄與避雷決策。
=============================================================================
"""

import json
import os
import sys

BASE_DIR = "/Users/mac/AGY本地工作區/專案資料夾/美食景點整理"
REFERENCE_FILE = os.path.join(BASE_DIR, "data", "community_controversy_reference.json")
UNIFIED_FILE = os.path.join(BASE_DIR, "data", "taiwan_food_guides_unified.json")

def check_store(store_name, reference_data):
    matched = []
    for item in reference_data:
        aliases = item.get("aliases", [item.get("name")])
        for alias in aliases:
            if len(alias) >= 2 and alias in store_name:
                matched.append(item)
                break
    return matched

def audit(target_file=UNIFIED_FILE):
    if not os.path.exists(REFERENCE_FILE):
        print(f"錯誤：找不到爭議對照庫: {REFERENCE_FILE}")
        return

    with open(REFERENCE_FILE, "r", encoding="utf-8") as f:
        references = json.load(f)

    with open(target_file, "r", encoding="utf-8") as f:
        stores = json.load(f)

    print(f"📊 執行社群爭議對照分析：待審查清單共 {len(stores)} 間店家，爭議基準共 {len(references)} 間...\n")

    hits = []
    for s in stores:
        sname = s.get("name", "")
        matches = check_store(sname, references)
        if matches:
            for m in matches:
                hits.append((s, m))

    if hits:
        print(f"⚠️ 發現 {len(hits)} 筆命中社群踩雷爭議名單，請依以下指引參考 Google 評論進行核查：\n")
        for s, ref in hits:
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"【待審店家】[{s.get('uid')}] {s.get('city')}{s.get('district')} {s.get('name')}")
            print(f"【爭議項目】{ref.get('name')} ({ref.get('id')})")
            print(f"【脆友痛點】{ref.get('communityPainPoints')}")
            print(f"【Google評論核查重點】{ref.get('auditFocus')}")
            print(f"【綜合判斷建議】{ref.get('judgmentGuideline')}")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    else:
        print("✅ 目前收錄清單無命中重大社群踩雷爭議名單。")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else UNIFIED_FILE
    audit(target)
