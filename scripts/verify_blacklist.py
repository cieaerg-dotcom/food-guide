#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
黑名單與雷店自動比對工具 (verify_blacklist.py)
-----------------------------------------------------------------------------
功能：
1. 讀取 data/blacklist_avoidance_database.json。
2. 比對 data/taiwan_food_guides_unified.json 或指定之 JSON 檔案。
3. 若發現任何現有店家命中黑名單，輸出警告並建議剔除或標示避雷。
=============================================================================
"""

import json
import os
import sys

BASE_DIR = "/Users/mac/AGY本地工作區/專案資料夾/美食景點整理"
BLACKLIST_FILE = os.path.join(BASE_DIR, "data", "blacklist_avoidance_database.json")
UNIFIED_FILE = os.path.join(BASE_DIR, "data", "taiwan_food_guides_unified.json")

def audit(target_file=UNIFIED_FILE):
    if not os.path.exists(BLACKLIST_FILE):
        print(f"錯誤：找不到黑名單數據庫: {BLACKLIST_FILE}")
        return

    with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
        blacklist = json.load(f)

    with open(target_file, "r", encoding="utf-8") as f:
        stores = json.load(f)

    print(f"開始執行黑名單比對：目標清單共 {len(stores)} 間店家，黑名單基準共 {len(blacklist)} 間...")

    hits = []
    for s in stores:
        sname = s.get("name", "")
        scity = s.get("city", "")
        for b in blacklist:
            bname = b.get("name", "")
            aliases = b.get("aliases", [bname])
            for alias in aliases:
                if len(alias) >= 2 and alias in sname:
                    hits.append({
                        "store_uid": s.get("uid"),
                        "store_name": sname,
                        "store_city": scity,
                        "blacklist_id": b.get("bid"),
                        "blacklist_name": bname,
                        "severity": b.get("severity"),
                        "matched_alias": alias
                    })
                    break

    if hits:
        print(f"\n⚠️ 警報！共發現 {len(hits)} 間店家命中踩雷黑名單：")
        for h in hits:
            print(f" - [{h['store_uid']}] {h['store_city']} {h['store_name']} 命中黑名單 [{h['blacklist_name']}] (嚴重度: {h['severity']})")
    else:
        print("\n✅ 安全！目前資料庫中「零店家」命中踩雷黑名單，所有店家皆通過反向雷店過濾審核！")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else UNIFIED_FILE
    audit(target)
