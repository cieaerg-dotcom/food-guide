#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Threads Thread & Replies Full Extractor
抓取 Threads 貼文、串文（Self-thread）與所有多頁留言回覆。
"""

import sys
import os
import re
import json
import ssl
import html as html_lib
import urllib.request
import urllib.parse
import argparse

CTX = ssl._create_unverified_context()
GRAPHQL_URL = "https://www.threads.net/api/graphql"

def resolve_url(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15"}
    )
    with urllib.request.urlopen(req, context=CTX) as resp:
        return resp.geturl()

def fetch_bot_html(target_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8"
    }
    req = urllib.request.Request(target_url, headers=headers)
    with urllib.request.urlopen(req, context=CTX) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def parse_initial_meta(html):
    lsd_match = re.findall(r'"LSD",\[\],\{"token":"([^"]+)"', html)
    lsd = lsd_match[0] if lsd_match else None
    
    app_id_match = re.findall(r'"APP_ID":"([^"]+)"', html)
    app_id = app_id_match[0] if app_id_match else "238260118697367"
    
    pos = html.find("adp_BarcelonaPostPageDownwardQueryRelayPreloader")
    variables = None
    query_id = None
    if pos != -1:
        vpos = html.find('"variables":', pos)
        if vpos != -1:
            sub = html[vpos + len('"variables":'):]
            decoder = json.JSONDecoder()
            variables, _ = decoder.raw_decode(sub)
        qpos = html.find('"queryID":"', pos)
        if qpos != -1:
            query_id = html[qpos + 11:].split('"')[0]
            
    return lsd, app_id, variables, query_id

def fetch_graphql_page(lsd, app_id, variables, query_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "x-ig-app-id": app_id,
        "x-fb-lsd": lsd,
        "content-type": "application/x-www-form-urlencoded",
        "sec-fetch-site": "same-origin",
    }
    data = urllib.parse.urlencode({
        "lsd": lsd,
        "variables": json.dumps(variables),
        "doc_id": query_id
    }).encode("utf-8")
    
    req = urllib.request.Request(GRAPHQL_URL, data=data, headers=headers)
    with urllib.request.urlopen(req, context=CTX) as resp:
        return json.loads(resp.read().decode("utf-8"))

def extract_posts_from_node(node, container):
    if not node:
        return
    if "posts" in node:
        for p in node["posts"]["edges"]:
            pn = p["node"]
            user = pn.get("user", {}).get("username", "")
            caption = pn.get("caption")
            text = caption.get("text", "") if caption else ""
            likes = pn.get("like_count", 0)
            container.append({
                "username": user,
                "text": text,
                "likes": likes
            })

def main():
    parser = argparse.ArgumentParser(description="Threads 貼文與回覆完整擷取工具")
    parser.add_argument("--url", required=True, help="Threads 貼文或分享網址")
    parser.add_argument("--output", required=True, help="儲存結果的 JSON 檔案路徑")
    args = parser.parse_args()

    resolved = resolve_url(args.url)
    print(f"解析目標網址: {resolved}")
    html = fetch_bot_html(resolved)
    
    lsd, app_id, variables, query_id = parse_initial_meta(html)
    if not (lsd and variables and query_id):
        print("無法從頁面提取必要的 GraphQL Token 與參數", file=sys.stderr)
        sys.exit(1)

    all_items = []
    
    # 提取主貼文內容（避免 DownwardQuery 僅返回串文回覆而遺漏編號 1~9 主文）
    og_desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html)
    og_title_match = re.search(r'<meta property="og:title" content="[^"]*?\(@([^)]+)\)', html)
    if og_desc_match:
        main_author = og_title_match.group(1) if og_title_match else "main_author"
        main_text = html_lib.unescape(og_desc_match.group(1))
        all_items.append({
            "username": main_author,
            "text": main_text,
            "likes": 0,
            "source": "main_post"
        })
    
    # 抓取第一頁
    page_data = fetch_graphql_page(lsd, app_id, variables, query_id)
    app_info = page_data.get("data", {}).get("media", {}).get("text_post_app_info", {})
    
    # 作者串文 (Self-Thread)
    self_thread = app_info.get("self_thread")
    if self_thread:
        extract_posts_from_node(self_thread, all_items)
        
    # 直接留言
    direct_replies = app_info.get("direct_replies", {})
    for edge in direct_replies.get("edges", []):
        extract_posts_from_node(edge.get("node"), all_items)
        
    # 分頁迴圈
    pinfo = direct_replies.get("page_info", {})
    page_num = 1
    while pinfo.get("has_next_page"):
        page_num += 1
        variables["after"] = pinfo.get("end_cursor")
        try:
            next_page = fetch_graphql_page(lsd, app_id, variables, query_id)
            next_app_info = next_page.get("data", {}).get("media", {}).get("text_post_app_info", {})
            next_direct = next_app_info.get("direct_replies", {})
            edges = next_direct.get("edges", [])
            if not edges:
                break
            for edge in edges:
                extract_posts_from_node(edge.get("node"), all_items)
            pinfo = next_direct.get("page_info", {})
            if page_num > 15:
                break
        except Exception as e:
            print(f"分頁抓取異常 (Page {page_num}): {e}", file=sys.stderr)
            break

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"total": len(all_items), "items": all_items}, f, ensure_ascii=False, indent=2)

    print(f"成功擷取 {len(all_items)} 則串文與留言，已存至: {args.output}")

if __name__ == "__main__":
    main()
