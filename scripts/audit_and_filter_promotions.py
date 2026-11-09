#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
防商業互捧與店家自薦過濾審核腳本 (audit_and_filter_promotions.py)
-----------------------------------------------------------------------------
功能：
1. 踢除社群洗版中的大型連鎖品牌、粗飽型批發小火鍋（如 MINI.D COFFEE、九星級鍋物）。
2. 針對店家親友團互 tag、官方自介店家（如鄉寓食事所、旭更廚房、樸拾等），
   客觀注入真實負評警示、排隊溢價預警、環境吵雜度與名不符實提醒。
3. 確保手冊維持「在地老饕真實口碑與嚴苛避雷」的最高純度。
=============================================================================
"""

import json
import os

BASE_DIR = "/Users/mac/AGY本地工作區/專案資料夾/美食景點整理"
UNIFIED_JSON = os.path.join(BASE_DIR, "data", "taiwan_food_guides_unified.json")

# 應踢除之店家名單（理由：大型連鎖加盟、粗飽批發型、非在地私房老饕級）
REMOVE_PATTERNS = [
    "九星級精緻鍋物",  # 平價批發百元火鍋，靠泡麵冰品吃到飽，非老饕私房
    "MINI.D COFFEE",  # 多那之連鎖集團網美店，標準化批發豆與甜點，非獨立特色店
]

# 需注入「去商業水軍／去店家自吹濾網」真實避雷警示之店家
CRITICAL_AUDIT_UPDATES = {
    "鄉寓食事所": {
        "tips": "【⚠️ 社群自介與親友互捧預警】Threads 串文常見店家官方帳號自薦與熟客 tag 拉抬！本質為『日式文青家常簡餐』，非頂級神級日料。健康路路段極難停車，店內座位少、尖峰期經常需要排隊；出餐速度較慢，若排隊超過 20 分鐘建議果斷轉往他處，理性看待切勿期望過高。",
        "rating": "日式家常定食 / 社群自推行銷多需理性看待"
    },
    "旭更廚房 (SHIU GENG KITCHEN)": {
        "tips": "【⚠️ 網美包裝與溢價預警】店內老件裝潢極具拍照優勢，但整體定位偏『網美早午餐簡餐』，套餐價位在新營偏高（約 300～400 元），份量對食量大者略顯精巧。客滿時空間偏吵雜、桌距較近；若純粹追求在地高 CP 值台菜老店者容易有期待落差；務必先電話訂位再前往。",
        "rating": "4.8 星復古美店 / 偏網美早午餐高價位"
    },
    "樸拾 (Pu Shi 日式料理)": {
        "tips": "【⚠️ 排隊成本與座位極少警示】脆友狂推的『鮭魚火焰捲』桌邊炙燒視覺效果佳，但全店【僅約 10 席吧檯位】且【嚴格不接電話訂位、一律現場排】。尖峰期常需等候 40～60 分鐘，對 3 人以上家庭朋友聚會極不友善；本質為精緻老屋丼飯小食，非高級懷石割烹，請衡量排隊時間成本。",
        "rating": "老屋炙燒生魚丼 / 僅10席吧檯無訂位排隊長"
    },
    "卓也灶腳 (卓也灶咖)": {
        "tips": "【⚠️ 真實口味與定價預警】主打無味精、原型食物清淡健康路線，重口味老饕常反應『湯頭太淡無味』；且在新營屬於中間偏高的精緻簡餐定價。適合長輩或偏好健康養生族群，重油重香愛好者請慎入；假日務必提前訂位。",
        "rating": "4.5 星庭園簡餐 / 口味偏清淡養生價格偏高"
    },
    "520窯烤 (復興店)": {
        "tips": "【⚠️ 夜市攤型串燒避雷】本質為街邊窯烤串燒攤，非精緻無煙日式串燒店。刷醬口味屬於台南傳統偏甜重鹹走向，先炸後烤若火候稍有不慎易顯油膩；出單速度受限於窯烤爐，現場買常需等候半小時以上，建議務必先電話預訂。",
        "rating": "台式窯烤串燒 / 醬汁偏甜重鹹現場等候久"
    }
}

def main():
    with open(UNIFIED_JSON, "r", encoding="utf-8") as f:
        stores = json.load(f)

    original_len = len(stores)
    filtered_stores = []

    for s in stores:
        # 1. 檢查是否符合踢除黑名單
        should_remove = False
        for pat in REMOVE_PATTERNS:
            if pat in s["name"]:
                print(f"🗑️ 剔除商業水軍/連鎖粗飽店: [{s['uid']}] {s['name']}")
                should_remove = True
                break
        if should_remove:
            continue

        # 2. 檢查是否需注入批判性避坑預警
        for target_name, audit_data in CRITICAL_AUDIT_UPDATES.items():
            if target_name in s["name"]:
                s["tips"] = audit_data["tips"]
                s["rating"] = audit_data["rating"]
                print(f"🔍 注入去水軍批判性避雷: [{s['uid']}] {s['name']}")

        filtered_stores.append(s)

    # 3. 重新編排臺南市店家的 UID 確保無斷號
    tn_count = 1
    for s in filtered_stores:
        if s.get("city") == "臺南市":
            s["uid"] = f"TN-{tn_count:02d}"
            tn_count += 1

    with open(UNIFIED_JSON, "w", encoding="utf-8") as f:
        json.dump(filtered_stores, f, ensure_ascii=False, indent=2)

    print(f"\n審核完成！原收錄 {original_len} 間 ➔ 剔除後純淨版 {len(filtered_stores)} 間 (臺南共 {tn_count - 1} 間)")

if __name__ == "__main__":
    main()
